# Soru Havuzu ve Sınıflandırma Sistemi — Kesin Gereksinimler

## 1. Amaç ve kapsam

Sistem, 8. sınıf matematik sorularını depolamak, düzenlemek, sınıflandırmak,
aramak, filtrelemek ve başka projelere API üzerinden sunmak için kurulacaktır.

- Başlangıç havuzu tek konu ve yaklaşık 1.000 sorudan oluşacaktır.
- İleride yeni konular eklenerek havuz büyüyecektir.
- İlk sürüm yerel bilgisayarda ve tek kullanıcıyla çalışacaktır.
- Daha sonra özel ve şifreli bir web ortamına taşınacaktır.
- Sistem yapay zekâ entegrasyonu içermeyecektir.

## 2. Sınıflandırma hiyerarşisi

Temel sıra şöyledir:

1. Konu
2. Konuya bağlı kazanımlar
3. Sorular
4. Sorunun çözüm biçimini tanımlayan soru tipi

Kurallar:

- Bir sorunun bir ana konusu bulunur.
- Bir soru gerektiğinde birden fazla ikincil konuya bağlanabilir.
- Bir soru birden fazla kazanıma bağlanabilir.
- Bir soru yalnızca bir soru tipine bağlanabilir.
- Soru tipi, sorunun kazanımlarını belirlemez veya değiştirmez.

## 3. Soru yapısı

Her soru:

- `Q000001` biçiminde değişmeyen ve tekrar kullanılmayan görünür bir koda sahip olur.
- Dört şıklıdır: A, B, C ve D.
- Yalnızca bir doğru cevabı vardır.
- Orijinal soru görselini saklar.
- Elle girilen LaTeX soru metnini saklar.
- A, B, C ve D şıklarını ayrı LaTeX alanlarında saklar.
- Ana konu, ikincil konular ve kazanımlarla ilişkilendirilir.
- Kaynak PDF adı, sayfa numarası ve kaynak soru numarasını saklar.
- Oluşturulma ve güncellenme zamanlarını saklar.

## 4. Havuza giriş için zorunlu alanlar

Bir soru nihai soru havuzuna girmeden önce aşağıdaki alanlar tamamlanmalıdır:

- Orijinal soru görseli
- Ana konu
- En az bir kazanım
- LaTeX soru metni
- LaTeX A, B, C ve D şıkları
- Doğru cevap
- Kaynak bilgileri

Aşağıdaki alanlar havuza girdikten sonra tamamlanabilir:

- Soru tipi
- 1–5 arasında zorluk düzeyi
- Çözüm

## 5. Çözüm

- Sistem çözüm üretmez ve çözümün doğruluğunu kontrol etmez.
- Çözüm kullanıcı tarafından düz metin veya LaTeX olarak girilir.
- Çözümü olmayan soru `çözüm bekliyor` durumunda tutulabilir.

## 6. Soru tipi

Soru tipi kullanıcı tarafından elle seçilir veya oluşturulur.

Her soru tipi şunları içerir:

- Değişmeyen `QT0001` biçiminde kod
- Ad
- Kısa açıklama
- Çözüm yöntemi veya işlem adımları
- Ayırt edici sınıflandırma ölçütleri
- Örnek sorular

Soru tipi olmayan soru `soru tipi bekliyor` durumunda tutulabilir. Tip tanımı
veya soru-tip ataması değiştirildiğinde eski değer saklanmaz; yeni değer mevcut
kaydın üzerine yazılır.

## 7. Zorluk düzeyi

- Ölçek 1–5 arasındadır.
- Kullanıcı tarafından elle girilir.
- Sistem tahmin veya öneri yapmaz.
- Eksikse soru `zorluk bekliyor` durumunda tutulabilir.

## 8. Tek soru yükleme

Kullanıcı:

1. Soru görselini yükler.
2. Ana konu ve varsa ikincil konuları seçer.
3. Bir veya daha fazla kazanım seçer.
4. Soru metni ve dört şıkkı LaTeX olarak girer.
5. Doğru cevabı belirler.
6. Kaynak bilgilerini girer.
7. İsterse çözüm, soru tipi ve zorluk düzeyini ekler.
8. Zorunlu bilgiler tamamlandığında soruyu havuza kaydeder.

## 9. PDF içe aktarma

> Uygulama sırası kararı: Bu bölümdeki özellikler diğer geliştirme
> aşamalarından ayrılmış ve yol haritasının son aşamasına ertelenmiştir.

PDF işlemleri yapay zekâ kullanmadan iki aşamada gerçekleştirilir.

