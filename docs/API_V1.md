# Soru Havuzu API v1

API kökü:

```text
/api/v1/
```

## Erişim politikası

`/health/`, `/api/v1/` ve `/api/v1/schema/` hassas soru verisi içermez ve
kimlik doğrulaması olmadan erişilebilir. Aşağıdaki soru uçlarının tamamı geçerli
bir token ve açıkça atanmış API rolü gerektirir:

- `/api/v1/questions/`
- `/api/v1/questions/{kod}/`
- `/api/v1/questions/random/`

Token istek başlığında gönderilir:

```http
Authorization: Token <anahtar>
```

Roller:

- `student`: Soru ve şıkları alır; `correct_answer`, `solution` ve arşiv bilgisi
  yanıtta bulunmaz. Eksik veya arşivlenmiş kayıtları dahil edemez.
- `server`: Doğru cevap ve çözüm dahil tam yanıtı alır. Eksik ve arşivlenmiş
  kayıtları açıkça isteyebilir.

Token bulunmayan veya geçersiz istek `401`, geçerli tokenı olup API rolü
bulunmayan kullanıcı ise `403` alır.

Yerel dosya depolamasında soru görseli adresleri de aynı tokenı gerektirir.
Öğrenci rolü yalnızca aktif ve tamamlanmış soruların görsellerine erişebilir.
S3 uyumlu özel depolamada görseller süreli imzalı bağlantılarla sunulur.

## Entegrasyon hesabı ve token yönetimi

Her tüketici uygulama için ayrı ve anlamlı bir kullanıcı adı kullanılmalıdır.
Komut, giriş parolası bulunmayan entegrasyon kullanıcısını ve seçilen rolü
oluşturur; token değerini yalnızca oluşturma anında terminale yazar.

Öğrenci/istemci tokenı:

```powershell
docker compose exec web python manage.py manage_api_token deneme-uygulamasi --role student
```

Güvenilir sunucu tokenı:

```powershell
docker compose exec web python manage.py manage_api_token sinav-sunucusu --role server
```

Mevcut tokenı yenileme:

```powershell
docker compose exec web python manage.py manage_api_token sinav-sunucusu --role server --rotate
```

Tokenı iptal etme:

```powershell
docker compose exec web python manage.py manage_api_token sinav-sunucusu --revoke
```

Token kaynak koda, Git'e, ekran görüntüsüne veya ortak bir belgeye yazılmamalı;
tüketici uygulamanın `.env` dosyasında veya uygun bir sır yönetim sisteminde
saklanmalıdır. Canlı ortamda token yalnızca HTTPS üzerinden gönderilmelidir.

## Uç noktalar

### Soru listesi

```http
GET /api/v1/questions/
```

Yanıtlar sayfa başına 25 kayıt olarak sayfalanır.

Desteklenen sorgu parametreleri:

- `q`: soru kodu veya soru metni
- `topics`: virgülle ayrılmış konu kodları
- `outcomes`: virgülle ayrılmış kazanım kodları
- `outcome_match`: `any` veya `all`
- `question_type`: soru tipi kodu
- `difficulty`: 1–5
- `exclude`: hariç tutulacak, virgülle ayrılmış soru kodları
- `page`: sayfa numarası

Yalnızca `server` rolünde kullanılabilen parametreler:

- `include_incomplete=true`
- `include_archived=true`

### Tek soru

```http
GET /api/v1/questions/Q000001/
```

### Rastgele seçim

```http
GET /api/v1/questions/random/?count=5
```

`count` 1–100 arasında olabilir. Liste uç noktasındaki filtrelerin tamamı ve
`exclude` parametresi rastgele seçimde de kullanılabilir.

Örnek:

```http
GET /api/v1/questions/random/
    ?outcomes=M.8.1.3.1,M.8.1.3.2
    &outcome_match=all
    &question_type=QT0004
    &difficulty=3
    &exclude=Q000012,Q000018
    &count=5
```

## Hız sınırları

Varsayılan sınırlar anonim tanıtım/şema istekleri için dakikada 60, tokenlı
kullanıcılar için dakikada 600 istektir. Bunlar `API_ANON_THROTTLE_RATE` ve
`API_USER_THROTTLE_RATE` ortam değişkenleriyle değiştirilebilir. Sınır aşılırsa
API `429 Too Many Requests` döndürür.

## Şema

OpenAPI 3 şeması:

```http
GET /api/v1/schema/
```
