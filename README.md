# Soru Havuzu ve Sınıflandırma Sistemi

LGS asistanı için soru havuzu üretimi projesidir.

Bu depo, 8. sınıf matematik sorularının konu, kazanım, soru tipi ve zorluk
bilgileriyle saklanacağı Django + PostgreSQL uygulamasının temelini içerir.

## Tamamlananlar

- Django proje iskeleti
- PostgreSQL bağlantı ayarları
- Docker Compose ile yerel çalışma ortamı
- Django REST Framework altyapısı
- Sürümlendirilmiş `/api/v1/` başlangıç adresi
- `/health/` sağlık kontrolü
- Temel uç nokta testleri
- Konu ve kazanım veri modelleri
- Değiştirilemeyen konu ve MEB kazanım kodları
- Konu–kazanım ilişkisi ve yönetim paneli
- Model kısıtları ve PostgreSQL testleri
- Otomatik ve tekrar kullanılmayan `Q000001` biçimli soru kodu
- Soru görseli, LaTeX metni, dört şık ve doğru cevap alanları
- Ana/ikincil konu ve çoklu kazanım ilişkileri
- Kaynak bilgileri ve zorunlu alan doğrulamaları
- Otomatik `QT0001` biçimli soru tipi kodu ve soru tipi tanımları
- 1–5 zorluk düzeyi ve çözüm alanı
- Soru tipi, zorluk ve çözüm bekleme durumları
- Oturum korumalı tek soru yönetim ekranları
- Soru ekleme, düzenleme, ayrıntı ve çözüm girişi
- Arşivleme, geri getirme ve kalıcı silme
- SHA-256 tabanlı aynı görsel uyarısı
- Kod ve soru metni araması
- Konu, kazanım, soru tipi, zorluk ve kaynak filtreleri
- Kazanımlarda `any/all` eşleşme mantığı
- Çalışma listeleri ve sayfalama
- `/api/v1/` altında sürümlendirilmiş REST API
- Güvenli öğrenci ve tokenlı sunucu yanıtları
- Filtrelenmiş liste ve rastgele soru seçimi
- OpenAPI şeması ve API kullanım belgesi
- Soru uçlarında zorunlu token ve öğrenci/sunucu rol ayrımı
- Uygulama bazlı token oluşturma, yenileme ve iptal komutu
- Soru görsellerinde oturum/token tabanlı erişim denetimi
- API hız sınırlaması ve güvenlik kayıtları
- Canlı ortam Django güvenlik ayarları
- Caddy ile HTTPS'li üretim Compose yapılandırması
- Yerel hacim veya özel S3 uyumlu medya depolaması
- Bütünlük kontrollü PostgreSQL ve medya yedekleme/geri yükleme araçları
- Özel web ortamı dağıtım belgesi

PDF yükleme ve geçici içe aktarma, yol haritasının son aşamasına ertelenmiştir.

API kullanımı için [API belgesine](docs/API_V1.md), özel web ortamı kurulumu,
HTTPS, dosya depolaması ve yedekleme için [dağıtım belgesine](docs/DEPLOYMENT.md)
bakın.

## Gereksinimler

- Docker Desktop veya Docker Engine
- Docker Compose

## İlk çalıştırma

1. Örnek ortam dosyasını kopyalayın:

   ```bash
   cp .env.example .env
   ```

2. `.env` içindeki geliştirme parolalarını değiştirin.

3. Uygulamayı oluşturup başlatın:

   ```bash
   docker compose up --build
   ```

4. Tarayıcıdan aşağıdaki adresleri açın:

   - Sağlık kontrolü: <http://localhost:8000/health/>
   - API başlangıcı: <http://localhost:8000/api/v1/>
   - Yönetim paneli: <http://localhost:8000/admin/>

## Yönetici hesabı oluşturma

Uygulama çalışırken ayrı bir terminalde:

```bash
docker compose exec web python manage.py createsuperuser
```

## Testler

Veritabanı ve web hizmeti çalışırken:

```bash
docker compose exec web python manage.py test
```

## Durdurma

```bash
docker compose down
```

Veritabanı verilerini de silmek isterseniz `docker compose down -v` komutu
kullanılabilir. Bu işlem yerel veritabanındaki tüm kayıtları kalıcı olarak siler.
