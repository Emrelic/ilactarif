"""İlaç adından farmasötik form / doz birimi tahminleri.

Bu yardımcılar, DB'de tarifi olmayan ilaçlar için Medula'dan gelen
"1.0" gibi çıplak bir doza anlamlı bir birim eklemek için kullanılır.

Örnekler:
    "ARVELES 25MG 20 FİLM TABLET"   → "tablet"
    "AMOKLAVIN BID FORTE ... SÜSPANSİYON" → "ml"
    "VISCOTEARS GOZ JELI 10 G"      → "damla" (kullanim_sekli='Göz üzerine' ise) / "doz"
    "NAZOFIX NAZAL SPREY"           → "doz"
    "DEVIT-3 ORAL DAMLA"            → "damla"
    "KETORAL %2 ŞAMPUAN"            → "uygulama"
"""
from __future__ import annotations


def guess_unit(drug_name: str, kullanim_sekli: str = "") -> str:
    """İlaç adı ve (varsa) Medula'nın 'Kullanım Şekli' alanından birim tahmin et.

    Döndürür: kısa Türkçe birim. Bulamazsa "" döner.
    """
    name  = (drug_name or "").upper()
    sekli = (kullanim_sekli or "").upper()

    # En spesifik kuralları önce yaz
    if "DAMLA" in name or "DAMLALI" in name:
        return "damla"
    if "GÖZ" in sekli or "GÖZ" in name and any(k in name for k in ("DAML", "JELI", "JEL ")):
        return "damla"
    if "BURUN" in sekli or "NAZAL" in name:
        return "doz" if "SPREY" in name else "damla"
    if "SPREY" in name:
        return "doz"
    if "İNHALER" in name or "INHALER" in name:
        return "puf"
    if any(k in name for k in ("SÜSPANSIYON", "SÜSPANSİYON", "ŞURUP", "SURUP",
                                "ORAL SOLÜSYON", "ORAL SOL", "SOLUSYON")):
        return "ml"
    if "GARGARA" in name:
        return "ml"
    if any(k in name for k in ("TABLET", "FİLM TB", "FILM TB", "FTB", "TB.",
                                "KAPSÜL", "KAPSUL", "DRAJE", "ÇİĞNEME",
                                "EFERVESAN", "AĞIZDA DAĞILAN", "AGIZDA DAGILAN")):
        return "tablet"
    if any(k in name for k in ("MERHEM", "POMAD", "KREM", "JEL ", " JEL")):
        return "uygulama"
    if "ŞAMPUAN" in name or "SAMPUAN" in name:
        return "uygulama"
    if "ENJEK" in name or "FLAKON" in name:
        return "doz"
    if "FİTİL" in name or "FITIL" in name or "SUPPOZ" in name:
        return "fitil"
    return ""


