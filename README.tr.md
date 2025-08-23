# osmank3-betikleri

Bu depo, çeşitli görevleri otomatikleştirmek ve basitleştirmek için bir betik koleksiyonu içerir.

## Betikler

### disk_sync.sh

Bu betik, bir kaynak dizini bir yapılandırma dosyasında tanımlanan bir disk bölümüne yedekler. Eşzamanlı senkronizasyon işlemleriyle bile güvenli bir şekilde ayırmayı sağlamak için bir bağlama sayacı kullanır.

**Kullanım:**

```bash
/bin/bash disk_sync.sh /kaynak/dizin
```

### exiv2retimer.py

Bu betik, fotoğrafların EXIF oluşturma tarihini belirli bir zaman farkına göre artırır veya azaltır. Ayrıca dosyaları oluşturma zamanlarına göre yeniden adlandırabilir ve yıl, ay ve güne göre bir dizin yapısına arşivleyebilir.

**Bağımlılıklar:**

*   pyexiv2

**Kullanım:**

```bash
python exiv2retimer.py [SEÇENEKLER] dosya veya dizin
```

### gexiv2retimer.py

`exiv2retimer.py` ile aynı işlevselliğe sahiptir, ancak `GExiv2` kitaplığını kullanır.

**Bağımlılıklar:**

*   Gexiv2

**Kullanım:**

```bash
python gexiv2retimer.py [SEÇENEKLER] dosya veya dizin
```

### mountCasper.py

Bu betik, canlı bir Linux dağıtımında kalıcı depolama için kullanılan bir `casper-rw` dosyasını bağlar ve ayırır.

**Kullanım:**

```bash
# Bağlamak için
python mountCasper.py mount

# Ayırmak için
python mountCasper.py umount
```

### prephome.py

Bu betik, bir kullanıcının ev dizinini farklı bir Linux dağıtımında kullanıma hazırlar. Kullanıcının dosyalarını yeni bir dizin yapısına taşıyabilir veya bağlayabilir.

**Kullanım:**

```bash
python prephome.py [KOMUT] [SEÇENEKLER]
```

### renamer.py

Bu betik, bir dizindeki resim dosyalarını oluşturulma tarihlerine göre yeniden adlandırır.

**Bağımlılıklar:**

*   kaa.metadata

**Kullanım:**

```bash
python renamer.py DİZİN
```

### retimesrt.py

Bu betik, bir SRT altyazı dosyasının zamanlamasını düzenler. Tüm altyazıların zamanını veya yalnızca belirli bir zamandan sonraki veya önceki altyazıların zamanını artırabilir veya azaltabilir. Ayrıca altyazı silebilir veya ekleyebilir.

**Kullanım:**

```bash
python retimesrt.py [SEÇENEKLER] dosya
```
