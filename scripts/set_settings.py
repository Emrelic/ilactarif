"""Eczane bilgilerini settings tablosuna işle."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilactarif.db import get_connection, init_schema

VALUES = {
    "eczane_adi": "İKİZLER ECZANESİ",
    "eczane_telefon": "0212 515 74 40",
    "eczane_adres": "",
}

with get_connection() as c:
    init_schema(c)
    for k, v in VALUES.items():
        c.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (k, v),
        )
    c.commit()
    for r in c.execute("SELECT key, value FROM settings"):
        print(f"  {r['key']:<20} = {r['value']!r}")
