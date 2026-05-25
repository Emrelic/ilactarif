"""Gprinter GP-1125D (veya diğer Windows yazıcı) ile etiket basma.

Strateji: Pillow ile üretilen PNG'leri pywin32 üzerinden yazıcının
sürücüsüne raster bitmap olarak gönderir. Yazıcı sürücüsünde 60x40 mm
etiket boyutu varsayılan olarak tanımlı olmalıdır.

Eğer Gprinter sürücüsünün varsayılan kağıt boyutu farklıysa, kullanıcı
"Aygıt ve Yazıcılar → Gprinter GP-1125D → Yazıcı Özellikleri" sekmesinde
60×40 mm boyutunu ayarlamalı.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import win32print
import win32ui
from PIL import Image, ImageWin

log = logging.getLogger("printer")


def list_printers() -> list[dict]:
    """Tüm yüklü yazıcıları listele."""
    out = []
    for flags, desc, name, comment in win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    ):
        out.append({"name": name, "description": desc, "comment": comment})
    return out


def find_printer(pattern: str = "Gprinter") -> Optional[str]:
    """İsmi pattern içeren ilk yazıcının tam adını döndür."""
    pat = pattern.lower()
    for p in list_printers():
        if pat in p["name"].lower():
            return p["name"]
    return None


def get_default_printer() -> str:
    return win32print.GetDefaultPrinter()


def print_image(
    image_path: Path | str,
    *,
    printer_name: Optional[str] = None,
    copies: int = 1,
    fit: str = "fit",   # "fit" (sığdır), "stretch" (kapla), "actual" (1:1)
) -> None:
    """Bir görsel dosyasını yazıcıya gönder.

    fit:
      "fit":     yazıcı sayfasına orantılı sığdır (boşluk olabilir).
      "stretch": kenardan kenara doldur (orantı bozulabilir).
      "actual":  1:1 piksel = 1 nokta (yazıcı DPI'sine göre).
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    printer_name = printer_name or find_printer("Gprinter") or get_default_printer()
    log.info("Yazıcı: %s", printer_name)

    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")

    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    try:
        # Yazıcı sayfasının fiziksel boyutu (piksel)
        page_w = hDC.GetDeviceCaps(110)   # HORZRES — yazılabilir alan
        page_h = hDC.GetDeviceCaps(111)   # VERTRES
        dpi_x  = hDC.GetDeviceCaps(88)    # LOGPIXELSX
        dpi_y  = hDC.GetDeviceCaps(90)    # LOGPIXELSY
        log.info("Yazıcı alan: %dx%d  DPI: %dx%d", page_w, page_h, dpi_x, dpi_y)

        # Sayfa boyutuna sığdır
        if fit == "stretch":
            target = (0, 0, page_w, page_h)
        elif fit == "actual":
            target = (0, 0, img.width, img.height)
        else:  # fit
            # Görüntüyü oranlı yazıcı sayfasına sığdır
            ratio = min(page_w / img.width, page_h / img.height)
            w = int(img.width * ratio)
            h = int(img.height * ratio)
            x = (page_w - w) // 2
            y = (page_h - h) // 2
            target = (x, y, x + w, y + h)

        for c in range(copies):
            hDC.StartDoc(f"ilactarif_{image_path.stem}")
            hDC.StartPage()
            dib = ImageWin.Dib(img)
            dib.draw(hDC.GetHandleOutput(), target)
            hDC.EndPage()
            hDC.EndDoc()
            log.info("Bask kopyası %d/%d gönderildi", c + 1, copies)
    finally:
        hDC.DeleteDC()


def print_many(image_paths, **kwargs) -> None:
    """Birden çok görseli sırayla bas."""
    for p in image_paths:
        print_image(p, **kwargs)
