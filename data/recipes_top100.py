"""En çok satan 100 ilacın tarif verisi.

Her entry: barkod, kategori, talimat, uyari, sure_gun.
Kullanılan dil/format referans İkizler Eczanesi etiketlerinden alınmıştır.

NOT: Bu veriler genel kullanım kalıplarını yansıtır. Spesifik hastaya yönelik
doktor dozu Medula'dan geldiği için Medula'dan gelen doz/sıklık öncelikli olmalı.
'talimat' alanı DB varsayılanıdır; Medula'da farklı doz yazıyorsa render
tarafında onun üzerine yazılır (gelecek iyileştirme).
"""

# yemek değerleri: "aç" | "tok" | "fark etmez" | "yemekten önce" | "yemekten sonra" | "yemekle"
RECIPES = [
    # === 1-3 NSAID / Parasetamol ağrı kesiciler ===
    {"barcode":"8699832090055","name":"ARVELES 25MG 20 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"8 SAATTE BİR 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Aksi söylenmediyse ağrınız oldukça kullanınız. Midenizde rahatsızlık yoksa veya ani ağrıda AÇ karnına kullanılabilir.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},
    {"barcode":"8699717090293","name":"DEXOFEN 25MG 20 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"8 SAATTE BİR 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Aksi söylenmediyse ağrınız oldukça kullanınız. Midenizde rahatsızlık yoksa ani ağrıda AÇ karnına kullanılabilir.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},
    {"barcode":"8699717010109","name":"PAROL 500MG 20 TABLET",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE AÇ VEYA TOK KARNINA BOL SU İLE YUTULUR.",
     "uyari":"Ağrı ve ateş oldukça kullanınız. Rahatsızlık düzeldiğinde ilacı bırakınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"fark etmez"},

    # === 4-6 Antibiyotik (Amoksisilin/klavulanat) ===
    {"barcode":"8699508090556","name":"CROXILEX-BID 1000MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},
    {"barcode":"8699745869971","name":"KLAVUNAT BID 1000MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},
    {"barcode":"8699525092472","name":"AMOKLAVIN BID 1000MG 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEKLERLE BİRLİKTE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekle"},

    # === 7-8 Naproksen / Tramadol (Diğer ağrı kesiciler) ===
    {"barcode":"8699514091530","name":"APRANAX FORTE 550MG 20 TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız. Aksi söylenmediyse ağrınız oldukça kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},
    {"barcode":"8699633129350","name":"DOLOREX 50MG 20 DRAJE",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE MİDE RAHATSIZLIĞINIZ YOKSA YEMEKTEN ÖNCE (VARSA SONRA) BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bölmeden, ezmeden, ağzınızda çiğnemeden yutunuz.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"yemekten önce"},

    # === 9 Gargara ===
    {"barcode":"8699580640069","name":"KLOROBEN 200ML GARGARA",
     "kategori":"AĞIZ-DİŞ İLACI",
     "talimat":"SABAH-ÖĞLE-AKŞAM YEMEKLERDEN SONRA 10 ML AĞIZ İÇİNDE 30 SANİYE ÇALKALANIP TÜKÜRÜLÜR.",
     "uyari":"Yutmayınız. Kullandıktan sonra ağzınızı suyla çalkalamayınız, en az 30 dakika bir şey yiyip içmeyiniz.",
     "sure_gun":7,"gunluk_kez":3},

    # === 10-12 Antibiyotik devamı ===
    {"barcode":"8699525093189","name":"AMOKLAVIN BID 1000MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEKLERLE BİRLİKTE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekle"},
    {"barcode":"8699716091536","name":"AUGMENTIN-BID 1000MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},
    {"barcode":"8699569090694","name":"KLAMOKS BID 1000MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 13 Çocuk parasetamol süspansiyon ===
    {"barcode":"8699522705160","name":"CALPOL 6 PLUS 250MG/5ML 150ML SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 4-6 SAAT ARA İLE AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Günde 4 dozdan fazla kullanmayınız.",
     "sure_gun":5,"gunluk_kez":4,"saat_arasi":6,"yemek":"fark etmez"},

    # === 14 Flurbiprofen ===
    {"barcode":"8699536090115","name":"MAJEZIK 100MG 15 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız. Aksi söylenmediyse ağrınız oldukça kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 15 Çocuk parasetamol süspansiyon (küçük yaş) ===
    {"barcode":"8699522705009","name":"CALPOL 120MG/5ML 150ML SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 4-6 SAAT ARA İLE AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Günde 4 dozdan fazla kullanmayınız.",
     "sure_gun":5,"gunluk_kez":4,"saat_arasi":6,"yemek":"fark etmez"},

    # === 16 KLAMOKS BID 1000 10'lu ===
    {"barcode":"8699569090328","name":"KLAMOKS BID 1000MG 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız. Tablet büyük gelirse ikiye bölerek, çiğnemeden su ile yutabilirsiniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 17 KLINDAVER ampul ===
    {"barcode":"8699788750584","name":"KLINDAVER 600MG/4ML 4ML 1 AMPUL",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 İĞNE (FLAKON) KAS İÇİNE VEYA SERUM İÇİNE KARIŞTIRILARAK SAĞLIK OCAĞI / HASTANE ORTAMINDA UYGULANIR.",
     "uyari":"İlacınız sağlık ocağı / hastane ortamında uygulanacaktır. İshal yapması durumunda mutlaka doktorunuza bilgi veriniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12},

    # === 18 ANDOREX gargara ===
    {"barcode":"8699746640315","name":"ANDOREX 200ML GARGARA",
     "kategori":"AĞIZ-DİŞ İLACI",
     "talimat":"SABAH-ÖĞLE-AKŞAM YEMEKLERDEN SONRA 10 ML AĞIZ İÇİNDE 30 SANİYE ÇALKALANIP TÜKÜRÜLÜR.",
     "uyari":"Yutmayınız. Kullandıktan sonra ağzınızı suyla çalkalamayınız.",
     "sure_gun":7,"gunluk_kez":3},

    # === 19 CORASPIN (kan sulandırıcı) ===
    {"barcode":"8699546130238","name":"CORASPIN 100MG 30 TABLET",
     "kategori":"KAN SULANDIRICI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, HER GÜN AYNI SAATTE, YEMEKTEN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Her gün aynı saatlerde, düzenli kullanınız. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten sonra"},

    # === 20 DOLVEN PEDİATRİK İBUPROFEN ===
    {"barcode":"8699809575158F","name":"DOLVEN PEDİATRİK 100MG/5ML 100ML ŞURUP",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 6-8 SAAT ARA İLE TOK KARNINA AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Tok karna verilmesi tercih edilir.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},

    # === 21-22 PAROL 30, AUGMENTIN BID 10 ===
    {"barcode":"8699717010093","name":"PAROL 500MG 30 TABLET",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE AÇ VEYA TOK KARNINA BOL SU İLE YUTULUR.",
     "uyari":"Ağrı ve ateş oldukça kullanınız. Rahatsızlık düzeldiğinde ilacı bırakınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"fark etmez"},
    {"barcode":"8699716091529","name":"AUGMENTIN-BID 1000MG 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 23 PAROL PLUS süspansiyon ===
    {"barcode":"8699717700079","name":"PAROL PLUS 250MG/5ML 150ML ORAL SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 4-6 SAAT ARA İLE AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Günde 4 dozdan fazla kullanmayınız.",
     "sure_gun":5,"gunluk_kez":4,"saat_arasi":6,"yemek":"fark etmez"},

    # === 24 CROXILEX 10 ===
    {"barcode":"8699508090488","name":"CROXILEX-BID 1000MG 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 25 TRAVAZOL krem ===
    {"barcode":"8699569350040","name":"TRAVAZOL 15GR KREM",
     "kategori":"MANTAR İLACI (DIŞ KULLANIM)",
     "talimat":"SABAH-AKŞAM TEMİZLENMİŞ KURU CİLDE İNCE BİR TABAKA HALİNDE SÜRÜLÜR.",
     "uyari":"Sadece dış kullanım içindir. Göz ve ağız ile temasından kaçınınız. Şikayet geçtikten sonra 1-2 hafta daha kullanmaya devam ediniz.",
     "sure_gun":14,"gunluk_kez":2},

    # === 26 BI-PROFENID ===
    {"barcode":"8699809018631","name":"BI-PROFENID 100MG UZATILMIŞ SALIMLI 20 ÇENTİKLİ TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Çiğnemeden, kırmadan bütün olarak yutunuz. Mide rahatsızlığı yapabilir.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 27 PAROL süsp ===
    {"barcode":"8699717700062","name":"PAROL 120MG/5ML 150ML ORAL SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 4-6 SAAT ARA İLE AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız.",
     "sure_gun":5,"gunluk_kez":4,"saat_arasi":6},

    # === 28 APRANAX PLUS ===
    {"barcode":"8699514090977","name":"APRANAX PLUS 20 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide koruyucu içerir, fakat tok alınması önerilir. Aksi söylenmediyse ağrınız oldukça kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 29 LANSOR mide ===
    {"barcode":"8699536160085","name":"LANSOR 30MG 28 MİKROPELLET KAPSÜL",
     "kategori":"MİDE İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, KAHVALTIDAN YARIM SAAT ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Aç karnına, kahvaltıdan en az 30 dakika önce alınız. Kapsülü çiğnemeden bütün olarak yutunuz.",
     "sure_gun":28,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 30 OROHEKS gargara ===
    {"barcode":"8699772646824","name":"OROHEKS PLUS GARGARA 200ML",
     "kategori":"AĞIZ-DİŞ İLACI",
     "talimat":"SABAH-ÖĞLE-AKŞAM YEMEKLERDEN SONRA 10 ML AĞIZ İÇİNDE 30 SANİYE ÇALKALANIP TÜKÜRÜLÜR.",
     "uyari":"Yutmayınız. Kullandıktan sonra ağzınızı suyla çalkalamayınız, en az 30 dakika bir şey yiyip içmeyiniz.",
     "sure_gun":7,"gunluk_kez":3},

    # === 31 DEX-FORTE ===
    {"barcode":"8697930094258","name":"DEX-FORTE 50MG 30 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 32 KLAVUNAT BID 1GR ===
    {"barcode":"8699717090064","name":"KLAVUNAT BID 1GR 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEĞİN BAŞLANGICINDA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 33 KLAMOKS BID FORT süsp ===
    {"barcode":"8699569280392","name":"KLAMOKS BID FORT 400MG/57MG 100ML SÜSPANSİYON",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] DOKTORUN ÖNERDİĞİ DOZDA YEMEĞİN BAŞLANGICINDA AĞIZDAN İÇİLİR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullandırınız. Buzdolabında saklayınız, kullanmadan iyice çalkalayınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 34 BELOC ZOK 50 (Metoprolol) ===
    {"barcode":"8699786030367","name":"BELOC ZOK 50MG 20 KONTROLLU SALINIMLI FİLM TABLET",
     "kategori":"TANSİYON İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, HER GÜN AYNI SAATTE, KAHVALTIDAN ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Her gün aynı saatlerde, düzenli içiniz. Tableti çiğnemeden, bütün olarak yutunuz.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 35 ECOPIRIN ===
    {"barcode":"8699514040019","name":"ECOPIRIN 100MG 30 ENTERIK TABLET",
     "kategori":"KAN SULANDIRICI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, HER GÜN AYNI SAATTE, YEMEKTEN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Her gün aynı saatlerde, düzenli kullanınız. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten sonra"},

    # === 36 RASTEL (Allerji) ===
    {"barcode":"8699586094217","name":"RASTEL 25MG 20 ÇENTİKLİ FİLM TABLET",
     "kategori":"ALLERJİ / KAŞINTI İLACI",
     "talimat":"GECE YATMADAN ÖNCE 1 TANE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Bu ilaç uyku hali yapabilir, kullanırken araç kullanmayınız.",
     "sure_gun":7,"gunluk_kez":1,"kullanim_zamani":["gece"]},

    # === 37 AMOKLAVIN BID FORTE süsp ===
    {"barcode":"8699525283214","name":"AMOKLAVIN BID FORTE 400/57MG 100ML SÜSPANSİYON",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] DOKTORUN ÖNERDİĞİ DOZDA YEMEKLERLE BİRLİKTE AĞIZDAN İÇİLİR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullandırınız. Buzdolabında saklayınız, kullanmadan iyice çalkalayınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekle"},

    # === 38 NEXIUM mide ===
    {"barcode":"8699786040045","name":"NEXIUM 40MG ENTERIK KAPLI 28 PELLET TABLET",
     "kategori":"MİDE İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, KAHVALTIDAN YARIM SAAT ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Aç karnına, kahvaltıdan en az 30 dakika önce alınız. Tableti çiğnemeden, bütün olarak yutunuz.",
     "sure_gun":28,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 39 APRALJIN FORTE ===
    {"barcode":"8699525092205","name":"APRALJIN FORTE 550MG 20 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 40 IBURAMIN ZERO süsp ===
    {"barcode":"8699591700240","name":"IBURAMIN ZERO 100ML SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 4-6 SAAT ARA İLE TOK KARNINA AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},

    # === 41 FLAGYL (Metronidazol) ===
    {"barcode":"8699809098572","name":"FLAGYL 500MG 20 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEKLERDEN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Bu ilacı kullanırken, kesinlikle ALKOL tüketmeyiniz! Antidepresan vb ilaç kullanıyorsanız mutlaka doktorunuza bilgi veriniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekten sonra"},

    # === 42 CROXILEX FORT süsp ===
    {"barcode":"8699508280162","name":"CROXILEX-BID FORT 400MG/57MG 100ML SÜSPANSİYON",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] DOKTORUN ÖNERDİĞİ DOZDA YEMEĞİN BAŞLANGICINDA AĞIZDAN İÇİLİR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullandırınız. Buzdolabında saklayınız, kullanmadan iyice çalkalayınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 43 PANTO mide ===
    {"barcode":"8699516042257","name":"PANTO 40MG 28 ENTERIK KAPLI TABLET",
     "kategori":"MİDE İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, KAHVALTIDAN YARIM SAAT ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Aç karnına, kahvaltıdan en az 30 dakika önce alınız. Tableti çiğnemeden, bütün olarak yutunuz.",
     "sure_gun":28,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 44 A-FERIN FORTE grip ===
    {"barcode":"8699570090058","name":"A-FERIN FORTE 30 FİLM TABLET",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE AÇ VEYA TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Bu ilaç hafif uyku sersemlik haline sebep olabilir, dikkat ediniz.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"fark etmez"},

    # === 45 MINOSET parasetamol ===
    {"barcode":"8699546015597","name":"MINOSET 500MG 20 TABLET",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE AÇ VEYA TOK KARNINA BOL SU İLE YUTULUR.",
     "uyari":"Ağrı ve ateş oldukça kullanınız. Rahatsızlık düzeldiğinde ilacı bırakınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"fark etmez"},

    # === 46 ILIADIN burun spreyi ===
    {"barcode":"8699563544902","name":"ILIADIN %0.05 10ML SPREY",
     "kategori":"BURUN AÇICI",
     "talimat":"SABAH-AKŞAM HER BURUN DELİĞİNE 1 SIKIM (PUF) UYGULANIR.",
     "uyari":"7 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
     "sure_gun":5,"gunluk_kez":2},

    # === 47 NUROFEN COLD+FLU ===
    {"barcode":"8699704016213","name":"NUROFEN COLD+FLU 24 TABLET",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"tok"},

    # === 48 PEDIFEN şurup ===
    {"barcode":"8699717570016","name":"PEDIFEN 100MG/5ML 100ML PEDIATRIK ŞURUP",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 6-8 SAAT ARA İLE TOK KARNINA AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},

    # === 49 KLINDAN ampul ===
    {"barcode":"8699569750024","name":"KLINDAN 600MG/4ML 4ML 1 AMPUL",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 İĞNE (FLAKON) KAS İÇİNE VEYA SERUM İÇİNE KARIŞTIRILARAK SAĞLIK OCAĞI / HASTANE ORTAMINDA UYGULANIR.",
     "uyari":"İlacınız sağlık ocağı / hastane ortamında uygulanacaktır. İshal yapması durumunda mutlaka doktorunuza bilgi veriniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12},

    # === 50 IBUCOLD C ===
    {"barcode":"8680760092235","name":"IBUCOLD C 30 FİLM TABLET",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"tok"},

    # === 51 APRANAX FORTE 10 ===
    {"barcode":"8699514091523","name":"APRANAX FORTE 550MG 10 TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 52 BI-PROFENID 150 ===
    {"barcode":"8699809018341","name":"BI-PROFENID 150MG 10 TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Çiğnemeden, kırmadan bütün olarak yutunuz. Mide rahatsızlığı yapabilir.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 53 BIOCLINE ampul ===
    {"barcode":"8699479750053","name":"BIOCLINE 600MG 1 AMPUL",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 İĞNE (FLAKON) KAS İÇİNE VEYA SERUM İÇİNE KARIŞTIRILARAK SAĞLIK OCAĞI / HASTANE ORTAMINDA UYGULANIR.",
     "uyari":"İlacınız sağlık ocağı / hastane ortamında uygulanacaktır.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12},

    # === 54 IBURAMIN COLD şurup ===
    {"barcode":"8699591570331","name":"IBURAMIN COLD ŞURUP 100ML",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM, DOKTORUN ÖNERDİĞİ DOZDA, TOK KARNINA AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Uyku hali yapabilir.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"tok"},

    # === 55 INFATRINI (mama, etiket gerek) ===
    {"barcode":"8716900558108","name":"INFATRINI 200ML",
     "kategori":"BESLENME ÜRÜNÜ",
     "talimat":"DOKTORUN ÖNERDİĞİ ŞEKİLDE, AĞIZDAN VEYA SONDADAN VERİLİR.",
     "uyari":"Açıldıktan sonra buzdolabında saklayınız, 24 saat içinde tüketiniz. Kullanmadan önce çalkalayınız.",
     "sure_gun":7},

    # === 56 AMOKLAVIN 625 ===
    {"barcode":"8699525093172","name":"AMOKLAVIN BID 625MG 14 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEKLERLE BİRLİKTE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekle"},

    # === 57 DEVIT-3 ampul ===
    {"barcode":"8699525750426","name":"DEVIT-3 300.000IU 1ML 1 AMPUL",
     "kategori":"D VİTAMİNİ",
     "talimat":"DOKTORUN ÖNERDİĞİ ŞEKİLDE 1 AMPUL AĞIZDAN İÇİLİR VEYA KAS İÇİNE UYGULANIR.",
     "uyari":"Ampul kırılırken dikkatli olunuz. Tekrar kullanım için doktorunuza danışınız.",
     "sure_gun":1,"gunluk_kez":1},

    # === 58 VENTOLIN INHALER ===
    {"barcode":"8699522521456","name":"VENTOLIN INHALER 100MCG/DOZ 200 DOZ",
     "kategori":"NEFES AÇICI (BRONKODİLATÖR)",
     "talimat":"NEFES DARLIĞI / HIRLAMA OLDUKÇA, AĞIZDAN DERİN NEFES ALARAK 1-2 PUF UYGULANIR (GÜNDE 4'TEN FAZLA OLMAMAK ÜZERE).",
     "uyari":"Kullandıktan sonra ağzınızı su ile çalkalayınız. Aşırı kullanım çarpıntıya yol açabilir, doktorunuza bildiriniz.",
     "sure_gun":30,"gunluk_kez":4,"saat_arasi":6},

    # === 59 LARGOPEN (Amoksisilin) ===
    {"barcode":"8699569010111","name":"LARGOPEN 1000MG 16 TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE AÇ VEYA TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"fark etmez"},

    # === 60 AMOKLAVIN 625 10 ===
    {"barcode":"8699525092465","name":"AMOKLAVIN BID 625MG 10 FİLM TABLET",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 TANE YEMEKLERLE BİRLİKTE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullanınız.",
     "sure_gun":5,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemekle"},

    # === 61 BENEXOL B12 ===
    {"barcode":"8699546099429","name":"BENEXOL B12 30 FİLM TABLET",
     "kategori":"B VİTAMİNİ DESTEĞİ",
     "talimat":"GÜNDE 1 DEFA 1 TANE, YEMEKTEN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Her gün aynı saatlerde düzenli kullanınız.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten sonra"},

    # === 62 APRALJIN FORTE 10 ===
    {"barcode":"8699525092199","name":"APRALJIN FORTE 550MG 10 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 63 FERRO SANOL (demir) ===
    {"barcode":"8699689161113","name":"FERRO SANOL DUODENAL 567.7MG 20 KAPSÜL",
     "kategori":"DEMİR DESTEĞİ",
     "talimat":"GÜNDE 1 DEFA 1 TANE, KAHVALTIDAN YARIM SAAT ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Aç karnına alınır. Süt, çay, kahve ile birlikte alınmaz. Dişlerde geçici renklenmeye sebep olabilir, dilin üzerine bırakmadan yutunuz.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 64 METPAMID (mide) ===
    {"barcode":"8699506012055","name":"METPAMID 10MG 30 TABLET",
     "kategori":"BULANTI KESİCİ",
     "talimat":"SABAH-ÖĞLE-AKŞAM YEMEKTEN YARIM SAAT ÖNCE 1 TANE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Uyku ve sersemlik haline sebep olabilir, araç kullanmayınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"yemekten önce"},

    # === 65 KLINDAN 300 ===
    {"barcode":"8699569750017","name":"KLINDAN 300MG/2ML 2ML 1 AMPUL",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] 1 İĞNE KAS İÇİNE VEYA SERUM İÇİNE KARIŞTIRILARAK SAĞLIK OCAĞI / HASTANE ORTAMINDA UYGULANIR.",
     "uyari":"Sağlık ocağı / hastane ortamında uygulanacaktır. İshal yapması durumunda mutlaka doktorunuza bilgi veriniz.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12},

    # === 66 THERAFLU ===
    {"barcode":"8699509090203","name":"THERAFLU FORTE 20 FİLM TABLET",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Bu ilaç hafif uyku hali yapabilir, dikkat ediniz.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"tok"},

    # === 67 FORZIGA (SGLT2) ===
    {"barcode":"8699786092730","name":"FORZIGA 10MG 28 FİLM TABLET (SGLT2 INH)",
     "kategori":"DİYABET / KALP YETMEZ. / BÖBREK HAS.",
     "talimat":"GÜNDE 1 KEZ 1 TANE, HER GÜN AYNI SAATLERDE, AÇ VEYA TOK KARNINA 1 BARDAK SU İLE İÇİNİZ.",
     "uyari":"Tableti ezmeden, çiğnemeden yutunuz. Her gün aynı saatlerde düzenli kullanınız. Bol su içiniz, idrar yolu enfeksiyonu belirtisinde doktora başvurun.",
     "sure_gun":28,"gunluk_kez":1,"yemek":"fark etmez"},

    # === 68 GERALGINE-K ===
    {"barcode":"8699578011253","name":"GERALGINE - K 20 TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-ÖĞLE-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Aksi söylenmediyse ağrınız oldukça kullanınız.",
     "sure_gun":5,"gunluk_kez":3,"yemek":"tok"},

    # === 69 D-COLEFOR ===
    {"barcode":"8680131752348","name":"D-COLEFOR 20.000IU 14 YUMUŞAK KAPSÜL",
     "kategori":"D VİTAMİNİ",
     "talimat":"HAFTADA 1 DEFA 1 TANE, YEMEKTEN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Her hafta aynı gün ve saatte kullanmaya çalışınız.",
     "sure_gun":98,"gunluk_kez":None,"yemek":"yemekten sonra"},

    # === 70 AUGMENTIN FORT süsp ===
    {"barcode":"8699522285808","name":"AUGMENTIN-BID FORT 400MG/57MG 100ML SÜSPANSİYON",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] DOKTORUN ÖNERDİĞİ DOZDA YEMEĞİN BAŞLANGICINDA AĞIZDAN İÇİLİR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullandırınız. Buzdolabında saklayınız, kullanmadan iyice çalkalayınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 71 BUSCOPAN (kasılma) ===
    {"barcode":"8699809127630","name":"BUSCOPAN 10MG 20 DRAJE",
     "kategori":"KARIN AĞRISI / KASILMA İLACI",
     "talimat":"AĞRI VEYA KASILMA OLDUKÇA, GÜNDE 3 KEZ 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Ağrınız geçtiğinde ilacı bırakınız.",
     "sure_gun":3,"gunluk_kez":3,"yemek":"tok"},

    # === 72 OTRIVINE burun ===
    {"barcode":"8699504540352","name":"OTRIVINE 10ML DOZ AYARLI BURUN SPREYİ",
     "kategori":"BURUN AÇICI",
     "talimat":"SABAH-AKŞAM HER BURUN DELİĞİNE 1 SIKIM (PUF) UYGULANIR.",
     "uyari":"7 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
     "sure_gun":5,"gunluk_kez":2},

    # === 73 CABRAL ===
    {"barcode":"8699559120011","name":"CABRAL 400MG 24 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 74 KLAVUNAT FORTE süsp ===
    {"barcode":"8699717280137","name":"KLAVUNAT BID FORTE 400MG/57MG 100ML SÜSPANSİYON",
     "kategori":"ANTİBİYOTİK",
     "talimat":"SABAH-AKŞAM [12 SAAT ARA İLE] DOKTORUN ÖNERDİĞİ DOZDA YEMEĞİN BAŞLANGICINDA AĞIZDAN İÇİLİR.",
     "uyari":"İlacınızı bitene kadar her gün düzenli kullandırınız. Buzdolabında saklayınız, kullanmadan iyice çalkalayınız.",
     "sure_gun":7,"gunluk_kez":2,"saat_arasi":12,"yemek":"yemek başlangıcında"},

    # === 75 DEVIT-3 ORAL DAMLA ===
    {"barcode":"8699525590435","name":"DEVIT-3 50.000IU/15ML ORAL DAMLA",
     "kategori":"D VİTAMİNİ",
     "talimat":"DOKTORUN ÖNERDİĞİ ŞEKİLDE GÜNLÜK / HAFTALIK DAMLA AĞIZDAN VERİLİR.",
     "uyari":"Kullanmadan önce çalkalayınız. Kapağı sıkıca kapatınız.",
     "sure_gun":30,"gunluk_kez":1},

    # === 76 IBU-FORT süsp ===
    {"barcode":"8699591700233","name":"IBU-FORT 200MG/5ML 100ML SÜSPANSİYON",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, DOKTORUN ÖNERDİĞİ DOZDA, 6-8 SAAT ARA İLE TOK KARNINA AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız.",
     "sure_gun":5,"gunluk_kez":3,"saat_arasi":8,"yemek":"tok"},

    # === 77 LEVOTIRON (Guatr) ===
    {"barcode":"8699514011187","name":"LEVOTIRON 100MCG 50 TABLET",
     "kategori":"GUATR İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE KAHVALTIDAN YARIM SAAT ÖNCE YARIM BARDAK SU İLE YUTULUR.",
     "uyari":"Tableti ezmeden, çiğnemeden yutunuz. Her gün aynı saatlerde, düzenli kullanınız.",
     "sure_gun":50,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 78 ILIADIN PED ===
    {"barcode":"8699563546029","name":"ILIADIN MERCK %0.025 10ML PEDIATRIK SPREY",
     "kategori":"BURUN AÇICI",
     "talimat":"SABAH-AKŞAM HER BURUN DELİĞİNE 1 SIKIM (PUF) UYGULANIR.",
     "uyari":"5 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
     "sure_gun":5,"gunluk_kez":2},

    # === 79 VOLTAREN SR ===
    {"barcode":"8699504030471","name":"VOLTAREN SR 75MG 10 RETARD TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Çiğnemeden, kırmadan bütün olarak yutunuz. Mide rahatsızlığı yapabilir.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 80 NOVALGIN ===
    {"barcode":"8699809015012","name":"NOVALGIN 500MG 20 TABLET",
     "kategori":"AĞRI KESİCİ - ATEŞ DÜŞÜRÜCÜ",
     "talimat":"AĞRI VEYA ATEŞ OLDUKÇA, GÜNDE 3 KEZ 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir.",
     "sure_gun":3,"gunluk_kez":3,"yemek":"tok"},

    # === 81 OKSAPAR (Enoksaparin) ===
    {"barcode":"8699828950110","name":"OKSAPAR 6000 ANTI-XAIU/0.6ML 2 HAZIR ENJEKTÖR",
     "kategori":"KAN SULANDIRICI (İĞNE)",
     "talimat":"GÜNDE 1 DEFA, HER GÜN AYNI SAATTE, KARIN BÖLGESİNE CİLT ALTI (SUBKUTAN) UYGULANIR.",
     "uyari":"Enjeksiyon yerini her seferinde değiştiriniz. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
     "sure_gun":7,"gunluk_kez":1},

    # === 82 DODEX B12 ===
    {"barcode":"8699525750556","name":"DODEX 1000MCG/ML 1ML 5 AMPUL",
     "kategori":"B12 VİTAMİNİ DESTEĞİ",
     "talimat":"DOKTORUN ÖNERDİĞİ ŞEKİLDE KAS İÇİNE UYGULANIR.",
     "uyari":"Sağlık ocağı / hastane ortamında uygulanacaktır.",
     "sure_gun":5,"gunluk_kez":1},

    # === 83 GAVISCON LIQUID ===
    {"barcode":"8699543700014","name":"GAVISCON LIQUID 200ML",
     "kategori":"MİDE İLACI (REFLÜ)",
     "talimat":"YEMEKLERDEN SONRA VE GECE YATMADAN ÖNCE 10-20 ML AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çalkalayınız. Diğer ilaçlarınızla en az 2 saat ara verecek şekilde alınız.",
     "sure_gun":14,"gunluk_kez":4,"yemek":"yemekten sonra"},

    # === 84 GAVISCON DOUBLE ===
    {"barcode":"8690570701067","name":"GAVISCON DOUBLE ACTION 200ML ORAL SÜSPANSİYON",
     "kategori":"MİDE İLACI (REFLÜ)",
     "talimat":"YEMEKLERDEN SONRA VE GECE YATMADAN ÖNCE 10-20 ML AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çalkalayınız. Diğer ilaçlarınızla en az 2 saat ara verecek şekilde alınız.",
     "sure_gun":14,"gunluk_kez":4,"yemek":"yemekten sonra"},

    # === 85 DUPHALAC (laktuloz) ===
    {"barcode":"8699820570217","name":"DUPHALAC 670MG/ML 300ML ŞURUP",
     "kategori":"KABIZLIK İLACI",
     "talimat":"SABAH KAHVALTIDA 1 ÖLÇEK (15 ML) AĞIZDAN İÇİLİR.",
     "uyari":"Bol su içiniz. Etki 2-3 günde başlayabilir.",
     "sure_gun":14,"gunluk_kez":1},

    # === 86 VENTOLIN NEBULES ===
    {"barcode":"8699522521494","name":"VENTOLIN NEBULES 2.5MG/2.5ML 20 NEBUL",
     "kategori":"NEFES AÇICI (NEBÜL)",
     "talimat":"SABAH-AKŞAM 1 FLAKON NEBULİZATÖR CİHAZIYLA SOLUNUR.",
     "uyari":"Açıldıktan sonra 24 saat içinde kullanılmalıdır. Çocukta dikkatle kullanınız.",
     "sure_gun":7,"gunluk_kez":2},

    # === 87 ZERO-P (parasetamol) ===
    {"barcode":"8699525095732","name":"ZERO-P 100MG 15 FİLM TABLET",
     "kategori":"AĞRI KESİCİ",
     "talimat":"SABAH-AKŞAM 1 TANE TOK KARNINA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Mide rahatsızlığı yapabilir, tok karnına alınız.",
     "sure_gun":5,"gunluk_kez":2,"yemek":"tok"},

    # === 88 DELTACORTRIL (Kortizon) ===
    {"barcode":"8699532010865","name":"DELTACORTRIL 5MG 20 TABLET",
     "kategori":"KORTİZON TEDAVİSİ",
     "talimat":"DOKTORUN ÖNERDİĞİ DOZDA, SABAH KAHVALTIDAN SONRA BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Doktor önerisi olmadan ilacı bırakmayınız, kademeli azaltılır. Tuz alımına dikkat ediniz.",
     "sure_gun":7,"gunluk_kez":1,"yemek":"yemekten sonra"},

    # === 89 A-FERIN PLUS PED şurup ===
    {"barcode":"8699570570147","name":"A-FERIN PLUS PEDIATRIK 100ML ŞURUP",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM, DOKTORUN ÖNERDİĞİ DOZDA, AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Uyku hali yapabilir.",
     "sure_gun":5,"gunluk_kez":3},

    # === 90 BELOC ZOK 25 ===
    {"barcode":"8699786030114","name":"BELOC ZOK 25MG 20 KONTROLLU SAL. FİLM TABLET",
     "kategori":"TANSİYON İLACI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, HER GÜN AYNI SAATTE, KAHVALTIDAN ÖNCE BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Her gün aynı saatlerde, düzenli içiniz. Tableti çiğnemeden, bütün olarak yutunuz.",
     "sure_gun":30,"gunluk_kez":1,"yemek":"yemekten önce"},

    # === 91 A-FERIN PED şurup ===
    {"barcode":"8699570570062","name":"A-FERIN PEDIATRIK ŞURUP 100ML",
     "kategori":"GRİP / SOĞUK ALGINLIĞINDA",
     "talimat":"SABAH-ÖĞLE-AKŞAM, DOKTORUN ÖNERDİĞİ DOZDA, AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çok iyi çalkalayınız. Uyku hali yapabilir.",
     "sure_gun":5,"gunluk_kez":3},

    # === 92 COLCHICUM DISPERT ===
    {"barcode":"8699559120028","name":"COLCHICUM DISPERT 0.5MG 50 FİLM TABLET",
     "kategori":"FMF / GUT TEDAVİSİ",
     "talimat":"DOKTORUN ÖNERDİĞİ DOZDA, GÜNDE 2-3 KEZ 1 TANE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"İshal yaparsa doktora başvurunuz. Greyfurt suyu ile birlikte alınmaz.",
     "sure_gun":30,"gunluk_kez":2,"yemek":"fark etmez"},

    # === 93 PLAVIX (Klopidogrel) ===
    {"barcode":"8699809097698","name":"PLAVIX 75MG 28 FİLM TABLET",
     "kategori":"KAN SULANDIRICI",
     "talimat":"GÜNDE 1 DEFA 1 TANE, HER GÜN AYNI SAATTE, AÇ VEYA TOK KARNINA BİR BARDAK SU İLE YUTULUR.",
     "uyari":"Her gün aynı saatlerde, düzenli kullanınız. Diş çekimi / ameliyat öncesi doktorunuza bilgi veriniz.",
     "sure_gun":28,"gunluk_kez":1,"yemek":"fark etmez"},

    # === 94 RHINFANT ===
    {"barcode":"8698613542028","name":"RHINFANT %0.01 10ML PEDİATRİK BURUN SPREYİ",
     "kategori":"BURUN AÇICI (BEBEK)",
     "talimat":"SABAH-AKŞAM HER BURUN DELİĞİNE 1 SIKIM UYGULANIR.",
     "uyari":"3 günden uzun süre kullanmayınız. Birden fazla kişi tarafından kullanılmamalıdır.",
     "sure_gun":3,"gunluk_kez":2},

    # === 95 COLEDAN D3 ===
    {"barcode":"8680199599701","name":"COLEDAN-D3 150.000IU/10ML ORAL DAMLA 10ML",
     "kategori":"D VİTAMİNİ",
     "talimat":"DOKTORUN ÖNERDİĞİ ŞEKİLDE GÜNLÜK / HAFTALIK DAMLA AĞIZDAN VERİLİR.",
     "uyari":"Kullanmadan önce çalkalayınız. Kapağı sıkıca kapatınız.",
     "sure_gun":30,"gunluk_kez":1},

    # === 96 GLIFOR (Metformin) ===
    {"barcode":"8699569090717","name":"GLIFOR 1000MG 100 FİLM TABLET",
     "kategori":"DİYABET / KALP YETMEZ. / BÖBREK HAS.",
     "talimat":"SABAH-AKŞAM 1 TANE YEMEKLE BİRLİKTE BİR BARDAK SUYLA YUTULUR.",
     "uyari":"Tableti ezmeden, çiğnemeden yutunuz. Mide bulantısı için yemekle alınız. Her gün düzenli kullanınız.",
     "sure_gun":30,"gunluk_kez":2,"yemek":"yemekle"},

    # === 97 FITO krem ===
    {"barcode":"8699772350493","name":"FITO %5 40GR KREM",
     "kategori":"CİLT İLACI (DIŞ KULLANIM)",
     "talimat":"GÜNDE 2-3 KEZ TEMİZLENMİŞ KURU CİLDE İNCE BİR TABAKA HALİNDE SÜRÜLÜR.",
     "uyari":"Sadece dış kullanım içindir. Göz ve ağız ile temasından kaçınınız.",
     "sure_gun":14,"gunluk_kez":3},

    # === 98 MAXIMUS gargara ===
    {"barcode":"8699580510034","name":"MAXIMUS %0.25 ORAL SPREY 30ML",
     "kategori":"BOĞAZ SPREYİ",
     "talimat":"SABAH-ÖĞLE-AKŞAM AĞIZ İÇİ TEMİZLENDİKTEN SONRA 1 FIŞ AĞIZ İÇİNDEN BOĞAZA SIKILIR.",
     "uyari":"Her defasında 4-5 puf sıkılabilir. Boğazınızda kalan kısmı yutabilirsiniz, fazla gelirse tükürebilirsiniz.",
     "sure_gun":7,"gunluk_kez":3},

    # === 99 BRICANYL DUO ===
    {"barcode":"8699786570214","name":"BRICANYL DUO 1.5MG/5ML + 66.5MG/5ML 100ML ŞURUP",
     "kategori":"NEFES AÇICI ŞURUP",
     "talimat":"SABAH-ÖĞLE-AKŞAM, DOKTORUN ÖNERDİĞİ DOZDA, AĞIZDAN İÇİLİR.",
     "uyari":"Kullanmadan önce çalkalayınız. Çarpıntı / titreme olursa doktora başvurunuz.",
     "sure_gun":7,"gunluk_kez":3},

    # === 100 ANDOREX ORAL SPREY ===
    {"barcode":"8699746510328","name":"ANDOREX 30ML ORAL SPREY",
     "kategori":"BOĞAZ SPREYİ",
     "talimat":"SABAH-ÖĞLE-AKŞAM AĞIZ İÇİ TEMİZLENDİKTEN SONRA 1 FIŞ AĞIZ İÇİNDEN BOĞAZA SIKILIR.",
     "uyari":"Her defasında 4-5 puf sıkılabilir. Yutmayınız.",
     "sure_gun":7,"gunluk_kez":3},
]