def guess_kategori(drug_name: str, kullanim_sekli: str = "") -> str:
    """İlaç adından etikette basılacak büyük kategori başlığı tahmin et.

    Referans etiket örneklerinden:
      ANTİBİYOTİK, AĞRI KESİCİ, AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ, TANSİYON İLACI,
      DİYABET / KALP YETMEZ. / BÖBREK HAS., KORTİZON TEDAVİSİ, KADIN HASTALIKLARINDA,
      KURU GÖZ RAHATSIZLIĞINDA, BOĞAZ SPREYİ, GRİP / SOĞUK ALGINLIĞINDA,
      ÖKSÜRÜK KESİCİ, GUATR İLACI, ANTİDEPRESAN.

    Bu fonksiyon, DB'de tarifi olmayan ilaçlar için makul bir tahmin döndürür.
    DB doldurulurken bu alan AI tarafından daha doğru atanmalı.
    """
    name = (drug_name or "").upper()
    sekli = (kullanim_sekli or "").upper()

    # Antibiyotikler (sık görülen marka adları)
    antibiyotik = ("AMOKLAVIN", "AUGMENTIN", "KLAMOKS", "CROXILEX", "KLAVUNAT",
                   "CEFAKS", "SEFAKLOR", "AZITRO", "ZITROMAX", "CEFIXIM",
                   "FUCIDIN", "FUSIDIC", "DEPOSEL", "RİLİNDAVER", "SEPTIN")
    if any(a in name for a in antibiyotik):
        return "ANTİBİYOTİK"

    # Ağrı kesiciler
    if any(k in name for k in ("ARVELES", "DEXOFEN", "APRANAX", "APROL", "DOLOREX",
                                "DEX-FORTE", "VOLTAREN", "DOLO", "MAJEZIK", "ETOL",
                                "BI-PROFENID", "PROFENID", "PONSTAN", "NAPROXEN",
                                "DICLOFENAC", "IBUFEN", "NUROFEN")):
        return "AĞRI KESİCİ"
    if any(k in name for k in ("PAROL", "TYLOL", "MINOSET", "VERMIDON", "PARASET",
                                "IBURAMIN ZERO", "CALPOL", "DOLVEN", "PEDIFEN",
                                "IBU-FORT", "IBUFEN")):
        return "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"

    # Mide ilaçları
    if any(k in name for k in ("OMEPRAZOL", "PANTPRAZOL", "LANSOPRAZOL", "NEXIUM",
                                "PARIET", "LANSOR", "PANTODAC", "ESOMEPRAZOL",
                                "RANITIDIN", "FAMOTIDIN", "RENNIE", "TALCID")):
        return "MİDE İLACI"

    # Tansiyon
    if any(k in name for k in ("AMLODIS", "AMLODIPIN", "CORALAN", "DELIX", "RAMI",
                                "COVERAM", "EXFORGE", "MICARDIS", "OLMETEC",
                                "NORVASC", "RAMIPRIL", "VALSAR", "LOSARTAN",
                                "PERINDOPRIL", "TENSAR")):
        return "TANSİYON İLACI"

    # Diyabet
    if any(k in name for k in ("GLUCOPHAGE", "GLUKOFEN", "DIAFORMIN", "METFORMIN",
                                "JANUVIA", "FORZIGA", "GALVUS", "AMARYL", "DIAMICRON",
                                "TRAJENTA", "JARDIANCE", "VICTOZA", "ONGLYZA",
                                "INSULIN", "LANTUS", "LEVEMIR")):
        return "DİYABET / KALP YETMEZ. / BÖBREK HAS."

    # Antidepresan
    if any(k in name for k in ("CIPRALEX", "ESCITALOPRAM", "PAROXAT", "PAROXETIN",
                                "SERTRALIN", "LUSTRAL", "FLUOXETIN", "PROZAC",
                                "VENLAFAXIN", "EFEXOR", "DULOXETIN", "CYMBALTA",
                                "MIRTAZAPIN", "REMERON", "LAGYL")):
        return "ANTİDEPRESAN"

    # Guatr
    if any(k in name for k in ("LEVOTIRON", "EUTHYROX", "BITIRON", "TIROMEL")):
        return "GUATR İLACI"

    # Kortizon
    if any(k in name for k in ("DEKORT", "DEPOMEDROL", "PREDNOL", "DELTACORTRIL",
                                "BETNESOL", "DEPRECT", "METİLPRED")):
        return "KORTİZON TEDAVİSİ"

    # Öksürük
    if any(k in name for k in ("KREVAL", "BRONKO", "EXPEKTORAN", "BISOLVON",
                                "MUKOLİT", "ERDOSTIN", "MUCOL")):
        return "ÖKSÜRÜK KESİCİ"

    # Grip
    if any(k in name for k in ("IBURAMIN COLD", "IBURAMIN PLUS", "GRİP", "CORYZA",
                                "THERAFLU", "BENICA")):
        return "GRİP / SOĞUK ALGINLIĞINDA"

    # Boğaz spreyi
    if "BOĞAZ" in name or ("BENPAIN" in name) or ("HEXORAL" in name) or ("STREPSILS" in name):
        return "BOĞAZ SPREYİ" if "SPREY" in name else "BOĞAZ İLACI"

    # Göz ilaçları
    if "GÖZ" in name or "GÖZ" in sekli or "GOZ" in name:
        if "JEL" in name or "JELI" in name:
            return "KURU GÖZ RAHATSIZLIĞINDA"
        if "VISCO" in name or "SYSTANE" in name or "TEARS" in name or "NATURA E" in name or "REFRESH" in name:
            return "KURU GÖZ RAHATSIZLIĞINDA"
        if "AZARGA" in name or "TIMOL" in name or "XALATAN" in name or "TRAVATAN" in name:
            return "GLOKOM İLACI"
        return "GÖZ İLACI"

    # Burun
    if "NAZOFIX" in name or "NAZAL" in name or "BURUN" in name:
        return "BURUN İLACI"

    # Kadın hastalıkları (fitil vb.)
    if "FİTİL" in name or "FITIL" in name or "OVUL" in name or "GINO" in name:
        return "KADIN HASTALIKLARINDA"

    # Kaşıntı
    if "ATARAX" in name or "ANTIHISTAMINIK" in name or "DESLORATADIN" in name or \
       "LORATADIN" in name or "ZYRTEC" in name or "DELODAY" in name:
        return "ALLERJİ / KAŞINTI İLACI"

    # Gargara
    if "GARGARA" in name or "MAXIMUS" in name or "KLOROBEN" in name:
        return "AĞIZ-DİŞ İLACI"

    return ""  # Bilinmiyor


