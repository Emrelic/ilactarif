"""Tüm 3887 ilacın tariflerini otomatik üret ve DB'ye yaz.

Mevcut tarifli ilaçlar (recipes_top100.py'den gelen) ÜZERİNE YAZILMAZ:
  ON CONFLICT(drug_id, label_type) durumunda eski reviewed=1 / 2 olanlar korunur.
  Sadece tarifsiz ilaçlar veya reviewed=0 (AI üretimi) olanlar güncellenir.

İdempotent: tekrar çalıştırılabilir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.bulk_recipes import (  # noqa: E402
    DEFAULT_GENERAL_UYARI,
    DEFAULT_UYARI,
    build_recipe,
)
from ilactarif.db import get_connection, init_schema  # noqa: E402

# AI/otomatik üretilmiş uyari metinleri — bunlar override edilebilir.
AI_GENERATED_UYARILAR = set(DEFAULT_UYARI.values()) | {DEFAULT_GENERAL_UYARI}


def main():
    with get_connection() as conn:
        init_schema(conn)

        # Tüm ilaçları sırayla al (en çok satandan başlayarak)
        drugs = conn.execute("""
            SELECT id, barcode, name, drug_type, sales_count, rank
            FROM drugs
            ORDER BY rank
        """).fetchall()
        print(f"Toplam ilaç: {len(drugs)}")

        # Hangi ilaçlar zaten manuel detaylı tarife sahip? (reviewed > 0 veya source dolu)
        # Şu an hepsi reviewed=0 ama recipes_top100.py'den gelenler kalitelidir.
        # Stratejimiz: tarifin uzunluğuna bak — büyükse manuel
        existing = {}
        for row in conn.execute("""
            SELECT drug_id, content_json, reviewed
            FROM drug_labels WHERE label_type = 1
        """):
            existing[row["drug_id"]] = row

        inserted, updated, skipped_manual = 0, 0, 0
        for d in drugs:
            recipe = build_recipe(d["name"])
            content_json = json.dumps(recipe, ensure_ascii=False)

            if d["id"] in existing:
                old = existing[d["id"]]
                old_content = json.loads(old["content_json"])
                # Eski reviewed > 0 ise (eczacı onayladıysa) dokunma
                if (old["reviewed"] or 0) > 0:
                    skipped_manual += 1
                    continue
                # Eski tarifte uyari_metni varsa ve AI üretimi DEĞİLSE (yani manuel
                # detaylı bir uyarı), tarifi koruyalım.
                old_uyari = (old_content.get("uyari_metni") or "").strip()
                if old_uyari and old_uyari not in AI_GENERATED_UYARILAR \
                        and not old_uyari.startswith("Doktorunuzun önerdiği"):
                    skipped_manual += 1
                    continue

                conn.execute("""
                    UPDATE drug_labels SET content_json = ?, filled_at = CURRENT_TIMESTAMP
                    WHERE drug_id = ? AND label_type = 1
                """, (content_json, d["id"]))
                updated += 1
            else:
                conn.execute("""
                    INSERT INTO drug_labels (drug_id, label_type, content_json, reviewed)
                    VALUES (?, 1, ?, 0)
                """, (d["id"], content_json))
                inserted += 1

        conn.commit()

        print(f"\n✓ İnsert: {inserted}")
        print(f"↻ Update: {updated}")
        print(f"⊘ Manuel detaylı (korundu): {skipped_manual}")

        # Kategori istatistiği
        print("\n=== Kategori dağılımı (Tüm DB) ===")
        rows = conn.execute("""
            SELECT json_extract(content_json, '$.kategori') AS kat, COUNT(*) AS n
            FROM drug_labels WHERE label_type = 1
            GROUP BY kat ORDER BY n DESC
            LIMIT 30
        """).fetchall()
        for r in rows:
            print(f"  {r['n']:>4}  {r['kat'] or '(boş)'}")

        # Tarifsiz kalan ilaç var mı?
        no_label = conn.execute("""
            SELECT COUNT(*) FROM drugs
            WHERE id NOT IN (SELECT drug_id FROM drug_labels WHERE label_type = 1)
        """).fetchone()[0]
        print(f"\nTarifsiz kalan ilaç: {no_label}")


if __name__ == "__main__":
    main()
