"""UIElementInspector arşivini analiz et → Medula sayfa yapısı haritası.

Her capture klasörü için:
  - 03_SourceCode.html varsa, içinden Document URL'i bul (head/title/href ipucu)
  - Form alanları (input/select), her birinin id/name/value
  - Tablolar (id, class, kolon başlıkları, satır sayısı)
  - Önemli butonlar ve linkler

Çıktı: docs/medula_archive_summary.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("HATA: beautifulsoup4 yüklü değil. Yükleniyor...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "lxml"])
    from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path.home() / "AppData" / "Local" / "UIElementInspector" / "Archive"
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)


def parse_html(p: Path) -> dict:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(txt, "lxml")

    # Title
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # Tüm input/select/textarea
    fields = []
    for el in soup.find_all(["input", "select", "textarea"]):
        fields.append({
            "tag":   el.name,
            "id":    el.get("id", ""),
            "name":  el.get("name", ""),
            "type":  el.get("type", ""),
            "value": (el.get("value", "") or "")[:80],
            "class": " ".join(el.get("class", []) or []),
        })

    # Tablolar
    tables = []
    for t in soup.find_all("table"):
        rows = t.find_all("tr")
        if not rows:
            continue
        first = rows[0]
        headers = [th.get_text(strip=True) for th in first.find_all(["th", "td"])]
        tables.append({
            "id":      t.get("id", ""),
            "class":   " ".join(t.get("class", []) or []),
            "rows":    len(rows),
            "headers": headers[:8],
        })

    # Form action'ları
    forms = []
    for f in soup.find_all("form"):
        forms.append({
            "id":     f.get("id", ""),
            "name":   f.get("name", ""),
            "action": f.get("action", ""),
        })

    return {
        "title":  title,
        "fields": fields[:60],   # ilk 60
        "tables": tables[:20],
        "forms":  forms,
        "size":   len(txt),
    }


def extract_url_from_report(report_path: Path) -> str:
    """5Tech raporundan DocumentUrl satırını çek."""
    if not report_path.exists():
        return ""
    txt = report_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"DocumentUrl:\s*(\S+)", txt)
    return m.group(1) if m else ""


def main():
    if not ARCHIVE.exists():
        print(f"Arşiv yok: {ARCHIVE}")
        return 1

    captures = []
    for d in sorted(ARCHIVE.iterdir()):
        if not d.is_dir():
            continue
        html = d / "03_SourceCode.html"
        rep5 = d / "01_Element_5Tech_Report.txt"
        info = {
            "name": d.name,
            "url":  extract_url_from_report(rep5),
            "has_html": html.exists(),
        }
        if html.exists():
            try:
                info.update(parse_html(html))
            except Exception as e:
                info["error"] = str(e)
        captures.append(info)

    # JSON dump
    json_out = OUT / "medula_archive_summary.json"
    json_out.write_text(json.dumps(captures, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON: {json_out}")

    # MD özet
    lines = ["# Medula Arşiv Analizi\n",
             f"Toplam capture: **{len(captures)}**",
             f"HTML içeren: **{sum(1 for c in captures if c.get('has_html'))}**\n",
             "## URL'ler (eşsiz)\n"]
    urls = sorted({c["url"] for c in captures if c.get("url")})
    for u in urls:
        lines.append(f"- `{u}`")
    lines.append("\n## Sayfa Detayları\n")

    for c in captures:
        if not c.get("has_html"):
            continue
        lines.append(f"\n### {c['name']}")
        lines.append(f"- URL: `{c.get('url','')}`")
        lines.append(f"- Title: {c.get('title','')}")
        lines.append(f"- HTML boyutu: {c.get('size','?')} byte")

        forms = c.get("forms", [])
        if forms:
            lines.append("- Form(lar):")
            for f in forms:
                lines.append(f"  - id=`{f['id']}` name=`{f['name']}` action=`{f['action']}`")

        tables = c.get("tables", [])
        if tables:
            lines.append("- Tablo(lar):")
            for t in tables:
                hdrs = " | ".join(t["headers"]) if t["headers"] else ""
                lines.append(f"  - id=`{t['id']}` class=`{t['class']}` rows={t['rows']} headers=[{hdrs}]")

        fields = c.get("fields", [])
        if fields:
            lines.append(f"- Alan sayısı: {len(fields)} (ilk 12 örnek):")
            for f in fields[:12]:
                lines.append(
                    f"  - `{f['tag']}` id=`{f['id']}` name=`{f['name']}` "
                    f"type=`{f['type']}` class=`{f['class']}` val=`{f['value']}`"
                )

    md_out = OUT / "medula_archive_summary.md"
    md_out.write_text("\n".join(lines), encoding="utf-8")
    print(f"MD:   {md_out}")
    print(f"\nÖzet:")
    print(f"  HTML capture: {sum(1 for c in captures if c.get('has_html'))}")
    print(f"  Eşsiz URL:    {len(urls)}")
    for u in urls:
        print(f"    · {u}")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
