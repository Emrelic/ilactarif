"""PİLOT DEMO — En çok satan birkaç ilaç için etiket önizlemesi.

Amaç: kullanıcı (eczacı) hem veri yapısını hem etiket görünümünü onaylasın.
Bu script demo verisini üretir; gerçek 100'lük dolum bundan sonra Web Search ile yapılır.

Üretilen:
  data/preview/*.png   — her etiket için ayrı PNG
  data/preview/report.html — toplu rapor (varsayılan tarayıcıda açılır)
"""
from __future__ import annotations

import json
import os
import sys
import webbrowser
from datetime import date, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.db import get_connection, init_schema  # noqa: E402
from ilactarif.label_render import (  # noqa: E402
    render_preparation_label,
    render_usage_label,
    render_warning_label,
)
from ilactarif.models import (  # noqa: E402
    PreparationLabel,
    UsageLabel,
    WarningLabel,
    to_dict,
)

PREVIEW_DIR = ROOT / "data" / "preview"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

DEMO_PATIENT = "AYŞE YILMAZ"
TODAY = date(2026, 5, 25)


# ---------------------------------------------------------------------------
# Demo ilaç verileri (Web Search ile doğrulanmış prospektüs bilgileri)
# ---------------------------------------------------------------------------
DEMOS = [
    # 1) ARVELES 25MG — Ağrı kesici (NSAID), tablet
    {
        "barcode_like": "%ARVELES 25MG 20%",
        "duration_days": 5,
        "usage": UsageLabel(
            ilac_turu="Ağrı kesici",
            doz="1 film tablet",
            gunluk_kez=3,
            saat_arasi=8,
            yemek="tok",
            sure="en fazla 5 gün",
            ek_not="Bol su ile alınız",
        ),
        "preparation": PreparationLabel(gerekli=False),
        "warning": WarningLabel(
            gerekli=True,
            uyarilar=[
                "Aç karnına almayınız, mide rahatsızlığı yapabilir",
                "Alkol ile birlikte kullanmayınız",
                "Diğer ağrı kesicilerle aynı anda kullanmayınız",
                "5 günden uzun süre kullanmayınız",
            ],
        ),
        "source": "https://kt.ilacprospektusu.com/ilac/8538-arveles-25-mg-film-tablet-kt",
    },

    # 2) PAROL 500MG — Parasetamol, tablet
    {
        "barcode_like": "%PAROL 500MG 20%",
        "duration_days": 5,
        "usage": UsageLabel(
            ilac_turu="Ağrı kesici / Ateş düşürücü",
            doz="1-2 tablet",
            saat_arasi=6,
            yemek="fark etmez",
            sure="gerektiğinde",
            ek_not="",
        ),
        "preparation": PreparationLabel(gerekli=False),
        "warning": WarningLabel(
            gerekli=True,
            uyarilar=[
                "Günde 8 tableti (4000 mg) AŞMAYINIZ",
                "Alkol kullanıyorsanız günde 4 tabletten fazla almayınız",
                "Karaciğer hastalığında doktora danışın",
                "Diğer parasetamollü ilaçlarla birlikte kullanmayınız",
            ],
        ),
        "source": "https://www.atabay.com/wp-content/uploads/2022/02/PAROL-500-tablet-KT.pdf",
    },

    # 3) AMOKLAVIN BID 1000MG — Antibiyotik, tablet
    {
        "barcode_like": "%AMOKLAVIN BID 1000MG 14%",
        "duration_days": 7,
        "usage": UsageLabel(
            ilac_turu="Antibiyotik",
            doz="1 film tablet",
            gunluk_kez=2,
            saat_arasi=12,
            kullanim_zamani=["sabah", "akşam"],
            yemek="yemek başlangıcında",
            sure="7 gün (doktorun belirttiği süre)",
            ek_not="Tableti çiğnemeden bütün yutunuz",
        ),
        "preparation": PreparationLabel(gerekli=False),
        "warning": WarningLabel(
            gerekli=True,
            uyarilar=[
                "ANTİBİYOTİĞİ BİTİRMEDEN BIRAKMAYINIZ",
                "İshal veya döküntü olursa doktora başvurun",
                "Doğum kontrol haplarının etkisini azaltabilir",
                "Mide rahatsızlığı için yemekle alınız",
            ],
        ),
        "source": "https://kt.ilacprospektusu.com/ilac/1251-amoklavin-bid-1000-mg-film-tablet-kt",
    },

    # 4) AMOKLAVIN BID FORTE 400/57 SÜSPANSİYON — Pediatri antibiyotik
    {
        "barcode_like": "%AMOKLAVIN BID FORTE 400/57MG 100ML%",
        "duration_days": 7,
        "usage": UsageLabel(
            ilac_turu="Antibiyotik (çocuk)",
            doz="kiloya göre ölçek",
            gunluk_kez=2,
            saat_arasi=12,
            kullanim_zamani=["sabah", "akşam"],
            yemek="yemek başlangıcında",
            sure="doktorun belirttiği süre",
            ek_not="Doktor önerdiği ölçekte verin",
        ),
        "preparation": PreparationLabel(
            gerekli=True,
            form="süspansiyon",
            adimlar=[
                "Şişeyi iyice çalkalayın, tozu gevşetin",
                "Kaynatılıp soğutulmuş suyu işaretli çizgiye kadar 2 kez bölerek ilave edin",
                "Her ilavede şişeyi kuvvetle çalkalayın",
                "Hazırladıktan sonra her kullanım öncesi çalkalayın",
            ],
            saklama="Buzdolabında (2-8°C) saklayın",
            acildiktan_sonra_gecerlilik="7 gün",
            her_kullanim_oncesi="Her kullanımdan önce çalkalayın",
        ),
        "warning": WarningLabel(
            gerekli=True,
            uyarilar=[
                "ANTİBİYOTİĞİ BİTİRMEDEN BIRAKMAYINIZ",
                "Buzdolabında saklayın, 7 gün içinde tüketin",
                "İshal veya döküntü olursa doktora başvurun",
                "Her kullanımdan önce çalkalayın",
            ],
        ),
        "source": "https://kt.ilacprospektusu.com/ilac/8253-amoklavin-bid-forte-400-57-mg-5-ml-oral-suspansiyon-kt",
    },
]


