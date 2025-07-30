# XML Dönüştürücü ve FTP Yükleyici

Bu proje, XML dosyalarını dönüştürür ve FTP ile hosting sunucunuza yükler. GitHub Actions ile 6 saatte bir otomatik olarak çalışır.

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

### Yerel Çalıştırma

1. FTP bilgilerinizi ayarlayın (isteğe bağlı):
```python
ftp_config = {
    'host': 'your-ftp-server.com',  # FTP sunucu adresi
    'port': 21,                     # FTP port (genellikle 21)
    'username': 'your-username',    # FTP kullanıcı adı
    'password': 'your-password',    # FTP şifre
    'remote_filename': 'baciodeneme.xml'  # Sunucuda kaydedilecek dosya adı
}
```

2. Programı çalıştırın:
```bash
python xml_converter.py
```

### GitHub Actions ile Otomatik Çalıştırma

1. **GitHub Secrets Ayarlayın**:
   - Repository'nizin Settings > Secrets and variables > Actions bölümüne gidin
   - Aşağıdaki secrets'ları ekleyin:
     - `FTP_HOST`: FTP sunucu adresi
     - `FTP_PORT`: FTP port (genellikle 21)
     - `FTP_USERNAME`: FTP kullanıcı adı
     - `FTP_PASSWORD`: FTP şifre
     - `FTP_REMOTE_FILENAME`: Sunucuda kaydedilecek dosya yolu

2. **Workflow Otomatik Çalışır**:
   - Her 6 saatte bir otomatik olarak çalışır
   - Manuel çalıştırmak için Actions sekmesinden "Run workflow" butonunu kullanın

## Özellikler

- XML dosyasını belirtilen URL'den indirir
- XML formatını istenen yapıya dönüştürür
- FTP ile hosting sunucunuza yükler
- FTP başarısız olursa otomatik olarak locale kaydeder
- GitHub Actions ile 6 saatte bir otomatik çalışır
- Hata yönetimi ve güvenlik önlemleri

## Güvenlik Notları

- FTP şifrenizi kod içinde saklamayın
- GitHub Secrets kullanarak güvenli şekilde saklayın
- Güvenli FTP (SFTP) kullanmanız önerilir

## Hata Durumları

- FTP bağlantı hatası durumunda dosya locale kaydedilir
- Tüm hatalar konsola yazdırılır
- Geçici dosyalar otomatik olarak temizlenir
- GitHub Actions logları 7 gün saklanır 