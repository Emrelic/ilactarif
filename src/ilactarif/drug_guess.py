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


# Etken madde / marka adı → kategori eşlemesi.
# İlaç adında bu anahtar kelimelerden biri geçerse ilgili kategori atanır.
# Sıralama önemli: önce daha spesifik (uzun) eşleşmeler yazılmalı, generic'ler sonra.
ETKEN_MADDE_KATEGORI = [
    # ============ ANTİBİYOTİKLER ============
    ("AMOKSI", "ANTİBİYOTİK"), ("AMOKLAVIN", "ANTİBİYOTİK"),
    ("AUGMENTIN", "ANTİBİYOTİK"), ("KLAMOKS", "ANTİBİYOTİK"),
    ("CROXILEX", "ANTİBİYOTİK"), ("KLAVUNAT", "ANTİBİYOTİK"),
    ("LARGOPEN", "ANTİBİYOTİK"), ("ALFOXIL", "ANTİBİYOTİK"),
    ("DUOCID", "ANTİBİYOTİK"), ("DEVASILIN", "ANTİBİYOTİK"),
    ("SULTAMICILLIN", "ANTİBİYOTİK"), ("UNASYN", "ANTİBİYOTİK"),
    ("AZITRO", "ANTİBİYOTİK"), ("ZITROMAX", "ANTİBİYOTİK"),
    ("AZOMAX", "ANTİBİYOTİK"), ("ZIMAX", "ANTİBİYOTİK"),
    ("KLARITRO", "ANTİBİYOTİK"), ("KLAX", "ANTİBİYOTİK"),
    ("ERITROMISIN", "ANTİBİYOTİK"), ("ROKLARIN", "ANTİBİYOTİK"),
    ("KLINDA", "ANTİBİYOTİK"), ("DALACIN", "ANTİBİYOTİK"),
    ("DOKSI", "ANTİBİYOTİK"), ("MONODOKS", "ANTİBİYOTİK"),
    ("TETRA", "ANTİBİYOTİK"), ("OKSITETRA", "ANTİBİYOTİK"),
    ("SIPRO", "ANTİBİYOTİK"), ("CIPRO", "ANTİBİYOTİK"),
    ("CIPROXIN", "ANTİBİYOTİK"), ("ROXIBAN", "ANTİBİYOTİK"),
    ("LEVOFLOK", "ANTİBİYOTİK"), ("TAVANIC", "ANTİBİYOTİK"),
    ("MOKSIFL", "ANTİBİYOTİK"), ("AVELOX", "ANTİBİYOTİK"),
    ("OFLOKSAS", "ANTİBİYOTİK"),
    ("METRONIDAZOL", "ANTİBİYOTİK"), ("FLAGYL", "ANTİBİYOTİK"),
    ("NIDAZOL", "ANTİBİYOTİK"), ("TINIDAZOL", "ANTİBİYOTİK"),
    ("VANKO", "ANTİBİYOTİK"), ("TEKOPLAN", "ANTİBİYOTİK"),
    ("LINEZOLID", "ANTİBİYOTİK"), ("ZYVOX", "ANTİBİYOTİK"),
    ("SEFAD", "ANTİBİYOTİK"), ("SEFAZOL", "ANTİBİYOTİK"),
    ("SEFAKS", "ANTİBİYOTİK"), ("SEFOTAK", "ANTİBİYOTİK"),
    ("SEFTRIAKSON", "ANTİBİYOTİK"), ("ROCEPHIN", "ANTİBİYOTİK"),
    ("DESEFIN", "ANTİBİYOTİK"), ("EQUIPHIN", "ANTİBİYOTİK"),
    ("IESEF", "ANTİBİYOTİK"), ("SEFAGEN", "ANTİBİYOTİK"),
    ("SEFIKSIM", "ANTİBİYOTİK"), ("SUPRAX", "ANTİBİYOTİK"),
    ("SEFAKLOR", "ANTİBİYOTİK"), ("CEFAKLOR", "ANTİBİYOTİK"),
    ("SEFUROKSIM", "ANTİBİYOTİK"), ("CEFAKS", "ANTİBİYOTİK"),
    ("AKSEF", "ANTİBİYOTİK"), ("ZINNAT", "ANTİBİYOTİK"),
    ("SEFPODOKS", "ANTİBİYOTİK"), ("ORELOX", "ANTİBİYOTİK"),
    ("MEROPENEM", "ANTİBİYOTİK"), ("MERONEM", "ANTİBİYOTİK"),
    ("IMIPENEM", "ANTİBİYOTİK"), ("TIENAM", "ANTİBİYOTİK"),
    ("PIPERA", "ANTİBİYOTİK"), ("TAZOSIN", "ANTİBİYOTİK"),
    ("AMPISILIN", "ANTİBİYOTİK"), ("PEN-OS", "ANTİBİYOTİK"),
    ("PROCAIN", "ANTİBİYOTİK"), ("DEPOPEN", "ANTİBİYOTİK"),
    ("DEVAPEN", "ANTİBİYOTİK"), ("BENZATIN", "ANTİBİYOTİK"),
    ("FUSIDIN", "ANTİBİYOTİK"), ("STAFINE", "ANTİBİYOTİK"),
    ("SULFA", "ANTİBİYOTİK"), ("BAKTRIM", "ANTİBİYOTİK"),
    ("TRIMETOPRIM", "ANTİBİYOTİK"), ("SEPTRIN", "ANTİBİYOTİK"),
    ("NITROFURAN", "ANTİBİYOTİK"), ("FURADANTIN", "ANTİBİYOTİK"),
    ("PIYELOSEPTYL", "ANTİBİYOTİK"),

    # ============ AĞRI KESİCİ (NSAID) ============
    ("ARVELES", "AĞRI KESİCİ"), ("DEXOFEN", "AĞRI KESİCİ"),
    ("DEKSKETOPROFEN", "AĞRI KESİCİ"), ("DEKSALJIN", "AĞRI KESİCİ"),
    ("KETOPROFEN", "AĞRI KESİCİ"), ("PROFENID", "AĞRI KESİCİ"),
    ("BI-PROFENID", "AĞRI KESİCİ"),
    ("IBUPROFEN", "AĞRI KESİCİ"), ("BRUFEN", "AĞRI KESİCİ"),
    ("DOLVEN", "AĞRI KESİCİ"), ("PEDIFEN", "AĞRI KESİCİ"),
    ("IBUFEN", "AĞRI KESİCİ"), ("IBU-FORT", "AĞRI KESİCİ"),
    ("NUROFEN", "AĞRI KESİCİ"), ("IBURAMIN", "AĞRI KESİCİ"),
    ("NAPROKSEN", "AĞRI KESİCİ"), ("APRANAX", "AĞRI KESİCİ"),
    ("APRALJIN", "AĞRI KESİCİ"), ("APROL", "AĞRI KESİCİ"),
    ("NAPROSYN", "AĞRI KESİCİ"),
    ("DICLOFENAC", "AĞRI KESİCİ"), ("DIKLOFENAK", "AĞRI KESİCİ"),
    ("VOLTAREN", "AĞRI KESİCİ"), ("CATAFLAM", "AĞRI KESİCİ"),
    ("DIKLORON", "AĞRI KESİCİ"), ("DOLOREX", "AĞRI KESİCİ"),
    ("ETOL", "AĞRI KESİCİ"), ("ETODOLAK", "AĞRI KESİCİ"),
    ("MELOKSIKAM", "AĞRI KESİCİ"), ("MOBIC", "AĞRI KESİCİ"),
    ("EXEN", "AĞRI KESİCİ"), ("MELOX", "AĞRI KESİCİ"),
    ("NIMESULID", "AĞRI KESİCİ"), ("MESULID", "AĞRI KESİCİ"),
    ("NIMETON", "AĞRI KESİCİ"),
    ("LORNOK", "AĞRI KESİCİ"), ("XEFO", "AĞRI KESİCİ"),
    ("PIROKSIKAM", "AĞRI KESİCİ"), ("FELDEN", "AĞRI KESİCİ"),
    ("FLURBIPROFEN", "AĞRI KESİCİ"), ("MAJEZIK", "AĞRI KESİCİ"),
    ("INDOMETASIN", "AĞRI KESİCİ"), ("ENDOL", "AĞRI KESİCİ"),
    ("DEX-FORTE", "AĞRI KESİCİ"),
    ("TRAMADOL", "AĞRI KESİCİ"), ("CONTRAMAL", "AĞRI KESİCİ"),
    ("ZALDIAR", "AĞRI KESİCİ"), ("ULTRAM", "AĞRI KESİCİ"),
    ("KODEIN", "AĞRI KESİCİ"), ("KATAFAST", "AĞRI KESİCİ"),
    ("PONSTAN", "AĞRI KESİCİ"), ("MEFENAMIK", "AĞRI KESİCİ"),
    ("DOLO-PROXEN", "AĞRI KESİCİ"), ("GERALGINE", "AĞRI KESİCİ"),
    ("CABRAL", "AĞRI KESİCİ"), ("ETOPAN", "AĞRI KESİCİ"),

    # ============ AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ (Parasetamol) ============
    ("PARASETAMOL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("PAROL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("TYLOL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("MINOSET", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("VERMIDON", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("CALPOL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("PANADOL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("CASIPRA", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("NOVALGIN", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("METAMIZOL", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("ANDOLOR", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),
    ("ZERO-P", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ"),

    # ============ MİDE İLAÇLARI ============
    ("OMEPRAZOL", "MİDE İLACI"), ("OMEPRAL", "MİDE İLACI"),
    ("LANSOPRAZOL", "MİDE İLACI"), ("LANSOR", "MİDE İLACI"),
    ("DEGASTROL", "MİDE İLACI"), ("LANTON", "MİDE İLACI"),
    ("PANTOPRAZOL", "MİDE İLACI"), ("PANTO", "MİDE İLACI"),
    ("PANTRO", "MİDE İLACI"), ("PANTPAS", "MİDE İLACI"),
    ("PANTPRO", "MİDE İLACI"),
    ("ESOMEPRAZOL", "MİDE İLACI"), ("NEXIUM", "MİDE İLACI"),
    ("ESONIX", "MİDE İLACI"), ("ESOPRAZOL", "MİDE İLACI"),
    ("RABEPRAZOL", "MİDE İLACI"), ("PARIET", "MİDE İLACI"),
    ("RABIZA", "MİDE İLACI"), ("RABIUM", "MİDE İLACI"),
    ("FAMOTIDIN", "MİDE İLACI"), ("FAMODAR", "MİDE İLACI"),
    ("RANITIDIN", "MİDE İLACI"), ("ZANTAC", "MİDE İLACI"),
    ("RANIVER", "MİDE İLACI"),
    ("GAVISCON", "MİDE İLACI (REFLÜ)"), ("RENNIE", "MİDE İLACI"),
    ("TALCID", "MİDE İLACI"), ("MAALOX", "MİDE İLACI"),
    ("MUCAINE", "MİDE İLACI"), ("RIOPAN", "MİDE İLACI"),
    ("ALGINIK", "MİDE İLACI (REFLÜ)"),
    ("METPAMID", "BULANTI KESİCİ"), ("METOKLOPRAMID", "BULANTI KESİCİ"),
    ("ZOFER", "BULANTI KESİCİ"), ("ONDANSETRON", "BULANTI KESİCİ"),
    ("DOMPERIDON", "BULANTI KESİCİ"), ("MOTILIUM", "BULANTI KESİCİ"),
    ("BUSCOPAN", "KARIN AĞRISI / KASILMA İLACI"),
    ("HYOSCIN", "KARIN AĞRISI / KASILMA İLACI"),
    ("DUSPATALIN", "KARIN AĞRISI / KASILMA İLACI"),

    # ============ TANSİYON ============
    ("AMLODIPIN", "TANSİYON İLACI"), ("AMLODIS", "TANSİYON İLACI"),
    ("NORVASC", "TANSİYON İLACI"), ("AMLOC", "TANSİYON İLACI"),
    ("AMLOPIN", "TANSİYON İLACI"), ("VASCALEX", "TANSİYON İLACI"),
    ("NIFEDIPIN", "TANSİYON İLACI"), ("ADALAT", "TANSİYON İLACI"),
    ("LERKANIDIPIN", "TANSİYON İLACI"), ("LERCADIP", "TANSİYON İLACI"),
    ("FELODIPIN", "TANSİYON İLACI"),
    ("LOSARTAN", "TANSİYON İLACI"), ("COZAAR", "TANSİYON İLACI"),
    ("LORISTA", "TANSİYON İLACI"), ("ARDUAN", "TANSİYON İLACI"),
    ("LOSTAR", "TANSİYON İLACI"),
    ("VALSARTAN", "TANSİYON İLACI"), ("DIOVAN", "TANSİYON İLACI"),
    ("VALTAN", "TANSİYON İLACI"),
    ("TELMISARTAN", "TANSİYON İLACI"), ("MICARDIS", "TANSİYON İLACI"),
    ("EDARBI", "TANSİYON İLACI"), ("KANDESARTAN", "TANSİYON İLACI"),
    ("ATACAND", "TANSİYON İLACI"),
    ("IRBESARTAN", "TANSİYON İLACI"), ("APROVEL", "TANSİYON İLACI"),
    ("OLMESARTAN", "TANSİYON İLACI"), ("OLMETEC", "TANSİYON İLACI"),
    ("ENALAPRIL", "TANSİYON İLACI"), ("VASOLAPRIL", "TANSİYON İLACI"),
    ("KONVERIL", "TANSİYON İLACI"),
    ("PERINDOPRIL", "TANSİYON İLACI"), ("COVERSYL", "TANSİYON İLACI"),
    ("COVERAM", "TANSİYON İLACI"), ("PRESTARIUM", "TANSİYON İLACI"),
    ("RAMIPRIL", "TANSİYON İLACI"), ("DELIX", "TANSİYON İLACI"),
    ("TRIATEC", "TANSİYON İLACI"),
    ("LISINOPRIL", "TANSİYON İLACI"), ("ZESTRIL", "TANSİYON İLACI"),
    ("KAPTOPRIL", "TANSİYON İLACI"), ("KAPRIL", "TANSİYON İLACI"),
    ("BISOPROLOL", "TANSİYON İLACI"), ("CONCOR", "TANSİYON İLACI"),
    ("BYOL", "TANSİYON İLACI"),
    ("METOPROLOL", "TANSİYON İLACI"), ("BELOC", "TANSİYON İLACI"),
    ("BELONOL", "TANSİYON İLACI"),
    ("ATENOLOL", "TANSİYON İLACI"), ("TENORMIN", "TANSİYON İLACI"),
    ("KARVEDILOL", "TANSİYON İLACI"), ("DILATREND", "TANSİYON İLACI"),
    ("NEBIVOLOL", "TANSİYON İLACI"), ("NEBILET", "TANSİYON İLACI"),
    ("PROPRANOLOL", "TANSİYON İLACI"), ("DIDERAL", "TANSİYON İLACI"),
    ("HIDROKLOROTIYAZID", "TANSİYON İLACI"),
    ("FUROSEMID", "TANSİYON İLACI"), ("LASIX", "TANSİYON İLACI"),
    ("DESAL", "TANSİYON İLACI"),
    ("SPIRONOLAKTON", "TANSİYON İLACI"), ("ALDACTONE", "TANSİYON İLACI"),
    ("INDAPAMID", "TANSİYON İLACI"), ("FLUDEKS", "TANSİYON İLACI"),
    ("EXFORGE", "TANSİYON İLACI"), ("EXTAVIA", "TANSİYON İLACI"),

    # ============ KOLESTEROL ============
    ("ATORVASTATIN", "KOLESTEROL İLACI"), ("LIPITOR", "KOLESTEROL İLACI"),
    ("LIPRIMAR", "KOLESTEROL İLACI"), ("ATOR", "KOLESTEROL İLACI"),
    ("LIPDOWN", "KOLESTEROL İLACI"),
    ("ROSUVASTATIN", "KOLESTEROL İLACI"), ("CRESTOR", "KOLESTEROL İLACI"),
    ("ROSUCOR", "KOLESTEROL İLACI"), ("ROSURI", "KOLESTEROL İLACI"),
    ("SIMVASTATIN", "KOLESTEROL İLACI"), ("ZOCOR", "KOLESTEROL İLACI"),
    ("SIMVA", "KOLESTEROL İLACI"),
    ("PRAVASTATIN", "KOLESTEROL İLACI"), ("PRAVACHOL", "KOLESTEROL İLACI"),
    ("FLUVASTATIN", "KOLESTEROL İLACI"), ("LESCOL", "KOLESTEROL İLACI"),
    ("EZETROL", "KOLESTEROL İLACI"), ("LIPIDIL", "KOLESTEROL İLACI"),
    ("FENOFIBRAT", "KOLESTEROL İLACI"),

    # ============ DİYABET ============
    ("METFORMIN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("GLIFOR", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("GLUCOPHAGE", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("GLUKOFEN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("DIAFORMIN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("GLIBENKLAMID", "DİYABET"),
    ("GLIKLAZID", "DİYABET"), ("DIAMICRON", "DİYABET"),
    ("GLIMEPIRID", "DİYABET"), ("AMARYL", "DİYABET"),
    ("GLIPIZID", "DİYABET"),
    ("SITAGLIPTIN", "DİYABET"), ("JANUVIA", "DİYABET"),
    ("VILDAGLIPTIN", "DİYABET"), ("GALVUS", "DİYABET"),
    ("LINAGLIPTIN", "DİYABET"), ("TRAJENTA", "DİYABET"),
    ("DAPAGLIFLOZIN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("FORZIGA", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("EMPAGLIFLOZIN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("JARDIANCE", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("INSULIN", "DİYABET"), ("LANTUS", "DİYABET"),
    ("LEVEMIR", "DİYABET"), ("NOVORAPID", "DİYABET"),
    ("HUMULIN", "DİYABET"), ("HUMALOG", "DİYABET"),
    ("TRESIBA", "DİYABET"), ("APIDRA", "DİYABET"),
    ("LIRAGLUTID", "DİYABET"), ("VICTOZA", "DİYABET"),
    ("OZEMPIC", "DİYABET"), ("SEMAGLUTID", "DİYABET"),
    ("DULAGLUTID", "DİYABET"), ("TRULICITY", "DİYABET"),

    # ============ KAN SULANDIRICI ============
    ("WARFARIN", "KAN SULANDIRICI"), ("COUMADIN", "KAN SULANDIRICI"),
    ("ASPIRIN", "KAN SULANDIRICI"), ("ECOPIRIN", "KAN SULANDIRICI"),
    ("CORASPIN", "KAN SULANDIRICI"), ("DISPRIL", "KAN SULANDIRICI"),
    ("ASOMA", "KAN SULANDIRICI"),
    ("KLOPIDOGREL", "KAN SULANDIRICI"), ("PLAVIX", "KAN SULANDIRICI"),
    ("KARDOGREL", "KAN SULANDIRICI"), ("PINGEL", "KAN SULANDIRICI"),
    ("TIKAGRELOR", "KAN SULANDIRICI"), ("BRILINTA", "KAN SULANDIRICI"),
    ("PRASUGREL", "KAN SULANDIRICI"), ("EFFIENT", "KAN SULANDIRICI"),
    ("APIKSABAN", "KAN SULANDIRICI"), ("ELIQUIS", "KAN SULANDIRICI"),
    ("RIVAROKSABAN", "KAN SULANDIRICI"), ("XARELTO", "KAN SULANDIRICI"),
    ("DABIGATRAN", "KAN SULANDIRICI"), ("PRADAXA", "KAN SULANDIRICI"),
    ("ENOKSAPARIN", "KAN SULANDIRICI (İĞNE)"),
    ("OKSAPAR", "KAN SULANDIRICI (İĞNE)"),
    ("KLEKSAN", "KAN SULANDIRICI (İĞNE)"),
    ("CLEXANE", "KAN SULANDIRICI (İĞNE)"),
    ("FRAXIPARIN", "KAN SULANDIRICI (İĞNE)"),
    ("FRAGMIN", "KAN SULANDIRICI (İĞNE)"),

    # ============ ANTİDEPRESAN / ANKSİYOLİTİK ============
    ("ESITALOPRAM", "ANTİDEPRESAN"), ("CIPRALEX", "ANTİDEPRESAN"),
    ("LEXAPRO", "ANTİDEPRESAN"),
    ("SITALOPRAM", "ANTİDEPRESAN"), ("CIPRAM", "ANTİDEPRESAN"),
    ("CITARO", "ANTİDEPRESAN"),
    ("FLUOKSETIN", "ANTİDEPRESAN"), ("PROZAC", "ANTİDEPRESAN"),
    ("DEPREXIT", "ANTİDEPRESAN"), ("ZEDPREX", "ANTİDEPRESAN"),
    ("SERTRALIN", "ANTİDEPRESAN"), ("LUSTRAL", "ANTİDEPRESAN"),
    ("ZOLOFT", "ANTİDEPRESAN"), ("SERTRALOFT", "ANTİDEPRESAN"),
    ("PAROKSETIN", "ANTİDEPRESAN"), ("PAROXAT", "ANTİDEPRESAN"),
    ("SEROXAT", "ANTİDEPRESAN"), ("XETANOR", "ANTİDEPRESAN"),
    ("VENLAFAKSIN", "ANTİDEPRESAN"), ("EFEXOR", "ANTİDEPRESAN"),
    ("DULOKSETIN", "ANTİDEPRESAN"), ("CYMBALTA", "ANTİDEPRESAN"),
    ("MIRTAZAPIN", "ANTİDEPRESAN"), ("REMERON", "ANTİDEPRESAN"),
    ("MIRTAS", "ANTİDEPRESAN"),
    ("BUPROPION", "ANTİDEPRESAN"), ("WELLBUTRIN", "ANTİDEPRESAN"),
    ("AMITRIPTILIN", "ANTİDEPRESAN"), ("LAROXYL", "ANTİDEPRESAN"),
    ("ALPRAZOLAM", "ANKSİYOLİTİK"), ("XANAX", "ANKSİYOLİTİK"),
    ("DIAZEPAM", "ANKSİYOLİTİK"), ("DIAZEM", "ANKSİYOLİTİK"),
    ("NERVIUM", "ANKSİYOLİTİK"),
    ("LORAZEPAM", "ANKSİYOLİTİK"), ("ATIVAN", "ANKSİYOLİTİK"),
    ("KLONAZEPAM", "ANKSİYOLİTİK"), ("RIVOTRIL", "ANKSİYOLİTİK"),
    ("BROMAZEPAM", "ANKSİYOLİTİK"), ("LEXOTANIL", "ANKSİYOLİTİK"),

    # ============ ANTİPSİKOTİK ============
    ("KETIAPIN", "ANTİPSİKOTİK"), ("SEROQUEL", "ANTİPSİKOTİK"),
    ("OLANZAPIN", "ANTİPSİKOTİK"), ("ZYPREXA", "ANTİPSİKOTİK"),
    ("REZAPIN", "ANTİPSİKOTİK"),
    ("RISPERIDON", "ANTİPSİKOTİK"), ("RISPERDAL", "ANTİPSİKOTİK"),
    ("ARIPIPRAZOL", "ANTİPSİKOTİK"), ("ABILIFY", "ANTİPSİKOTİK"),
    ("ABIZOL", "ANTİPSİKOTİK"),
    ("KLOZAPIN", "ANTİPSİKOTİK"), ("LEPONEX", "ANTİPSİKOTİK"),
    ("HALOPERIDOL", "ANTİPSİKOTİK"), ("NORODOL", "ANTİPSİKOTİK"),

    # ============ ANTİEPİLEPTİK ============
    ("VALPROAT", "ANTİEPİLEPTİK"), ("DEPAKIN", "ANTİEPİLEPTİK"),
    ("CONVULEX", "ANTİEPİLEPTİK"),
    ("LAMOTRIJIN", "ANTİEPİLEPTİK"), ("LAMICTAL", "ANTİEPİLEPTİK"),
    ("LEVETIRASETAM", "ANTİEPİLEPTİK"), ("KEPPRA", "ANTİEPİLEPTİK"),
    ("KARBAMAZEPIN", "ANTİEPİLEPTİK"), ("TEGRETOL", "ANTİEPİLEPTİK"),
    ("GABAPENTIN", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("NEURONTIN", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("PREGABALIN", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("LYRICA", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("PRAGIOLA", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("FENITOIN", "ANTİEPİLEPTİK"), ("EPANUTIN", "ANTİEPİLEPTİK"),

    # ============ ASTIM / KOAH ============
    ("SALBUTAMOL", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("VENTOLIN", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("ASTHALIN", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("FORMOTEROL", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("FORADIL", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("OXIS", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("SALMETEROL", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("SEREVENT", "NEFES AÇICI (BRONKODİLATÖR)"),
    ("BUDESONID", "ASTIM İLACI (KORTİZON)"),
    ("PULMICORT", "ASTIM İLACI (KORTİZON)"),
    ("FLUTIKAZON", "ASTIM İLACI (KORTİZON)"),
    ("FLIXOTIDE", "ASTIM İLACI (KORTİZON)"),
    ("SYMBICORT", "ASTIM İLACI"), ("SERETIDE", "ASTIM İLACI"),
    ("RELVAR", "ASTIM İLACI"), ("FOSTER", "ASTIM İLACI"),
    ("TIOTROPIUM", "ASTIM İLACI"), ("SPIRIVA", "ASTIM İLACI"),
    ("IPRATROPIUM", "ASTIM İLACI"), ("ATROVENT", "ASTIM İLACI"),
    ("MONTELUKAST", "ASTIM İLACI"), ("ONCEAIR", "ASTIM İLACI"),
    ("AIRFLUS", "ASTIM İLACI"), ("SINGULAIR", "ASTIM İLACI"),

    # ============ ALERJİ / ANTİHİSTAMİNİK ============
    ("SETIRİZİN", "ALLERJİ / KAŞINTI İLACI"),
    ("ZYRTEC", "ALLERJİ / KAŞINTI İLACI"),
    ("ZYRTEX", "ALLERJİ / KAŞINTI İLACI"),
    ("CETRIN", "ALLERJİ / KAŞINTI İLACI"),
    ("LEVOSETIRİZİN", "ALLERJİ / KAŞINTI İLACI"),
    ("XYZAL", "ALLERJİ / KAŞINTI İLACI"),
    ("LORATADIN", "ALLERJİ / KAŞINTI İLACI"),
    ("CLARINEX", "ALLERJİ / KAŞINTI İLACI"),
    ("DESLORATADIN", "ALLERJİ / KAŞINTI İLACI"),
    ("AERIUS", "ALLERJİ / KAŞINTI İLACI"),
    ("DELODAY", "ALLERJİ / KAŞINTI İLACI"),
    ("FEKSOFENADIN", "ALLERJİ / KAŞINTI İLACI"),
    ("ALLEGRA", "ALLERJİ / KAŞINTI İLACI"),
    ("HIDROKSIZIN", "ALLERJİ / KAŞINTI İLACI"),
    ("ATARAX", "ALLERJİ / KAŞINTI İLACI"),
    ("RASTEL", "ALLERJİ / KAŞINTI İLACI"),
    ("PRIMOFENON", "ALLERJİ / KAŞINTI İLACI"),
    ("AVIL", "ALLERJİ / KAŞINTI İLACI"),

    # ============ KORTİZON (SİSTEMİK) ============
    ("PREDNIZOLON", "KORTİZON TEDAVİSİ"),
    ("DELTACORTRIL", "KORTİZON TEDAVİSİ"),
    ("PREDNOL", "KORTİZON TEDAVİSİ"),
    ("METILPREDNIZOLON", "KORTİZON TEDAVİSİ"),
    ("DEPOMEDROL", "KORTİZON TEDAVİSİ"),
    ("MEDROL", "KORTİZON TEDAVİSİ"),
    ("DEKSAMETAZON", "KORTİZON TEDAVİSİ"),
    ("DEKORT", "KORTİZON TEDAVİSİ"),
    ("BETAMETAZON", "KORTİZON TEDAVİSİ"),
    ("BETNESOL", "KORTİZON TEDAVİSİ"),
    ("BETACORTON", "KORTİZON TEDAVİSİ"),

    # ============ VİTAMİNLER VE MİNERALLER ============
    ("KOLEKALSIFEROL", "D VİTAMİNİ"), ("DEVIT", "D VİTAMİNİ"),
    ("DEPOSEK", "D VİTAMİNİ"), ("D-COLEFOR", "D VİTAMİNİ"),
    ("COLEDAN", "D VİTAMİNİ"), ("MAGNADD", "D VİTAMİNİ"),
    ("RAYACAL", "D VİTAMİNİ"), ("VIGANTOL", "D VİTAMİNİ"),
    ("KALSIYUM", "KALSİYUM DESTEĞİ"), ("CALCIMAX", "KALSİYUM DESTEĞİ"),
    ("OS-CAL", "KALSİYUM DESTEĞİ"), ("CACIT", "KALSİYUM DESTEĞİ"),
    ("DEMIR", "DEMİR DESTEĞİ"), ("FERRO", "DEMİR DESTEĞİ"),
    ("FERRUM", "DEMİR DESTEĞİ"), ("GLUKOFER", "DEMİR DESTEĞİ"),
    ("FERINJECT", "DEMİR DESTEĞİ"), ("VENOFER", "DEMİR DESTEĞİ"),
    ("MALTOFER", "DEMİR DESTEĞİ"),
    ("DODEX", "B12 VİTAMİNİ DESTEĞİ"), ("B12", "B12 VİTAMİNİ DESTEĞİ"),
    ("KOBAMAMID", "B12 VİTAMİNİ DESTEĞİ"),
    ("BENEXOL", "B VİTAMİNİ DESTEĞİ"), ("BEDOZE", "B VİTAMİNİ DESTEĞİ"),
    ("NEUROBION", "B VİTAMİNİ DESTEĞİ"),
    ("MULTİVİT", "VİTAMİN DESTEĞİ"), ("CENTRUM", "VİTAMİN DESTEĞİ"),
    ("SUPRADYN", "VİTAMİN DESTEĞİ"), ("BEROCCA", "VİTAMİN DESTEĞİ"),
    ("FOLIK", "FOLİK ASİT DESTEĞİ"), ("FOLBIOL", "FOLİK ASİT DESTEĞİ"),
    ("MAGNEZYUM", "MAGNEZYUM DESTEĞİ"),
    ("ZINK", "ÇİNKO DESTEĞİ"), ("ZINCO", "ÇİNKO DESTEĞİ"),

    # ============ TİROİD ============
    ("LEVOTIROKSIN", "GUATR İLACI"), ("LEVOTIRON", "GUATR İLACI"),
    ("EUTHYROX", "GUATR İLACI"), ("BITIRON", "GUATR İLACI"),
    ("TIROMEL", "GUATR İLACI"), ("PROPILTIYO", "GUATR İLACI"),

    # ============ ANTİVİRAL ============
    ("ASIKLOVIR", "ANTİVİRAL"), ("ZOVIRAX", "ANTİVİRAL"),
    ("VALASIKLOVIR", "ANTİVİRAL"), ("VALTREX", "ANTİVİRAL"),
    ("OSELTAMIVIR", "ANTİVİRAL"), ("TAMIFLU", "ANTİVİRAL"),

    # ============ ÜRİK ASİT / GUT ============
    ("ALLOPURINOL", "ÜRİK ASİT İLACI"), ("ÜROKSIM", "ÜRİK ASİT İLACI"),
    ("FEBUKSOSTAT", "ÜRİK ASİT İLACI"), ("ADENURIK", "ÜRİK ASİT İLACI"),
    ("KOLŞISIN", "FMF / GUT TEDAVİSİ"), ("COLCHICUM", "FMF / GUT TEDAVİSİ"),

    # ============ ÖKSÜRÜK / EKSPEKTORAN ============
    ("ERDOSTIN", "ÖKSÜRÜK KESİCİ"), ("BISOLVON", "ÖKSÜRÜK KESİCİ"),
    ("MUCOLIT", "ÖKSÜRÜK KESİCİ"), ("AMBROKSOL", "ÖKSÜRÜK KESİCİ"),
    ("BROMHEKSIN", "ÖKSÜRÜK KESİCİ"), ("BRONKO", "ÖKSÜRÜK KESİCİ"),
    ("DEXTROMETORFAN", "ÖKSÜRÜK KESİCİ"),
    ("PULMOTAB", "ÖKSÜRÜK KESİCİ"), ("KREVAL", "ÖKSÜRÜK KESİCİ"),
    ("KARMOLIS", "ÖKSÜRÜK KESİCİ"), ("THYMIPIN", "ÖKSÜRÜK KESİCİ"),

    # ============ GRİP ============
    ("A-FERIN", "GRİP / SOĞUK ALGINLIĞINDA"),
    ("IBURAMIN COLD", "GRİP / SOĞUK ALGINLIĞINDA"),
    ("THERAFLU", "GRİP / SOĞUK ALGINLIĞINDA"),
    ("NUROFEN COLD", "GRİP / SOĞUK ALGINLIĞINDA"),
    ("IBUCOLD", "GRİP / SOĞUK ALGINLIĞINDA"),
    ("PARAFON", "GRİP / SOĞUK ALGINLIĞINDA"),

    # ============ GÖZ İLAÇLARI ============
    ("XALATAN", "GLOKOM İLACI"), ("LATANOPROST", "GLOKOM İLACI"),
    ("TRAVATAN", "GLOKOM İLACI"), ("TRAVOPROST", "GLOKOM İLACI"),
    ("TIMOL", "GLOKOM İLACI"), ("TIMOPRESS", "GLOKOM İLACI"),
    ("BRIMONIDIN", "GLOKOM İLACI"), ("ALPHAGAN", "GLOKOM İLACI"),
    ("AZARGA", "GLOKOM İLACI"), ("COSOPT", "GLOKOM İLACI"),
    ("GANFORT", "GLOKOM İLACI"),
    ("VISCOTEARS", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("SYSTANE", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("TEARS NATURALE", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("REFRESH", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("THERA TEARS", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("OPTIVE", "KURU GÖZ RAHATSIZLIĞINDA"),
    ("BLEPHAGEL", "GÖZ KAPAĞI BAKIMI"),

    # ============ BURUN ============
    ("ILIADIN", "BURUN AÇICI"), ("OTRIVINE", "BURUN AÇICI"),
    ("OTRIVIN", "BURUN AÇICI"), ("RHINFANT", "BURUN AÇICI (BEBEK)"),
    ("OKSIMETAZOLIN", "BURUN AÇICI"), ("AFRIN", "BURUN AÇICI"),
    ("PHYSIOMER", "BURUN BAKIMI (TUZ)"),
    ("STERIMAR", "BURUN BAKIMI (TUZ)"), ("OCEAN", "BURUN BAKIMI (TUZ)"),
    ("NAZOFIX", "BURUN BAKIMI"), ("RHINASE", "BURUN İLACI"),
    ("NASONEX", "BURUN İLACI (KORTİZON)"),
    ("AVAMYS", "BURUN İLACI (KORTİZON)"),
    ("FLIXONASE", "BURUN İLACI (KORTİZON)"),

    # ============ KADIN HASTALIKLARI ============
    ("FLUKONAZOL", "MANTAR İLACI"), ("DIFLUCAN", "MANTAR İLACI"),
    ("FLUSER", "MANTAR İLACI"),
    ("KLOTRIMAZOL", "KADIN HASTALIKLARINDA"),
    ("CANESTEN", "KADIN HASTALIKLARINDA"),
    ("GINO-TRAVOGEN", "KADIN HASTALIKLARINDA"),
    ("FLUOMIZIN", "KADIN HASTALIKLARINDA"),
    ("LAGYL", "KADIN HASTALIKLARINDA"),
    ("MIKOGYN", "KADIN HASTALIKLARINDA"),
    ("TRAVAZOL", "MANTAR İLACI"),
    ("LAMISIL", "MANTAR İLACI"), ("TERBISIL", "MANTAR İLACI"),
    ("KETOKONAZOL", "MANTAR İLACI"), ("KETORAL", "MANTAR İLACI"),
    ("NIZORAL", "MANTAR İLACI"),
    ("MIKONAZOL", "MANTAR İLACI"), ("DAKTARIN", "MANTAR İLACI"),

    # ============ DOĞUM KONTROL / HORMON ============
    ("DİYANE", "DOĞUM KONTROL"), ("YASMIN", "DOĞUM KONTROL"),
    ("YAZ", "DOĞUM KONTROL"), ("MICROGYNON", "DOĞUM KONTROL"),
    ("CERAZETTE", "DOĞUM KONTROL"), ("BELARA", "DOĞUM KONTROL"),
    ("ETINIL", "DOĞUM KONTROL"),
    ("PROGESTERON", "HORMON"), ("CRINONE", "HORMON"),
    ("DUFASTON", "HORMON"), ("LUTORAL", "HORMON"),
    ("PROGYNOVA", "HORMON"), ("ESTROFEM", "HORMON"),

    # ============ PROSTAT ============
    ("FINASTERID", "PROSTAT İLACI"), ("PROSCAR", "PROSTAT İLACI"),
    ("DUTASTERID", "PROSTAT İLACI"), ("AVODART", "PROSTAT İLACI"),
    ("TAMSULOSIN", "PROSTAT İLACI"), ("FLOMAX", "PROSTAT İLACI"),
    ("URIMAX", "PROSTAT İLACI"), ("VESITRIM", "PROSTAT İLACI"),

    # ============ KEMİK / OSTEOPOROZ ============
    ("ALENDRON", "OSTEOPOROZ İLACI"), ("FOSAMAX", "OSTEOPOROZ İLACI"),
    ("FOSAVANCE", "OSTEOPOROZ İLACI"),
    ("RISEDRON", "OSTEOPOROZ İLACI"), ("ACTONEL", "OSTEOPOROZ İLACI"),
    ("DENOSUMAB", "OSTEOPOROZ İLACI"), ("PROLIA", "OSTEOPOROZ İLACI"),
    ("STRONTYUM", "OSTEOPOROZ İLACI"),

    # ============ KABIZLIK / İSHAL ============
    ("LAKTULOZ", "KABIZLIK İLACI"), ("DUPHALAC", "KABIZLIK İLACI"),
    ("LAKTITOL", "KABIZLIK İLACI"), ("LAEVOLAC", "KABIZLIK İLACI"),
    ("PEG", "KABIZLIK İLACI"), ("MOVICOL", "KABIZLIK İLACI"),
    ("BISAKODIL", "KABIZLIK İLACI"), ("DULCOLAX", "KABIZLIK İLACI"),
    ("SENNA", "KABIZLIK İLACI"), ("SENADE", "KABIZLIK İLACI"),
    ("LOPERAMID", "İSHAL KESİCİ"), ("DIAREST", "İSHAL KESİCİ"),
    ("LOPERIN", "İSHAL KESİCİ"), ("DIAFOR", "İSHAL KESİCİ"),
    ("SACCHAROMYCES", "PROBİYOTİK"), ("PROBIO", "PROBİYOTİK"),
    ("ENTEROGERMINA", "PROBİYOTİK"),

    # ============ GARGARALAR / AĞIZ ============
    ("KLOROBEN", "AĞIZ-DİŞ İLACI"), ("ANDOREX", "AĞIZ-DİŞ İLACI"),
    ("OROHEKS", "AĞIZ-DİŞ İLACI"), ("MAXIMUS", "BOĞAZ SPREYİ"),
    ("BENZIDAMIN", "AĞIZ-DİŞ İLACI"), ("TANTUM", "AĞIZ-DİŞ İLACI"),
    ("KLORHEKSIDIN", "AĞIZ-DİŞ İLACI"), ("HEXORAL", "AĞIZ-DİŞ İLACI"),
    ("STREPSILS", "BOĞAZ İLACI"), ("BENPAIN", "BOĞAZ SPREYİ"),

    # ============ CİLT (DIŞ KULLANIM) ============
    ("FITO", "CİLT İLACI (DIŞ KULLANIM)"),
    ("BEPANTHEN", "CİLT İLACI (DIŞ KULLANIM)"),
    ("MADECASSOL", "CİLT İLACI (DIŞ KULLANIM)"),
    ("FUSIDIK", "CİLT İLACI (ANTİBİYOTİK)"),
    ("FUCIDIN", "CİLT İLACI (ANTİBİYOTİK)"),
    ("MUPIROSIN", "CİLT İLACI (ANTİBİYOTİK)"),
    ("BACTROBAN", "CİLT İLACI (ANTİBİYOTİK)"),
    ("EFICAN", "CİLT İLACI"),
    ("BETNOVATE", "CİLT İLACI (KORTİZON)"),
    ("ELOCON", "CİLT İLACI (KORTİZON)"),
    ("ADVANTAN", "CİLT İLACI (KORTİZON)"),
    ("HYDROCORTISON", "CİLT İLACI (KORTİZON)"),
    ("PROTOPIC", "CİLT İLACI (EGZEMA)"),
    ("ELIDEL", "CİLT İLACI (EGZEMA)"),
    ("DAIVOBET", "SEDEF HASTALIĞI İLACI"),
    ("DAIVONEX", "SEDEF HASTALIĞI İLACI"),

    # ============ NÖROLOJİ (PARKİNSON / ALZHEİMER) ============
    ("LEVODOPA", "PARKİNSON İLACI"), ("MADOPAR", "PARKİNSON İLACI"),
    ("SINEMET", "PARKİNSON İLACI"),
    ("PRAMIPEKSOL", "PARKİNSON İLACI"), ("OPRYMEA", "PARKİNSON İLACI"),
    ("RIVASTIGMIN", "ALZHEİMER İLACI"), ("EXELON", "ALZHEİMER İLACI"),
    ("DONEPEZIL", "ALZHEİMER İLACI"), ("ARICEPT", "ALZHEİMER İLACI"),
    ("MEMANTIN", "ALZHEİMER İLACI"), ("EBIXA", "ALZHEİMER İLACI"),

    # ============ KASIK / KAS GEVŞETİCİ ============
    ("MYOLASTAN", "KAS GEVŞETİCİ"), ("TOLPERIZON", "KAS GEVŞETİCİ"),
    ("MYDOCALM", "KAS GEVŞETİCİ"), ("MUSCORIL", "KAS GEVŞETİCİ"),
    ("BENADON", "KAS GEVŞETİCİ"),
    ("TIYOKOLŞIKOSID", "KAS GEVŞETİCİ"),

    # ============ SİNİR AĞRISI ============
    ("TIAPRID", "SİNİR AĞRISI / VERTİGO"),
    ("BETAHIST", "VERTİGO İLACI"), ("VASOSERC", "VERTİGO İLACI"),
    ("MIKRONOR", "VERTİGO İLACI"),

    # ============ ZAYIFLAMA / İŞTAH KESİCİ ============
    ("ORLISTAT", "ZAYIFLAMA İLACI"), ("XENICAL", "ZAYIFLAMA İLACI"),
    ("MOUNJARO", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("TIRZEPATID", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),

    # ============ BATCH 1 — ANTİBİYOTİK (yaygın marka adları) ============
    ("SULCID", "ANTİBİYOTİK"), ("ALFASID", "ANTİBİYOTİK"),
    ("MACROL", "ANTİBİYOTİK"), ("KLAMER", "ANTİBİYOTİK"),
    ("CLASEM", "ANTİBİYOTİK"), ("ENFEXIA", "ANTİBİYOTİK"),
    ("CEFTINEX", "ANTİBİYOTİK"), ("AZELTIN", "ANTİBİYOTİK"),
    ("ZIMAKS", "ANTİBİYOTİK"), ("BITERAL", "ANTİBİYOTİK"),
    ("FIXEF", "ANTİBİYOTİK"), ("CEFDIFIX", "ANTİBİYOTİK"),
    ("ULTROX", "ANTİBİYOTİK"), ("CEMPES", "ANTİBİYOTİK"),
    ("IESPOR", "ANTİBİYOTİK"), ("NOVOSEF", "ANTİBİYOTİK"),
    ("UNACEFIN", "ANTİBİYOTİK"), ("MAKSIPOR", "ANTİBİYOTİK"),
    ("DEPOSILIN", "ANTİBİYOTİK"), ("ORNISID", "ANTİBİYOTİK"),
    ("BACTRIM", "ANTİBİYOTİK"), ("CLEOCIN", "ANTİBİYOTİK"),
    ("ANDAZOL", "ANTİBİYOTİK"),  # albendazol antiparaziter
    ("GENTA", "ANTİBİYOTİK"),    # gentamisin
    ("INFEX", "ANTİBİYOTİK"),    # siprofloksasin
    ("ZIVER", "ANTİVİRAL"),      # asiklovir
    ("AKLOVIR", "ANTİVİRAL"), ("ASIVIRAL", "ANTİVİRAL"),
    ("FLUCAN", "MANTAR İLACI"),
    ("DIAFURYL", "İSHAL KESİCİ"),
    ("MAFLOR", "PROBİYOTİK"),
    ("FUCITEC", "CİLT İLACI (ANTİBİYOTİK)"),

    # ============ BATCH 1 — TANSİYON ============
    ("HIPERSAR", "TANSİYON İLACI"), ("EXCALIBA", "TANSİYON İLACI"),
    ("IRDAPIN", "TANSİYON İLACI"), ("VASOXEN", "TANSİYON İLACI"),
    ("CARDURA", "TANSİYON İLACI"), ("CANDEXIL", "TANSİYON İLACI"),
    ("BETABLOK", "TANSİYON İLACI"), ("MONOPRIL", "TANSİYON İLACI"),
    ("DILTIZEM", "TANSİYON İLACI"), ("TRIPLIXAM", "TANSİYON İLACI"),
    ("TELMODIP", "TANSİYON İLACI"), ("CO-IRDA", "TANSİYON İLACI"),
    ("HYZAAR", "TANSİYON İLACI"), ("CANDECARD", "TANSİYON İLACI"),
    ("ENAPRIL", "TANSİYON İLACI"), ("SINOPRYL", "TANSİYON İLACI"),
    ("GOPTEN", "TANSİYON İLACI"), ("MONOVAS", "TANSİYON İLACI"),
    ("VASTAREL", "TANSİYON İLACI"),  # trimetazidin (angina)
    ("MONOKET", "TANSİYON İLACI"),   # isosorbid (angina)
    ("TANSIFA", "TANSİYON İLACI"),
    ("SANELOC", "TANSİYON İLACI"),   # metoprolol

    # ============ BATCH 1 — ANTİDEPRESAN / ANTİPSİKOTİK / ANKSİYOLİTİK ============
    ("CEDRINA", "ANTİPSİKOTİK"), ("QUET", "ANTİPSİKOTİK"),
    ("KETYA", "ANTİPSİKOTİK"), ("REXAPIN", "ANTİPSİKOTİK"),
    ("RIXPER", "ANTİPSİKOTİK"),
    ("CITOLES", "ANTİDEPRESAN"), ("PAXERA", "ANTİDEPRESAN"),
    ("SECITA", "ANTİDEPRESAN"), ("SELECTRA", "ANTİDEPRESAN"),
    ("REDEPRA", "ANTİDEPRESAN"), ("ZEDPRA", "ANTİDEPRESAN"),
    ("ADELEKS", "ANTİDEPRESAN"),  # essitalopram
    ("CITOL", "ANTİDEPRESAN"),    # sitalopram
    ("ZOLAX", "ANKSİYOLİTİK"),    # alprazolam

    # ============ BATCH 1 — AĞRI KESİCİ / KAS GEVŞETİCİ ============
    ("DICLOMEC", "AĞRI KESİCİ"), ("LEODEX", "AĞRI KESİCİ"),
    ("NIMES", "AĞRI KESİCİ"), ("KETAVEL", "AĞRI KESİCİ"),
    ("EDOLAR", "AĞRI KESİCİ"), ("DEXPASS", "AĞRI KESİCİ"),
    ("DOLINE", "AĞRI KESİCİ"),
    ("DUROGESIC", "AĞRI KESİCİ (KUVVETLİ)"),
    ("FENTANIL", "AĞRI KESİCİ (KUVVETLİ)"),
    ("MUSCOFLEX", "KAS GEVŞETİCİ"), ("TYOFLEX", "KAS GEVŞETİCİ"),
    ("TIYOKAS", "KAS GEVŞETİCİ"), ("FLEXO", "KAS GEVŞETİCİ"),

    # ============ BATCH 1 — DİYABET / MİDE / VİTAMİN ============
    ("GLIFIX", "DİYABET"),    # pioglitazon
    ("MATOFIN", "DİYABET / KALP YETMEZ. / BÖBREK HAS."),
    ("GLIMAX", "DİYABET"),
    ("GLUCOBAY", "DİYABET"),
    ("JANUMET", "DİYABET"),   # sitagliptin+metformin
    ("GALVIKS", "DİYABET"),   # vildagliptin+metformin
    ("ESMAX", "MİDE İLACI"),  # esomeprazol
    ("PULCET", "MİDE İLACI"), # pantoprazol
    ("BEMIKS", "B VİTAMİNİ DESTEĞİ"),
    ("DESIFEROL", "D VİTAMİNİ"),
    ("APIKOBAL", "B12 VİTAMİNİ DESTEĞİ"),
    ("MUCOVIT-C", "VİTAMİN DESTEĞİ"),

    # ============ BATCH 1 — ALERJİ / ASTIM / BURUN ============
    ("ALLERSET", "ALLERJİ / KAŞINTI İLACI"),
    ("ZADITEN", "ALLERJİ / KAŞINTI İLACI"),
    ("LEVMONT", "ASTIM İLACI"),  # levosetirizin+montelukast
    ("ZESPIRA", "ASTIM İLACI"),  # montelukast
    ("M-FURO", "BURUN İLACI"),
    ("MOMECON", "BURUN İLACI"),
    ("INFLACORT", "KORTİZON TEDAVİSİ"),
    ("BEKLAZON", "ASTIM İLACI"),

    # ============ BATCH 1 — ANTİEPİLEPTİK / SİNİR ============
    ("GABASET", "ANTİEPİLEPTİK / SİNİR AĞRISI"),
    ("EPIXX", "ANTİEPİLEPTİK"),   # levetirasetam
    ("TRILEPTAL", "ANTİEPİLEPTİK"),
    ("OKSKARBAZEPIN", "ANTİEPİLEPTİK"),

    # ============ BATCH 1 — KAN SULANDIRICI / ANEMİ ============
    ("HIBOR", "KAN SULANDIRICI (İĞNE)"),
    ("ARANESP", "ANEMİ TEDAVİSİ (İĞNE)"),
    ("BINOCRIT", "ANEMİ TEDAVİSİ (İĞNE)"),
    ("EPREX", "ANEMİ TEDAVİSİ (İĞNE)"),

    # ============ BATCH 1 — VERTİGO / KARIN AĞRISI / İSHAL ============
    ("BETASERC", "VERTİGO İLACI"),
    ("DEBRIDAT", "KARIN AĞRISI / KASILMA İLACI"),
    ("TRIBUDAT", "KARIN AĞRISI / KASILMA İLACI"),
    ("DICETEL", "KARIN AĞRISI / KASILMA İLACI"),

    # ============ BATCH 1 — HORMON / KADIN HASTALIKLARI ============
    ("PROGESTAN", "HORMON"),
    ("CRINONE", "HORMON"),  # zaten var ama
    ("MICTONORM", "AŞIRI AKTİF MESANE İLACI"),

    # ============ BATCH 1 — DEHB / EREKSİYON / ÜROLOJİ ============
    ("ATOMINEX", "DEHB İLACI"), ("ATTEX", "DEHB İLACI"),
    ("MEDIKINET", "DEHB İLACI"), ("CONCERTA", "DEHB İLACI"),
    ("METILFENIDAT", "DEHB İLACI"), ("ATOMOKSETIN", "DEHB İLACI"),
    ("CIALIS", "EREKSİYON İLACI"), ("SILDEGRA", "EREKSİYON İLACI"),
    ("TADALAFIL", "EREKSİYON İLACI"), ("SILDENAFIL", "EREKSİYON İLACI"),
    ("LIFTA", "EREKSİYON İLACI"),
    ("PRILIGY", "ERKEN BOŞALMA İLACI"),
    ("DAPOKSETIN", "ERKEN BOŞALMA İLACI"),

    # ============ BATCH 1 — CİLT / MANTAR ============
    ("ZALAIN", "MANTAR İLACI"), ("DERMIFIN", "MANTAR İLACI"),
    ("FUNIT", "MANTAR İLACI"), ("FLUZOLE", "MANTAR İLACI"),
    ("ITRAKONAZOL", "MANTAR İLACI"), ("TERBINAFIN", "MANTAR İLACI"),
    ("SERTAKONAZOL", "MANTAR İLACI"),
    ("DERMOVATE", "CİLT İLACI (KORTİZON)"),
    ("LOCODERM", "CİLT İLACI (KORTİZON)"),

    # ============ BATCH 1 — ÖKSÜRÜK / MUKOLİTİK ============
    ("ASIST", "ÖKSÜRÜK KESİCİ"),
    ("NAC", "ÖKSÜRÜK KESİCİ"),
    ("ASETILSISTEIN", "ÖKSÜRÜK KESİCİ"),
    ("MUKOTIK", "ÖKSÜRÜK KESİCİ"),
    ("NOTUSS", "ÖKSÜRÜK KESİCİ"),
    ("LEVOPRONT", "ÖKSÜRÜK KESİCİ"),
    ("COLDAWAY", "GRİP / SOĞUK ALGINLIĞINDA"),

    # ============ BATCH 1 — ROMATİZMA / İMMÜNOSUPRESİF ============
    ("METOART", "ROMATİZMA / İLTİHAP İLACI"),
    ("METOTREKSAT", "ROMATİZMA / İLTİHAP İLACI"),
    ("SANDIMMUN", "İMMÜNOSUPRESİF İLAÇ"),
    ("PROGRAF", "İMMÜNOSUPRESİF İLAÇ"),
    ("SIKLOSPORIN", "İMMÜNOSUPRESİF İLAÇ"),
    ("TAKROLIMUS", "İMMÜNOSUPRESİF İLAÇ"),
    ("ASACOL", "BAĞIRSAK İLTİHABI İLACI"),
    ("MESALAZIN", "BAĞIRSAK İLTİHABI İLACI"),

    # ============ BATCH 1 — KOLESTEROL / NÖROLOJİ ============
    ("ALVASTIN", "KOLESTEROL İLACI"),
    ("LIPANTHYL", "KOLESTEROL İLACI"),
    ("NOOTROPIL", "NÖROLOJİ İLACI"),   # piracetam
    ("PIRACETAM", "NÖROLOJİ İLACI"),

    # ============ BATCH 1 — KANSER İLACI ============
    ("TEMODAL", "KANSER İLACI"),
    ("TAMOXIFEN", "KANSER İLACI"),
    ("LUCRIN", "KANSER İLACI"),  # leuprolid

    # ============ BATCH 1 — KISIRLIK ============
    ("GONAL-F", "KISIRLIK TEDAVİSİ"),
    ("FOLITROPIN", "KISIRLIK TEDAVİSİ"),
    ("MENOPUR", "KISIRLIK TEDAVİSİ"),
    ("PUREGON", "KISIRLIK TEDAVİSİ"),

    # ============ BATCH 1 — BAĞIŞIKLIK / DİYALİZ ============
    ("CUVITRU", "BAĞIŞIKLIK SİSTEMİ İLACI"),
    ("IMMUNOGLOBULIN", "BAĞIŞIKLIK SİSTEMİ İLACI"),
    ("PHYSIONEAL", "PERİTON DİYALİZ SOLÜSYONU"),
    ("CAPD", "PERİTON DİYALİZ SOLÜSYONU"),

    # ============ BATCH 1 — CİLT BAKIM / DİĞER ============
    ("UREDERM", "CİLT İLACI (DIŞ KULLANIM)"),
    ("KENACORT-A", "CİLT İLACI (KORTİZON)"),
]


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

    # En kapsamlı tarama: etken madde / marka sözlüğünde eşleşme ara.
    # Sıralama önemli: önce daha uzun/spesifik anahtarları kontrol et
    for key, kategori in sorted(ETKEN_MADDE_KATEGORI, key=lambda kv: -len(kv[0])):
        if key in name:
            return kategori

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
