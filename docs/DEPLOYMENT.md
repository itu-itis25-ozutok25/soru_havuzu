# Özel web ortamına dağıtım

Bu belge, uygulamanın tek bir özel Linux sunucusunda Docker Compose ve otomatik
HTTPS sağlayan Caddy ile çalıştırılması için hazırlanmıştır. Gerçek alan adı,
sunucu ve nesne depolama sağlayıcısı seçilmeden uzak dağıtım yapılmaz.

## Erişim politikası

- `/health/`, `/api/v1/` ve `/api/v1/schema/` tanılama/belgeleme amacıyla
  açıktır ve soru verisi içermez.
- Yönetim ekranları Django oturumu gerektirir.
- Soru API uçları token ve `api_student` veya `api_server` rolü gerektirir.
- Yerel hacimdeki soru görselleri Caddy tarafından doğrudan açılmaz; Django
  üzerinden oturum veya API rolü denetiminden geçer.
- Sunucuya doğrudan `8000` veya `5432` portu açılmaz. İnternete yalnızca Caddy
  üzerinden `80` ve `443` portları sunulur.

## Sunucu ön koşulları

1. Güncel bir Linux sunucusu hazırlayın ve güvenlik güncellemelerini uygulayın.
2. Docker Engine ile Compose eklentisini kurun.
3. Alan adının DNS kaydını sunucunun genel IP adresine yönlendirin.
4. Güvenlik duvarında yalnızca SSH, HTTP (`80`) ve HTTPS (`443`) portlarını
   açın. SSH erişimini mümkünse anahtar ve izinli IP ile sınırlandırın.

## Canlı ortam sırları

Örnek dosyayı gerçek, Git tarafından yok sayılan dosyaya kopyalayın:

```powershell
Copy-Item .env.production.example .env.production
```

En az 50 karakterlik rastgele bir Django anahtarı üretmek için:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

`.env.production` içinde en az şu değerleri değiştirin:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `POSTGRES_PASSWORD`
- `APP_DOMAIN`

Bu dosyayı Git'e eklemeyin. Dosya izinlerini yalnızca dağıtım kullanıcısının
okuyabileceği şekilde sınırlandırın. Tokenlar da bu dosyaya değil, onları
kullanan uygulamanın sır deposuna yazılmalıdır.

## İlk dağıtım

Yapılandırmayı doğrulayın:

```powershell
docker compose --env-file .env.production -f compose.production.yml config --quiet
```

Servisleri oluşturup başlatın:

```powershell
docker compose --env-file .env.production -f compose.production.yml up -d --build
```

Caddy, DNS doğruysa alan adı için TLS sertifikasını otomatik alır ve HTTP
isteklerini HTTPS'ye yönlendirir. Durumu kontrol edin:

```powershell
docker compose --env-file .env.production -f compose.production.yml ps
docker compose --env-file .env.production -f compose.production.yml logs --tail 100 web proxy
```

Django dağıtım güvenliği kontrolü:

```powershell
docker compose --env-file .env.production -f compose.production.yml exec web python manage.py check --deploy
```

## İlk yönetici ve API hesapları

Yönetim paneli için ayrı bir insan hesabı oluşturun:

```powershell
docker compose --env-file .env.production -f compose.production.yml exec web python manage.py createsuperuser
```

Her tüketici uygulama için ayrı token oluşturun:

```powershell
docker compose --env-file .env.production -f compose.production.yml exec web python manage.py manage_api_token deneme-uygulamasi --role student
docker compose --env-file .env.production -f compose.production.yml exec web python manage.py manage_api_token sinav-sunucusu --role server
```

Tokenı terminalden yalnızca bir kez kopyalayın ve tüketici uygulamanın sır
deposuna koyun. Yenileme ve iptal komutları `docs/API_V1.md` içindedir.

## Dosya depolaması

Varsayılan üretim tanımı medya dosyalarını Docker'ın `media_data` hacminde
tutar. Tek sunucu için çalışır; düzenli yedek zorunludur.

S3 uyumlu özel nesne depolaması kullanmak için `.env.production` içinde
`DJANGO_USE_S3=true` yapıp `S3_BUCKET_NAME`, `S3_ACCESS_KEY_ID`,
`S3_SECRET_ACCESS_KEY`, `S3_REGION_NAME` ve gerekiyorsa `S3_ENDPOINT_URL`
değerlerini doldurun. Nesneler özel tutulur ve Django süreli imzalı URL üretir.
Erişim anahtarına yalnızca ilgili bucket için gerekli en düşük yetkiyi verin.

## Yedekleme

Yerel Compose ortamı:

```powershell
.\scripts\backup.ps1
```

Üretim Compose ortamı:

```powershell
.\scripts\backup.ps1 -ComposeFile compose.production.yml
```

Komut PostgreSQL özel biçimli dökümünü, medya arşivini ve SHA-256 bütünlük
manifestini tarihli bir `backups/` klasörüne yazar. `backups/` Git tarafından
yok sayılır. Yedekleri ayrıca şifreli ve sunucu dışındaki bir konuma aktarın.

En az bir geri yükleme denemesi yapılmamış yedek güvenilir kabul edilmemelidir.

## Geri yükleme

Geri yükleme mevcut veritabanı ve medya içeriğini değiştirir; araç bu nedenle
PowerShell onayı ister:

```powershell
.\scripts\restore.ps1 -BackupPath .\backups\20260920-120000
```

Üretimde:

```powershell
.\scripts\restore.ps1 -BackupPath .\backups\20260920-120000 -ComposeFile compose.production.yml
```

Araç önce manifestteki SHA-256 değerlerini doğrular, web servisini durdurur,
veritabanı ile medyayı geri yükler ve web servisini yeniden başlatır.

## Güncelleme

1. Önce yedek alın.
2. Yeni kodu indirin.
3. İmajı yeniden oluşturup servisleri başlatın:

```powershell
docker compose --env-file .env.production -f compose.production.yml up -d --build
```

4. `check --deploy`, sağlık adresi, yönetim girişi ve rol bazlı API erişimini
   kontrol edin.
5. Sorun halinde önceki sürüm koduna dönüp doğrulanmış yedeği geri yükleyin.

## Düzenli işletim kontrol listesi

- Tokenları tüketici uygulama bazında ayrı tutun; paylaşmayın.
- Kullanılmayan tokenları hemen iptal edin ve şüpheli tokenları yenileyin.
- Web, güvenlik ve ters vekil kayıtlarını düzenli inceleyin.
- İşletim sistemi ve konteyner imajı güvenlik güncellemelerini uygulayın.
- Veritabanı ve medya yedeklerini düzenli alın, saklama süresi belirleyin.
- Geri yükleme işlemini ayrı bir ortamda periyodik olarak deneyin.
- HTTPS sertifikası ve disk kullanımını izleyin.
