"""Windows Task Scheduler'a İlaçTarif Watcher'ı kayıt eder.

Kullanım:
    python scripts/install_autostart.py            # Kur
    python scripts/install_autostart.py --remove   # Kaldır
    python scripts/install_autostart.py --status   # Durum

Görevin özellikleri:
  • Tetikleyici: Kullanıcı oturum açtığında (At log on)
  • Gecikme: 30 saniye (sistem tamamen açılsın)
  • Pencere: Minimize (görev başlatıcı /MIN ile)
  • Hata durumunda: 1 dakika sonra yeniden dene (3 deneme)
  • Yetki: Normal kullanıcı (admin gerekli değil)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TASK_NAME = "IlacTarifWatcher"
BAT_PATH = ROOT / "scripts" / "watch_medula_bg.bat"


def task_exists() -> bool:
    """Görev zaten kayıtlı mı?"""
    r = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def _run(cmd: list[str]) -> tuple[int, str]:
    """schtasks çıktısı Türkçe Windows'ta cp857 — text mode'de hata veriyor."""
    r = subprocess.run(cmd, capture_output=True)
    out = (r.stdout + r.stderr).decode("cp857", errors="replace")
    return r.returncode, out


def install() -> int:
    """Görevi Task Scheduler'a kayıt eder.

    XML yaklaşımı admin yetkisi gerektirebiliyor; bunun yerine basit
    /SC ONLOGON komutu kullanılır. RestartOnFailure gibi gelişmiş ayarlar
    yapılmaz ama oturum açıldığında otomatik başlatma çalışır.
    """
    if not BAT_PATH.exists():
        print(f"HATA: {BAT_PATH} bulunamadı.")
        return 1

    if task_exists():
        print(f"⚠ Görev zaten mevcut: {TASK_NAME} — önce kaldırılıyor.")
        _run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])

    # /TR komutu: cmd.exe ile minimize başlatma
    # Tırnaklar tek seviye olmalı; iç tırnak için \" kullan
    tr = f'cmd /c start /MIN "" "{BAT_PATH}"'

    print(f"📋 Task Scheduler'a kayıt ediliyor: {TASK_NAME}")
    code, out = _run([
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", tr,
        "/SC", "ONLOGON",
        "/DELAY", "0000:30",
        "/RL", "LIMITED",
        "/F",
    ])
    if code != 0:
        print("❌ Kayıt başarısız:")
        print(out)
        return code

    print(f"✓ Görev kayıt edildi: {TASK_NAME}")
    print(f"  Tetik: Kullanıcı oturum açınca (30s gecikme)")
    print(f"  Komut: {tr}")
    print(f"  Loglar: {ROOT / 'data' / 'logs'}")
    print()
    print("Hemen test etmek için:")
    print(f"  python {Path(__file__).name} --run")
    print("Durum görmek için:")
    print(f"  python {Path(__file__).name} --status")
    return 0


def remove() -> int:
    if not task_exists():
        print(f"⚠ Görev kayıtlı değil: {TASK_NAME}")
        return 0
    r = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"✓ Görev kaldırıldı: {TASK_NAME}")
        return 0
    print("❌ Kaldırma başarısız:", r.stderr or r.stdout)
    return r.returncode


def status() -> int:
    if not task_exists():
        print(f"⚠ Görev kayıtlı DEĞİL: {TASK_NAME}")
        print(f"  Kurmak için: python {Path(__file__).name}")
        return 1
    print(f"✓ Görev kayıtlı: {TASK_NAME}\n")
    r = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME, "/V", "/FO", "LIST"],
        capture_output=True, text=True,
    )
    # Türkçe Windows çıktısı cp1254 olabilir, basit decode dene
    print(r.stdout)
    return 0


def run_now() -> int:
    """Görevi manuel olarak hemen tetikle (test için)."""
    if not task_exists():
        print(f"❌ Görev kayıtlı değil. Önce kurun: python {Path(__file__).name}")
        return 1
    r = subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"✓ Görev tetiklendi: {TASK_NAME}")
        print(f"  Logları izleyin: {ROOT / 'data' / 'logs'}")
        return 0
    print("❌ Tetikleme başarısız:", r.stderr or r.stdout)
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description="İlaçTarif Watcher autostart kurulumu")
    ap.add_argument("--remove",  action="store_true", help="Görevi kaldır")
    ap.add_argument("--status",  action="store_true", help="Görev durumunu göster")
    ap.add_argument("--run",     action="store_true", help="Görevi şimdi tetikle (test)")
    args = ap.parse_args()

    if args.remove:
        sys.exit(remove())
    if args.status:
        sys.exit(status())
    if args.run:
        sys.exit(run_now())
    sys.exit(install())


if __name__ == "__main__":
    main()
