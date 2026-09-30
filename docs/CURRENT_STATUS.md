# Mevcut Durum ve Devir Notu

## Tamamlanan aşamalar

### Aşama 1 — Temel kurulum

- Django proje iskeleti
- PostgreSQL ortam değişkenleri
- Dockerfile ve Docker Compose
- Django REST Framework kurulumu
- `/health/` sağlık uç noktası
- `/api/v1/` başlangıç uç noktası
- İki temel test

### Aşama 2 — Konu ve kazanım hiyerarşisi

- Benzersiz ve değiştirilemeyen kodlu konu modeli
- MEB kodlu ve bir konuya zorunlu olarak bağlı kazanım modeli
- Boş değer ve benzersizlik kısıtları
- Bağlı kazanımı bulunan konular için silme koruması
- Konu ve kazanım yönetim paneli kayıtları
- İlk `core` migration'ı
- Model, kısıt ve yönetim paneli testleri

### Aşama 3 — Soru veri modeli

- Silinse bile tekrar kullanılmayan otomatik `Q000001` soru kodu
- Orijinal soru görseli ve elle girilen LaTeX soru metni
- Ayrı LaTeX A, B, C ve D şıkları ile tek doğru cevap
- Bir ana konu, birden fazla ikincil konu ve birden fazla kazanım ilişkisi
- Kaynak PDF adı, sayfa numarası ve kaynak soru numarası
- Oluşturulma ve güncellenme zamanları
- Zorunlu alanlar ve sınıflandırma tutarlılığı doğrulamaları
- Soru yönetim paneli kaydı
- Soru modeli ve veritabanı kısıtı testleri

### Aşama 4 — Soru tipi ve zorluk

- Silinse bile tekrar kullanılmayan otomatik `QT0001` soru tipi kodu
- Soru tipi adı, kısa açıklaması, çözüm yöntemi ve sınıflandırma ölçütleri
- Soru tiplerine birden fazla örnek soru bağlama
- Sorulara isteğe bağlı tek soru tipi atama
- 1–5 arasında isteğe bağlı zorluk düzeyi
- Düz metin veya LaTeX çözüm alanı
- Soru tipi, zorluk ve çözüm bekleme durumları
- Tüm isteğe bağlı alanlar tamamlandığında tamamlanma durumu
- Soru tipi yönetim paneli ve soru listesinde durum gösterimi
- Model, kısıt, ilişki ve durum testleri

### Aşama 5 — Tek soru yönetim ekranları

- Oturum açma ve kullanıcıya özel soru yönetim alanı
- Aktif ve arşivlenmiş soru listeleri
- Soru ekleme, düzenleme ve ayrıntı ekranları
- Orijinal görsel ve LaTeX içerik gösterimi
- Ayrı çözüm giriş ekranı
- Geri alınabilir arşivleme ve arşivden çıkarma
- Onay ekranlı kalıcı silme ve görsel dosyasını temizleme
- Görsel değiştirildiğinde eski dosyayı temizleme
- SHA-256 ile aynı görseli tespit etme
- Uyarı sonrasında açık kullanıcı onayıyla aynı görseli kaydetme
- Yönetim ekranı ve dosya işlemi testleri

### Aşama 6 — Arama ve filtreleme

- Soru kodu ve LaTeX soru metninde arama
- Ana veya ikincil konuya göre çoklu filtreleme
- Kazanımlarda `herhangi birini içerir` ve `tamamını içerir` mantıkları
- Soru tipi ve 1–5 zorluk filtreleri
- Kaynak PDF adı ve kaynak soru numarası filtreleri
- Soru tipi, zorluk ve çözüm bekleme çalışma listeleri
- Tamamlanan ve arşivlenen soru listeleri
- Çalışma listeleri için anlık kayıt sayıları
- Filtreleri koruyan, sayfa başına 25 kayıtlık sayfalama
- Arama, filtre, çalışma listesi ve sayfalama testleri

### Aşama 7 — REST API

- `/api/v1/` altında sürümlendirilmiş salt-okunur API
- Sayfalanmış soru listesi ve tek soru uç noktası
- Tek veya çoklu rastgele soru seçimi
- Konu, kazanım, soru tipi ve zorluk filtreleri
- Kazanımlarda `any/all` eşleşme mantığı
- Daha önce kullanılan soru kodlarını hariç tutma
- Eksik ve arşivlenmiş soruları varsayılan olarak dışarıda bırakma
- Tokensız öğrenci yanıtlarında doğru cevap ve çözümü gizleme
- Yetkili tokenla doğru cevap ve çözüme erişim
- Yetkili istekte eksik veya arşivlenmiş kayıtları açıkça dahil etme
- OpenAPI 3 şeması ve API kullanım belgesi
- API güvenliği, filtreleri ve hata davranışları için otomatik testler

