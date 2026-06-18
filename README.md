## DataFlow - Veri Doğrulama ve Aktarım Paneli

DataFlow, CSV ve Excel dosyalarının sisteme yüklenmeden önce kontrol edilmesini, hatalı kayıtların ayrıştırılmasını ve temiz verilerin veritabanına aktarılmasını sağlayan web tabanlı bir veri yönetim panelidir.

Bu projede amaç yalnızca dosya yüklemek değil; yüklenen verinin kalitesini kontrol etmek, hatalı kayıtları raporlamak ve aktarım sürecini takip edilebilir hale getirmektir.

## Proje Özeti

Kullanıcı sisteme bir CSV veya Excel dosyası yükler. Sistem dosyayı okur, ilk kayıtları önizleme ekranında gösterir ve veriler üzerinde doğrulama kontrolleri yapar.

Doğrulama sonucunda kayıtlar ikiye ayrılır:

- Temiz kayıtlar
- Hatalı kayıtlar

Temiz kayıtlar veritabanına aktarılabilir. Hatalı kayıtlar ise ayrı bir ekranda satır numarası, hata türü ve açıklamasıyla birlikte gösterilir.



## Ekran Görüntüleri

### Veri Önizleme
[Veri Önizleme](screenshots/veri_onizleme.jpg)

### Veri Doğrulama Hataları
[Veri Doğrulama Hataları](screenshots/hatalar.jpg)

### Hata Raporu 
[Hata Raporları](screenshots.raporlama.jpg)


## Kurulum ve Çalıştırma

Projeyi bilgisayarınıza klonlayın:
-git clone https://github.com/seherynar/DataFlow.git
-cd DataFlow

### Sanal ortam oluşturun:
-python -m venv venv
-venv\Scripts\activate

### Gerekli paketleri yükleyin:
-pip install -r requirements.txt

### Uygulamayı çalıştırın:
-python app.py

### Tarayıcıdan açın:
-http://127.0.0.1:5050


## Kullanılan Teknolojiler

- Python
- Flask
- SQLite
- SQLAlchemy
- Pandas
- HTML
- CSS
- Bootstrap


## Proje Yapısı

```text
dataflow/
│
├── app.py
├── database.py
├── validators.py
├── importer.py
├── audit.py
├── reports.py
├── requirements.txt
├── README.md
│
├── uploads/
├── exports/
├── data/
│
├── sample_files/
│   ├── customers_sample.csv
│   └── customers_sample.xlsx
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── preview.html
│   ├── errors.html
│   ├── imports.html
│   ├── audit_logs.html
│   └── reports.html
│
└── static/
    └── style.css