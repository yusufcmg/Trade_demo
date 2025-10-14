# 🚀 GenetiX Production Deployment Guide v2.3.0

**Mevcut Sistemleri Etkilemeden Güvenli Deployment Planı**

---

## 📋 İçindekiler

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Safe Deployment Strategy](#safe-deployment-strategy)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Rollback Plan](#rollback-plan)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## ✅ Pre-Deployment Checklist

### Sunucu Hazırlığı

- [ ] **Sunucu Erişimi Doğrulama**
  ```bash
  ssh user@your-server-ip
  # Başarılı bağlantı kontrolü
  ```

- [ ] **Mevcut Sistemleri Tespit Et**
  ```bash
  # Çalışan servisleri listele
  systemctl list-units --type=service --state=running | grep -i trade
  
  # Kullanılan portları kontrol et
  sudo lsof -i -P -n | grep LISTEN
  
  # Python process'leri kontrol et
  ps aux | grep python
  ```

- [ ] **Disk Alanı Kontrolü**
  ```bash
  df -h
  # En az 2GB boş alan olmalı
  ```

- [ ] **Python Versiyonu**
  ```bash
  python3 --version
  # Python 3.8+ gerekli
  ```

### API ve Konfigürasyon

- [ ] **Binance Testnet API Keys**
  - API Key: `__________________`
  - Secret Key: `__________________`
  - Test edildi: [ ] Evet [ ] Hayır

- [ ] **Config Dosyası Hazırlığı**
  - `production/config/production_config.json` düzenlendi
  - API keys eklendi
  - Symbols listesi doğru (8 coin)
  - Portfolio weights ayarlandı
  - Risk limitleri set edildi

### Güvenlik

- [ ] **Firewall Kuralları**
  ```bash
  # Sadece gerekli portları aç
  sudo ufw allow 22/tcp      # SSH
  sudo ufw allow 8080/tcp    # Dashboard (opsiyonel)
  sudo ufw enable
  ```

- [ ] **.env Dosyası** (API keys için)
  ```bash
  # .env dosyası oluştur
  echo "BINANCE_API_KEY=your_key" > production/.env
  echo "BINANCE_SECRET_KEY=your_secret" >> production/.env
  chmod 600 production/.env
  ```

---

## 🛡️ Safe Deployment Strategy

### Port Isolation

**Problem:** Mevcut sistemler port 8080 kullanıyor olabilir  
**Çözüm:** Alternatif port kullan

```bash
# Port 8080 kullanımda mı kontrol et
lsof -i :8080

# Eğer kullanımdaysa, config'de farklı port ayarla
# production_config.json:
{
  "dashboard": {
    "port": 8081  # veya başka bir port
  }
}
```

### Process Isolation

**Strateji:** Her sistem kendi systemd service'i ile çalışır

```bash
# Mevcut servisler
systemctl list-units --type=service | grep trade

# Yeni servis adı: genetix-bot-v2 (çakışma yok!)
```

### Resource Limits

**CPU ve Memory limitleri** systemd service'de ayarlandı:

```ini
CPUQuota=80%       # Max %80 CPU kullan
MemoryLimit=2G     # Max 2GB RAM
```

### Rollback Support

Her deployment öncesi **otomatik backup** alınır:

```bash
# Backup lokasyonu
backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## 📦 Step-by-Step Deployment

### Adım 1: Deployment Script'i İndir

```bash
cd /home/ubuntu/genetix/evrimx/production/deploy

# Script'i executable yap
chmod +x safe_deploy.sh
```

### Adım 2: Safety Checks

```bash
./safe_deploy.sh check
```

**Expected Output:**
```
✅ Prerequisites OK
✅ Disk space OK (15GB available)
✅ Port 8080 is available
✅ Service check complete
✅ All safety checks passed ✓
```

**Eğer Port Kullanımdaysa:**
```bash
⚠️  Port 8080 is already in use
   Process using port: node (PID: 1234)
   
# Config'de portu değiştir:
nano production/config/production_config.json
# "dashboard_port": 8081 yap
```

### Adım 3: Initial Installation

```bash
./safe_deploy.sh install
```

**Bu komut:**
- ✅ Virtual environment oluşturur
- ✅ Dependencies kurar
- ✅ Directories hazırlar
- ✅ Systemd service configure eder
- ✅ Otomatik backup alır

**Beklenen süre:** 2-5 dakika

### Adım 4: Config Düzenleme

```bash
nano production/config/production_config.json
```

**Kritik Ayarlar:**
```json
{
  "api_credentials": {
    "api_key": "YOUR_ACTUAL_API_KEY",
    "secret_key": "YOUR_ACTUAL_SECRET_KEY"
  },
  "symbols_to_trade": [
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "ADAUSDT", "DOTUSDT", "LINKUSDT",
    "LTCUSDT", "SOLUSDT"
  ],
  "trading_config": {
    "max_positions": 5,
    "base_position_percent": 10.0,
    "leverage": 5
  },
  "risk_management": {
    "max_daily_loss_usd": 100.0,
    "max_daily_loss_percent": 5.0
  },
  "dashboard": {
    "port": 8080  # veya alternatif port
  }
}
```

### Adım 5: Test Mode (Dry Run)

**İlk çalıştırmayı DRY RUN ile yap:**

```bash
# Manuel dry run test
cd /home/ubuntu/genetix/evrimx
source venv/bin/activate
python3 production/production_bot_v2.py --dry-run --config production/config/production_config.json
```

**Kontrol Edilecekler:**
- ✅ API bağlantısı başarılı
- ✅ Bakiye okunuyor
- ✅ Market data yükleniyor
- ✅ Sinyal üretimi çalışıyor
- ✅ Hata yok

**Test süre:** 1-2 dakika, sonra Ctrl+C ile durdur.

### Adım 6: Service Başlatma

```bash
./safe_deploy.sh start
```

**Expected Output:**
```
▶ Starting GenetiX bot...
✅ Bot started successfully
   Status: active

🟢 Service: RUNNING
⏱️  Uptime: Mon 2025-10-14 01:30:15 UTC
🌐 Dashboard: http://localhost:8080
```

### Adım 7: İlk Doğrulama

```bash
# Status kontrol
./safe_deploy.sh status

# Log kontrol (realtime)
./safe_deploy.sh logs
```

---

## ✓ Post-Deployment Verification

### 1. Service Health Check (İlk 5 Dakika)

```bash
# Her 30 saniyede status kontrol
watch -n 30 './safe_deploy.sh status'
```

**Kontrol Edilecekler:**
- ✅ Service RUNNING durumunda
- ✅ Memory kullanımı normal (<500MB)
- ✅ CPU kullanımı makul (<50%)
- ✅ Log'da hata yok

### 2. Dashboard Erişimi

```bash
# Browser'da aç
http://your-server-ip:8080
```

**Görülmesi Gerekenler:**
- ✅ Real-time bakiye
- ✅ Position sayısı
- ✅ Daily P&L
- ✅ Son işlemler

### 3. Log Analysis (İlk 1 Saat)

```bash
# Error count
sudo journalctl -u genetix-bot-v2 | grep -i error | wc -l
# 0 olmalı (veya çok az)

# Warning count
sudo journalctl -u genetix-bot-v2 | grep -i warning | wc -l
# Az olmalı

# Trade activity
sudo journalctl -u genetix-bot-v2 | grep "Position OPENED\|Position CLOSED"
```

### 4. Performance Metrics (İlk 24 Saat)

**Metrics Dosyası:**
```bash
cat results/production/results_$(date +%Y%m%d).json | jq '{
  balance: .account_balance,
  daily_pnl: .daily_pnl,
  trades: .statistics.trades_closed,
  win_rate: .statistics.win_rate,
  positions: .open_positions
}'
```

**Beklenen Değerler:**
- Win Rate: >40%
- Drawdown: <15%
- Trades/day: 5-10
- Position sayısı: ≤5

---

## 🔄 Rollback Plan

### Hızlı Rollback (Acil Durum)

```bash
# Bot'u durdur
./safe_deploy.sh stop

