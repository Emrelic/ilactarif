"""Manuel etiket girişi GUI'sini başlat."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.ui.manual_label_ui import main

if __name__ == "__main__":
    main()
