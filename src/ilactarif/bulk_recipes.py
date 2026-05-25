"""Kategori bazlı otomatik tarif üretimi.

3887 ilacın hepsini drug_guess ile otomatik doldurabilmek için:
  - Kategoriye göre varsayılan UYARI metni
  - Kategoriye göre varsayılan sure_gun (tedavi süresi)
  - Kategoriye göre varsayılan saat_arasi / gunluk_kez / yemek

Bu modül sayesinde DB'de tarifsiz hiçbir ilaç kalmaz.
İleride manuel olarak detaylandırılan ilaçlar (recipes_top100.py gibi)
bu otomatik varsayılanların üzerine yazılır.
"""
from __future__ import annotations

from .drug_guess import (
    build_kullanim_talimati,
    guess_form,
    guess_kategori,
)


# Kategoriye göre tedavi süresi (gün)
DEFAULT_SURE_GUN = {
    "ANTİBİYOTİK":                   7,
    "AĞRI KESİCİ":                   5,
    "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ":   5,
    "MİDE İLACI":                   28,
    "MİDE İLACI (REFLÜ)":           14,
    "TANSİYON İLACI":               30,
    "DİYABET / KALP YETMEZ. / BÖBREK HAS.": 28,
    "KAN SULANDIRICI":              30,
    "KAN SULANDIRICI (İĞNE)":        7,
    "KORTİZON TEDAVİSİ":             7,
    "GUATR İLACI":                  50,
    "ANTİDEPRESAN":                 28,
    "GRİP / SOĞUK ALGINLIĞINDA":     5,
    "ÖKSÜRÜK KESİCİ":                7,
    "ALLERJİ / KAŞINTI İLACI":       7,
    "BOĞAZ SPREYİ":                  7,
    "BOĞAZ İLACI":                   7,
    "AĞIZ-DİŞ İLACI":                7,
    "BURUN AÇICI":                   5,
    "BURUN AÇICI (BEBEK)":           3,
    "BURUN İLACI":                   7,
    "GÖZ İLACI":                     7,
    "KURU GÖZ RAHATSIZLIĞINDA":     30,
    "GLOKOM İLACI":                 30,
    "KADIN HASTALIKLARINDA":         7,
    "CİLT İLACI (DIŞ KULLANIM)":    14,
    "MANTAR İLACI (DIŞ KULLANIM)":  14,
    "KARIN AĞRISI / KASILMA İLACI":  3,
    "BULANTI KESİCİ":                5,
    "KABIZLIK İLACI":               14,
    "FMF / GUT TEDAVİSİ":           30,
    "B VİTAMİNİ DESTEĞİ":           30,
    "B12 VİTAMİNİ DESTEĞİ":          5,
    "DEMİR DESTEĞİ":                30,
    "D VİTAMİNİ":                   30,
    "NEFES AÇICI (BRONKODİLATÖR)":  30,
    "NEFES AÇICI (NEBÜL)":           7,
    "NEFES AÇICI ŞURUP":             7,
    "BESLENME ÜRÜNÜ":                7,
}