# Rollback yap
./safe_deploy.sh rollback

# Eski versiyonu başlat
sudo systemctl start genetix-bot  # (eski servis adı)
```

### Manuel Rollback

```bash
# 1. Yeni bot'u durdur
./safe_deploy.sh stop

# 2. Backup'ı restore et
cd /home/ubuntu/genetix/evrimx
tar -xzf backups/backup_20251014_013000.tar.gz

# 3. Eski config'i geri yükle
cp backups/backup_20251014_013000/production/config/production_config.json production/config/

# 4. Servisi devre dışı bırak
sudo systemctl disable genetix-bot-v2

# 5. Eski sistemi başlat (varsa)
# ... eski sistem restart komutları
```

### Rollback Trigger Kriterleri

**Otomatik rollback gerekir eğer:**
- ❌ Service 3 kez arka arkaya crash
- ❌ İlk 1 saatte >5% kayıp
- ❌ Memory leak (>1.5GB kullanım)
- ❌ API bağlantısı sürekli kopuyor

---

## 📊 Monitoring & Maintenance

### Daily Checks

**Her gün 09:00'da:**

```bash
./safe_deploy.sh status
```

**Kontrol Listesi:**
- [ ] Service UP
- [ ] Daily P&L makul (±5%)
- [ ] No critical errors
- [ ] Disk space OK

### Weekly Maintenance

**Her Pazar:**

```bash
# Log rotation (otomatik)
# Results backup
cp results/production/results_$(date +%Y%m%d).json backups/weekly/

