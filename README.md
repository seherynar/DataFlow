## DataFlow - Veri Doğrulama ve Aktarım Paneli

DataFlow, CSV ve Excel dosyalarının sisteme yüklenmeden önce kontrol edilmesini, hatalı kayıtların ayrıştırılmasını ve temiz verilerin veritabanına aktarılmasını sağlayan web tabanlı bir veri yönetim panelidir.

Bu projede amaç yalnızca dosya yüklemek değil; yüklenen verinin kalitesini kontrol etmek, hatalı kayıtları raporlamak ve aktarım sürecini takip edilebilir hale getirmektir.

## Proje Özeti

Kullanıcı sisteme bir CSV veya Excel dosyası yükler. Sistem dosyayı okur, ilk kayıtları önizleme ekranında gösterir ve veriler üzerinde doğrulama kontrolleri yapar.

Doğrulama sonucunda kayıtlar ikiye ayrılır:

- Temiz kayıtlar
- Hatalı kayıtlar

Temiz kayıtlar veritabanına aktarılabilir. Hatalı kayıtlar ise ayrı bir ekranda satır numarası, hata türü ve açıklamasıyla birlikte gösterilir.

## Özellikler

- Web tabanlı yönetim paneli
- CSV ve Excel dosyası yükleme
- Veri önizleme ekranı
- Zorunlu kolon kontrolü
- Boş alan kontrolü
- E-posta format kontrolü
- Telefon format kontrolü
- Tarih format kontrolü
- Sayısal değer kontrolü
- Negatif değer kontrolü
- Tekrarlı kayıt kontrolü
- Temiz ve hatalı kayıt ayrımı
- Temiz kayıtları veritabanına aktarma
- Hatalı kayıtları CSV olarak dışa aktarma
- Aktarım geçmişi
- Audit log kayıtları
- Rollback ile aktarımı geri alma
- Dashboard ve raporlama ekranı

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