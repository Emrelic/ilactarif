"""En çok satan 100 ilacın listesini dosyaya yaz (ben dolduracağım)."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilactarif.db import get_connection

with get_connection() as c:
    rows = c.execute("""
        SELECT rank, barcode, name, sales_count
        FROM drugs
        WHERE drug_type = 'İLAÇ'
        ORDER BY rank
        LIMIT 100
    """).fetchall()

out = Path(__file__).resolve().parents[1] / "docs" / "top100.txt"
out.parent.mkdir(exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"{r['rank']:>3}. {r['sales_count']:>5}  {r['barcode']}  {r['name']}\n")

print(f"Yazıldı: {out}")
print(f"İlk 20:")
for r in rows[:20]:
    print(f"  #{r['rank']:>3} ({r['sales_count']:>5}) {r['name']}")
