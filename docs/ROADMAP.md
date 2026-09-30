# Geliştirme Yol Haritası

## Aşama 1 — Temel kurulum

- Django proje iskeleti
- PostgreSQL yapılandırması
- Docker Compose
- Django REST Framework altyapısı
- `/health/` ve `/api/v1/` başlangıç adresleri
- Temel testler

## Aşama 2 — Konu ve kazanım hiyerarşisi

- Konu modeli ve değişmeyen konu kodu
- Kazanım modeli ve MEB kazanım kodu
- Konu–kazanım ilişkisi
- Yönetim paneli
- Model kısıtları ve testler

## Aşama 3 — Soru veri modeli

- Soru ve `Q000001` kodu
- Dört şık ve doğru cevap
- Ana/ikincil konu ilişkileri
- Çoklu kazanım ilişkisi
- Görsel, LaTeX, kaynak ve zaman alanları
- Zorunlu alan doğrulamaları

## Aşama 4 — Soru tipi ve zorluk

- Soru tipi ve `QT0001` kodu
- Soru tipi açıklama alanları
- 1–5 zorluk düzeyi
- Bekleyen/tamamlanan durum hesapları

## Aşama 5 — Tek soru yönetim ekranları

- Ekleme
- Düzenleme
- Görüntüleme
- Çözüm girişi
- Arşivleme ve kalıcı silme
- Aynı görsel hash uyarısı

## Aşama 6 — Arama ve filtreleme

- ID ve metin araması
- Konu, kazanım, tip ve zorluk filtreleri
- Kazanımlarda `any/all` mantığı
- Çalışma listeleri
- Sayfalama

## Aşama 7 — API

- Öğrenciye güvenli soru yanıtı
- Yetkili sunucuya tam soru yanıtı
- Liste ve rastgele seçim
- Filtreler ve hariç tutulan soru kodları
- Temel token kimlik doğrulaması
- API testleri ve şema belgesi

## Aşama 8 — API güvenlik sertleştirmesi ve dağıtım hazırlığı

- Soru verisi döndüren API uçlarında anonim erişimi kapatma
- Sağlık, API kökü ve şema uçlarının erişim politikasını açıkça belirleme
- Öğrenci/istemci ve güvenilir sunucu rollerini birbirinden ayırma
- Öğrenci/istemci tokenlarının doğru cevap, çözüm, eksik ve arşivlenmiş kayıtlara
  erişmesini engelleme
- Yalnızca yetkili sunucu rolüne tam soru yanıtı ve hassas dahil etme
  seçeneklerini açma
- Her tüketici uygulama için ayrı entegrasyon kullanıcısı ve token oluşturma
- Token oluşturma, güvenli teslim, iptal ve yenileme sürecini belgeleme
- Token ve diğer sırları kaynak koddan/Git'ten uzak tutup ortam değişkeni veya
  uygun sır yönetimiyle saklama
- Anonim, öğrenci/istemci ve yetkili sunucu erişim matrisini otomatik testlerle
  doğrulama
- API istekleri için hız sınırlama ve güvenlik kayıtlarını yapılandırma
- Canlı ortamda HTTPS zorunluluğu
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, güvenilir kaynaklar, güvenli çerezler
  ve ters vekil ayarlarını canlı ortama göre sıkılaştırma
- Yedekleme ve geri yükleme
- Dosya depolama uyarlaması
- Özel web ortamına dağıtım belgeleri

## Aşama 9 — PDF geçici içe aktarma

- PDF yükleme
- Deterministik soru alanı önerileri
- Elle kırpma düzeltmesi
- Metin katmanından cevap anahtarı okuma
- Elle LaTeX, cevap, konu ve kazanım girişi
- Eksik PDF içe aktarma kayıtları çalışma listesi
- Nihai havuza toplu aktarma
- PDF bağımlılıkları için son dağıtım doğrulaması
