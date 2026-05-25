"""Medula reçete HTML → yapısal veri.

Medula iki ekranda ilaç bilgisi gösterir; ikisini de destekliyoruz:

  1) ReceteIslem2.jsp + form `f`     → reçete yazma/inceleme
     - Tablo id 'f:tbl1', class 'dataTableEx'
     - Kolonlar: Barkod | Adet/Periyot/Doz | Stk/Raf | Adı | Tutar | Fark | Rapor

  2) ReceteIslem2.jsp + form `form1` → karekod onay (KarekodIslem.jsp'ye action)
     - Tablo borderTable
     - Kolonlar: RAF | İlaç Adı | Reçeteki Adet | Stok | Doz | Eksik KK
     - 'Doz' sütununda "2 x 1,00 (1Günde)" formatı

Output: PrescriptionCapture (hasta + ilaç listesi).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Optional

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Veri yapıları
# ---------------------------------------------------------------------------
@dataclass
class CapturedDrug:
    barkod: str = ""
    ad: str = ""
    adet: str = ""                # "1" / "6"
    doz_ham: str = ""             # "Günde 1 x 1.0" / "2 x 1,00 (1Günde)" / "1 / Günde / 1 Adet"
    doz_gunluk_kez: Optional[int] = None
    doz_birim_adedi: Optional[float] = None   # "1.0" → 1.0
    doz_birim: str = ""           # "Adet" / "Gram" / "Mililitre"
    periyot: str = ""             # "Günde" / "Haftada" / "Ayda" / "Yılda"
    raf: str = ""                 # "E.6 (4)" gibi
    aciklama: str = ""            # Doktor notu, varsa
    tutar: str = ""
    kullanim_sekli: str = ""      # "Ağızdan", "Göz üzerine", "Cilt üzerine" gibi
    urun_id: str = ""             # Medula'nın iç urunid attribute'u


@dataclass
class PrescriptionCapture:
    page_kind: str = ""           # "e_recete_detay" | "e_recete_sorgu_sonuc"
                                   # | "recete_yazma" | "karekod_onay" | "diger"
    document_url: str = ""
    hasta_ad: str = ""
    hasta_tc: str = ""
    recete_no: str = ""           # E-Reçete No (örn. 2NY2W16)
    takip_no: str = ""
    recete_tarihi: str = ""
    recete_turu: str = ""         # Normal/Kırmızı vb.
    recete_alt_turu: str = ""     # Ayaktan/Yatan vb.
    dr_ad: str = ""
    dr_brans: str = ""
    drugs: list = field(default_factory=list)
    tanılar: list = field(default_factory=list)   # [(ICD-10 kodu, tanı metni)]
    raw_kalem_kutu: str = ""      # "2 KALEM, 2 KUTU GETİRİN" gibi
    eczane: str = ""


# ---------------------------------------------------------------------------
# Yardımcı: hücreyi normalize et
# ---------------------------------------------------------------------------
def _t(el) -> str:
    if el is None:
        return ""
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))


# ---------------------------------------------------------------------------
# Sayfa tipi tespiti
# ---------------------------------------------------------------------------
def detect_page_kind(soup: BeautifulSoup) -> str:
    # En spesifik: E-Reçete Detay (hem E-Reçete Bilgileri hem İlaç Bilgileri başlıkları)
    header_texts = {_t(tr) for tr in soup.find_all("tr", class_="headerRow")}
    if "İlaç Bilgileri" in header_texts and "E-Reçete Bilgileri" in header_texts:
        return "e_recete_detay"
    # E-Reçete sorgu sonuç (hasta seçim listesi)
    if soup.find("table", id="form1:tableExERecete"):
        return "e_recete_sorgu_sonuc"
    # Reçete yazma (Kartlı reçete, f:tbl1)
    if soup.find("form", id="f") and soup.find("table", id="f:tbl1"):
        return "recete_yazma"
    # Karekod onay
    form1 = soup.find("form", id="form1")
    if form1 and "KarekodIslem.jsp" in (form1.get("action") or ""):
        return "karekod_onay"
    # E-Reçete sorgu formu (henüz reçete seçilmemiş)
    if soup.find(string=re.compile(r"E-Reçete\s*Sorgu", re.IGNORECASE)):
        return "e_recete_sorgu_form"
    return "diger"


# ---------------------------------------------------------------------------
# Eczane ve hasta bilgisi (üst banner + reçete no kutuları)
# ---------------------------------------------------------------------------
def _extract_eczane(soup: BeautifulSoup) -> str:
    t = soup.find("td", class_="menuText")
    return _t(t)


def _extract_recete_meta(soup: BeautifulSoup) -> dict:
    """Reçete No, Hasta TC, Hasta Adı, Reçete Tarihi gibi alanları arar."""
    meta = {}
    # Türkçe etiketleri arayıp komşu hücredeki değeri al
    label_map = {
        "Reçete No":   "recete_no",
        "Reçete Tarihi": "recete_tarihi",
        "Hasta T.C.":   "hasta_tc",
        "Hasta TC":     "hasta_tc",
        "Hasta Adı":    "hasta_ad",
        "Hak Sahibi":   "hasta_ad",
        "Dr. Ad/Soyad": "dr_ad",
        "Dr Ad/Soyad":  "dr_ad",
    }
    for td in soup.find_all(["td", "label", "span"]):
        txt = _t(td)
        for label, key in label_map.items():
            if txt.startswith(label) and key not in meta:
                # Aynı td içinde değer olabilir (Reçete No: 0)
                m = re.match(rf"^{re.escape(label)}\s*[:：]?\s*(.+)$", txt)
                val = (m.group(1).strip() if m else "")
                if not val:
                    # Komşu td/span/label'a bak
                    nxt = td.find_next(["td", "span", "label", "input"])
                    if nxt is not None:
                        if nxt.name == "input":
                            val = nxt.get("value", "")
                        else:
                            val = _t(nxt)
                if val:
                    meta[key] = val
                break
    return meta


# ---------------------------------------------------------------------------
# Sayfa tipi 1: Reçete yazma (form f, f:tbl1)
# ---------------------------------------------------------------------------
def parse_recete_yazma(soup: BeautifulSoup) -> PrescriptionCapture:
    cap = PrescriptionCapture(page_kind="recete_yazma")
    cap.eczane = _extract_eczane(soup)
    cap.__dict__.update({k: v for k, v in _extract_recete_meta(soup).items() if v})

    tbl = soup.find("table", id="f:tbl1")
    if not tbl:
        return cap

    # Tablonun başlıkları: ' | Barkod | Adet/Periyot/Doz | Stk/Raf | Adı | Tutar | Fark | Rapor'
    # Her satır: <tr> ... <td>Barkod</td> <td>Doz kompleks</td> <td>Stk/Raf</td> <td>Adı</td> ...
    rows = tbl.find_all("tr", recursive=True)
    for tr in rows:
        cells = tr.find_all("td", recursive=False)
        if len(cells) < 5:
            continue

        # İlk hücre genelde sıra-checkbox; ikinci barkod input
        barkod = ""
        # Barkod hücresi input içerebilir
        bk_inp = cells[1].find("input")
        if bk_inp and bk_inp.get("value"):
            barkod = bk_inp.get("value", "")
        else:
            barkod = _t(cells[1])

        doz_blob = _t(cells[2])
        stk_raf  = _t(cells[3]) if len(cells) > 3 else ""
        ad       = _t(cells[4]) if len(cells) > 4 else ""
        tutar    = _t(cells[5]) if len(cells) > 5 else ""

        # Boş satırları atla
        if not (barkod or ad):
            continue
        # Başlık satırlarını atla
        if barkod.lower() in {"barkod"} or "barkod" == barkod.lower():
            continue

        drug = CapturedDrug(
            barkod=barkod, ad=ad, doz_ham=doz_blob, tutar=tutar
        )
        # Stok/Raf "131" gibi; bazen "11048" — raf bilgisi her zaman ayrı görünmüyor
        drug.raf = stk_raf
        _parse_doz(drug, doz_blob)
        cap.drugs.append(drug)

    # Toplam ve kalem/kutu
    box30 = soup.find(id="f:box30")
    if box30:
        cap.raw_kalem_kutu = _t(box30)

    return cap


# ---------------------------------------------------------------------------
# Sayfa tipi 2: Karekod onay (form1)
# ---------------------------------------------------------------------------
def parse_karekod_onay(soup: BeautifulSoup) -> PrescriptionCapture:
    cap = PrescriptionCapture(page_kind="karekod_onay")
    cap.eczane = _extract_eczane(soup)
    cap.__dict__.update({k: v for k, v in _extract_recete_meta(soup).items() if v})

    # İlk borderTable + "RAF / İlaç Adı / Reçeteki Adet / Stok / Doz / Eksik KK"
    # bulalım — başlık satırına göre tabloyu seç
    target = None
    for tbl in soup.find_all("table"):
        headers = [_t(c) for c in tbl.find_all(["th", "td"])[:6]]
        if headers and "RAF" in headers and "İlaç Adı" in headers and "Doz" in headers:
            target = tbl
            break
    if not target:
        return cap

    header_cells = []
    for tr in target.find_all("tr"):
        header_cells = [_t(c) for c in tr.find_all(["th", "td"])]
        if header_cells and "RAF" in header_cells:
            break
    if not header_cells:
        return cap

    # Kolon indeksleri
    def col(name): return header_cells.index(name) if name in header_cells else -1
    ci_raf = col("RAF"); ci_ad = col("İlaç Adı"); ci_radet = col("Reçeteki Adet")
    ci_stok = col("Stok"); ci_doz = col("Doz"); ci_eks = col("Eksik KK Adet")

    for tr in target.find_all("tr"):
        cells = [_t(c) for c in tr.find_all(["th", "td"])]
        if not cells or cells == header_cells:
            continue
        if len(cells) < max(ci_ad, ci_doz) + 1:
            continue
        # Boş satır filtresi
        ad = cells[ci_ad] if ci_ad >= 0 else ""
        if not ad or ad == "İlaç Adı":
            continue
        drug = CapturedDrug(
            ad=ad,
            raf=cells[ci_raf] if ci_raf >= 0 else "",
            adet=cells[ci_radet] if ci_radet >= 0 else "",
            doz_ham=cells[ci_doz] if ci_doz >= 0 else "",
        )
        _parse_doz(drug, drug.doz_ham)
        cap.drugs.append(drug)

    return cap


# ---------------------------------------------------------------------------
# Sayfa tipi 3: E-Reçete Detay (asıl hedef sayfa)
# ---------------------------------------------------------------------------
def parse_e_recete_detay(soup: BeautifulSoup) -> PrescriptionCapture:
    cap = PrescriptionCapture(page_kind="e_recete_detay")
    cap.eczane = _extract_eczane(soup)

    # Hasta adı: "Geri Dön" butonunun yanındaki TD (label, color blue) genelde
    # ama daha güvenilir yöntem: "T.C.Kimlik No" label'ının değerini al,
    # ve eczane menüText üstündeki başlığı al.

    # "E-Reçete Bilgileri" başlığını içeren <table>'ı bul
    info_table = None
    for tr in soup.find_all("tr", class_="headerRow"):
        if _t(tr) == "E-Reçete Bilgileri":
            info_table = tr.find_parent("table")
            break
    if info_table:
        # Label → value haritası: "label" sınıflı TD'nin (içinde Span outputText),
        # bir sonraki "label" TD değerdir
        cells = info_table.find_all("td", class_="label")
        i = 0
        kv = {}
        while i < len(cells) - 1:
            ktxt = _t(cells[i])
            vtxt = _t(cells[i + 1])
            if ktxt and vtxt:
                kv[ktxt.rstrip(":").strip()] = vtxt
            i += 1
        # Daha hassas: SPAN[class=outputText][style=COLOR: blue]
        for span in info_table.select("span.outputText"):
            style = (span.get("style") or "").lower()
            if "blue" not in style:
                continue
            # Önceki kardeş hücredeki label'ı bul
            td = span.find_parent("td")
            if not td:
                continue
            prev_td = td.find_previous_sibling("td")
            if not prev_td:
                continue
            # 'TD>:<TD>span' yapısı, geriye 2 td gerekebilir
            label_td = prev_td
            for _ in range(2):
                lbl_text = _t(label_td)
                if lbl_text and ":" not in lbl_text and "<" not in lbl_text:
                    break
                prev2 = label_td.find_previous_sibling("td")
                if prev2 is None: break
                label_td = prev2
            label = _t(label_td).rstrip(":").strip()
            value = _t(span)
            if label and value:
                kv[label] = value

        cap.recete_no      = kv.get("E-Reçete No", "")
        cap.takip_no       = kv.get("Takip No", "")
        cap.hasta_tc       = kv.get("T.C.Kimlik No", "") or kv.get("T.C. Kimlik No", "")
        cap.recete_tarihi  = kv.get("Reçete Tarihi", "")
        cap.recete_turu    = kv.get("Reçete Türü", "")
        cap.recete_alt_turu= kv.get("Reçete Alt Türü", "")
        cap.dr_ad          = kv.get("Doktor Adı/Soyadı", "") or kv.get("Doktor Ad/Soyad", "")
        cap.dr_brans       = kv.get("Doktor Branş", "")

    # Hasta adı: form1:textKisiAdi (ad) + form1:textKisiSoyadi (soyad)
    ad_span    = soup.find("span", id=re.compile(r"textKisiAdi$"))
    soyad_span = soup.find("span", id=re.compile(r"textKisiSoyadi$"))
    parts = []
    if ad_span:    parts.append(_t(ad_span))
    if soyad_span: parts.append(_t(soyad_span))
    if parts:
        cap.hasta_ad = " ".join(p for p in parts if p)

    # İlaç Bilgileri bloğu: "İlaç Bilgileri" header TR'sinin sonraki kardeşleri
    drug_header = None
    for tr in soup.find_all("tr", class_="headerRow"):
        if _t(tr) == "İlaç Bilgileri":
            drug_header = tr
            break
    if drug_header:
        # Aynı TBODY içinde, sonraki row1 sınıflı TR'leri tara
        tbody = drug_header.parent
        for tr in tbody.find_all("tr", recursive=False):
            cls = tr.get("class") or []
            if "row1" not in cls and "row2" not in cls:
                continue
            cells = tr.find_all("td", recursive=False)
            if len(cells) < 2:
                continue
            # "Adı : " ile başlayan TR'ler asıl ilaç satırları
            first_txt = _t(cells[0])
            if not first_txt.startswith("Adı"):
                continue

            drug = CapturedDrug()
            # urunid attribute
            drug.urun_id = cells[0].get("urunid", "") or ""
            # cells: [Adı:, ADI_VALUE, Adet:, ADET, Kullanım:, DOZ, Kullanım Şekli:, ŞEKİL]
            def cell(idx):
                return _t(cells[idx]) if idx < len(cells) else ""

            ad_blob = cell(1)
            # "VISCOTEARS 2 MG/G GOZ JELI 10 G (8681738440010)" → ad + barkod
            m = re.match(r"^(.*?)\s*\((\d{8,14})\)\s*$", ad_blob)
            if m:
                drug.ad = m.group(1).strip()
                drug.barkod = m.group(2)
            else:
                drug.ad = ad_blob

            drug.adet = cell(3)
            drug.doz_ham = cell(5)
            drug.kullanim_sekli = cell(7)
            _parse_doz(drug, drug.doz_ham)
            cap.drugs.append(drug)

    # Tanılar (ICD-10 + isim)
    tani_tbl = soup.find("table", id=re.compile(r"^form1:tableEx3"))
    if tani_tbl:
        for tr in tani_tbl.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 2:
                kod = _t(cells[0])
                tani = _t(cells[1])
                if re.match(r"^[A-Z]\d{2}(\.\d+)?", kod):
                    cap.tanılar.append((kod, tani))

    return cap


# ---------------------------------------------------------------------------
# Sayfa tipi 4: E-Reçete sorgu sonuç (hasta + reçete listesi)
# ---------------------------------------------------------------------------
def parse_e_recete_sorgu_sonuc(soup: BeautifulSoup) -> PrescriptionCapture:
    cap = PrescriptionCapture(page_kind="e_recete_sorgu_sonuc")
    cap.eczane = _extract_eczane(soup)

    # Hasta adı: tablonun hemen üstündeki "blue" başlık
    tbl = soup.find("table", id="form1:tableExERecete")
    if tbl:
        prev = tbl.find_previous("span", class_="outputText")
        if prev:
            cap.hasta_ad = _t(prev)
    return cap


# ---------------------------------------------------------------------------
# Doz string'ini ayrıştır: "2 x 1,00 (1Günde)" / "1 / Günde / 1 Adet" /
# "Günde 1 x 1.0" / "Günde 3 x 1,5"
# ---------------------------------------------------------------------------
RX_DOZ_X = re.compile(
    r"(?P<kez>\d+)\s*x\s*(?P<adet>\d+(?:[.,]\d+)?)\s*\(?(?:(?P<periyot_kez>\d+)\s*)?"
    r"(?P<periyot>Günde|Haftada|Ayda|Yılda)?\)?",
    re.IGNORECASE,
)
# "Günde 1 x 1.0" gibi (önce periyot, sonra kez x adet)
RX_DOZ_GUNDE_X = re.compile(
    r"(?P<periyot>Günde|Haftada|Ayda|Yılda)\s+(?P<kez>\d+)\s*x\s*(?P<adet>\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)
RX_DOZ_SLASH = re.compile(
    r"(?P<adet>\d+(?:[.,]\d+)?)\s*/\s*(?P<periyot>Günde|Haftada|Ayda|Yılda)\s*/\s*"
    r"(?P<birim_adedi>\d+(?:[.,]\d+)?)\s*(?P<birim>Adet|Gram|Mililitre|ml|gr)?",
    re.IGNORECASE,
)


def _parse_doz(drug: CapturedDrug, blob: str) -> None:
    if not blob:
        return
    # Önce "Günde 1 x 1.0" formatını dene (E-Reçete Detay sayfası)
    m = RX_DOZ_GUNDE_X.search(blob)
    if m:
        drug.periyot = m.group("periyot")
        drug.doz_gunluk_kez = int(m.group("kez"))
        drug.doz_birim_adedi = float(m.group("adet").replace(",", "."))
        m2 = re.search(r"(Adet|Gram|Mililitre|ml|gr|Damla|Ölçek)", blob, re.IGNORECASE)
        if m2:
            drug.doz_birim = m2.group(1).capitalize()
        return
    m = RX_DOZ_X.search(blob)
    if m:
        drug.doz_gunluk_kez = int(m.group("kez"))
        drug.doz_birim_adedi = float(m.group("adet").replace(",", "."))
        drug.periyot = m.group("periyot") or "Günde"
        m2 = re.search(r"(Adet|Gram|Mililitre|ml|gr|Damla|Ölçek)", blob, re.IGNORECASE)
        drug.doz_birim = m2.group(1).capitalize() if m2 else ""
        return
    m = RX_DOZ_SLASH.search(blob)
    if m:
        drug.doz_birim_adedi = float(m.group("adet").replace(",", "."))
        drug.periyot = m.group("periyot") or "Günde"
        drug.doz_birim = (m.group("birim") or "").capitalize()


# ---------------------------------------------------------------------------
# Genel giriş noktası
# ---------------------------------------------------------------------------
def parse_html(html: str, document_url: str = "") -> PrescriptionCapture:
    soup = BeautifulSoup(html, "lxml")
    kind = detect_page_kind(soup)
    if kind == "e_recete_detay":
        cap = parse_e_recete_detay(soup)
    elif kind == "e_recete_sorgu_sonuc":
        cap = parse_e_recete_sorgu_sonuc(soup)
    elif kind == "recete_yazma":
        cap = parse_recete_yazma(soup)
    elif kind == "karekod_onay":
        cap = parse_karekod_onay(soup)
    else:
        cap = PrescriptionCapture(page_kind=kind)
        cap.eczane = _extract_eczane(soup)
    cap.document_url = document_url
    return cap


def to_dict(cap: PrescriptionCapture) -> dict:
    d = asdict(cap)
    d["drugs"] = [asdict(x) for x in cap.drugs]
    return d
