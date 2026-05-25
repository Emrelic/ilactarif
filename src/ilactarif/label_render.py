"""Etiket görseli üretimi — Pillow ile.

Hedef yazıcı: Gprinter GP-1125D (203 DPI, 60×40 mm)
  60 mm × 203 DPI / 25.4 = 479.7 ≈ 480 px (en)
  40 mm × 203 DPI / 25.4 = 319.8 ≈ 320 px (boy)

3 etiket tipi üretir:
  1) Kullanım (UsageLabel)
  2) Hazırlama (PreparationLabel)
  3) Uyarı (WarningLabel)

Sade kompozisyon, fontlar Windows'ta hazır gelen arial ailesi.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .models import PreparationLabel, UsageLabel, WarningLabel

# Etiket fiziksel boyutu
LABEL_W = 480   # 60 mm @ 203 DPI
LABEL_H = 320   # 40 mm @ 203 DPI
DPI = 203

# Kenar boşlukları
PAD_X = 10
PAD_Y = 6

# Renkler (termal yazıcı tek renk basar; PNG'de siyah-beyaz)
BG = "white"
FG = "black"


# ---------------------------------------------------------------------------
# Font yükleme
# ---------------------------------------------------------------------------
def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Windows'taki arial/arialbd fontunu döndürür."""
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        # Sistem fontu bulunamazsa fallback
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def _text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap(text: str, font, max_w: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Basit kelime-bazlı satır sarma."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if _text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw_footer(draw: ImageDraw.ImageDraw, eczane: str, telefon: str) -> None:
    """Etiketin alt çizgisi + eczane bilgisi (referans format: 'AD / TELEFON')."""
    font = _font(13, bold=True)
    line_y = LABEL_H - 24
    draw.line([(PAD_X, line_y), (LABEL_W - PAD_X, line_y)], fill="black", width=1)
    parts = [eczane.strip()]
    if telefon:
        # Referansta "İKİZLER ECZANESİ / 0212-515-74-40" formatı
        parts.append(telefon.replace(" ", "-"))
    txt = " / ".join(p for p in parts if p)
    w = _text_w(draw, txt, font)
    draw.text(((LABEL_W - w) // 2, line_y + 4), txt, font=font, fill="black")


def _format_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")


# ---------------------------------------------------------------------------
# Tip 1 — Kullanım etiketi
# ---------------------------------------------------------------------------
def _truncate(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _draw_black_bar(
    d: ImageDraw.ImageDraw,
    y: int, h: int,
    *,
    left:  str = "", left_font=None,
    right: str = "", right_font=None,
    center: str = "", center_font=None,
) -> None:
    """Siyah arka plan üzerine beyaz yazı bant."""
    d.rectangle([0, y, LABEL_W, y + h], fill="black")
    pad_l = 8
    if center and center_font:
        w = _text_w(d, center, center_font)
        # Pillow textbbox üst-sıfırlı, dikey ortalama için ofset gerekli
        try:
            bbox = center_font.getbbox(center)
            ascent = -bbox[1]
        except Exception:
            ascent = 0
        ty = y + (h - (bbox[3] - bbox[1])) // 2 - ascent + (bbox[3] // 4)
        d.text(((LABEL_W - w) // 2, ty), center, font=center_font, fill="white")
        return
    if left and left_font:
        try:
            bbox = left_font.getbbox(left)
        except Exception:
            bbox = (0, 0, 0, 0)
        text_h = (bbox[3] - bbox[1]) or left_font.size
        ty = y + (h - text_h) // 2 - bbox[1]
        d.text((pad_l, ty), left, font=left_font, fill="white")
    if right and right_font:
        rw = _text_w(d, right, right_font)
        try:
            bbox = right_font.getbbox(right)
        except Exception:
            bbox = (0, 0, 0, 0)
        text_h = (bbox[3] - bbox[1]) or right_font.size
        ty = y + (h - text_h) // 2 - bbox[1]
        d.text((LABEL_W - pad_l - rw, ty), right, font=right_font, fill="white")


def _build_talimat_fallback(label: UsageLabel, ilac_adi: str) -> str:
    """UsageLabel.kullanim_talimati boşsa otomatik üret."""
    from .drug_guess import build_kullanim_talimati
    return build_kullanim_talimati(
        drug_name=ilac_adi,
        gunluk_kez=label.gunluk_kez,
        saat_arasi=label.saat_arasi,
        kullanim_zamani=label.kullanim_zamani,
        yemek=label.yemek,
        doz_str=label.doz,
        kullanim_sekli=label.kullanim_sekli,
    )


def render_usage_label(
    *,
    hasta_adi: str,
    ilac_adi: str,
    label: UsageLabel,
    recete_tarihi: Optional[date] = None,
    bitis_tarihi: Optional[date] = None,
    eczane_adi: str = "İKİZLER ECZANESİ",
    eczane_telefon: str = "",
) -> Image.Image:
    """Etiket 1 — referans format (İkizler Eczanesi):

      [Siyah bant 1] HASTA AD                              TARİH
      [Siyah bant 2] İLAÇ ADI                Bitiş Tarihi:XX
      [Siyah bant 3]                  İLAÇ TÜRÜ
                       (boş alan)
        Büyük kullanım talimatı cümlesi (1-4 satır)
        UYARI : küçük yazı uyarı (varsa)
      ──────────────────────────────
      İKİZLER ECZANESİ / 0212-515-74-40
    """
    img = Image.new("RGB", (LABEL_W, LABEL_H), "white")
    d = ImageDraw.Draw(img)

    # Bant fontları
    f_hasta = _font(15, bold=True)
    f_drug  = _font(11, bold=True)
    f_cat   = _font(14, bold=True)

    # Bant 1: Hasta + Reçete tarihi
    bar1_h = 26
    tarih_str = _format_date(recete_tarihi) if recete_tarihi else ""
    _draw_black_bar(d, 0, bar1_h,
                    left=hasta_adi.upper(), left_font=f_hasta,
                    right=tarih_str,        right_font=f_hasta)

    # Bant 2: İlaç adı + Bitiş tarihi
    bar2_y, bar2_h = bar1_h, 20
    drug_text = _truncate(ilac_adi.upper(), 38)
    bitis_str = f"Bitiş Tarihi:{_format_date(bitis_tarihi)}" if bitis_tarihi else ""
    _draw_black_bar(d, bar2_y, bar2_h,
                    left=drug_text, left_font=f_drug,
                    right=bitis_str, right_font=f_drug)

    # Bant 3: İlaç kategorisi (büyük, ortada)
    bar3_y, bar3_h = bar2_y + bar2_h, 22
    kategori = (label.kategori or label.ilac_turu or "").strip().upper()
    if kategori:
        _draw_black_bar(d, bar3_y, bar3_h, center=kategori, center_font=f_cat)
    else:
        # Boş kategori durumunda yine de bantı çiz (boş), tutarlı görünüm için
        _draw_black_bar(d, bar3_y, bar3_h, center=" ", center_font=f_cat)

    # Kullanım talimatı (asıl mesaj, kalın siyah)
    body_y = bar3_y + bar3_h + 6
    f_use  = _font(15, bold=True)
    talimat = (label.kullanim_talimati or "").strip()
    if not talimat:
        talimat = _build_talimat_fallback(label, ilac_adi)
    if talimat:
        lines = _wrap(talimat, f_use, LABEL_W - 2 * PAD_X, d)
        for ln in lines[:4]:
            d.text((PAD_X, body_y), ln, font=f_use, fill="black")
            body_y += 19

    # UYARI satırı (küçük)
    uyari = (label.uyari_metni or "").strip()
    if uyari:
        body_y += 2
        f_w = _font(11)
        head = "UYARI : "
        text = head + uyari
        lines = _wrap(text, f_w, LABEL_W - 2 * PAD_X, d)
        for ln in lines[:3]:
            d.text((PAD_X, body_y), ln, font=f_w, fill="black")
            body_y += 13

    _draw_footer(d, eczane_adi, eczane_telefon)
    return img


# ---------------------------------------------------------------------------
# Tip 2 — Hazırlama etiketi
# ---------------------------------------------------------------------------
def render_preparation_label(
    *,
    hasta_adi: str,
    ilac_adi: str,
    label: PreparationLabel,
    eczane_adi: str = "İKİZLER ECZANESİ",
    eczane_telefon: str = "",
) -> Image.Image:
    img = Image.new("RGB", (LABEL_W, LABEL_H), BG)
    d = ImageDraw.Draw(img)

    f_top    = _font(15, bold=True)
    f_title  = _font(16, bold=True)
    f_step   = _font(13)
    f_meta   = _font(12, bold=True)

    # Üst: hasta · ilaç
    d.text((PAD_X, PAD_Y), hasta_adi.upper(), font=f_top, fill=FG)
    ilac_short = ilac_adi if len(ilac_adi) <= 28 else ilac_adi[:26] + "…"
    w = _text_w(d, ilac_short, _font(12))
    d.text((LABEL_W - PAD_X - w, PAD_Y + 2), ilac_short, font=_font(12), fill=FG)

    # Başlık
    title = f"HAZIRLAMA ({label.form.upper()})" if label.form else "HAZIRLAMA TALİMATI"
    d.text((PAD_X, PAD_Y + 24), title, font=f_title, fill=FG)

    # Ayırıcı
    sep_y = PAD_Y + 46
    d.line([(PAD_X, sep_y), (LABEL_W - PAD_X, sep_y)], fill=FG, width=1)

    # Adımlar
    y = sep_y + 6
    for i, adim in enumerate(label.adimlar[:4], 1):
        prefix = f"{i}. "
        lines = _wrap(prefix + adim, f_step, LABEL_W - 2 * PAD_X, d)
        for ln in lines:
            d.text((PAD_X, y), ln, font=f_step, fill=FG)
            y += 15
            if y > LABEL_H - 80:
                break
        if y > LABEL_H - 80:
            break

    # Meta: saklama + geçerlilik
    meta_parts = []
    if label.saklama:
        meta_parts.append(label.saklama)
    if label.acildiktan_sonra_gecerlilik:
        meta_parts.append(f"Açıldıktan sonra {label.acildiktan_sonra_gecerlilik}")
    if meta_parts:
        meta = " · ".join(meta_parts)
        lines = _wrap(meta, f_meta, LABEL_W - 2 * PAD_X, d)
        my = LABEL_H - 60 - 16 * len(lines)
        for ln in lines:
            w = _text_w(d, ln, f_meta)
            d.text(((LABEL_W - w) // 2, my), ln, font=f_meta, fill=FG)
            my += 15

    _draw_footer(d, eczane_adi, eczane_telefon)
    return img


# ---------------------------------------------------------------------------
# Tip 3 — Uyarı etiketi
# ---------------------------------------------------------------------------
def render_warning_label(
    *,
    hasta_adi: str,
    ilac_adi: str,
    label: WarningLabel,
    eczane_adi: str = "İKİZLER ECZANESİ",
    eczane_telefon: str = "",
) -> Image.Image:
    img = Image.new("RGB", (LABEL_W, LABEL_H), BG)
    d = ImageDraw.Draw(img)

    f_top   = _font(15, bold=True)
    f_title = _font(17, bold=True)
    f_item  = _font(14)

    # Üst: hasta · ilaç
    d.text((PAD_X, PAD_Y), hasta_adi.upper(), font=f_top, fill=FG)
    ilac_short = ilac_adi if len(ilac_adi) <= 28 else ilac_adi[:26] + "…"
    w = _text_w(d, ilac_short, _font(12))
    d.text((LABEL_W - PAD_X - w, PAD_Y + 2), ilac_short, font=_font(12), fill=FG)

    # Başlık
    title = "ÖNEMLİ UYARILAR"
    w = _text_w(d, title, f_title)
    d.text(((LABEL_W - w) // 2, PAD_Y + 26), title, font=f_title, fill=FG)

    # Ayırıcı
    sep_y = PAD_Y + 52
    d.line([(PAD_X, sep_y), (LABEL_W - PAD_X, sep_y)], fill=FG, width=1)

    y = sep_y + 8
    for u in label.uyarilar[:4]:
        bullet = "• "
        lines = _wrap(bullet + u, f_item, LABEL_W - 2 * PAD_X, d)
        for ln in lines:
            d.text((PAD_X, y), ln, font=f_item, fill=FG)
            y += 17
            if y > LABEL_H - 50:
                break
        if y > LABEL_H - 50:
            break

    _draw_footer(d, eczane_adi, eczane_telefon)
    return img


# ---------------------------------------------------------------------------
# Tek noktadan üretim (dispatcher)
# ---------------------------------------------------------------------------
def render_label(label_type: int, **kwargs) -> Image.Image:
    if label_type == 1:
        return render_usage_label(**kwargs)
    if label_type == 2:
        return render_preparation_label(**kwargs)
    if label_type == 3:
        return render_warning_label(**kwargs)
    raise ValueError(f"Bilinmeyen etiket tipi: {label_type}")
