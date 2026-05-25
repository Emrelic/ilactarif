"""Yazıcı testi — bir örnek etiketi Gprinter GP-1125D'ye gönder.

KULLANIM:
  1) Yazıcının kabloları takılı + termal etiket rulosu yerinde olsun.
  2) Bu scripti çalıştırın: python scripts/test_print.py
  3) Sonuçta tek bir etiket çıkmalı (AHMET YILMAZ - AMOKLAVIN BID 1000).

Opsiyonel:
    python scripts/test_print.py --list           # yazıcıları listele
    python scripts/test_print.py --file path.png  # belirli bir PNG'yi bas
    python scripts/test_print.py --fit stretch    # kenardan kenara
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.printer import (
    find_printer,
    get_default_printer,
    list_printers,
    print_image,
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("test_print")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true",
                    help="Yüklü yazıcıları listele")
    ap.add_argument("--file", type=Path, default=None,
                    help="Basılacak PNG yolu (varsayılan: AMOKLAVIN örneği)")
    ap.add_argument("--fit", choices=("fit", "stretch", "actual"), default="fit")
    ap.add_argument("--printer", default=None,
                    help="Yazıcı adı (varsayılan: Gprinter'i otomatik bul)")
    ap.add_argument("--copies", type=int, default=1)
    args = ap.parse_args()

    if args.list:
        print("\n=== Yüklü yazıcılar ===")
        for p in list_printers():
            print(f"  · {p['name']}")
        print(f"\nVarsayılan: {get_default_printer()}")
        found = find_printer("Gprinter")
        print(f"Otomatik Gprinter eşleşmesi: {found or '(bulunamadı)'}")
        return 0

    # Hangi PNG?
    if args.file:
        png = args.file
    else:
        # Sample render'da üretilen AMOKLAVIN BID 1000 etiketini kullan
        candidates = sorted(
            (ROOT / "data" / "live_preview").glob("*DEMO123_8699525093189_label1.png"),
            reverse=True,
        )
        if not candidates:
            log.error("Sample etiket bulunamadı. Önce scripts/sample_render.py çalıştırın.")
            return 1
        png = candidates[0]

    log.info("Bask dosyası: %s", png)
    if not png.exists():
        log.error("Dosya yok: %s", png)
        return 1

    printer = args.printer or find_printer("Gprinter") or get_default_printer()
    log.info("Yazıcı: %s", printer)

    print_image(png, printer_name=printer, copies=args.copies, fit=args.fit)
    log.info("✓ Bask işi gönderildi. Yazıcıdan çıkmasını bekleyin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
