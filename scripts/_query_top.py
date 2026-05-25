"""Geçici: en çok satan şurup/süspansiyonları listele."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilactarif.db import get_connection

with get_connection() as c:
    rows = c.execute("""
        SELECT rank, name, sales_count FROM drugs
        WHERE (name LIKE '%SÜSPANSİYON%' OR name LIKE '%SUSPANSIYON%'
               OR name LIKE '%ŞURUP%' OR name LIKE '%SURUP%'
               OR name LIKE '%ORAL SOL%'
               OR name LIKE '%DAMLA%')
          AND drug_type = 'İLAÇ'
        ORDER BY sales_count DESC LIMIT 15
    """).fetchall()
    print("En çok satan şurup/süspansiyon/damla:")
    for r in rows:
        print(f"  #{r['rank']:>4}  {r['sales_count']:>5} adet  {r['name']}")