def build_kullanim_talimati(
    *,
    drug_name: str,
    gunluk_kez=None,
    saat_arasi=None,
    kullanim_zamani=None,
    yemek: str = "",
    doz_str: str = "",
    kullanim_sekli: str = "",
) -> str:
    """Yapılandırılmış alanlardan etiketteki büyük kullanım cümlesi üret.

    Çıktı örnekleri:
        "SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR."
        "GÜNDE 1 DEFA 1 TANE AÇ VEYA TOK KARNINA BİR BARDAK SUYLA YUTULUR."
        "SABAH-AKŞAM 1 ÖLÇEK AÇ VEYA TOK KARNINA İÇİLİR."
        "SABAH-ÖĞLE-AKŞAM-GECE YATMADAN 1 DAMLA GÖZ KAPAĞI ARASINA DAMLATILIR."
    """
    name = (drug_name or "").upper()

    # 1) Zaman ifadesi (SABAH-AKŞAM / SABAH-ÖĞLE-AKŞAM / GÜNDE N DEFA)
    zaman_kelimeleri = {
        "sabah": "SABAH", "öğle": "ÖĞLE", "akşam": "AKŞAM",
        "gece": "GECE YATMADAN", "yatmadan": "GECE YATMADAN",
    }
    kullanim_zamani = kullanim_zamani or []
    zaman_parts = []
    for z in kullanim_zamani:
        k = (z or "").strip().lower()
        if k in zaman_kelimeleri:
            zaman_parts.append(zaman_kelimeleri[k])

    if zaman_parts:
        zaman_str = "-".join(zaman_parts)
        if saat_arasi:
            zaman_str += f" [{saat_arasi} SAAT ARA İLE]"
    elif gunluk_kez:
        if gunluk_kez == 2 and not zaman_parts:
            zaman_str = "SABAH-AKŞAM"
            if saat_arasi:
                zaman_str += f" [{saat_arasi} SAAT ARA İLE]"
        elif gunluk_kez == 3:
            zaman_str = "SABAH-ÖĞLE-AKŞAM"
        elif gunluk_kez == 4:
            zaman_str = "SABAH-ÖĞLE-AKŞAM-GECE YATMADAN"
        else:
            zaman_str = f"GÜNDE {gunluk_kez} DEFA"
    elif saat_arasi:
        zaman_str = f"{saat_arasi} SAATTE BİR"
    else:
        zaman_str = "GÜNDE 1 DEFA"

    # 2) Doz ifadesi
    doz_str = (doz_str or "").strip().upper() or "1 TANE"

    # 3) Yemek durumu
    yemek_text_map = {
        "aç":                  "AÇ KARNINA",
        "tok":                 "TOK KARNINA",
        "yemekten önce":       "YEMEKTEN ÖNCE",
        "yemekten sonra":      "YEMEKTEN SONRA",
        "yemek başlangıcında": "YEMEĞİN HEMEN BAŞINDA",
        "yemekle":             "YEMEKLE BİRLİKTE",
        "fark etmez":          "AÇ VEYA TOK KARNINA",
    }
    yemek_text = yemek_text_map.get((yemek or "").strip().lower(), "")

    # 4) Bitiş fiili — ÖNCE Medula'nın "Kullanım Şekli" alanına bak (en güvenilir).
    #    Yoksa ilaç adındaki form ipuçlarına düş.
    ks = (kullanim_sekli or "").upper()
    suyla = ""
    if "GÖZ" in ks:
        bitis = "GÖZ KAPAĞI ARASINA DAMLATILIR"
    elif "BURUN" in ks or "NAZAL" in ks:
        bitis = "BURUN İÇİNE SIKILIR" if "SPREY" in name else "BURUN İÇİNE DAMLATILIR"
    elif "KULAK" in ks:
        bitis = "KULAK İÇİNE DAMLATILIR"
    elif "VAJİNAL" in ks or "VAJEN" in ks:
        bitis = "VAJEN İÇİNE YERLEŞTİRİLİR"
    elif "REKTAL" in ks or "MAKAT" in ks:
        bitis = "MAKATTAN UYGULANIR"
    elif "CİLT" in ks or "DERİ" in ks or "ÜZERİNE SÜR" in ks:
        bitis = "ETKİLENEN BÖLGEYE SÜRÜLÜR"
    elif "AĞIZ" in ks and "GARGARA" in name:
        bitis = "AĞIZ İÇİNDE ÇALKALANIP TÜKÜRÜLÜR"
    elif "AĞIZ" in ks and "SPREY" in name:
        bitis = "AĞIZ İÇİNDEN BOĞAZA SIKILIR"
    elif any(k in name for k in ("ŞURUP", "SURUP", "SÜSPANS", "SÜSPANSIYON", "SÜSPANSİYON")):
        bitis = "İÇİLİR"
    elif "GARGARA" in name:
        bitis = "AĞIZ İÇİNDE ÇALKALANIP TÜKÜRÜLÜR"
    elif "DAMLA" in name:
        bitis = "DAMLATILIR"
    elif "SPREY" in name and ("BOĞAZ" in name or "AĞIZ" in name):
        bitis = "AĞIZ İÇİNDEN BOĞAZA SIKILIR"
    elif "SPREY" in name and ("NAZAL" in name or "BURUN" in name):
        bitis = "BURUN İÇİNE SIKILIR"
    elif "JEL" in name or "MERHEM" in name or "KREM" in name or "POMAD" in name:
        bitis = "ETKİLENEN BÖLGEYE SÜRÜLÜR"
    elif "FİTİL" in name or "FITIL" in name or "OVUL" in name:
        bitis = "VAJEN İÇİNE YERLEŞTİRİLİR"
    elif "SUPPOZ" in name:
        bitis = "MAKATTAN UYGULANIR"
    elif "ENJEK" in name or "FLAKON" in name or "İĞNE" in name:
        bitis = "UYGULANIR"
    elif "ŞAMPUAN" in name or "SAMPUAN" in name:
        bitis = "SAÇA UYGULANIR"
    else:
        # Tablet/kapsül varsayılan
        bitis = "YUTULUR"
        suyla = "BİR BARDAK SUYLA"

    # Cümleyi birleştir
    parts = [zaman_str, doz_str]
    if yemek_text:
        parts.append(yemek_text)
    if suyla:
        parts.append(suyla)
    parts.append(bitis)
    cumle = " ".join(parts).strip()
    if not cumle.endswith("."):
        cumle += "."
    return cumle