# Performance review
cat results/production/results_$(date +%Y%m%d).json | jq .statistics
```

### Monthly Tasks

- [ ] Config review (risk limitleri hala uygun mu?)
- [ ] Strategy performance analizi
- [ ] Log cleanup (>30 gün eski loglar)
- [ ] Backup cleanup (>90 gün eski backuplar)

### Alerting Setup (Opsiyonel)

**Telegram bildirimleri:**

```json
// production_config.json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "notifications": {
      "trade_opened": true,
      "trade_closed": true,
      "daily_summary": true,
      "error_alerts": true
    }
  }
}
```

---

## 🆘 Troubleshooting

### Service Başlamıyor

```bash
# Detaylı log
sudo journalctl -u genetix-bot-v2 -n 100 --no-pager

# Manuel test
cd /home/ubuntu/genetix/evrimx
source venv/bin/activate
python3 production/production_bot_v2.py --dry-run
```

### API Errors

```bash
# API connectivity test
curl -X GET "https://testnet.binancefuture.com/fapi/v1/ping"
# Response: {}

# API key test
curl -H "X-MBX-APIKEY: YOUR_API_KEY" \
  "https://testnet.binancefuture.com/fapi/v2/balance"
```

### Memory Issues

```bash
# Memory kullanımı
ps aux | grep production_bot | awk '{print $4"%", $6/1024"MB"}'

# Eğer >1GB ise restart
./safe_deploy.sh restart
```

### Dashboard Erişilemiyor

```bash
# Port kontrolü
lsof -i :8080

# Firewall kontrolü
sudo ufw status

# Port aç (gerekirse)
sudo ufw allow 8080/tcp
```

---

## 📞 Support & Resources

### Documentation
- **Production README:** `production/README.md`
- **Config Reference:** `production/config/README.md`
- **API Docs:** `docs/API.md`

### Logs
- **Bot Logs:** `logs/production/bot_YYYYMMDD.log`
- **Trade Logs:** `logs/production/trades_YYYYMMDD.log`
- **Error Logs:** `logs/production/errors_YYYYMMDD.log`
- **System Logs:** `journalctl -u genetix-bot-v2`

### Files
- **Results:** `results/production/results_YYYYMMDD.json`
- **Backups:** `backups/backup_YYYYMMDD_HHMMSS.tar.gz`
- **Config:** `production/config/production_config.json`

### Quick Commands Reference

```bash
# Check system
./safe_deploy.sh check

# Install
./safe_deploy.sh install

# Start
./safe_deploy.sh start

# Stop
./safe_deploy.sh stop

# Restart
./safe_deploy.sh restart

# Status
./safe_deploy.sh status

# Logs
./safe_deploy.sh logs

# Rollback
./safe_deploy.sh rollback
```

---

## ✅ Final Checklist

**Deployment tamamlandı, son kontroller:**

- [ ] Service running (`systemctl is-active genetix-bot-v2`)
- [ ] Dashboard accessible (http://server-ip:8080)
- [ ] Logs normal (no critical errors)
- [ ] First trade executed successfully
- [ ] API keys working
- [ ] Risk limits configured
- [ ] Backup created
- [ ] Monitoring setup
- [ ] Telegram alerts (opsiyonel)
- [ ] Documentation reviewed

**🎉 Deployment Başarılı!**

---

**Version:** 2.3.0  
**Date:** 2025-10-14  
**Author:** Yusuf Çekmegil  
**License:** MIT
