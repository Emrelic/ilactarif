"""Kaydedilmiş canlı HTML'leri yeniden parse edip yeni etiket render'ı ile önizle.

Watcher'ın daha önce kaydettiği data/live_preview/raw_*.html dosyalarından
yenilenmiş etiket önizlemesi üretir. Watcher'ı tekrar tetiklemeden test için.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.medula_parser import parse_html
# handle_recete fonksiyonunu import etmek için watch_medula.py'yi modül olarak yükle
import importlib.util
spec = importlib.util.spec_from_file_location("watch_medula", ROOT / "scripts" / "watch_medula.py")
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)

LIVE_DIR = ROOT / "data" / "live_preview"

raws = sorted(LIVE_DIR.glob("raw_*.html"))
print(f"Kaydedilmiş canlı HTML: {len(raws)}")
for p in raws:
    print(f"  → {p.name}")
    html = p.read_text(encoding="utf-8", errors="ignore")
    cap = parse_html(html)
    if cap.page_kind != "e_recete_detay":
        print(f"    Atlandı: page_kind={cap.page_kind}")
        continue
    wm.handle_recete(cap, html)
