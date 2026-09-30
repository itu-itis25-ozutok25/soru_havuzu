# Kesinleşmiş Kararlar

1. SQLite ile başlanmayacak; doğrudan PostgreSQL kullanılacak.
2. Sistem yalnızca 8. sınıf matematikle başlayacak.
3. İlk sürüm tek kullanıcılıdır.
4. İlk kullanım yerel, sonraki kullanım özel web ortamıdır.
5. Sistem yapay zekâ entegrasyonu içermeyecek.
6. Soru metni ve şıkların LaTeX içeriği elle girilecek.
7. PDF soru ayırma yalnızca deterministik sayfa düzeni kurallarıyla denenecek.
8. Taranmış cevap anahtarına OCR uygulanmayacak; cevaplar elle girilecek.
9. Soru tipi ve zorluk elle belirlenecek.
10. Çözüm üretilmeyecek veya doğrulanmayacak; yalnızca saklanacak.
11. Kazanımlar konuların altında yer alacak.
12. Bir soru birden fazla kazanıma bağlanabilir.
13. Bir soru bir ana ve birden fazla ikincil konuya bağlanabilir.
14. Bir soru yalnızca bir soru tipine bağlanabilir.
15. Geçmiş sınıflandırma değerleri tutulmayacak; değişiklik mevcut kaydın üzerine yazılacak.
16. Tamamen aynı görsel tekrar yüklenirse uyarı verilecek.
17. Arşivleme ve kalıcı silme ayrı işlemler olacak.
18. Başka projeler sisteme doğrudan veritabanıyla değil REST API üzerinden bağlanacak.
19. Öğrenci API yanıtında doğru cevap ve çözüm bulunmayacak.
20. Yetkili sunucu doğru cevap ve çözüme erişebilecek.
21. PDF yükleme ve geçici içe aktarma özellikleri diğer aşamalardan ayrı olarak
    yol haritasının son aşamasında geliştirilecek.
22. Soru verisi döndüren API uçları anonim erişime kapalı olacak ve token
    gerektirecek.
23. Öğrenci/istemci ve güvenilir sunucu tokenları ayrı roller kullanacak; yalnızca
    güvenilir sunucu doğru cevap, çözüm, eksik ve arşivlenmiş kayıtlara
    erişebilecek.
24. Her tüketici uygulama ayrı entegrasyon hesabı ve token kullanacak; tokenlar
    kaynak kodda tutulmayacak ve canlı ortamda yalnızca HTTPS ile taşınacak.
25. Sağlık kontrolü, API kökü ve OpenAPI şeması hassas veri içermediği sürece
    kimlik doğrulaması olmadan erişilebilir olacak.
