"""Windows Startup klasörüne kısayol ekler (alternatif: Task Scheduler yerine).

Windows kullanıcı oturum açtığında Startup klasöründeki kısayolları otomatik
çalıştırır. Admin yetkisi gerektirmez, Task Scheduler'dan daha basittir.

Kullanım:
    python scripts/install_startup.py             # Kur
    python scripts/install_startup.py --remove    # Kaldır
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BAT_PATH = ROOT / "scripts" / "watch_medula_bg.bat"

STARTUP_DIR = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
SHORTCUT_NAME = "IlacTarif_Watcher.lnk"
SHORTCUT_PATH = STARTUP_DIR / SHORTCUT_NAME


def install() -> int:
    if not BAT_PATH.exists():
        print(f"HATA: {BAT_PATH} bulunamadı.")
        return 1

    STARTUP_DIR.mkdir(parents=True, exist_ok=True)

    # pywin32 ile shortcut oluştur
    try:
        from win32com.client import Dispatch
    except ImportError:
        print("HATA: pywin32 paketi yüklü değil. pip install pywin32")
        return 1

    if SHORTCUT_PATH.exists():
        print(f"⚠ Kısayol zaten mevcut: {SHORTCUT_PATH}")
        SHORTCUT_PATH.unlink()
        print("  Önce silindi, yeniden kuruluyor…")

    shell = Dispatch("WScript.Shell")
    sc = shell.CreateShortCut(str(SHORTCUT_PATH))
    sc.TargetPath = "cmd.exe"
    sc.Arguments = f'/c start /MIN "" "{BAT_PATH}"'
    sc.WorkingDirectory = str(ROOT)
    sc.WindowStyle = 7  # 7 = Minimized
    sc.Description = "İlaçTarif Watcher — Medula etiket sistemi"
    sc.IconLocation = "cmd.exe,0"
    sc.save()

    print(f"✓ Startup kısayolu oluşturuldu:")
    print(f"  {SHORTCUT_PATH}")
    print(f"  Hedef: {BAT_PATH}")
    print()
    print("Bir sonraki oturum açışında otomatik başlayacak.")
    print("Hemen test etmek için:")
    print(f"  {BAT_PATH}")
    return 0


def remove() -> int:
    if not SHORTCUT_PATH.exists():
        print(f"⚠ Kısayol zaten yok: {SHORTCUT_PATH}")
        return 0
    SHORTCUT_PATH.unlink()
    print(f"✓ Kısayol silindi: {SHORTCUT_PATH}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Startup klasörü autostart kurulumu")
    ap.add_argument("--remove", action="store_true", help="Kısayolu kaldır")
    args = ap.parse_args()
    sys.exit(remove() if args.remove else install())


if __name__ == "__main__":
    main()
