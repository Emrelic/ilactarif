"""Canlı Medula izleyici — gerçek demo.

KULLANIM:
  1) Botanik EOS'u açın, içinden Medula'ya giriş yapın.
  2) Bu scripti çalıştırın:  python scripts/watch_medula.py
  3) Medula'da bir hastanın e-reçetesini açın (E-Reçete Sorgu → seç → Detay).
  4) Sistem detay sayfasını görür görmez:
     - Konsola hasta + ilaç + doz bilgilerini yazar
     - Etiket önizleme HTML'ini üretir ve tarayıcıda açar
  5) Ctrl+C ile durdurun.
"""
from __future__ import annotations

import datetime
import json
import logging
import sys
import time
import webbrowser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("watch")

from ilactarif.db import get_connection, init_schema  # noqa: E402
from ilactarif.drug_guess import (  # noqa: E402
    build_kullanim_talimati,
    guess_form,
    guess_kategori,
    guess_unit,
)
from ilactarif.label_render import (  # noqa: E402
    render_preparation_label,
    render_usage_label,
    render_warning_label,
)
from ilactarif.medula_parser import PrescriptionCapture  # noqa: E402
from ilactarif.medula_watcher import MedulaWatcher  # noqa: E402
from ilactarif.models import (  # noqa: E402
    PreparationLabel,
    UsageLabel,
    WarningLabel,
)


PREVIEW_DIR = ROOT / "data" / "live_preview"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# DB'deki tarif bilgileriyle birleştir — yoksa Medula'dan gelenle minimum üret
# ---------------------------------------------------------------------------
def lookup_db_drug(conn, barkod: str, ad: str):
    """Barkod yoksa adı ile fuzzy ara."""
    if barkod:
        row = conn.execute("SELECT * FROM drugs WHERE barcode = ?", (barkod,)).fetchone()
        if row:
            return row
    # Ad ile arama: ilaç adı kelimelerinin ilkini al
    first_word = (ad or "").split(" ")[0]
    if not first_word:
        return None
    row = conn.execute(
        "SELECT * FROM drugs WHERE name LIKE ? ORDER BY sales_count DESC LIMIT 1",
        (f"{first_word}%",),
    ).fetchone()
    return row


def db_label(conn, drug_id: int, label_type: int):
    row = conn.execute(
        "SELECT content_json FROM drug_labels WHERE drug_id=? AND label_type=?",
        (drug_id, label_type),
    ).fetchone()
    if not row:
        return None
    try:
        return json.loads(row["content_json"])
    except Exception:
        return None


