"""Sentetik bir reçete oluşturup DB'deki tariflerle etiket önizleme üret.

100 ilaç tarifimizden çeşitli kategorilere ait birkaç ilaç ile örnek etiket gösterir.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# watch_medula.handle_recete'i yeniden kullan
spec = importlib.util.spec_from_file_location("watch_medula", ROOT / "scripts" / "watch_medula.py")
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)

from ilactarif.medula_parser import CapturedDrug, PrescriptionCapture

# Sentetik reçete: gerçek bir Türk hastanın ilaçları gibi
cap = PrescriptionCapture(
    page_kind="e_recete_detay",
    hasta_ad="AHMET YILMAZ",
    hasta_tc="12345678901",
    recete_no="DEMO123",
    takip_no="DEMO456",
    recete_tarihi="26/05/2026",
    recete_turu="Normal",
    recete_alt_turu="Ayaktan",
    dr_ad="DEMO DOKTOR",
    dr_brans="Aile Hekimi",
)

# 6 ilaçlı tipik reçete — farklı kategorilerden
cap.drugs = [
    CapturedDrug(
        barkod="8699525093189", ad="AMOKLAVIN BID 1000MG 14 FİLM TABLET",
        adet="1", doz_ham="Günde 2 x 1.0",
        doz_gunluk_kez=2, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    CapturedDrug(
        barkod="8699832090055", ad="ARVELES 25MG 20 FİLM TABLET",
        adet="1", doz_ham="Günde 3 x 1.0",
        doz_gunluk_kez=3, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    CapturedDrug(
        barkod="8699717010109", ad="PAROL 500MG 20 TABLET",
        adet="1", doz_ham="Günde 3 x 1.0",
        doz_gunluk_kez=3, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    CapturedDrug(
        barkod="8699514011187", ad="LEVOTIRON 100MCG 50 TABLET",
        adet="1", doz_ham="Günde 1 x 1.0",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    CapturedDrug(
        barkod="8699786092730", ad="FORZIGA 10MG 28 FİLM TABLET (SGLT2 INH)",
        adet="1", doz_ham="Günde 1 x 1.0",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    CapturedDrug(
        barkod="8699525283214", ad="AMOKLAVIN BID FORTE 400/57MG 100ML SÜSPANSİYON",
        adet="1", doz_ham="Günde 2 x 5.0",
        doz_gunluk_kez=2, doz_birim_adedi=5.0, doz_birim="Mililitre", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
]

wm.handle_recete(cap, html="<sample/>")
