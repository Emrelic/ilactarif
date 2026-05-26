"""Manuel etiket girişi GUI - Tkinter.

Özellikler:
  • Hasta adı + (opsiyonel) TC
  • İlaç ekleme: barkod, karekod (GS1 DataMatrix) veya isim arama
  • Karekod parse: (01)GTIN(17)YYMMDD(10)LOT(21)SN → barkod ayıklama
  • İsim arama: anlık autocomplete
  • Her ilaç için doz, günlük kez, uyarı (uzun text, düzenlenebilir)
  • Etiket önizleme + Yazdır (Gprinter)
"""
from __future__ import annotations

import datetime
import json
import re
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from typing import Optional

from ..bulk_recipes import (
    DEFAULT_DOZ,
    DEFAULT_GENERAL_UYARI,
    DEFAULT_SURE_GUN,
    DEFAULT_UYARI,
    build_recipe,
)
from ..db import get_connection, init_schema
from ..drug_guess import build_kullanim_talimati, guess_form, guess_kategori, guess_unit
from ..label_render import render_usage_label
from ..models import UsageLabel

# ---------------------------------------------------------------------------
# Karekod parse: GS1 DataMatrix
# ---------------------------------------------------------------------------
# Türkiye İTS karekodu örnek: "010869983209005517240731101234212345678"
#   (01) GTIN-14 (14 hane)  → barkod
#   (17) Son kullanma YYMMDD (6 hane)
#   (10) Lot No (variable, GS ile sonlanır)
#   (21) Seri No (variable)
GS1_AI_RE = re.compile(r"01(\d{14})")


def parse_karekod(raw: str) -> Optional[str]:
    """Karekoddan barkodu (EAN-13) çıkar; düz barkodsa olduğu gibi döner.

    GS1: (01) AI sonrası 14 hane GTIN. EAN-13'ün başına 0 eklenmiş şekli.
    Sondaki 13 haneyi al → EAN-13.
    """
    s = (raw or "").strip()
    # FNC1 / GS karakteri ve parantezleri temizle
    s = s.replace("(", "").replace(")", "").replace("\x1d", "").replace("", "")

    # Düz barkod: 8 veya 13 hane
    if s.isdigit() and len(s) in (8, 13):
        return s

    # GTIN-14 (ilk hane 0 ise) — direkt barkod döner
    if s.isdigit() and len(s) == 14 and s.startswith("0"):
        return s[1:]

    # GS1: 01 ile başlayan 14 hane
    m = GS1_AI_RE.search(s)
    if m:
        gtin = m.group(1)
        # GTIN-14, ilk hane genelde 0 → kırp
        return gtin[1:] if gtin.startswith("0") else gtin

    # Bulunamadıysa ham veri
    return s if s.isdigit() and len(s) >= 8 else None


# ---------------------------------------------------------------------------
# Tek bir ilaç satırı (state)
# ---------------------------------------------------------------------------
class DrugRow:
    def __init__(self, barcode: str, name: str, drug_id: Optional[int]):
        self.drug_id = drug_id
        self.barcode = barcode
        self.name = name
        # Defaults — DB'den al
        kategori, talimat, uyari, sure_gun = self._db_recipe()
        self.kategori = kategori
        self.talimat = talimat
        self.uyari = uyari
        self.sure_gun = sure_gun
        # Manuel düzenleme alanları
        self.gunluk_kez = 1
        self.doz_birim = guess_unit(name) or "Tane"
        self.doz_adet = 1.0

    def _db_recipe(self):
        """DB'de varsa tarifi al, yoksa drug_guess ile üret."""
        if self.drug_id is not None:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT content_json FROM drug_labels WHERE drug_id=? AND label_type=1",
                    (self.drug_id,),
                ).fetchone()
                if row:
                    try:
                        r = json.loads(row["content_json"])
                        return (
                            r.get("kategori", ""),
                            r.get("kullanim_talimati", ""),
                            r.get("uyari_metni", ""),
                            r.get("sure_gun", 7),
                        )
                    except Exception:
                        pass
        # Fallback: drug_guess'ten üret
        r = build_recipe(self.name)
        return (r["kategori"], r["kullanim_talimati"], r["uyari_metni"], r["sure_gun"])