# ---------------------------------------------------------------------------
# E-reçete yakalandığında: etiket görselleri üret + HTML rapor + aç
# ---------------------------------------------------------------------------
def handle_recete(cap: PrescriptionCapture, html: str) -> None:
    log.info("YAKALANDI: %s — hasta=%s, ilaç=%d, dr=%s",
             cap.recete_no, cap.hasta_ad, len(cap.drugs), cap.dr_ad)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Ham HTML'i kaydet (debug için)
    (PREVIEW_DIR / f"raw_{ts}_{cap.recete_no}.html").write_text(html, encoding="utf-8")

    with get_connection() as conn:
        init_schema(conn)
        s = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings")}
        eczane_adi = s.get("eczane_adi", "İKİZLER ECZANESİ")
        eczane_tel = s.get("eczane_telefon", "")

        # Reçete tarihinden Python date çevir
        try:
            d, m, y = cap.recete_tarihi.split("/")
            r_date = datetime.date(int(y), int(m), int(d))
        except Exception:
            r_date = datetime.date.today()
        # Adet × günlük kez bilgilerinden sure_gun fallback hesabı (Medula doz × adet)
        def _adet_to_int(s):
            try: return int((s or "").strip())
            except Exception: return None

        items = []
        for drug in cap.drugs:
            # Medula'dan kullanım bilgileri → UsageLabel
            # Doz birimi yoksa ilaç adından tahmin et (damla/tablet/ml vb.)
            birim = drug.doz_birim or guess_unit(drug.ad, drug.kullanim_sekli)
            adet  = drug.doz_birim_adedi
            doz_str = ""
            if adet is not None:
                # 1.0 → "1", 0.5 → "0,5"
                if float(adet).is_integer():
                    adet_s = str(int(adet))
                else:
                    adet_s = f"{adet:.1f}".replace(".", ",")
                doz_str = f"{adet_s} {birim}".strip() if birim else adet_s
            if not doz_str:
                doz_str = drug.doz_ham

            # Etikette basılacak kategori (DB yoksa ilaç adından tahmin)
            kategori = guess_kategori(drug.ad, drug.kullanim_sekli) or guess_form(drug.ad).upper()

            # Otomatik kullanım talimatı (DB doldurulmuş ilaçlar için DB üzerinden override edilecek)
            talimat = build_kullanim_talimati(
                drug_name=drug.ad,
                gunluk_kez=drug.doz_gunluk_kez,
                saat_arasi=None,
                kullanim_zamani=[],
                yemek="",
                doz_str=doz_str,
                kullanim_sekli=drug.kullanim_sekli,
            )

            usage = UsageLabel(
                kategori=kategori,
                kullanim_talimati=talimat,
                uyari_metni="",
                ilac_turu=guess_form(drug.ad),
                doz=doz_str,
                gunluk_kez=drug.doz_gunluk_kez,
                yemek="",
                kullanim_zamani=[],
                kullanim_sekli=drug.kullanim_sekli,
            )
            prep = PreparationLabel(gerekli=False)
            warn = WarningLabel(gerekli=False)

            # DB'de varsa override (ilaç türü, uyarılar bizden)
            db_row = lookup_db_drug(conn, drug.barkod, drug.ad)
            db_match = None
            if db_row:
                db_match = dict(db_row)
                # İlaç türü ve uyarıları DB'den al
                u1 = db_label(conn, db_row["id"], 1)
                u2 = db_label(conn, db_row["id"], 2)
                u3 = db_label(conn, db_row["id"], 3)
                if u1:
                    # Yeni format alanları (DB'den override)
                    if u1.get("kategori"):           usage.kategori = u1["kategori"]
                    if u1.get("kullanim_talimati"): usage.kullanim_talimati = u1["kullanim_talimati"]
                    if u1.get("uyari_metni"):       usage.uyari_metni = u1["uyari_metni"]
                    if u1.get("sure_gun"):          usage.sure_gun = u1["sure_gun"]
                    # Geriye uyumluluk
                    usage.ilac_turu = u1.get("ilac_turu") or usage.ilac_turu
                    if not usage.yemek:        usage.yemek = u1.get("yemek", "")
                    if not usage.ek_not:       usage.ek_not = u1.get("ek_not", "")
                    if not usage.kullanim_zamani: usage.kullanim_zamani = u1.get("kullanim_zamani", []) or []
                    if not usage.sure:         usage.sure = u1.get("sure", "")
                if u2:
                    prep = PreparationLabel(**{**PreparationLabel().__dict__, **u2})
                if u3:
                    warn = WarningLabel(**{**WarningLabel().__dict__, **u3})

            # Bitiş tarihi hesabı:
            #   DB'de sure_gun varsa onu kullan
            #   Yoksa Medula'dan: adet × gunluk_kez^(-1) → tahmini gün
            bitis_date = None
            sure_gun = usage.sure_gun
            if not sure_gun:
                adet = _adet_to_int(drug.adet)
                if adet and drug.doz_gunluk_kez and drug.doz_birim_adedi:
                    # Toplam alınacak doz adedi / günlük alım = gün sayısı
                    total = adet  # 1 kutuda kaç birim olduğu DB'den çıkmaz; basit yaklaşım: adet=gün cinsinden tedavi
                    daily = drug.doz_gunluk_kez * drug.doz_birim_adedi
                    if daily > 0:
                        # Reçete adedi kaç kutu/birim → genel yaklaşım: adet * 10 / daily varsayımı yanlış
                        # Bunun yerine sade: adet kutu olduğunu varsay, 1 kutu ~ 10-20 birim
                        # Belirsizliği bırak, sadece DB sure_gun'a güveniyoruz
                        sure_gun = None
            if sure_gun:
                bitis_date = r_date + datetime.timedelta(days=int(sure_gun))

            # Etiketleri render et
            slug = f"{ts}_{cap.recete_no}_{drug.barkod or drug.ad[:8]}"
            p1 = PREVIEW_DIR / f"{slug}_label1.png"
            render_usage_label(
                hasta_adi=cap.hasta_ad, ilac_adi=drug.ad, label=usage,
                recete_tarihi=r_date, bitis_tarihi=bitis_date,
                eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
            ).save(p1)

            p2 = None
            if prep.gerekli:
                p2 = PREVIEW_DIR / f"{slug}_label2.png"
                render_preparation_label(
                    hasta_adi=cap.hasta_ad, ilac_adi=drug.ad, label=prep,
                    eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
                ).save(p2)

            p3 = None
            if warn.gerekli:
                p3 = PREVIEW_DIR / f"{slug}_label3.png"
                render_warning_label(
                    hasta_adi=cap.hasta_ad, ilac_adi=drug.ad, label=warn,
                    eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
                ).save(p3)

            items.append({
                "drug": drug, "db": db_match,
                "usage": usage, "prep": prep, "warn": warn,
                "p1": p1, "p2": p2, "p3": p3,
            })

    # HTML rapor
    html_out = build_preview_html(cap, items, eczane_adi, eczane_tel)
    out_path = PREVIEW_DIR / f"preview_{ts}_{cap.recete_no}.html"
    out_path.write_text(html_out, encoding="utf-8")
    log.info("Önizleme: %s", out_path)
    webbrowser.open(out_path.as_uri())