# Kategoriye göre varsayılan UYARI metni
DEFAULT_UYARI = {
    "ANTİBİYOTİK":
        "İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
    "AĞRI KESİCİ":
        "Mide rahatsızlığı yapabilir, tok karnına alınız. Aksi söylenmediyse ağrınız oldukça kullanınız.",
    "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ":
        "Ağrı ve ateş oldukça kullanınız. Rahatsızlık düzeldiğinde ilacı bırakınız.",
    "MİDE İLACI":
        "Aç karnına, kahvaltıdan en az 30 dakika önce alınız. Tableti çiğnemeden, bütün olarak yutunuz.",
    "MİDE İLACI (REFLÜ)":
        "Kullanmadan önce çalkalayınız. Diğer ilaçlarınızla en az 2 saat ara verecek şekilde alınız.",
    "TANSİYON İLACI":
        "Her gün aynı saatlerde, düzenli içiniz. Tableti çiğnemeden, bütün olarak yutunuz.",
    "DİYABET / KALP YETMEZ. / BÖBREK HAS.":
        "Tableti ezmeden, çiğnemeden yutunuz. Her gün aynı saatlerde düzenli kullanınız.",
    "KAN SULANDIRICI":
        "Her gün aynı saatlerde, düzenli kullanınız. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
    "KAN SULANDIRICI (İĞNE)":
        "Enjeksiyon yerini her seferinde değiştiriniz. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
    "KORTİZON TEDAVİSİ":
        "Doktor önerisi olmadan ilacı bırakmayınız, kademeli azaltılır. Tuz alımına dikkat ediniz.",
    "GUATR İLACI":
        "Tableti ezmeden, çiğnemeden yutunuz. Her gün aynı saatlerde, düzenli kullanınız.",
    "ANTİDEPRESAN":
        "Bu ilacı kullanırken alkol tüketmeyiniz. Doktor önerisi olmadan bırakmayınız.",
    "GRİP / SOĞUK ALGINLIĞINDA":
        "Bu ilaç hafif uyku sersemlik haline sebep olabilir, dikkat ediniz.",
    "ÖKSÜRÜK KESİCİ":
        "Bol sıvı tüketiniz. Şikayet 5 günden uzun sürerse doktora başvurunuz.",
    "ALLERJİ / KAŞINTI İLACI":
        "Bu ilaç uyku hali yapabilir, kullanırken araç kullanmayınız.",
    "BOĞAZ SPREYİ":
        "Her defasında 4-5 puf sıkılabilir. Boğazınızda kalan kısmı yutabilirsiniz, fazla gelirse tükürebilirsiniz.",
    "BOĞAZ İLACI":
        "Bol sıvı tüketiniz.",
    "AĞIZ-DİŞ İLACI":
        "Yutmayınız. Kullandıktan sonra ağzınızı suyla çalkalamayınız, en az 30 dakika bir şey yiyip içmeyiniz.",
    "BURUN AÇICI":
        "7 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
    "BURUN AÇICI (BEBEK)":
        "3 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
    "BURUN İLACI":
        "Birden fazla kişi tarafından kullanılmamalıdır.",
    "GÖZ İLACI":
        "Şişe ucunu göze değdirmeyiniz. Birden fazla kişi tarafından kullanılmamalıdır.",
    "KURU GÖZ RAHATSIZLIĞINDA":
        "Şişe ucunu göze değdirmeyiniz. Açıldıktan sonra 1 ay içinde tüketiniz.",
    "GLOKOM İLACI":
        "Her gün aynı saatlerde düzenli damlatınız. Şişe ucunu göze değdirmeyiniz.",
    "KADIN HASTALIKLARINDA":
        "Tedaviye eşinizle birlikte devam etmeniz gerekebilir, doktorunuza danışınız.",
    "CİLT İLACI (DIŞ KULLANIM)":
        "Sadece dış kullanım içindir. Göz ve ağız ile temasından kaçınınız.",
    "MANTAR İLACI (DIŞ KULLANIM)":
        "Sadece dış kullanım içindir. Şikayet geçtikten sonra 1-2 hafta daha kullanmaya devam ediniz.",
    "KARIN AĞRISI / KASILMA İLACI":
        "Ağrınız geçtiğinde ilacı bırakınız.",
    "BULANTI KESİCİ":
        "Uyku ve sersemlik haline sebep olabilir, araç kullanmayınız.",
    "KABIZLIK İLACI":
        "Bol su içiniz. Etki 2-3 günde başlayabilir.",
    "FMF / GUT TEDAVİSİ":
        "İshal yaparsa doktora başvurunuz. Greyfurt suyu ile birlikte alınmaz.",
    "B VİTAMİNİ DESTEĞİ":
        "Her gün aynı saatlerde düzenli kullanınız.",
    "B12 VİTAMİNİ DESTEĞİ":
        "Sağlık ocağı / hastane ortamında uygulanacaktır.",
    "DEMİR DESTEĞİ":
        "Aç karnına alınır. Süt, çay, kahve ile birlikte alınmaz. Dişlerde geçici renklenmeye sebep olabilir.",
    "D VİTAMİNİ":
        "Kullanmadan önce çalkalayınız. Doktor önerisi olmadan dozu artırmayınız.",
    "NEFES AÇICI (BRONKODİLATÖR)":
        "Kullandıktan sonra ağzınızı su ile çalkalayınız. Aşırı kullanım çarpıntıya yol açabilir.",
    "NEFES AÇICI (NEBÜL)":
        "Açıldıktan sonra 24 saat içinde kullanılmalıdır.",
    "NEFES AÇICI ŞURUP":
        "Kullanmadan önce çalkalayınız. Çarpıntı / titreme olursa doktora başvurunuz.",
    "BESLENME ÜRÜNÜ":
        "Açıldıktan sonra buzdolabında saklayınız, 24 saat içinde tüketiniz.",
}

