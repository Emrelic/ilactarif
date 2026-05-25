"""Arşivdeki Medula HTML'leri parse edip sonuçları yaz."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ilactarif.medula_parser import parse_html, to_dict  # noqa: E402

ARCHIVE = Path.home() / "AppData" / "Local" / "UIElementInspector" / "Archive"


def extract_url(report_path: Path) -> str:
    if not report_path.exists():
        return ""
    txt = report_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"DocumentUrl:\s*(\S+)", txt)
    return m.group(1) if m else ""


def main():
    out_dir = ROOT / "data" / "medula_test"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for d in sorted(ARCHIVE.iterdir()):
        html = d / "03_SourceCode.html"
        if not html.exists():
            continue
        url = extract_url(d / "01_Element_5Tech_Report.txt")
        try:
            cap = parse_html(html.read_text(encoding="utf-8", errors="ignore"), document_url=url)
        except Exception as e:
            print(f"HATA: {d.name}: {e}")
            continue
        results.append({
            "capture": d.name,
            "url": url,
            "kind": cap.page_kind,
            "eczane": cap.eczane,
            "hasta_ad": cap.hasta_ad,
            "hasta_tc": cap.hasta_tc,
            "recete_no": cap.recete_no,
            "dr_ad": cap.dr_ad,
            "drug_count": len(cap.drugs),
            "drugs": [{
                "ad": x.ad,
                "barkod": x.barkod,
                "adet": x.adet,
                "doz_ham": x.doz_ham,
                "gunluk_kez": x.doz_gunluk_kez,
                "birim_adedi": x.doz_birim_adedi,
                "periyot": x.periyot,
                "birim": x.doz_birim,
                "raf": x.raf,
            } for x in cap.drugs],
            "kalem_kutu": cap.raw_kalem_kutu,
        })

    out_json = out_dir / "parser_results.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON: {out_json}\n")

    # Konsola özet
    for r in results:
        if r["kind"] == "diger" or r["drug_count"] == 0:
            continue
        print("─" * 78)
        print(f"[{r['kind']:>12}]  {r['capture']}")
        print(f"  URL:      {r['url']}")
        print(f"  Eczane:   {r['eczane']}")
        if r['hasta_ad']: print(f"  Hasta:    {r['hasta_ad']}")
        if r['recete_no']: print(f"  Reçete:   {r['recete_no']}")
        if r['dr_ad']:    print(f"  Dr:       {r['dr_ad']}")
        print(f"  İlaç sayısı: {r['drug_count']}")
        for i, drug in enumerate(r["drugs"], 1):
            doz_pretty = f"{drug['gunluk_kez']}x {drug['birim_adedi']} {drug['birim']}/{drug['periyot']}" \
                if drug['gunluk_kez'] else drug['doz_ham']
            print(f"    {i}. [{drug['raf']:>10}] {drug['ad']:<55}  doz: {doz_pretty}")
        if r["kalem_kutu"]:
            print(f"  → {r['kalem_kutu']}")


if __name__ == "__main__":
    main()
