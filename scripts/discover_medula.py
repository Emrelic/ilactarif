"""Canlı MEDULA pencerelerini bul ve içlerinden HTML çek.

KULLANIM:
  1) Botanik EOS'u açın, içinden Medula'ya giriş yapın.
  2) Medula'da herhangi bir reçete sayfası açın (KartsizEreceteSorgu veya
     ReceteIslem2.jsp gibi).
  3) Bu scripti çalıştırın:  python scripts/discover_medula.py
  4) Çıktıyı paylaşın — kaydedilen HTML'leri parser ile test edip
     etiket önizlemesini oluşturabileceğim.

Çıktı:
  - data/live_capture/live_<timestamp>_w<n>_ie<m>.html   (yakalanan canlı HTML)
  - data/live_capture/discover_<timestamp>.log           (özet log)
"""
from __future__ import annotations

import datetime
import sys
import traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import comtypes

from ilactarif.medula_capture import (  # noqa: E402
    enum_top_windows,
    find_medula_windows,
    find_ie_servers_all,
    capture_window,
    capture_one,
)


def main():
    comtypes.CoInitialize()

    out_dir = ROOT / "data" / "live_capture"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = out_dir / f"discover_{ts}.log"
    log_lines: list[str] = []

    def log(msg=""):
        print(msg)
        log_lines.append(msg)

    log(f"=== MEDULA KEŞİF — {ts} ===\n")

    # 1) Tüm üst seviye pencereleri görelim — kullanıcı kontrol etsin
    log("--- Tüm görünür pencereler (filtre: dolu başlık) ---")
    for hwnd, title, cls, pid in enum_top_windows():
        flag = "*" if ("MEDULA" in title.upper() or "BOTANIK" in title.upper()
                       or "ECZANE" in title.upper()) else " "
        log(f" {flag} hwnd=0x{hwnd:08X}  pid={pid:>6}  cls={cls:<45}  title={title}")

    log("\n--- 'MEDULA' başlıklı pencereler ---")
    medula_wins = find_medula_windows()
    if not medula_wins:
        log("UYARI: Başlığında 'MEDULA' geçen pencere bulunamadı.")
        log("Olası nedenler:")
        log("  - Botanik EOS henüz açılmamış")
        log("  - Pencere minimize ya da gizli")
        log("  - Başlık başka bir formatta")
        log("\nTüm visible pencerelerdeki Internet_Explorer_Server'ları taranıyor...")
        servers = find_ie_servers_all()
        log(f"Bulunan IE_Server toplam: {len(servers)}")
        for parent_hwnd, ie_hwnd in servers:
            log(f"  parent=0x{parent_hwnd:X}  ie=0x{ie_hwnd:X}  → HTML çekme deneniyor...")
            cap = capture_one(ie_hwnd)
            if "error" in cap:
                log(f"     HATA: {cap['error']}")
            else:
                log(f"     OK  URL: {cap.get('url','?')}")
                f = out_dir / f"live_{ts}_orphan_ie{ie_hwnd:X}.html"
                f.write_text(cap.get("html", "") or "", encoding="utf-8")
                log(f"     Kaydedildi: {f.name} ({len(cap.get('html',''))} byte)")
    else:
        for i, w in enumerate(medula_wins, 1):
            log(f"\n[{i}] {w.title}")
            log(f"    hwnd=0x{w.hwnd:X}  class={w.class_name}  pid={w.pid}")
            log(f"    Internet Explorer_Server alt-pencere sayısı: {len(w.ie_servers)}")
            if not w.ie_servers:
                log("    UYARI: IE_Server child yok — Botanik EOS bu pencerede HTML kullanmıyor olabilir")
                continue
            caps = capture_window(w)
            for j, cap in enumerate(caps, 1):
                ie = cap.get("ie_hwnd", 0)
                if "error" in cap:
                    log(f"    IE#{j} (0x{ie:X}) HATA: {cap['error']}")
                    continue
                log(f"    IE#{j} (0x{ie:X})  URL: {cap.get('url','?')}")
                log(f"             title: {cap.get('title','')}")
                html = cap.get("html", "") or ""
                f = out_dir / f"live_{ts}_w{i}_ie{j}.html"
                f.write_text(html, encoding="utf-8")
                log(f"             HTML kaydedildi: {f.name} ({len(html)} byte)")

    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    log(f"\nLog: {log_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