def guess_form(drug_name: str) -> str:
    """İlaç adından genel farmasötik form/kategori tahmin et.

    DB'de tarifi yokken etiketin 2. satırında ('ilaç türü') gösterilebilir.
    Kategori değil, FORM döndürür ('Göz damlası', 'Süspansiyon' gibi).
    """
    name = (drug_name or "").upper()
    if "GÖZ" in name and "DAML" in name:    return "Göz damlası"
    if "GÖZ" in name and "JEL" in name:     return "Göz jeli"
    if "GÖZ" in name and "POMAD" in name:   return "Göz pomadı"
    if "NAZAL" in name or "BURUN" in name:  return "Burun spreyi" if "SPREY" in name else "Burun damlası"
    if "KULAK" in name and "DAML" in name:  return "Kulak damlası"
    if "ŞURUP" in name or "SURUP" in name:  return "Şurup"
    if "SÜSPANSIYON" in name or "SÜSPANSİYON" in name: return "Süspansiyon"
    if "GARGARA" in name:                   return "Gargara"
    if "ŞAMPUAN" in name or "SAMPUAN" in name: return "Şampuan"
    if "MERHEM" in name:                    return "Merhem"
    if "KREM" in name:                      return "Krem"
    if "POMAD" in name:                     return "Pomad"
    if "JEL " in name or " JEL" in name:    return "Jel"
    if "FİTİL" in name or "FITIL" in name:  return "Fitil"
    if "EFERVESAN" in name:                 return "Efervesan tablet"
    if "ÇİĞNEME" in name:                   return "Çiğneme tablet"
    if "AĞIZDA DAĞILAN" in name or "AGIZDA DAGILAN" in name: return "Ağızda dağılan tablet"
    if "FİLM TABLET" in name or "FILM TB" in name or "FTB" in name: return "Film tablet"
    if "TABLET" in name or "TB." in name:   return "Tablet"
    if "KAPSÜL" in name or "KAPSUL" in name: return "Kapsül"
    if "DRAJE" in name:                     return "Draje"
    if "ENJEK" in name:                     return "Enjeksiyon"
    if "FLAKON" in name:                    return "Flakon"
    if "SPREY" in name:                     return "Sprey"
    return ""
