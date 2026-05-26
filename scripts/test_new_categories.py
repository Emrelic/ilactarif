"""Yeni eklediğimiz farklı kategorilerden ilaçlar için etiket testi.

Batch 1-13'te eklenen markaların etiket çıktısını görmek için.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("watch_medula", ROOT / "scripts" / "watch_medula.py")
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)

from ilactarif.medula_parser import CapturedDrug, PrescriptionCapture


# Çok kategorili sentetik bir reçete
cap = PrescriptionCapture(
    page_kind="e_recete_detay",
    hasta_ad="FATMA KAYA",
    hasta_tc="98765432109",
    recete_no="TESTNEW",
    takip_no="TESTNEW2",
    recete_tarihi="26/05/2026",
    recete_turu="Normal",
    recete_alt_turu="Ayaktan",
    dr_ad="UZM. DR. AYŞE",
    dr_brans="Dahiliye",
)

# Yeni eklediğimiz kategorilerden çeşitli ilaçlar
cap.drugs = [
    # Antipsikotik (batch 1)
    CapturedDrug(
        barkod="", ad="GYREX 100MG 30 FİLM TABLET",
        adet="1", doz_ham="Günde 1 x 1.0",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    # Sinir ağrısı (batch 13)
    CapturedDrug(
        barkod="", ad="NERUDA 300MG 50 FİLM TABLET",
        adet="1", doz_ham="Günde 3 x 1.0",
        doz_gunluk_kez=3, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    # Kan sulandırıcı (batch 13)
    CapturedDrug(
        barkod="", ad="TILANTA 90MG 56 FİLM TABLET",
        adet="1", doz_ham="Günde 2 x 1.0",
        doz_gunluk_kez=2, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    # Antibiyotik idrar yolu (batch 2)
    CapturedDrug(
        barkod="", ad="UROCARE 3GR SAŞE",
        adet="1", doz_ham="Tek doz",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Saşe", periyot="Tek doz",
        kullanim_sekli="Ağızdan",
    ),
    # Ereksiyon (batch 13)
    CapturedDrug(
        barkod="", ad="HARDCIS 5MG 28 FİLM TABLET",
        adet="1", doz_ham="Günde 1 x 1.0",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    # Alzheimer (batch 13)
    CapturedDrug(
        barkod="", ad="COGITO 10MG 30 FİLM TABLET",
        adet="1", doz_ham="Günde 1 x 1.0",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Günde",
        kullanim_sekli="Ağızdan",
    ),
    # Göz damlası (batch 8)
    CapturedDrug(
        barkod="", ad="LUCENTIS 10MG/ML 0.3ML 1 FLAKON",
        adet="1", doz_ham="Aylık",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Flakon", periyot="Aylık",
        kullanim_sekli="Göze enjeksiyon",
    ),
    # Mantar tırnak (batch 10)
    CapturedDrug(
        barkod="", ad="LOCERYL %5 TIRNAK CİLASI 2.5ML",
        adet="1", doz_ham="Haftada 1",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Uygulama", periyot="Haftada",
        kullanim_sekli="Tırnak",
    ),
    # Astım inhaler (batch 4)
    CapturedDrug(
        barkod="", ad="FORPACK 12/200MCG CAPSAIR 60 KAPSÜL İNHALASYON TOZ",
        adet="1", doz_ham="Günde 2 x 1.0",
        doz_gunluk_kez=2, doz_birim_adedi=1.0, doz_birim="Puf", periyot="Günde",
        kullanim_sekli="İnhalasyon",
    ),
    # Migren (batch 3)
    CapturedDrug(
        barkod="", ad="ZOMIG 2.5MG 6 FİLM TABLET",
        adet="1", doz_ham="Migren atağında",
        doz_gunluk_kez=1, doz_birim_adedi=1.0, doz_birim="Tablet", periyot="Migren atağında",
        kullanim_sekli="Ağızdan",
    ),
]

wm.handle_recete(cap, html="<test/>")