def esc(s):
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_preview_html(cap, items, eczane_adi, eczane_tel) -> str:
    lines = ["""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<title>E-Reçete Önizleme — """ + esc(cap.recete_no) + """</title>
<style>
  body { font-family:'Segoe UI', Arial, sans-serif; background:#f3f4f8; margin:0; padding:20px; color:#222;}
  h1 { font-size:22px; margin:0;}
  .hdr { background:#fff; padding:14px 18px; border:1px solid #ddd; border-radius:8px; margin-bottom:16px;}
  .hdr .row { display:flex; gap:24px; flex-wrap:wrap; margin-top:6px; color:#444; font-size:14px;}
  .hdr b { color:#1a4a7c;}
  .drug { background:#fff; border:1px solid #ddd; border-radius:8px; padding:14px 18px; margin-bottom:18px;}
  .drug h2 { margin:0 0 6px; font-size:17px; color:#1a4a7c;}
  .meta { color:#666; font-size:13px; margin-bottom:10px;}
  .labels { display:flex; gap:12px; flex-wrap:wrap;}
  .lab { border:1px solid #ccc; padding:6px; background:#fafafa; border-radius:6px;}
  .lab .cap { font-size:11px; color:#555; margin-bottom:4px; font-weight:600;}
  .lab img { display:block; width:480px; height:320px; border:1px dashed #999;}
  .warn { color:#a00; font-size:12px; font-weight:600;}
  .ok { color:#070; font-size:12px; font-weight:600;}
  .tan { font-size:12px; color:#555; margin-top:6px;}
  details { margin-top:8px; font-size:12px;}
  pre { background:#0f1115; color:#cfe; padding:8px; border-radius:6px; overflow:auto; font-size:11px;}
</style></head><body>"""]
    lines.append('<div class="hdr">')
    lines.append(f"<h1>E-Reçete: <b>{esc(cap.recete_no)}</b></h1>")
    lines.append('<div class="row">')
    lines.append(f"<span><b>Hasta:</b> {esc(cap.hasta_ad)}</span>")
    lines.append(f"<span><b>TC:</b> {esc(cap.hasta_tc)}</span>")
    lines.append(f"<span><b>Tarih:</b> {esc(cap.recete_tarihi)}</span>")
    lines.append(f"<span><b>Doktor:</b> {esc(cap.dr_ad)} ({esc(cap.dr_brans)})</span>")
    lines.append(f"<span><b>Tür:</b> {esc(cap.recete_turu)} / {esc(cap.recete_alt_turu)}</span>")
    lines.append('</div>')
    if cap.tanılar:
        lines.append('<div class="tan"><b>Tanılar:</b> ')
        lines.append(", ".join(f"{esc(k)} {esc(v)}" for k, v in cap.tanılar))
        lines.append('</div>')
    lines.append('</div>')

    for it in items:
        d = it["drug"]
        lines.append('<div class="drug">')
        lines.append(f"<h2>{esc(d.ad)}</h2>")
        meta = []
        if d.barkod: meta.append(f"Barkod {esc(d.barkod)}")
        if d.adet:   meta.append(f"Adet {esc(d.adet)}")
        if d.doz_ham: meta.append(f"Doz: {esc(d.doz_ham)}")
        if d.kullanim_sekli: meta.append(f"Kullanım Şekli: {esc(d.kullanim_sekli)}")
        lines.append(f"<div class='meta'>{' · '.join(meta)}</div>")
        if it["db"]:
            lines.append(f"<div class='ok'>✓ DB eşleşmesi: {esc(it['db']['name'])} (rank #{it['db']['rank']})</div>")
        else:
            lines.append("<div class='warn'>⚠ DB'de bu ilaç için tarif yok — varsayılan etiket basıldı</div>")
        lines.append('<div class="labels">')
        if it["p1"]:
            lines.append(f'<div class="lab"><div class="cap">1 · Kullanım</div><img src="{it["p1"].name}"></div>')
        if it["p2"]:
            lines.append(f'<div class="lab"><div class="cap">2 · Hazırlama</div><img src="{it["p2"].name}"></div>')
        if it["p3"]:
            lines.append(f'<div class="lab"><div class="cap">3 · Uyarı</div><img src="{it["p3"].name}"></div>')
        lines.append('</div></div>')

    lines.append("</body></html>")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Ana döngü
# ---------------------------------------------------------------------------
def main():
    log.info("Watcher başlıyor… Botanik EOS + Medula açık olmalı.")
    log.info("Medula'da bir e-reçete açın → otomatik önizleme açılacak.")
    log.info("Ctrl+C ile durdurun.")
    w = MedulaWatcher(on_recete=handle_recete, interval=1.0)
    w.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Durduruluyor…")
        w.stop()


if __name__ == "__main__":
    main()