# Kategoriye göre günlük kez / saat arası / yemek varsayılanları
DEFAULT_DOZ = {
    "ANTİBİYOTİK":          {"gunluk_kez": 2, "saat_arasi": 12, "yemek": "yemek başlangıcında"},
    "AĞRI KESİCİ":          {"gunluk_kez": 2,                    "yemek": "tok"},
    "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ": {"gunluk_kez": 3,             "yemek": "fark etmez"},
    "MİDE İLACI":           {"gunluk_kez": 1,                    "yemek": "yemekten önce"},
    "MİDE İLACI (REFLÜ)":   {"gunluk_kez": 4,                    "yemek": "yemekten sonra"},
    "TANSİYON İLACI":       {"gunluk_kez": 1,                    "yemek": "yemekten önce"},
    "DİYABET / KALP YETMEZ. / BÖBREK HAS.": {"gunluk_kez": 1,    "yemek": "yemekle"},
    "KAN SULANDIRICI":      {"gunluk_kez": 1,                    "yemek": "yemekten sonra"},
    "KORTİZON TEDAVİSİ":    {"gunluk_kez": 1,                    "yemek": "yemekten sonra"},
    "GUATR İLACI":          {"gunluk_kez": 1,                    "yemek": "yemekten önce"},
    "ANTİDEPRESAN":         {"gunluk_kez": 1,                    "yemek": "fark etmez"},
    "GRİP / SOĞUK ALGINLIĞINDA": {"gunluk_kez": 3,               "yemek": "tok"},
    "ÖKSÜRÜK KESİCİ":       {"gunluk_kez": 3,                    "yemek": "fark etmez"},
    "ALLERJİ / KAŞINTI İLACI": {"gunluk_kez": 1,                 "yemek": "fark etmez"},
    "BOĞAZ SPREYİ":         {"gunluk_kez": 3},
    "AĞIZ-DİŞ İLACI":       {"gunluk_kez": 3},
    "BURUN AÇICI":          {"gunluk_kez": 2},
    "BURUN AÇICI (BEBEK)":  {"gunluk_kez": 2},
    "GÖZ İLACI":            {"gunluk_kez": 3},
    "KURU GÖZ RAHATSIZLIĞINDA": {"gunluk_kez": 3},
    "GLOKOM İLACI":         {"gunluk_kez": 2},
    "KADIN HASTALIKLARINDA": {"gunluk_kez": 1, "kullanim_zamani": ["gece"]},
    "CİLT İLACI (DIŞ KULLANIM)": {"gunluk_kez": 2},
    "MANTAR İLACI (DIŞ KULLANIM)": {"gunluk_kez": 2},
    "KARIN AĞRISI / KASILMA İLACI": {"gunluk_kez": 3,            "yemek": "tok"},
    "BULANTI KESİCİ":       {"gunluk_kez": 3,                    "yemek": "yemekten önce"},
    "KABIZLIK İLACI":       {"gunluk_kez": 1},
    "FMF / GUT TEDAVİSİ":   {"gunluk_kez": 2,                    "yemek": "fark etmez"},
    "B VİTAMİNİ DESTEĞİ":   {"gunluk_kez": 1,                    "yemek": "yemekten sonra"},
    "DEMİR DESTEĞİ":        {"gunluk_kez": 1,                    "yemek": "yemekten önce"},
    "D VİTAMİNİ":           {"gunluk_kez": 1},
    "NEFES AÇICI (BRONKODİLATÖR)": {"gunluk_kez": 4, "saat_arasi": 6},
    "NEFES AÇICI (NEBÜL)":  {"gunluk_kez": 2},
    "NEFES AÇICI ŞURUP":    {"gunluk_kez": 3},
}

DEFAULT_GENERAL_UYARI = "Doktorunuzun önerdiği doz ve süreye uyunuz. Herhangi bir yan etki durumunda doktorunuza başvurunuz."


def build_recipe(drug_name: str, kullanim_sekli: str = "") -> dict:
    """Bir ilaç adı için otomatik tarif üret. Kategori bilinmiyorsa generic döner."""
    kategori = guess_kategori(drug_name, kullanim_sekli) or guess_form(drug_name).upper()
    doz = DEFAULT_DOZ.get(kategori, {})
    talimat = build_kullanim_talimati(
        drug_name=drug_name,
        gunluk_kez=doz.get("gunluk_kez"),
        saat_arasi=doz.get("saat_arasi"),
        kullanim_zamani=doz.get("kullanim_zamani", []),
        yemek=doz.get("yemek", ""),
        doz_str="1 TANE",
        kullanim_sekli=kullanim_sekli,
    )
    return {
        "kategori":          kategori,
        "kullanim_talimati": talimat,
        "uyari_metni":       DEFAULT_UYARI.get(kategori, DEFAULT_GENERAL_UYARI),
        "sure_gun":          DEFAULT_SURE_GUN.get(kategori, 7),
        "ilac_turu":         kategori.title(),
        "gunluk_kez":        doz.get("gunluk_kez"),
        "saat_arasi":        doz.get("saat_arasi"),
        "yemek":             doz.get("yemek", ""),
        "kullanim_zamani":   doz.get("kullanim_zamani", []),
    }
