"""Yakalanan canlı Medula HTML'i parse edip içeriği göster."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.medula_parser import parse_html, to_dict

LIVE_DIR = ROOT / "data" / "live_capture"

files = sorted(LIVE_DIR.glob("live_*_w*_ie*.html"))
if not files:
    files = sorted(LIVE_DIR.glob("live_*.html"))

for p in files:
    print("=" * 78)
    print(f"DOSYA: {p.name}  ({p.stat().st_size} byte)")
    html = p.read_text(encoding="utf-8", errors="ignore")
    cap = parse_html(html)
    d = to_dict(cap)
    print(f"  Sayfa tipi: {d['page_kind']}")
    print(f"  Title:      ", end="")
    # ufak title okuma
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    print(soup.title.string.strip() if soup.title else "")
    print(f"  Eczane:     {d['eczane']}")
    print(f"  Hasta adı:  {d['hasta_ad']}")
    print(f"  Hasta TC:   {d['hasta_tc']}")
    print(f"  Reçete no:  {d['recete_no'][:80]}")
    print(f"  Dr:         {d['dr_ad']}")
    print(f"  İlaç sayısı:{len(d['drugs'])}")
    for i, drug in enumerate(d["drugs"], 1):
        print(f"    {i}. {drug['ad']!r}")
        print(f"        barkod={drug['barkod']!r}  adet={drug['adet']!r}  raf={drug['raf']!r}")
        print(f"        doz={drug['doz_ham']!r}  -> {drug['doz_gunluk_kez']}x{drug['doz_birim_adedi']} {drug['doz_birim']}/{drug['periyot']}")
    if d.get("raw_kalem_kutu"):
        print(f"  Kalem/Kutu: {d['raw_kalem_kutu']}")
