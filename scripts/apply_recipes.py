"""recipes_top100.py içindeki tarifleri SQLite drug_labels tablosuna yaz."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# data/recipes_top100.py'yi dinamik import et
spec = importlib.util.spec_from_file_location(
    "recipes_top100", ROOT / "data" / "recipes_top100.py"
)
rec_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec_mod)

from ilactarif.db import get_connection, init_schema  # noqa: E402

RECIPES = rec_mod.RECIPES


def main():
    print(f"Tarif sayısı: {len(RECIPES)}")

    with get_connection() as conn:
        init_schema(conn)

        ok, skipped = 0, 0
        for r in RECIPES:
            barcode = r["barcode"]
            drug = conn.execute(
                "SELECT id, name FROM drugs WHERE barcode = ?", (barcode,)
            ).fetchone()
            if not drug:
                print(f"  ! Barkod DB'de yok: {barcode}  ({r.get('name', '')})")
                skipped += 1
                continue

            content = {
                "kategori":          r.get("kategori", ""),
                "kullanim_talimati": r.get("talimat", ""),
                "uyari_metni":       r.get("uyari", ""),
                "sure_gun":          r.get("sure_gun"),
                # Geriye uyumluluk için eski alanlar
                "ilac_turu":         r.get("kategori", "").title(),
                "gunluk_kez":        r.get("gunluk_kez"),
                "saat_arasi":        r.get("saat_arasi"),
                "yemek":             r.get("yemek", ""),
                "kullanim_zamani":   r.get("kullanim_zamani", []),
            }
            content_json = json.dumps(content, ensure_ascii=False)

            conn.execute("""
                INSERT INTO drug_labels (drug_id, label_type, content_json, source_url, reviewed)
                VALUES (?, 1, ?, '', 0)
                ON CONFLICT(drug_id, label_type) DO UPDATE SET
                    content_json = excluded.content_json,
                    filled_at    = CURRENT_TIMESTAMP
            """, (drug["id"], content_json))
            ok += 1

        conn.commit()

        total_drugs   = conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
        total_labeled = conn.execute(
            "SELECT COUNT(DISTINCT drug_id) FROM drug_labels WHERE label_type=1"
        ).fetchone()[0]
        print(f"\n  ✓ Yazıldı: {ok}")
        print(f"  ! Atlandı (barkod yok): {skipped}")
        print(f"\nDB durumu: {total_labeled} ilaç tarifli / {total_drugs} toplam")

        # Kategori dağılımı
        print("\nKategori dağılımı:")
        rows = conn.execute("""
            SELECT json_extract(content_json, '$.kategori') AS kat, COUNT(*) AS n
            FROM drug_labels WHERE label_type = 1
            GROUP BY kat ORDER BY n DESC
        """).fetchall()
        for r in rows:
            print(f"  {r['n']:>3}  {r['kat'] or '(boş)'}")


if __name__ == "__main__":
    main()
