"""3 yeni capture (e reçete*) HTML'lerini parse et."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilactarif.medula_parser import parse_html

ARCH = Path.home() / "AppData" / "Local" / "UIElementInspector" / "Archive"

TARGETS = [
    "e reçete sorgu ana ekranı",
    "e reçete sorgulanmış ekran",
    "e reçete sayfası",
]

for name in TARGETS:
    p = ARCH / name / "03_SourceCode.html"
    print("=" * 78)
    print(f"DOSYA: {name}")
    if not p.exists():
        print("  ! HTML yok")
        continue
    html = p.read_text(encoding="utf-8", errors="ignore")
    cap = parse_html(html)
    print(f"  Sayfa tipi:  {cap.page_kind}")
    print(f"  Eczane:      {cap.eczane}")
    print(f"  Hasta adı:   {cap.hasta_ad}")
    print(f"  Hasta TC:    {cap.hasta_tc}")
    print(f"  E-Reçete No: {cap.recete_no}")
    print(f"  Takip No:    {cap.takip_no}")
    print(f"  Tarih:       {cap.recete_tarihi}")
    print(f"  Tür:         {cap.recete_turu} / {cap.recete_alt_turu}")
    print(f"  Doktor:      {cap.dr_ad}  ({cap.dr_brans})")
    print(f"  İlaç sayısı: {len(cap.drugs)}")
    for i, d in enumerate(cap.drugs, 1):
        print(f"    {i}. {d.ad}")
        print(f"        barkod: {d.barkod}   adet: {d.adet}")
        print(f"        doz:    {d.doz_ham!r}  →  {d.doz_gunluk_kez}x{d.doz_birim_adedi}{d.doz_birim or ''} / {d.periyot}")
        print(f"        kullanım şekli: {d.kullanim_sekli}")
    if cap.tanılar:
        print(f"  Tanılar:")
        for kod, ad in cap.tanılar:
            print(f"    - {kod}  {ad}")