Aşama 7 ilk tamamlandığında tokensız öğrenci yanıtı ve herhangi bir geçerli
tokenla tam sunucu yanıtı kullanıyordu. Bu geçici davranış Aşama 8'de
sertleştirilmiştir.

### Aşama 8 — API güvenlik sertleştirmesi ve dağıtım hazırlığı

- Soru verisi uçlarında zorunlu token kimlik doğrulaması
- `api_student` ve `api_server` gruplarıyla açık rol ayrımı
- Öğrenci tokenında cevap, çözüm, eksik ve arşivlenmiş kayıt koruması
- Yalnızca sunucu rolünde tam yanıt ve hassas dahil etme seçenekleri
- API rolü bulunmayan geçerli tokenlara erişim reddi
- Her tüketici uygulama için ayrı, parolasız entegrasyon hesabı
- Token oluşturma, rol atama, yenileme ve iptal yönetim komutu
- İnsan/yönetici hesabına entegrasyon tokenı atanmasını engelleme
- Yerel soru görsellerinde oturum veya API rolü denetimi
- Özel nesne depolamasında süreli imzalı görsel bağlantıları
- Anonim ve tokenlı API hız sınırları ile güvenlik kayıtları
- Canlı ortam sır, HTTPS, HSTS, güvenli çerez, izinli sunucu ve ters vekil ayarları
- PostgreSQL bağlantısında isteğe bağlı TLS ayarı
- Yerel medya hacmi ve özel S3 uyumlu nesne depolaması seçenekleri
- Gunicorn ve otomatik HTTPS sağlayan Caddy içeren üretim Compose tanımı
- SHA-256 manifestli PostgreSQL ve medya yedekleme aracı
- Onay ve bütünlük kontrolü gerektiren geri yükleme aracı
- Özel web ortamı kurulum, güncelleme ve işletim belgesi
- API erişim matrisi ve token yaşam döngüsü için otomatik testler

Gerçek alan adı, uzak sunucu ve nesne depolama sağlayıcısı henüz seçilmediği için
uzak dağıtım yapılmamıştır. Herhangi bir tüketici uygulama tanımlanmadığından
gerçek API tokenı da oluşturulmamıştır.

Docker Desktop ve WSL 2 kurulmuş, PostgreSQL 17 servisi Docker Compose ile
çalıştırılmıştır. Django sistem ve canlı dağıtım güvenlik kontrolleri hatasız
tamamlanmış; migration gerçek PostgreSQL veritabanına uygulanmış ve toplam
altmış bir test başarıyla geçmiştir. Yedekleme aracı gerçek yerel veritabanında
denenmiş, geri yükleme aracı veri değiştirmeyen önizleme modunda doğrulanmıştır.

## Yerel proje

Kullanıcının yeni ana proje klasörü:

```text
C:\Users\ozuto\Documents\Project\soru_havuzu
```

Klasör bir GitHub deposuna bağlanmış ve push edilmiştir. Yeni çalışmalar bu
yerel proje açıldıktan sonra yürütülmelidir.

## Sıradaki iş

`docs/ROADMAP.md` içindeki **Aşama 9 — PDF geçici içe aktarma**.

Çalışmaya başlamadan önce:

1. Depodaki gerçek dosyaları incele.
2. Tamamlanan aşamaların dosyalarının mevcut olup olmadığını doğrula.
3. Kullanıcı değişikliklerini koru.
4. PDF işlemlerini yapay zekâ veya OCR eklemeden yalnızca kesin gereksinimlerdeki
   deterministik kurallarla geliştir.
5. Geçici PDF kayıtlarına nihai `Q` kodu verme; yalnızca zorunlu alanları
   tamamlanan kayıtları soru havuzuna aktar.
6. PDF bağımlılıklarını son üretim imajına ekle ve dağıtım kontrollerini yenile.
7. Test sonuçlarını kullanıcıya bildir.

PDF yükleme ve geçici içe aktarma geliştirmeleri kullanıcı kararıyla bağımsız
**Aşama 9** olarak yol haritasının sonuna ertelenmiştir.
