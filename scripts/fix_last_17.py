"""Kalan 17 form-kategori ilacı için manuel kategori atama.

Türkçe karakter sorunları nedeniyle drug_guess sözlüğü ile eşleşmeyen
ilaçların kategorisini doğrudan SQL UPDATE ile düzeltir.
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.bulk_recipes import (  # noqa: E402
    DEFAULT_DOZ,
    DEFAULT_GENERAL_UYARI,
    DEFAULT_SURE_GUN,
    DEFAULT_UYARI,
)
from ilactarif.db import get_connection  # noqa: E402
from ilactarif.drug_guess import build_kullanim_talimati  # noqa: E402


# (name LIKE pattern, kategori)
ASSIGNMENTS = [
    ("BENEDAY%", "ANTİEPİLEPTİK / SİNİR AĞRISI"),       # B1+B6+B12+α-lipoik (diyabetik nöropati)
    ("IMEX%", "SİVİLCE İLACI"),                          # tetrasiklin
    ("POT-K%", "ELEKTROLİT"),                            # potasyum klorür
    ("NOSKAR%", "CİLT İLACI (YARA İYİLEŞTİRİCİ)"),       # soğan+heparin+allantoin
    ("TAZERACIN%", "ANTİBİYOTİK"),                       # piperasilin+tazobaktam
    ("PAINLESS%", "AĞRI KESİCİ"),                        # mentol+metil salisilat
    ("REMIDON%", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),         # parasetamol+kafein
    ("PREGNYL%", "KISIRLIK TEDAVİSİ"),                   # hCG
    ("ACE PLUS%", "VİTAMİN DESTEĞİ"),                    # A+C+E+selenyum
    ("DEMOX%", "GÖZ İLACI"),                             # moksifloksasin
    ("SIHHAT POV%", "ANTİSEPTİK"),                       # povidon iyot
    ("TRE %", "SİVİLCE İLACI"),                          # tretinoin
    ("FOLİODE%", "FOLİK ASİT DESTEĞİ"),                  # folik asit
    ("FOLIODE%", "FOLİK ASİT DESTEĞİ"),
    ("BERAVİT%", "VİTAMİN DESTEĞİ"),                     # multivitamin
    ("BERAVIT%", "VİTAMİN DESTEĞİ"),
    ("CÖREK OTU%", "BİTKİSEL DESTEK"),
    ("ÇÖREK OTU%", "BİTKİSEL DESTEK"),
]


def main():
    with get_connection() as conn:
        total_updated = 0
        for pattern, kategori in ASSIGNMENTS:
            drugs = conn.execute(
                "SELECT id, name FROM drugs WHERE name LIKE ?", (pattern,)
            ).fetchall()
            if not drugs:
                continue

            doz = DEFAULT_DOZ.get(kategori, {})
            uyari = DEFAULT_UYARI.get(kategori, DEFAULT_GENERAL_UYARI)
            sure_gun = DEFAULT_SURE_GUN.get(kategori, 7)

            for d in drugs:
                talimat = build_kullanim_talimati(
                    drug_name=d["name"],
                    gunluk_kez=doz.get("gunluk_kez"),
                    saat_arasi=doz.get("saat_arasi"),
                    kullanim_zamani=doz.get("kullanim_zamani", []),
                    yemek=doz.get("yemek", ""),
                    doz_str="1 TANE",
                )
                recipe = {
                    "kategori":          kategori,
                    "kullanim_talimati": talimat,
                    "uyari_metni":       uyari,
                    "sure_gun":          sure_gun,
                    "ilac_turu":         kategori.title(),
                    "gunluk_kez":        doz.get("gunluk_kez"),
                    "saat_arasi":        doz.get("saat_arasi"),
                    "yemek":             doz.get("yemek", ""),
                    "kullanim_zamani":   doz.get("kullanim_zamani", []),
                }
                conn.execute("""
                    UPDATE drug_labels SET content_json = ?, filled_at = CURRENT_TIMESTAMP
                    WHERE drug_id = ? AND label_type = 1
                """, (json.dumps(recipe, ensure_ascii=False), d["id"]))
                total_updated += 1
                print(f"  ✓ {d['name'][:60]} → {kategori}")
        conn.commit()
        print(f"\nToplam güncellenen: {total_updated}")


if __name__ == "__main__":
    main()
