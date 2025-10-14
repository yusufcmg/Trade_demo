# 📁 Production Klasör Yapısı

```
production/
├── README.md                     # Ana dokümantasyon
├── STRUCTURE.md                  # Bu dosya - klasör yapısı
├── production_bot.py             # Ana production bot
├── .env.example                  # Environment variables örneği
│
├── config/                       # Konfigürasyon dosyaları
│   └── production_config.json    # Production config şablonu
│
└── deploy/                       # Deployment araçları
    ├── deploy.sh                 # Otomatik deployment script
    └── genetix-bot.service       # Systemd service dosyası
```

## 📋 Dosya Açıklamaları

### Ana Dosyalar

#### `production_bot.py`
- **İşlev:** 7/24 çalışan ana trading bot
- **Özellikler:**
  - Async trading loop
  - Graceful shutdown
  - Risk yönetimi
  - Health checks
  - Dashboard entegrasyonu
  - Telegram bildirimleri

#### `README.md`
- **İşlev:** Detaylı kullanım kılavuzu
- **İçerik:**
  - Kurulum adımları
  - Konfigürasyon
  - Kullanım örnekleri
  - Monitoring
  - Sorun giderme

#### `.env.example`
- **İşlev:** Environment variables şablonu
- **Kullanım:**
  ```bash
  cp .env.example .env
  nano .env  # API keys ekle
  ```

### config/

#### `production_config.json`
- **İşlev:** Bot konfigürasyonu
- **Ayarlar:**
  - API credentials
  - Trading semboller
  - Risk parametreleri
  - Strategy ayarları
  - Monitoring seçenekleri

### deploy/

#### `deploy.sh`
- **İşlev:** Otomatik deployment
- **Komutlar:**
  ```bash
  ./deploy.sh install   # İlk kurulum
  ./deploy.sh start     # Bot'u başlat
  ./deploy.sh stop      # Bot'u durdur
  ./deploy.sh restart   # Yeniden başlat
  ./deploy.sh status    # Durum
  ./deploy.sh logs      # Log'ları izle
  ```

#### `genetix-bot.service`
- **İşlev:** Systemd service tanımı
- **Özellikler:**
  - Otomatik başlatma
  - Auto-restart on failure
  - Resource limits
  - Security hardening

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
cd production
chmod +x deploy/deploy.sh
./deploy/deploy.sh install
```

### 2. Konfigürasyon
```bash
# Environment variables
cp .env.example .env
nano .env

# Bot config
nano config/production_config.json
```

### 3. Başlatma
```bash
./deploy/deploy.sh start
./deploy/deploy.sh logs
```

## 📊 Monitoring

### Dashboard
```
http://YOUR_SERVER:8080/dashboard.html
```

### Log Dosyaları
```
logs/production/production_bot_*.log
```

### Sonuç Dosyaları
```
results/production/results_*.json
```

### Systemd Status
```bash
sudo systemctl status genetix-bot
sudo journalctl -u genetix-bot -f
```

## 🔧 Bakım

### Güncelleme
```bash
git pull
./deploy/deploy.sh update
./deploy/deploy.sh restart
```

### Log Temizleme
```bash
# Otomatik: logrotate yapılandırması
# Manuel:
find logs/production -name "*.log" -mtime +30 -delete
```

### Backup
```bash
# Config
cp config/production_config.json config/backup_$(date +%Y%m%d).json

# Sonuçlar
tar -czf results_backup_$(date +%Y%m%d).tar.gz results/production/
```

## ⚠️ Güvenlik

- ✅ `.env` dosyasını **asla** git'e commit etmeyin
- ✅ `config/production_config.json` içindeki API keys'i `.env`'e taşıyın
- ✅ Firewall kurallarını ayarlayın
- ✅ SSH key authentication kullanın
- ✅ Düzenli backup alın

## 📞 Destek

Sorun yaşarsanız:
1. `README.md` dosyasını okuyun
2. Log dosyalarını kontrol edin
3. `./deploy/deploy.sh status` çalıştırın
4. GitHub Issues'a yazın