# ---------------------------------------------------------------------------
# Yardımcı: ilacı barkod LIKE ile bul
# ---------------------------------------------------------------------------
def find_drug(conn, like: str):
    return conn.execute(
        "SELECT * FROM drugs WHERE name LIKE ? ORDER BY sales_count DESC LIMIT 1",
        (like,),
    ).fetchone()


def upsert_label(conn, drug_id: int, label_type: int, content: dict, source: str):
    conn.execute("""
        INSERT INTO drug_labels (drug_id, label_type, content_json, source_url, reviewed)
        VALUES (?, ?, ?, ?, 0)
        ON CONFLICT(drug_id, label_type) DO UPDATE SET
            content_json = excluded.content_json,
            source_url   = excluded.source_url,
            filled_at    = CURRENT_TIMESTAMP
    """, (drug_id, label_type, json.dumps(content, ensure_ascii=False), source))


# ---------------------------------------------------------------------------
# Ana
# ---------------------------------------------------------------------------
def main() -> int:
    rows = []
    with get_connection() as conn:
        init_schema(conn)
        # eczane bilgisi
        s = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings")}
        eczane_adi = s.get("eczane_adi", "İKİZLER ECZANESİ")
        eczane_tel = s.get("eczane_telefon", "")

        for demo in DEMOS:
            drug = find_drug(conn, demo["barcode_like"])
            if not drug:
                print(f"UYARI: bulunamadı: {demo['barcode_like']}")
                continue
            drug_id = drug["id"]
            ilac_adi = drug["name"]
            print(f"-- {ilac_adi}  (rank #{drug['rank']}, {drug['sales_count']} adet)")

            # DB'ye yaz
            upsert_label(conn, drug_id, 1, to_dict(demo["usage"]), demo["source"])
            upsert_label(conn, drug_id, 2, to_dict(demo["preparation"]), demo["source"])
            upsert_label(conn, drug_id, 3, to_dict(demo["warning"]), demo["source"])

            bitis = TODAY + timedelta(days=demo["duration_days"])

            # Etiket 1 — Kullanım
            img1 = render_usage_label(
                hasta_adi=DEMO_PATIENT, ilac_adi=ilac_adi, label=demo["usage"],
                recete_tarihi=TODAY, bitis_tarihi=bitis,
                eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
            )
            p1 = PREVIEW_DIR / f"drug{drug_id}_label1.png"
            img1.save(p1)

            # Etiket 2 — Hazırlama (sadece gerekli ise üret)
            p2 = None
            if demo["preparation"].gerekli:
                img2 = render_preparation_label(
                    hasta_adi=DEMO_PATIENT, ilac_adi=ilac_adi, label=demo["preparation"],
                    eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
                )
                p2 = PREVIEW_DIR / f"drug{drug_id}_label2.png"
                img2.save(p2)

            # Etiket 3 — Uyarı
            p3 = None
            if demo["warning"].gerekli:
                img3 = render_warning_label(
                    hasta_adi=DEMO_PATIENT, ilac_adi=ilac_adi, label=demo["warning"],
                    eczane_adi=eczane_adi, eczane_telefon=eczane_tel,
                )
                p3 = PREVIEW_DIR / f"drug{drug_id}_label3.png"
                img3.save(p3)

            rows.append({
                "drug": drug,
                "usage": demo["usage"],
                "prep": demo["preparation"],
                "warn": demo["warning"],
                "p1": p1, "p2": p2, "p3": p3,
                "bitis": bitis,
                "source": demo["source"],
            })
        conn.commit()

    # HTML rapor
    html = build_html(rows, eczane_adi, eczane_tel)
    report_path = PREVIEW_DIR / "report.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"\nRapor: {report_path}")

    # Tarayıcıda aç
    webbrowser.open(report_path.as_uri())
    return 0


