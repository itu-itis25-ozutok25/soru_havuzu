# Soru Havuzu ve Sınıflandırma Sistemi

Bu depo, 8. sınıf matematik sorularının konu, kazanım, soru tipi ve zorluk
bilgileriyle saklanacağı Django + PostgreSQL uygulamasının temelini içerir.

## İlk aşamada tamamlananlar

- Django proje iskeleti
- PostgreSQL bağlantı ayarları
- Docker Compose ile yerel çalışma ortamı
- Django REST Framework altyapısı
- Sürümlendirilmiş `/api/v1/` başlangıç adresi
- `/health/` sağlık kontrolü
- Temel uç nokta testleri

Konu, kazanım, soru ve soru tipi veri modelleri sonraki aşamalarda eklenecektir.

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

