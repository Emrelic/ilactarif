"""İlaç etiketi içerik şemaları.

Her ilaç için 3 etiket tipi tanımlıdır. İçerik SQLite'ta JSON olarak tutulur;
bu modül o JSON'ın hangi alanları içerdiğini ve doğrulama yardımcılarını barındırır.

Tasarım ilkeleri:
  - Alanlar opsiyoneldir; AI veya eczacı hangisini doldurursa doldursun esnek olmalı.
  - Görüntüleme tarafı (etiket render) eksik alanları atlar.
  - Pilot 100 ilaç sonrası şema gerekirse genişletilecek (örn. ek pediatri/gebelik alanları).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Tip 1 — Kullanım/dozaj etiketi (her ilaç için doldurulur)
# ---------------------------------------------------------------------------
@dataclass
class UsageLabel:
    """Etiket 1: Hasta nasıl kullanacak?

    Örnek doldurulmuş hali:
        ilac_turu        = "Antibiyotik"
        doz              = "1 tablet"
        gunluk_kez       = 2
        kullanim_zamani  = ["sabah", "akşam"]
        yemek            = "tok"
        sure             = "7 gün"
        ek_not           = ""
    """
    # Yeni (referans format için ana alanlar)
    kategori: str = ""             # Etikete basılan büyük başlık. Örn:
                                    # "ANTİBİYOTİK", "AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
                                    # "TANSİYON İLACI", "DİYABET / KALP YETMEZ. / BÖBREK HAS.",
                                    # "KORTİZON TEDAVİSİ", "KURU GÖZ RAHATSIZLIĞINDA",
                                    # "BOĞAZ SPREYİ", "GRİP / SOĞUK ALGINLIĞINDA"
    kullanim_talimati: str = ""    # Etiketin orta bölümündeki asıl büyük cümle. Örn:
                                    # "SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE TOK KARNINA"
                                    # " BİR BARDAK SUYLA YUTULUR."
    uyari_metni: str = ""          # "UYARI :" satırında basılan küçük yazı uyarı.
                                    # Örn: "İlacınızı bitene kadar her gün düzenli kullanınız."

    # Eski yapılandırılmış alanlar — kullanim_talimati boşsa bunlardan otomatik
    # cümle üretmeye yarar. AI doldururken bu alanları da doldurabilir.
    ilac_turu: str = ""            # "Antibiyotik", "Mide ilacı", "Ağrı kesici" vb. (kategori ile aynı işlevsellik)
    doz: str = ""                  # "1 tablet", "5 ml", "1 ölçek" gibi serbest metin
    gunluk_kez: Optional[int] = None       # 1-6
    saat_arasi: Optional[int] = None       # "8 saatte bir" → 8
    kullanim_zamani: List[str] = field(default_factory=list)
                                            # ["sabah", "öğle", "akşam", "gece yatmadan önce"]
    yemek: str = ""                # "aç" | "tok" | "yemekten önce" | "yemekten sonra"
    sure: str = ""                 # "5 gün", "10 gün", "doktor önerdiği sürece"
    sure_gun: Optional[int] = None # Bitiş tarihi hesabı için: reçete tarihi + sure_gun gün
    ek_not: str = ""               # serbest metin
    kullanim_sekli: str = ""       # Medula'dan: "Göz üzerine", "Ağızdan", "Cilt üzerine"


# ---------------------------------------------------------------------------
# Tip 2 — Hazırlama etiketi (sadece şurup, süspansiyon, damla vb. için)
# ---------------------------------------------------------------------------
@dataclass
class PreparationLabel:
    """Etiket 2: Hasta veya eczacı ilacı nasıl hazırlayacak?"""
    gerekli: bool = False          # Çoğu tablette False olur, basılmaz
    form: str = ""                 # "süspansiyon", "şurup", "damla", "toz"
    adimlar: List[str] = field(default_factory=list)
                                    # ["Şişe iyice çalkalanır",
                                    #  "İşaretli çizgiye kadar kaynamış-soğutulmuş su ilave edilir",
                                    #  "Tekrar çalkalanır"]
    saklama: str = ""              # "Buzdolabı 2-8°C", "Oda sıcaklığı, kuru yerde"
    acildiktan_sonra_gecerlilik: str = ""   # "7 gün", "14 gün"
    her_kullanim_oncesi: str = ""  # "Her kullanımdan önce çalkalayınız" vb.


# ---------------------------------------------------------------------------
# Tip 3 — Uyarı etiketi (önemli kullanım uyarıları)
# ---------------------------------------------------------------------------
@dataclass
class WarningLabel:
    """Etiket 3: Hastanın bilmesi gereken kritik uyarılar."""
    gerekli: bool = False          # Önemli uyarısı olmayan ilaçlarda False
    uyarilar: List[str] = field(default_factory=list)
                                    # 1-4 madde, her biri kısa cümle. Örn:
                                    # ["Antibiyotiği bitirmeden bırakmayın",
                                    #  "Alkol ile kullanmayın",
                                    #  "Araç-makine kullanmayın"]


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def to_dict(obj) -> dict:
    """dataclass → dict, JSON'a hazır."""
    return asdict(obj)


LABEL_TYPE_USAGE       = 1
LABEL_TYPE_PREPARATION = 2
LABEL_TYPE_WARNING     = 3

LABEL_TYPE_NAMES = {
    LABEL_TYPE_USAGE:       "Kullanım",
    LABEL_TYPE_PREPARATION: "Hazırlama",
    LABEL_TYPE_WARNING:     "Uyarı",
}
