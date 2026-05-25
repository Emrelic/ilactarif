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
    # ---- batch 1 yeni kategoriler ----
    "AĞRI KESİCİ (KUVVETLİ)":        7,
    "DEHB İLACI":                   30,
    "EREKSİYON İLACI":               1,
    "ERKEN BOŞALMA İLACI":           1,
    "ANEMİ TEDAVİSİ (İĞNE)":        14,
    "AŞIRI AKTİF MESANE İLACI":     30,
    "ROMATİZMA / İLTİHAP İLACI":    30,
    "İMMÜNOSUPRESİF İLAÇ":          30,
    "BAĞIRSAK İLTİHABI İLACI":      30,
    "VERTİGO İLACI":                14,
    "KANSER İLACI":                 28,
    "KISIRLIK TEDAVİSİ":             7,
    "BAĞIŞIKLIK SİSTEMİ İLACI":     28,
    "PERİTON DİYALİZ SOLÜSYONU":    30,
    "NÖROLOJİ İLACI":               30,
    "ANTİPSİKOTİK":                 28,
    "ANKSİYOLİTİK":                 14,
    "ANTİEPİLEPTİK":                28,
    "ANTİEPİLEPTİK / SİNİR AĞRISI": 28,
    "MANTAR İLACI":                  7,
    "PROBİYOTİK":                    7,
    "İSHAL KESİCİ":                  3,
    "PROSTAT İLACI":                30,
    "OSTEOPOROZ İLACI":             28,
    "KAS GEVŞETİCİ":                 5,
    "ÜRİK ASİT İLACI":              30,
    "PARKİNSON İLACI":              30,
    "ALZHEİMER İLACI":              30,
    "ANTİVİRAL":                     7,
    "CİLT İLACI (ANTİBİYOTİK)":      7,
    "CİLT İLACI (KORTİZON)":         7,
    "CİLT İLACI (EGZEMA)":          14,
    "SEDEF HASTALIĞI İLACI":        28,
    "DOĞUM KONTROL":                28,
    "HORMON":                       28,
    "KALSİYUM DESTEĞİ":             30,
    "MAGNEZYUM DESTEĞİ":            30,
    "ÇİNKO DESTEĞİ":                30,
    "FOLİK ASİT DESTEĞİ":           30,
    "VİTAMİN DESTEĞİ":              30,
    "GÖZ KAPAĞI BAKIMI":            14,
    "BURUN BAKIMI":                  7,
    "BURUN BAKIMI (TUZ)":            7,
    "BURUN İLACI (KORTİZON)":       30,
    "ASTIM İLACI":                  30,
    "ASTIM İLACI (KORTİZON)":       30,
    "MİDE İLACI (REFLÜ)":           14,
    "ZAYIFLAMA İLACI":              28,
    "GÖZ İLACI":                     7,
    # ---- batch 2/3 yeni kategoriler ----
    "ANTİBİYOTİK (İDRAR YOLU)":      3,
    "KALP RİTM İLACI":              30,
    "KANAMA DURDURUCU":              3,
    "RADYOLOJİK KONTRAST MADDESİ":   1,
    "AŞI":                           1,
    "BÜYÜME HORMONU":               30,
    "TANSİYON İLACI / PROSTAT İLACI": 30,
    "SİVİLCE İLACI":                60,
    "CİLT İLACI (YANIK)":           14,
    "CİLT İLACI (LEKE)":            30,
    "SAÇ DÖKÜLMESİ İLACI":          90,
    "HEMOROİD İLACI":                7,
    "TOPLARDAMAR / VARİS İLACI":    30,
    "VARİS İLACI":                  30,
    "KARACİĞER İLACI":              30,
    "SİNDİRİM ENZİMİ":              30,
    "DOLAŞIM / HAFIZA DESTEĞİ":     30,
    "SİGARA BIRAKMA":               30,
    "MS İLACI":                     30,
    "MİGREN İLACI":                  1,
    "BİYOLOJİK İLAÇ":               28,
    "LOKAL ANESTEZİK":               1,
    "SOMATOSTATİN İLACI":           30,
    "VEREM İLACI":                 180,
    # ---- batch 4 yeni kategoriler ----
    "BİT / UYUZ İLACI":              1,
    "KARIN GAZI İLACI":              7,
    "E VİTAMİNİ DESTEĞİ":           30,
    "ACİL İLACI":                    1,
    # ---- batch 5 ----
    "BÖBREK HASTALIĞI İLACI":       30,
    "KOLON TEMİZLEYİCİ":             1,
    "AKCİĞER İLACI (YENİDOĞAN)":     1,
    "KALP YETMEZLİĞİ İLACI":        30,
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
    # ---- batch 1 yeni kategoriler ----
    "AĞRI KESİCİ (KUVVETLİ)":
        "Bu ilaç güçlü bir ağrı kesicidir. Doktorunuzun belirlediği dozu aşmayınız. Araç kullanmayınız.",
    "DEHB İLACI":
        "Her gün aynı saatte alınız. Doktorunuza danışmadan ilacı bırakmayınız.",
    "EREKSİYON İLACI":
        "Cinsel ilişkiden 30-60 dakika önce alınız. 24 saat içinde 1 doz aşmayınız.",
    "ERKEN BOŞALMA İLACI":
        "Cinsel ilişkiden 1-3 saat önce alınız. Günde 1'den fazla alınmaz.",
    "ANEMİ TEDAVİSİ (İĞNE)":
        "Sağlık ocağı / hastane ortamında uygulanacaktır. Saklama koşullarına dikkat ediniz.",
    "AŞIRI AKTİF MESANE İLACI":
        "Ağız kuruluğu yapabilir. Bol su tüketmeye dikkat ediniz.",
    "ROMATİZMA / İLTİHAP İLACI":
        "Doktorunuzun belirlediği dozda kullanınız. Kan tahlilleri ile takip ediliyor olmalısınız.",
    "İMMÜNOSUPRESİF İLAÇ":
        "Bu ilaç bağışıklığı baskılar. Enfeksiyon belirtilerinde doktorunuza başvurunuz.",
    "BAĞIRSAK İLTİHABI İLACI":
        "Her gün aynı saatlerde, doktorunuzun belirlediği dozda kullanınız.",
    "VERTİGO İLACI":
        "Baş dönmesi ve dengesizlik geçince ilacı bırakabilirsiniz.",
    "KANSER İLACI":
        "Onkoloji takibinizde belirlenen şemaya göre kullanınız. Bulantı yaparsa doktorunuza bildiriniz.",
    "KISIRLIK TEDAVİSİ":
        "Tedavi şeması doktorunuz tarafından belirlenir. Buzdolabında saklayınız.",
    "BAĞIŞIKLIK SİSTEMİ İLACI":
        "Sağlık ocağı / hastane ortamında uygulanacaktır.",
    "PERİTON DİYALİZ SOLÜSYONU":
        "Diyaliz hemşirenizin verdiği talimatlara göre kullanınız. Steril şartlara dikkat ediniz.",
    "NÖROLOJİ İLACI":
        "Her gün aynı saatlerde, düzenli kullanınız. Doktor önerisi olmadan bırakmayınız.",
    "ANTİPSİKOTİK":
        "Doktor önerisi olmadan ilacı bırakmayınız. Alkol ile birlikte kullanmayınız.",
    "ANKSİYOLİTİK":
        "Bu ilaç uyku ve sersemlik yapabilir, araç kullanmayınız. Bağımlılık yapabilir, doktor önerisi olmadan uzun süre kullanmayınız.",
    "ANTİEPİLEPTİK":
        "Doktor önerisi olmadan kesinlikle bırakmayınız, nöbete sebep olabilir. Her gün aynı saatlerde alınız.",
    "ANTİEPİLEPTİK / SİNİR AĞRISI":
        "Doktor önerisi olmadan kesinlikle bırakmayınız. Uyku hali yapabilir, araç kullanmayınız.",
    "MANTAR İLACI":
        "Şikayet geçtikten sonra 1-2 hafta daha kullanmaya devam ediniz.",
    "PROBİYOTİK":
        "Antibiyotik ile birlikte alınıyorsa 2 saat arayla kullanınız.",
    "İSHAL KESİCİ":
        "Bol sıvı tüketiniz. 2 günden uzun süren ishalde doktora başvurunuz.",
    "PROSTAT İLACI":
        "Her gün aynı saatte düzenli kullanınız. Ayağa kalkarken baş dönmesi olabilir.",
    "OSTEOPOROZ İLACI":
        "Aç karnına, bol su ile alınız. 30 dakika yatmayınız, dik durunuz.",
    "KAS GEVŞETİCİ":
        "Uyku hali yapabilir, araç kullanmayınız. Tedavi 5-7 günden uzun sürmemelidir.",
    "ÜRİK ASİT İLACI":
        "Bol su tüketiniz. Her gün aynı saatte düzenli kullanınız.",
    "PARKİNSON İLACI":
        "Her gün aynı saatlerde düzenli kullanınız. Doktor önerisi olmadan bırakmayınız.",
    "ALZHEİMER İLACI":
        "Her gün aynı saatte düzenli kullanınız. Bulantı yapabilir, yemek ile alınız.",
    "ANTİVİRAL":
        "Şikayet başladıktan sonra en kısa sürede kullanmaya başlayınız. Bol sıvı tüketiniz.",
    "CİLT İLACI (ANTİBİYOTİK)":
        "Sadece dış kullanım içindir. Etkilenen bölgeye ince bir tabaka halinde sürünüz.",
    "CİLT İLACI (KORTİZON)":
        "Sadece dış kullanım içindir. Yüz bölgesine uzun süreli kullanmayınız. Bol miktarda sürmeyiniz.",
    "CİLT İLACI (EGZEMA)":
        "Sadece dış kullanım içindir. Güneşten korununuz. Kullanım sonrası ellerinizi yıkayınız.",
    "SEDEF HASTALIĞI İLACI":
        "Sadece dış kullanım içindir. Yüz ve genital bölgeye sürmeyiniz.",
    "DOĞUM KONTROL":
        "Her gün aynı saatte düzenli alınız. Unutulan dozda doktora / eczacıya başvurunuz.",
    "HORMON":
        "Doktor önerisi olmadan kesinlikle dozu değiştirmeyiniz, bırakmayınız.",
    "KALSİYUM DESTEĞİ":
        "Bol su ile alınız. Demir / tiroid ilaçlarınızdan 2 saat ayrı alınız.",
    "MAGNEZYUM DESTEĞİ":
        "Aç karnına alındığında ishal yapabilir, yemekle alınız.",
    "ÇİNKO DESTEĞİ":
        "Aç karnına alındığında bulantı yapabilir, yemekle alınız.",
    "FOLİK ASİT DESTEĞİ":
        "Her gün aynı saatte düzenli alınız.",
    "VİTAMİN DESTEĞİ":
        "Her gün aynı saatte düzenli alınız.",
    "GÖZ KAPAĞI BAKIMI":
        "Sadece dış kullanım içindir. Göze değdirmeyiniz.",
    "BURUN BAKIMI":
        "Birden fazla kişi tarafından kullanılmamalıdır.",
    "BURUN BAKIMI (TUZ)":
        "Her yaşta güvenle kullanılabilir. Birden fazla kişi tarafından kullanılmamalıdır.",
    "BURUN İLACI (KORTİZON)":
        "Düzenli kullanıldığında 1-2 hafta içinde tam etki başlar. Birden fazla kişi tarafından kullanılmamalıdır.",
    "ASTIM İLACI":
        "Her gün aynı saatlerde düzenli kullanınız. Atak sırasında değil, korunma amaçlıdır.",
    "ASTIM İLACI (KORTİZON)":
        "Kullandıktan sonra ağzınızı su ile çalkalayınız. Düzenli kullanılır, atakta değildir.",
    "ZAYIFLAMA İLACI":
        "Diyet ve egzersiz ile birlikte etki gösterir. Yağlı yemeklerden kaçınınız.",
    "GÖZ İLACI":
        "Şişe ucunu göze değdirmeyiniz. Birden fazla kişi tarafından kullanılmamalıdır.",
    # ---- batch 2/3 yeni kategoriler ----
    "ANTİBİYOTİK (İDRAR YOLU)":
        "Bol su tüketiniz. Tek doz olarak yatmadan önce, idrarınızı tam boşalttıktan sonra alınız.",
    "KALP RİTM İLACI":
        "Her gün aynı saatlerde düzenli alınız. Doktor önerisi olmadan bırakmayınız.",
    "KANAMA DURDURUCU":
        "Doktorun belirlediği süre boyunca kullanınız. Aşırı pıhtılaşma riskinde belirti olursa doktora başvurunuz.",
    "RADYOLOJİK KONTRAST MADDESİ":
        "Sağlık ocağı / hastane ortamında uygulanır. İşlem öncesi açlık gerekebilir.",
    "AŞI":
        "Sağlık personeli tarafından uygulanır. Saklama zincirini bozmayınız.",
    "BÜYÜME HORMONU":
        "Buzdolabında saklayınız (2-8°C). Her gün aynı saatte, akşam uygulayınız.",
    "TANSİYON İLACI / PROSTAT İLACI":
        "İlk doz baş dönmesi yapabilir, ayağa kalkarken yavaş hareket ediniz. Her gün aynı saatte alınız.",
    "SİVİLCE İLACI":
        "Güneşten korununuz, koruyucu krem kullanınız. Yan etkilerini takip ediniz.",
    "CİLT İLACI (YANIK)":
        "Sadece dış kullanım içindir. Etkilenen yanık bölgesine ince tabaka halinde sürünüz.",
    "CİLT İLACI (LEKE)":
        "Sadece dış kullanım içindir. Güneşten korunmak için yüksek faktörlü güneş kremi kullanınız.",
    "SAÇ DÖKÜLMESİ İLACI":
        "Saç derisi kuru iken sürünüz. 3-6 ay düzenli kullanım sonrası etki başlar.",
    "HEMOROİD İLACI":
        "Tuvaletten sonra, temizlik sonrası uygulayınız. Etkili olması için yeterli sürede kullanılmalıdır.",
    "TOPLARDAMAR / VARİS İLACI":
        "Her gün aynı saatte düzenli alınız. Bol su içiniz, ayaklarınızı yüksekte tutunuz.",
    "VARİS İLACI":
        "Doktorun belirlediği süre boyunca kullanınız. Sklerozan tedavi ise hastanede yapılır.",
    "KARACİĞER İLACI":
        "Her gün aynı saatte düzenli kullanınız. Doktor takibinde olunuz.",
    "SİNDİRİM ENZİMİ":
        "Yemekle birlikte, ana yemeklerle alınız. Ezmeyiniz, çiğnemeyiniz.",
    "DOLAŞIM / HAFIZA DESTEĞİ":
        "Yemekle birlikte alınız. Etkisinin başlaması için en az 4-6 hafta gerekir.",
    "SİGARA BIRAKMA":
        "Sigarayı bırakma sürecinde destek için kullanılır. Aşırı dozdan kaçınınız.",
    "MS İLACI":
        "Saklama koşullarına dikkat ediniz. Sağlık ocağı / hastane ortamında uygulanır.",
    "MİGREN İLACI":
        "Migren atağının başlangıcında erken alınız. 24 saatte 2 dozdan fazla alınmaz.",
    "BİYOLOJİK İLAÇ":
        "Buzdolabında saklayınız (2-8°C). Enfeksiyon belirtilerinde doktora başvurunuz.",
    "LOKAL ANESTEZİK":
        "Sağlık personeli tarafından uygulanır.",
    "SOMATOSTATİN İLACI":
        "Buzdolabında saklayınız. Doktorun belirlediği dozda kullanınız.",
    "VEREM İLACI":
        "Tedaviyi kesinlikle yarıda bırakmayınız. Her gün düzenli, aç karnına alınız.",
    "BİT / UYUZ İLACI":
        "Tüm vücuda boyundan aşağıya uygulanır. 8-12 saat beklendikten sonra yıkanır. Gerekirse 1 hafta sonra tekrarlanır.",
    "KARIN GAZI İLACI":
        "Yemekten sonra ve yatmadan önce alınız. Çiğneme tabletini çiğneyerek alınız.",
    "E VİTAMİNİ DESTEĞİ":
        "Her gün aynı saatte yemekle birlikte alınız.",
    "ACİL İLACI":
        "Acil durumlarda kullanılır. Saklama koşullarına dikkat ediniz, son kullanma tarihini takip ediniz.",
    "BÖBREK HASTALIĞI İLACI":
        "Doktorun belirlediği şekilde kullanınız. Yemeklerle birlikte alınması gerekiyorsa belirtilen şekilde uygulayınız.",
    "KOLON TEMİZLEYİCİ":
        "İşlem öncesi belirtilen saatlerde, bol su ile karıştırarak içiniz. Yakınınızda tuvalet bulundurunuz.",
    "AKCİĞER İLACI (YENİDOĞAN)":
        "Hastane ortamında bebek doktoru tarafından uygulanır.",
    "KALP YETMEZLİĞİ İLACI":
        "Her gün aynı saatlerde düzenli alınız. Tuz alımına dikkat ediniz, ağırlığınızı takip ediniz.",
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
    # ---- batch 1 yeni kategoriler ----
    "AĞRI KESİCİ (KUVVETLİ)": {"gunluk_kez": 1},  # genelde uzun etkili
    "DEHB İLACI":           {"gunluk_kez": 1, "kullanim_zamani": ["sabah"], "yemek": "yemekten sonra"},
    "EREKSİYON İLACI":      {"gunluk_kez": 1},
    "ERKEN BOŞALMA İLACI":  {"gunluk_kez": 1},
    "ANEMİ TEDAVİSİ (İĞNE)":{"gunluk_kez": 1},
    "AŞIRI AKTİF MESANE İLACI": {"gunluk_kez": 1, "yemek": "fark etmez"},
    "ROMATİZMA / İLTİHAP İLACI": {"gunluk_kez": 1, "yemek": "yemekle"},
    "İMMÜNOSUPRESİF İLAÇ":  {"gunluk_kez": 2, "saat_arasi": 12, "yemek": "yemekten önce"},
    "BAĞIRSAK İLTİHABI İLACI": {"gunluk_kez": 3, "yemek": "tok"},
    "VERTİGO İLACI":        {"gunluk_kez": 3, "yemek": "tok"},
    "ANTİPSİKOTİK":         {"gunluk_kez": 1, "kullanim_zamani": ["gece"], "yemek": "fark etmez"},
    "ANKSİYOLİTİK":         {"gunluk_kez": 1, "yemek": "fark etmez"},
    "ANTİEPİLEPTİK":        {"gunluk_kez": 2, "saat_arasi": 12, "yemek": "fark etmez"},
    "ANTİEPİLEPTİK / SİNİR AĞRISI": {"gunluk_kez": 2, "saat_arasi": 12, "yemek": "fark etmez"},
    "MANTAR İLACI":         {"gunluk_kez": 1, "yemek": "yemekle"},
    "PROBİYOTİK":           {"gunluk_kez": 1, "yemek": "yemekten önce"},
    "İSHAL KESİCİ":         {"gunluk_kez": 3, "yemek": "fark etmez"},
    "PROSTAT İLACI":        {"gunluk_kez": 1, "kullanim_zamani": ["gece"], "yemek": "yemekten sonra"},
    "OSTEOPOROZ İLACI":     {"gunluk_kez": 1, "kullanim_zamani": ["sabah"], "yemek": "aç"},
    "KAS GEVŞETİCİ":        {"gunluk_kez": 2, "saat_arasi": 12, "yemek": "tok"},
    "ÜRİK ASİT İLACI":      {"gunluk_kez": 1, "yemek": "yemekten sonra"},
    "PARKİNSON İLACI":      {"gunluk_kez": 3, "yemek": "yemekten önce"},
    "ALZHEİMER İLACI":      {"gunluk_kez": 1, "yemek": "yemekle"},
    "ANTİVİRAL":            {"gunluk_kez": 5, "yemek": "fark etmez"},
    "CİLT İLACI (ANTİBİYOTİK)": {"gunluk_kez": 3},
    "CİLT İLACI (KORTİZON)":    {"gunluk_kez": 2},
    "CİLT İLACI (EGZEMA)":      {"gunluk_kez": 2},
    "SEDEF HASTALIĞI İLACI":    {"gunluk_kez": 1},
    "DOĞUM KONTROL":        {"gunluk_kez": 1, "kullanim_zamani": ["akşam"]},
    "HORMON":               {"gunluk_kez": 1, "yemek": "fark etmez"},
    "KALSİYUM DESTEĞİ":     {"gunluk_kez": 1, "yemek": "yemekle"},
    "MAGNEZYUM DESTEĞİ":    {"gunluk_kez": 1, "yemek": "yemekle"},
    "ÇİNKO DESTEĞİ":        {"gunluk_kez": 1, "yemek": "yemekle"},
    "FOLİK ASİT DESTEĞİ":   {"gunluk_kez": 1, "yemek": "fark etmez"},
    "VİTAMİN DESTEĞİ":      {"gunluk_kez": 1, "yemek": "yemekten sonra"},
    "GÖZ KAPAĞI BAKIMI":    {"gunluk_kez": 2},
    "BURUN BAKIMI":         {"gunluk_kez": 3},
    "BURUN BAKIMI (TUZ)":   {"gunluk_kez": 4},
    "BURUN İLACI (KORTİZON)":   {"gunluk_kez": 1, "kullanim_zamani": ["sabah"]},
    "ASTIM İLACI":          {"gunluk_kez": 2, "saat_arasi": 12},
    "ASTIM İLACI (KORTİZON)":   {"gunluk_kez": 2, "saat_arasi": 12},
    "MİDE İLACI (REFLÜ)":   {"gunluk_kez": 4, "yemek": "yemekten sonra"},
    "ZAYIFLAMA İLACI":      {"gunluk_kez": 3, "yemek": "yemekle"},
    "GÖZ İLACI":            {"gunluk_kez": 3},
    "KANSER İLACI":         {"gunluk_kez": 1, "yemek": "tok"},
    "PERİTON DİYALİZ SOLÜSYONU": {"gunluk_kez": 4},
    "NÖROLOJİ İLACI":       {"gunluk_kez": 3, "yemek": "yemekle"},
    "KISIRLIK TEDAVİSİ":    {"gunluk_kez": 1},
    "BAĞIŞIKLIK SİSTEMİ İLACI": {"gunluk_kez": 1},
    # ---- batch 2/3 ----
    "ANTİBİYOTİK (İDRAR YOLU)": {"gunluk_kez": 1, "kullanim_zamani": ["gece"], "yemek": "aç"},
    "KALP RİTM İLACI":      {"gunluk_kez": 1, "yemek": "tok"},
    "KANAMA DURDURUCU":     {"gunluk_kez": 3, "yemek": "fark etmez"},
    "RADYOLOJİK KONTRAST MADDESİ": {"gunluk_kez": 1},
    "AŞI":                  {"gunluk_kez": 1},
    "BÜYÜME HORMONU":       {"gunluk_kez": 1, "kullanim_zamani": ["akşam"]},
    "TANSİYON İLACI / PROSTAT İLACI": {"gunluk_kez": 1, "kullanim_zamani": ["gece"]},
    "SİVİLCE İLACI":        {"gunluk_kez": 1, "kullanim_zamani": ["akşam"]},
    "CİLT İLACI (YANIK)":   {"gunluk_kez": 2},
    "CİLT İLACI (LEKE)":    {"gunluk_kez": 2},
    "SAÇ DÖKÜLMESİ İLACI":  {"gunluk_kez": 2},
    "HEMOROİD İLACI":       {"gunluk_kez": 3},
    "TOPLARDAMAR / VARİS İLACI": {"gunluk_kez": 2, "yemek": "tok"},
    "VARİS İLACI":          {"gunluk_kez": 1},
    "KARACİĞER İLACI":      {"gunluk_kez": 2, "yemek": "tok"},
    "SİNDİRİM ENZİMİ":      {"gunluk_kez": 3, "yemek": "yemekle"},
    "DOLAŞIM / HAFIZA DESTEĞİ": {"gunluk_kez": 2, "yemek": "tok"},
    "SİGARA BIRAKMA":       {"gunluk_kez": 1},
    "MS İLACI":             {"gunluk_kez": 1},
    "MİGREN İLACI":         {"gunluk_kez": 1},
    "BİYOLOJİK İLAÇ":       {"gunluk_kez": 1},
    "LOKAL ANESTEZİK":      {"gunluk_kez": 1},
    "SOMATOSTATİN İLACI":   {"gunluk_kez": 1},
    "VEREM İLACI":          {"gunluk_kez": 1, "kullanim_zamani": ["sabah"], "yemek": "aç"},
    "BİT / UYUZ İLACI":     {"gunluk_kez": 1},
    "KARIN GAZI İLACI":     {"gunluk_kez": 3, "yemek": "yemekten sonra"},
    "E VİTAMİNİ DESTEĞİ":   {"gunluk_kez": 1, "yemek": "yemekle"},
    "ACİL İLACI":           {"gunluk_kez": 1},
    "BÖBREK HASTALIĞI İLACI": {"gunluk_kez": 3, "yemek": "yemekle"},
    "KOLON TEMİZLEYİCİ":    {"gunluk_kez": 1},
    "AKCİĞER İLACI (YENİDOĞAN)": {"gunluk_kez": 1},
    "KALP YETMEZLİĞİ İLACI": {"gunluk_kez": 2, "saat_arasi": 12},
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