# ---------------------------------------------------------------------------
# Ana pencere
# ---------------------------------------------------------------------------
class ManualLabelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("İlaçTarif — Manuel Etiket Girişi")
        self.geometry("1200x780")
        self.minsize(1000, 640)
        self._init_db()
        self._build_ui()
        self.rows: list[DrugRow] = []
        self._refresh_table()

    def _init_db(self):
        with get_connection() as conn:
            init_schema(conn)
            s = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings")}
            self.eczane_adi = s.get("eczane_adi", "İKİZLER ECZANESİ")
            self.eczane_tel = s.get("eczane_telefon", "")

    # ------------------------------------------------------------------
    # UI iskeleti
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Üst: Hasta bilgileri
        top = ttk.LabelFrame(self, text="Hasta / Reçete", padding=8)
        top.pack(fill="x", padx=10, pady=(10, 6))

        ttk.Label(top, text="Hasta adı:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.var_hasta = tk.StringVar()
        ttk.Entry(top, textvariable=self.var_hasta, width=32, font=("Segoe UI", 11)).grid(
            row=0, column=1, sticky="w", padx=4
        )

        ttk.Label(top, text="TC (ops.):").grid(row=0, column=2, sticky="e", padx=4)
        self.var_tc = tk.StringVar()
        ttk.Entry(top, textvariable=self.var_tc, width=14).grid(row=0, column=3, sticky="w", padx=4)

        ttk.Label(top, text="Reçete tarihi:").grid(row=0, column=4, sticky="e", padx=4)
        self.var_tarih = tk.StringVar(value=datetime.date.today().strftime("%d/%m/%Y"))
        ttk.Entry(top, textvariable=self.var_tarih, width=12).grid(row=0, column=5, sticky="w", padx=4)

        # Orta: İlaç ekleme alanı
        add = ttk.LabelFrame(self, text="İlaç Ekle", padding=8)
        add.pack(fill="x", padx=10, pady=6)

        ttk.Label(add, text="Barkod / Karekod:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.var_barkod = tk.StringVar()
        self.ent_barkod = ttk.Entry(add, textvariable=self.var_barkod, width=42, font=("Consolas", 11))
        self.ent_barkod.grid(row=0, column=1, sticky="w", padx=4)
        self.ent_barkod.bind("<Return>", self._on_barkod_enter)
        ttk.Button(add, text="Ekle (Enter)", command=self._on_barkod_enter).grid(row=0, column=2, padx=4)

        ttk.Label(add, text="İsimle ara:").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        self.var_ara = tk.StringVar()
        self.ent_ara = ttk.Entry(add, textvariable=self.var_ara, width=42, font=("Segoe UI", 11))
        self.ent_ara.grid(row=1, column=1, sticky="w", padx=4)
        self.ent_ara.bind("<KeyRelease>", self._on_search_typed)

        # Arama sonuç listesi
        self.lst_results = tk.Listbox(add, height=6, width=80, font=("Consolas", 10))
        self.lst_results.grid(row=2, column=0, columnspan=3, sticky="we", padx=4, pady=4)
        self.lst_results.bind("<Double-Button-1>", self._on_result_double)
        self.lst_results.bind("<Return>", self._on_result_double)

        add.columnconfigure(1, weight=1)

        # Eklenen ilaçlar tablosu (Treeview)
        tbl = ttk.LabelFrame(self, text="Eklenen İlaçlar", padding=8)
        tbl.pack(fill="both", expand=True, padx=10, pady=6)

        cols = ("name", "doz", "kez", "kategori", "uyari")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", height=8)
        self.tree.heading("name", text="İlaç adı")
        self.tree.heading("doz",  text="Doz")
        self.tree.heading("kez",  text="Günlük")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("uyari", text="Uyarı (özet)")
        self.tree.column("name",     width=300)
        self.tree.column("doz",      width=80,  anchor="center")
        self.tree.column("kez",      width=60,  anchor="center")
        self.tree.column("kategori", width=180)
        self.tree.column("uyari",    width=460)

        ysb = ttk.Scrollbar(tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        self.tree.bind("<Double-Button-1>", self._on_row_edit)

        # Tablo altı: sil / temizle butonları
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=4)
        ttk.Button(btns, text="Seçili Satırı Düzenle", command=self._on_row_edit).pack(side="left", padx=2)
        ttk.Button(btns, text="Seçili Satırı Sil", command=self._on_row_delete).pack(side="left", padx=2)
        ttk.Button(btns, text="Tümünü Temizle", command=self._on_clear_all).pack(side="left", padx=2)

        # Alt: Önizleme + Yazdır
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(6, 12))
        ttk.Button(bottom, text="📄 Önizleme HTML", command=self._on_preview).pack(side="left", padx=4, ipady=4)
        ttk.Button(bottom, text="🖨 Yazıcıdan Çıkar", command=self._on_print).pack(side="left", padx=4, ipady=4)
        ttk.Button(bottom, text="Çıkış", command=self.destroy).pack(side="right", padx=4)

        self.status = tk.StringVar(value="Hazır.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

        self.ent_barkod.focus_set()

    # ------------------------------------------------------------------
    # İlaç bulma
    # ------------------------------------------------------------------
    def _find_drug_by_barcode(self, barcode: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT id, barcode, name FROM drugs WHERE barcode=?", (barcode,)
            ).fetchone()

    def _search_drugs_by_name(self, q: str, limit: int = 30):
        q = q.strip()
        if len(q) < 2:
            return []
        with get_connection() as conn:
            return conn.execute(
                "SELECT id, barcode, name FROM drugs WHERE name LIKE ? "
                "ORDER BY sales_count DESC LIMIT ?",
                (f"%{q}%", limit),
            ).fetchall()

    # ------------------------------------------------------------------
    # Olaylar
    # ------------------------------------------------------------------
    def _on_barkod_enter(self, event=None):
        raw = self.var_barkod.get().strip()
        if not raw:
            return
        barcode = parse_karekod(raw)
        if not barcode:
            self.status.set(f"❌ Karekod/barkod tanınamadı: {raw[:40]}")
            return
        row = self._find_drug_by_barcode(barcode)
        if not row:
            # DB'de yok — yine de eklemesine izin ver (manuel ad sor)
            from tkinter.simpledialog import askstring
            ad = askstring("İlaç DB'de yok",
                           f"Barkod: {barcode}\nİlaç adını manuel girin:", parent=self)
            if not ad:
                return
            self._add_drug(barcode, ad, drug_id=None)
        else:
            self._add_drug(row["barcode"], row["name"], drug_id=row["id"])
        self.var_barkod.set("")
        self.ent_barkod.focus_set()

    def _on_search_typed(self, event=None):
        q = self.var_ara.get()
        self.lst_results.delete(0, "end")
        results = self._search_drugs_by_name(q)
        self._search_results = results
        for r in results:
            self.lst_results.insert("end", f"{r['barcode']:15} | {r['name']}")
        if results:
            self.status.set(f"{len(results)} sonuç bulundu — listeden seçin (çift tıkla)")
        else:
            self.status.set("Sonuç yok.")

    def _on_result_double(self, event=None):
        sel = self.lst_results.curselection()
        if not sel:
            return
        row = self._search_results[sel[0]]
        self._add_drug(row["barcode"] or "", row["name"], drug_id=row["id"])
        self.var_ara.set("")
        self.lst_results.delete(0, "end")
        self.ent_barkod.focus_set()

    def _add_drug(self, barcode: str, name: str, drug_id: Optional[int]):
        # Mükerrer önle
        for r in self.rows:
            if r.barcode and r.barcode == barcode:
                self.status.set(f"⚠ Zaten ekli: {name}")
                return
        self.rows.append(DrugRow(barcode, name, drug_id))
        self._refresh_table()
        self.status.set(f"✓ Eklendi: {name}")

    def _refresh_table(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, r in enumerate(self.rows):
            doz_str = self._format_doz(r)
            uyari_kisa = (r.uyari or "")[:80]
            self.tree.insert("", "end", iid=str(i),
                             values=(r.name, doz_str, r.gunluk_kez, r.kategori, uyari_kisa))

    def _format_doz(self, r: DrugRow) -> str:
        if float(r.doz_adet).is_integer():
            s = str(int(r.doz_adet))
        else:
            s = f"{r.doz_adet:.1f}".replace(".", ",")
        return f"{s} {r.doz_birim}" if r.doz_birim else s

    def _on_row_delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.rows[idx]
        self._refresh_table()

    def _on_clear_all(self):
        if not self.rows:
            return
        if messagebox.askyesno("Onay", f"{len(self.rows)} ilacı silmek istediğinize emin misiniz?"):
            self.rows.clear()
            self._refresh_table()

    def _on_row_edit(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        EditDrugDialog(self, self.rows[idx], on_save=self._refresh_table)

    # ------------------------------------------------------------------
    # Çıktı: önizleme & yazdır
    # ------------------------------------------------------------------
    def _build_labels(self):
        hasta = (self.var_hasta.get() or "").strip().upper()
        if not hasta:
            messagebox.showwarning("Eksik", "Hasta adı boş olamaz.")
            return None
        if not self.rows:
            messagebox.showwarning("Eksik", "Hiç ilaç eklenmedi.")
            return None
        try:
            d, m, y = self.var_tarih.get().split("/")
            r_date = datetime.date(int(y), int(m), int(d))
        except Exception:
            r_date = datetime.date.today()

        images = []
        for r in self.rows:
            talimat = r.talimat
            if not talimat:
                doz = self._format_doz(r)
                talimat = build_kullanim_talimati(
                    drug_name=r.name, gunluk_kez=r.gunluk_kez, doz_str=doz,
                )
            label = UsageLabel(
                kategori=r.kategori, kullanim_talimati=talimat, uyari_metni=r.uyari,
                ilac_turu=guess_form(r.name), doz=self._format_doz(r),
                gunluk_kez=r.gunluk_kez, sure_gun=r.sure_gun,
            )
            bitis = r_date + datetime.timedelta(days=int(r.sure_gun or 7))
            img = render_usage_label(
                hasta_adi=hasta, ilac_adi=r.name, label=label,
                recete_tarihi=r_date, bitis_tarihi=bitis,
                eczane_adi=self.eczane_adi, eczane_telefon=self.eczane_tel,
            )
            images.append((r, img))
        return images

    def _on_preview(self):
        out = self._build_labels()
        if not out:
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_dir = Path(__file__).resolve().parents[3] / "data" / "live_preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        html_lines = ['<!DOCTYPE html><html><head><meta charset="utf-8"><style>',
                      'body{font-family:Segoe UI;background:#f3f4f8;padding:18px}',
                      '.lab{display:inline-block;margin:8px;background:#fff;border:1px solid #ccc;padding:6px;border-radius:6px}',
                      '.lab img{display:block;width:480px;height:320px;border:1px dashed #999}',
                      '.cap{font-size:12px;color:#555;margin-bottom:4px}',
                      '</style></head><body>']
        for i, (r, img) in enumerate(out):
            p = preview_dir / f"manual_{ts}_{i}.png"
            img.save(p)
            html_lines.append(f'<div class="lab"><div class="cap">{r.name}</div><img src="{p.name}"></div>')
        html_lines.append('</body></html>')
        out_path = preview_dir / f"manual_preview_{ts}.html"
        out_path.write_text("".join(html_lines), encoding="utf-8")
        webbrowser.open(out_path.as_uri())
        self.status.set(f"✓ Önizleme açıldı: {out_path.name}")

    def _on_print(self):
        out = self._build_labels()
        if not out:
            return
        try:
            from .. import printer
        except ImportError:
            messagebox.showerror("Yazıcı", "Printer modülü yüklenemedi.")
            return
        if not messagebox.askyesno("Yazdır",
                                   f"{len(out)} etiket yazıcıya gönderilecek. Onay?"):
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_dir = Path(__file__).resolve().parents[3] / "data" / "live_preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        sent = 0
        for i, (r, img) in enumerate(out):
            p = preview_dir / f"manual_{ts}_{i}.png"
            img.save(p)
            try:
                printer.print_image(p)
                sent += 1
            except Exception as e:
                messagebox.showerror("Yazıcı hatası", f"{r.name}\n\n{e}")
                break
        self.status.set(f"🖨 {sent} etiket yazdırıldı.")


# ---------------------------------------------------------------------------
# Satır düzenleme dialogu
# ---------------------------------------------------------------------------
class EditDrugDialog(tk.Toplevel):
    def __init__(self, parent: ManualLabelApp, row: DrugRow, on_save):
        super().__init__(parent)
        self.title(f"Düzenle — {row.name}")
        self.geometry("700x540")
        self.row = row
        self.on_save = on_save
        self._build()

    def _build(self):
        pad = {"padx": 6, "pady": 4}
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # İlaç adı (readonly)
        ttk.Label(frm, text="İlaç:").grid(row=0, column=0, sticky="e", **pad)
        ttk.Label(frm, text=self.row.name, font=("Segoe UI", 11, "bold")).grid(
            row=0, column=1, columnspan=3, sticky="w", **pad
        )

        # Kategori
        ttk.Label(frm, text="Kategori:").grid(row=1, column=0, sticky="e", **pad)
        self.var_kategori = tk.StringVar(value=self.row.kategori)
        ttk.Entry(frm, textvariable=self.var_kategori, width=40).grid(
            row=1, column=1, columnspan=3, sticky="we", **pad
        )

        # Doz adet + birim + günlük kez + süre
        ttk.Label(frm, text="Doz adedi:").grid(row=2, column=0, sticky="e", **pad)
        self.var_adet = tk.StringVar(value=str(self.row.doz_adet))
        ttk.Entry(frm, textvariable=self.var_adet, width=8).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Birim:").grid(row=2, column=2, sticky="e", **pad)
        self.var_birim = tk.StringVar(value=self.row.doz_birim)
        ttk.Combobox(frm, textvariable=self.var_birim, width=12,
                     values=["Tane", "Tablet", "Kapsül", "ML", "Damla", "Puf", "Ölçek",
                             "Uygulama", "Fitil"]).grid(row=2, column=3, sticky="w", **pad)

        ttk.Label(frm, text="Günlük kez:").grid(row=3, column=0, sticky="e", **pad)
        self.var_kez = tk.StringVar(value=str(self.row.gunluk_kez))
        ttk.Combobox(frm, textvariable=self.var_kez, width=6,
                     values=["1", "2", "3", "4"]).grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Süre (gün):").grid(row=3, column=2, sticky="e", **pad)
        self.var_sure = tk.StringVar(value=str(self.row.sure_gun or 7))
        ttk.Entry(frm, textvariable=self.var_sure, width=6).grid(row=3, column=3, sticky="w", **pad)

        # Kullanım talimatı (büyük)
        ttk.Label(frm, text="Kullanım talimatı:").grid(row=4, column=0, sticky="ne", **pad)
        self.txt_talimat = tk.Text(frm, width=60, height=4, font=("Segoe UI", 10), wrap="word")
        self.txt_talimat.grid(row=4, column=1, columnspan=3, sticky="we", **pad)
        self.txt_talimat.insert("1.0", self.row.talimat or "")

        # Uyarı metni (uzun)
        ttk.Label(frm, text="UYARI (elle yazılabilir):").grid(row=5, column=0, sticky="ne", **pad)
        self.txt_uyari = tk.Text(frm, width=60, height=8, font=("Segoe UI", 10), wrap="word")
        self.txt_uyari.grid(row=5, column=1, columnspan=3, sticky="we", **pad)
        self.txt_uyari.insert("1.0", self.row.uyari or "")

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)
        frm.rowconfigure(5, weight=1)

        # Butonlar
        btns = ttk.Frame(self, padding=8)
        btns.pack(fill="x")
        ttk.Button(btns, text="Kaydet", command=self._save).pack(side="right", padx=4)
        ttk.Button(btns, text="İptal", command=self.destroy).pack(side="right", padx=4)

    def _save(self):
        try:
            self.row.doz_adet = float(self.var_adet.get().replace(",", "."))
        except Exception:
            self.row.doz_adet = 1.0
        self.row.doz_birim = self.var_birim.get().strip()
        try:
            self.row.gunluk_kez = int(self.var_kez.get())
        except Exception:
            self.row.gunluk_kez = 1
        try:
            self.row.sure_gun = int(self.var_sure.get())
        except Exception:
            self.row.sure_gun = 7
        self.row.kategori = self.var_kategori.get().strip()
        self.row.talimat = self.txt_talimat.get("1.0", "end").strip()
        self.row.uyari = self.txt_uyari.get("1.0", "end").strip()
        self.on_save()
        self.destroy()


def main():
    app = ManualLabelApp()
    app.mainloop()


if __name__ == "__main__":
    main()