### Geçici içe aktarma alanı

1. PDF yüklenir.
2. Sorular; soru numaraları, boşluklar ve sayfa düzeni gibi kurallarla otomatik
   ayrılmaya çalışılır.
3. Kullanıcı soru kırpma alanlarını kontrol edip düzeltebilir.
4. PDF'de gerçek metin katmanı varsa sondaki cevap anahtarı otomatik okunmaya
   çalışılır.
5. Cevap anahtarı görüntüyse cevaplar elle girilir; OCR kullanılmaz.
6. Kullanıcı her soru için LaTeX içeriğini elle yazar.
7. Konu ve kazanımlar tek tek seçilebilir veya `soru no → kazanımlar` listesi
   topluca yapıştırılabilir.

### Nihai havuza aktarma

- Zorunlu alanları tamamlanan sorular nihai havuza aktarılır.
- Eksik kayıtlar geçici alanda kalır.
- Geçici kayıtlara kalıcı `Q` kodu verilmez.

## 10. Aynı soru kontrolü

- Anlamsal benzerlik analizi yapılmaz.
- Yalnızca birebir aynı görselin yeniden yüklenmesi dosya özeti/hash üzerinden
  tespit edilir.
- Sistem uyarı verir; kaydetme kararı kullanıcıya bırakılır.

## 11. Arama ve filtreleme

Sorular şu alanlarla aranabilir ve filtrelenebilir:

- Soru kodu
- Soru metni
- Ana ve ikincil konular
- Kazanımlar
- Soru tipi
- Zorluk düzeyi
- Kaynak PDF
- Kaynak soru numarası
- Tamamlanma durumu

Birden fazla kazanım seçildiğinde hem `herhangi birini içerir` hem de `tamamını
içerir` seçenekleri desteklenir.

## 12. Çalışma listeleri

- Soru tipi bekleyenler
- Zorluk bekleyenler
- Çözüm bekleyenler
- Tamamlananlar
- Arşivlenenler
- Eksik PDF içe aktarma kayıtları

## 13. Arşivleme ve silme

- Sorular geri getirilebilir biçimde arşivlenebilir.
- Kalıcı silme ayrı ve açık bir işlemdir.
- Silinen veya arşivlenen soruların `Q` kodları başka sorulara verilmez.

## 14. API ve başka projeye bağlanma

Başka projeler PostgreSQL veritabanına doğrudan bağlanmaz. Sürümlendirilmiş ve
yetkilendirilmiş REST API kullanır.

- API kökü `/api/v1/` olur.
- Filtrelenmiş soru listesi alınabilir.
- Tek veya birden fazla rastgele soru alınabilir.
- Konu, kazanım, soru tipi ve 1–5 zorluk düzeyi filtrelenebilir.
- Çoklu kazanım sorgularında `any` ve `all` mantıkları desteklenir.
- Daha önce kullanılmış soru kodları sorgudan hariç tutulabilir.
- Eksik ve arşivlenmiş sorular varsayılan olarak döndürülmez.
- Soru verisi döndüren tüm uç noktalar token gerektirir.
- Öğrenci/istemci rolündeki tokenın yanıtında doğru cevap ve çözüm gizlenir;
  eksik veya arşivlenmiş kayıtları dahil etmesine izin verilmez.
- Yetkili sunucu rolündeki token doğru cevap ve çözüme erişebilir; eksik veya
  arşivlenmiş kayıtları açıkça isteyebilir.
- Her tüketici uygulama ayrı entegrasyon hesabı ve token kullanır.
- Sağlık kontrolü, API kökü ve şema hassas soru verisi içermediği için açık
  tutulabilir.
- Canlı ortamda API yalnızca HTTPS üzerinden sunulur ve tokenlar kaynak koddan
  ayrı bir sır olarak saklanır.
- API sürümü değiştiğinde mevcut istemciler mümkün olduğunca bozulmaz.
- API davranışları otomatik testlerle doğrulanır.

Örnek hedef sorgu:

```http
GET /api/v1/questions/random
    ?outcomes=M.8.1.3.1,M.8.1.3.2
    &outcome_match=all
    &question_type=QT0004
    &difficulty=3
    &exclude=Q000012,Q000018
    &count=5
```

## 15. Teknik yapı

- Django
- PostgreSQL
- Django REST Framework
- KaTeX
- PyMuPDF
- Yapay zekâsız sayfa düzeni işlemleri için OpenCV
- Docker Compose
- İlk aşamada yerel dosya sistemi
- İnternete geçildiğinde uygun nesne dosya depolaması