def build_html(rows, eczane_adi, eczane_tel) -> str:
    parts = ["""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<title>İlaç Tarif – Pilot Önizleme</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background:#f4f4f7; margin:0; padding:24px; color:#222; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .hdr { margin-bottom: 24px; color:#555; }
  .drug { background:#fff; border:1px solid #ddd; border-radius:8px; padding:16px 18px; margin-bottom:22px; }
  .drug h2 { margin:0 0 4px; font-size: 18px; color:#1a4a7c; }
  .meta { color:#666; font-size:13px; margin-bottom:14px; }
  .labels { display:flex; gap:14px; flex-wrap:wrap; }
  .lab { border:1px solid #ccc; padding:8px; background:#fafafa; border-radius:6px; }
  .lab .cap { font-size: 12px; color:#555; margin-bottom:4px; font-weight:600; }
  .lab img { display:block; width: 480px; height:320px; image-rendering: pixelated; border:1px dashed #999; }
  details { margin-top: 10px; font-size: 13px; }
  details summary { cursor:pointer; color:#1a4a7c; }
  pre { background:#0f1115; color:#cfe; padding:10px; border-radius:6px; overflow:auto; font-size:12px; }
  .src { font-size:12px; color:#888; margin-top:6px; }
  .src a { color:#888; }
</style></head><body>
<h1>İlaç Tarif – Pilot Önizleme (4 demo ilaç)</h1>
<div class="hdr">Hasta: <b>"""]
    parts.append(DEMO_PATIENT)
    parts.append("""</b> · Reçete tarihi: """)
    parts.append(TODAY.strftime("%d.%m.%Y"))
    parts.append(""" · Eczane: <b>""")
    parts.append(eczane_adi)
    if eczane_tel:
        parts.append(f" · {eczane_tel}")
    parts.append("</b><br><small>Etiket boyutu: 60×40 mm @ 203 DPI = 480×320 px (Gprinter GP-1125D)</small></div>")

    for r in rows:
        d = r["drug"]
        parts.append(f'<div class="drug"><h2>{escape(d["name"])}</h2>')
        parts.append(f'<div class="meta">Rank #{d["rank"]} · 7 yılda {d["sales_count"]} adet · {escape(d["manufacturer"] or "")}</div>')
        parts.append('<div class="labels">')
        if r["p1"]:
            parts.append(f'<div class="lab"><div class="cap">1 · Kullanım</div><img src="{r["p1"].name}"></div>')
        if r["p2"]:
            parts.append(f'<div class="lab"><div class="cap">2 · Hazırlama</div><img src="{r["p2"].name}"></div>')
        if r["p3"]:
            parts.append(f'<div class="lab"><div class="cap">3 · Uyarı</div><img src="{r["p3"].name}"></div>')
        parts.append('</div>')
        parts.append('<details><summary>Ham veri (JSON)</summary><pre>')
        data = {
            "kullanim":  to_dict(r["usage"]),
            "hazirlama": to_dict(r["prep"]),
            "uyari":     to_dict(r["warn"]),
        }
        parts.append(escape(json.dumps(data, ensure_ascii=False, indent=2)))
        parts.append('</pre></details>')
        parts.append(f'<div class="src">Kaynak: <a href="{r["source"]}" target="_blank">{r["source"]}</a></div>')
        parts.append('</div>')
    parts.append("</body></html>")
    return "".join(parts)


def escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    raise SystemExit(main())
