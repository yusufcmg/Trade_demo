# 🚀 Frankfurt Sunucu Deployment Rehberi

## 📊 Sunucu Durumu Analizi

**Sunucu**: frankfurt-sunucu (161.35.76.27)  
**Kullanıcı**: yusuf  
**OS**: Ubuntu (systemd tabanlı)

### Kullanılan Portlar
```
✅ Port 22:   SSH (sshd)
✅ Port 53:   DNS (systemd-resolved) - local only
✅ Port 80:   Nginx (web server)
✅ Port 443:  Nginx (SSL)
✅ Port 3000: Docker container
✅ Port 5000: Gunicorn (Flask app - 5 workers)
✅ Port 5432: PostgreSQL - local only
```

### Boş Portlar
```
✅ Port 8080: AVAILABLE for Trading Bot Dashboard
✅ Port 8081-8090: Available (alternatives)
```

### Çalışan Servisler
- ✅ Nginx (web server)
- ✅ PostgreSQL@14-main
- ✅ Docker daemon
- ✅ SSH server
- ✅ Containerd
- ✅ DigitalOcean monitoring

### Önemli Notlar
1. **Port 8080**: Tamamen boş, trading bot dashboard için ideal
2. **Gunicorn**: Port 5000'de Flask app çalışıyor (çakışma yok)
3. **Nginx**: Reverse proxy olarak kullanılabilir (opsiyonel)
4. **Systemd**: Servis yönetimi için mevcut

---

## 🎯 Deployment Stratejisi

### Güvenli Deployment Prensiplerim
1. ✅ **Mevcut servislere dokunma** (Gunicorn, Nginx, PostgreSQL korunacak)
2. ✅ **Port izolasyonu** (8080 kullanacağız, çakışma yok)
3. ✅ **Systemd service** (genetix-bot-v2 - benzersiz isim)
4. ✅ **Log rotation** (disk dolmasını önlemek)
5. ✅ **Auto-restart** (crash durumunda otomatik başlatma)
6. ✅ **Graceful shutdown** (pozisyonlar korunacak)

---

## 📦 Deployment Adımları

### 1️⃣ Sunucuya Bağlan
```bash
ssh yusuf@161.35.76.27
```

### 2️⃣ Repository'yi Klonla
```bash
cd ~
git clone https://github.com/yusufcmg/Trade_demo.git
cd Trade_demo
```

### 3️⃣ Python Virtual Environment Oluştur
```bash
# Python 3 kurulu mu kontrol
python3 --version

# Virtual environment oluştur
python3 -m venv venv

# Aktifleştir
source venv/bin/activate
```

### 4️⃣ Bağımlılıkları Kur
```bash
# Pip upgrade
pip install --upgrade pip

# Requirements yükle
pip install -r requirements.txt

# TA-Lib binary (Ubuntu için)
sudo apt-get update
sudo apt-get install -y python3-dev build-essential wget

# TA-Lib source'dan kurulum (gerekirse)
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ~/Trade_demo
pip install TA-Lib
```

### 5️⃣ Test Run (Dry Mode)
```bash
# Konfigürasyon kontrolü
cat config/production_config.json | jq .api_credentials

# Dry run ile test
python production_bot_v2.py --dry-run

# Ctrl+C ile durdur
```

**Beklenen Çıktı:**
```
================================================================================
🤖 GenetiX Production Trading Bot v2.3.0
================================================================================
Strategy: Multi-Timeframe Validated (89.54% consistency)
Mode:     🧪 DRY RUN
Symbols:  8 coins (BTC, ETH, BNB, ADA, DOT, LINK, LTC, SOL)
...
🌐 Dashboard server started on port 8080
📊 Dashboard: http://localhost:8080
💰 Account Balance: $10,000.00 USDT
✅ Bot initialized successfully!
```

### 6️⃣ Dashboard Kontrolü
Yeni terminal'de:
```bash
curl http://localhost:8080/api/stats
```

**Beklenen Response:**
```json
{
  "balance": 10000.0,
  "daily_pnl": 0.0,
  "total_pnl": 0.0,
  "positions": 0,
  "trades": 0,
  "win_rate": 0.0,
  "status": "running"
}
```

### 7️⃣ Systemd Service Kurulumu

#### A) Service File Hazırla
```bash
cd deploy

# Service file'ı düzenle (path'leri güncelle)
nano genetix-bot.service
```

**Güncellenecek Satırlar:**
```ini
[Service]
WorkingDirectory=/home/yusuf/Trade_demo
Environment="PATH=/home/yusuf/Trade_demo/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/yusuf/Trade_demo/venv/bin/python production_bot_v2.py
User=yusuf
Group=yusuf
```

#### B) Service Kur ve Başlat
```bash
# safe_deploy.sh ile otomatik kurulum
chmod +x safe_deploy.sh
sudo ./safe_deploy.sh install
sudo ./safe_deploy.sh deploy_service
sudo ./safe_deploy.sh start
```

**VEYA Manuel Kurulum:**
```bash
# Service file'ı kopyala
sudo cp genetix-bot.service /etc/systemd/system/genetix-bot-v2.service

# Systemd reload
sudo systemctl daemon-reload

# Service enable (boot'ta başlasın)
sudo systemctl enable genetix-bot-v2

# Service başlat
sudo systemctl start genetix-bot-v2

# Durum kontrol
sudo systemctl status genetix-bot-v2
```

### 8️⃣ Doğrulama

#### Log Kontrolü
```bash
# Real-time logs
sudo journalctl -u genetix-bot-v2 -f

# Son 100 satır
sudo journalctl -u genetix-bot-v2 -n 100

# Today's logs
sudo journalctl -u genetix-bot-v2 --since today

# Bot log dosyaları
tail -f ~/Trade_demo/logs/production/bot_$(date +%Y%m%d).log
```

#### Dashboard Erişimi

**Local Test:**
```bash
curl http://localhost:8080/api/stats
curl http://localhost:8080/api/positions
curl http://localhost:8080/api/activity
```

**External Access (opsiyonel):**
Nginx reverse proxy ile:
```nginx
# /etc/nginx/sites-available/trading-bot
server {
    listen 80;
    server_name trade.yourdomain.com;  # veya IP
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Port Kontrolü
```bash
sudo lsof -i :8080
```

**Beklenen Çıktı:**
```
COMMAND     PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3   12345  yusuf    6u  IPv4 123456      0t0  TCP *:8080 (LISTEN)
```

#### Process Kontrolü
```bash
ps aux | grep production_bot_v2
```

---

## 🔧 Systemd Komutları

### Temel Komutlar
```bash
# Başlat
sudo systemctl start genetix-bot-v2

# Durdur
sudo systemctl stop genetix-bot-v2

# Yeniden başlat
sudo systemctl restart genetix-bot-v2

# Durum
sudo systemctl status genetix-bot-v2

# Loglar
sudo journalctl -u genetix-bot-v2 -f
```

### Safe Deploy Script
```bash
cd ~/Trade_demo/deploy

# Kurulum
sudo ./safe_deploy.sh install

# Service deploy
sudo ./safe_deploy.sh deploy_service

# Başlat
sudo ./safe_deploy.sh start

# Durdur
sudo ./safe_deploy.sh stop

# Restart
sudo ./safe_deploy.sh restart

# Durum
sudo ./safe_deploy.sh status

# Loglar
sudo ./safe_deploy.sh logs

# Rollback
sudo ./safe_deploy.sh rollback
```

---

## 📊 İzleme ve Monitoring

### Dashboard
```bash
# Web browser'da aç:
http://161.35.76.27:8080

# veya localhost'tan:
http://localhost:8080
```

**Dashboard Özellikleri:**
- 💰 Account Balance (real-time)
- 📊 Daily P&L
- 💵 Total P&L
- 📍 Open Positions (live)
- 📝 Total Trades
- ✅ Win Rate
- 🔴 Bot Status
- 📋 Activity Log (last 10 events)

### Log Dosyaları
```bash
# Ana bot log
tail -f ~/Trade_demo/logs/production/bot_$(date +%Y%m%d).log

# Trade log
tail -f ~/Trade_demo/logs/production/trades_$(date +%Y%m%d).log

# Error log
tail -f ~/Trade_demo/logs/production/errors_$(date +%Y%m%d).log
```

### Systemd Journal
```bash
# Real-time
sudo journalctl -u genetix-bot-v2 -f

# Bugünkü loglar
sudo journalctl -u genetix-bot-v2 --since today

# Son 1 saat
sudo journalctl -u genetix-bot-v2 --since "1 hour ago"

# Sadece ERROR
sudo journalctl -u genetix-bot-v2 -p err
```

### Resource Monitoring
```bash
# CPU ve Memory kullanımı
systemctl status genetix-bot-v2

# Detaylı process info
ps aux | grep production_bot_v2

# Resource limits
systemctl show genetix-bot-v2 | grep -i limit
```

---

## ⚠️ Troubleshooting

### Bot Başlamıyor

**Kontrol 1: Service Status**
```bash
sudo systemctl status genetix-bot-v2
```

**Kontrol 2: Logs**
```bash
sudo journalctl -u genetix-bot-v2 -n 50
```

**Kontrol 3: Python Path**
```bash
# Virtual env aktif mi?
which python
# Beklenen: /home/yusuf/Trade_demo/venv/bin/python

# Service file path'i doğru mu?
cat /etc/systemd/system/genetix-bot-v2.service | grep ExecStart
```

**Kontrol 4: Permissions**
```bash
# Log directory yazılabilir mi?
ls -la ~/Trade_demo/logs/production/

# Config okunabilir mi?
cat ~/Trade_demo/config/production_config.json
```

**Çözüm:**
```bash
# Service reload
sudo systemctl daemon-reload

# Restart
sudo systemctl restart genetix-bot-v2
```

### Port 8080 Meşgul

**Kontrol:**
```bash
sudo lsof -i :8080
```

**Process'i öldür:**
```bash
sudo kill -9 <PID>
```

**Alternatif Port Kullan:**
```bash
# production_config.json'u düzenle
nano ~/Trade_demo/config/production_config.json

# "dashboard_port" değerini değiştir (8081, 8082, etc.)
```

### Dashboard Açılmıyor

**Kontrol 1: Flask Running?**
```bash
curl http://localhost:8080/api/stats
```

**Kontrol 2: Firewall**
```bash
# UFW status
sudo ufw status

# Port 8080 izin ver
sudo ufw allow 8080/tcp
```

**Kontrol 3: Bot Logs**
```bash
tail -f ~/Trade_demo/logs/production/bot_$(date +%Y%m%d).log | grep Dashboard
```

### API Connection Error

**Kontrol 1: API Credentials**
```bash
cat ~/Trade_demo/config/production_config.json | jq .api_credentials
```

**Kontrol 2: Testnet Erişimi**
```bash
curl https://testnet.binancefuture.com/fapi/v1/ping
```

**Beklenen:** `{}`

**Kontrol 3: Internet Connection**
```bash
ping -c 4 8.8.8.8
```

### Yüksek Memory Kullanımı

**Kontrol:**
```bash
ps aux | grep production_bot_v2
```

**Restart:**
```bash
sudo systemctl restart genetix-bot-v2
```

**Memory Limit Ayarla:**
```bash
sudo nano /etc/systemd/system/genetix-bot-v2.service

# Ekle:
[Service]
MemoryMax=2G

# Reload
sudo systemctl daemon-reload
sudo systemctl restart genetix-bot-v2
```

---

## 🔄 Güncelleme (Update)

### Git Pull ile Güncelleme
```bash
cd ~/Trade_demo

# Bot'u durdur
sudo systemctl stop genetix-bot-v2

# Güncellemeleri çek
git pull origin main

# Bağımlılıkları güncelle (gerekirse)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Bot'u başlat
sudo systemctl start genetix-bot-v2

# Durumu kontrol
sudo systemctl status genetix-bot-v2
```

### Safe Deploy ile Güncelleme
```bash
cd ~/Trade_demo/deploy
sudo ./safe_deploy.sh update
```

---

## 🛡️ Güvenlik

### Firewall Ayarları
```bash
# Sadece gerekli portları aç
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (Nginx)
sudo ufw allow 443/tcp   # HTTPS (Nginx)
sudo ufw allow 8080/tcp  # Dashboard (opsiyonel, sadece internal kullanım için)

# UFW enable
sudo ufw enable

# Status
sudo ufw status verbose
```

### API Keys Güvenliği
```bash
# Config dosyası izinleri
chmod 600 ~/Trade_demo/config/production_config.json

# Sadece yusuf kullanıcısı okuyabilir
ls -la ~/Trade_demo/config/production_config.json
```

### Log Rotation
```bash
# Otomatik log rotation (systemd)
# genetix-bot.service içinde TimedRotatingFileHandler mevcut

# Manuel temizlik (eski logları sil)
find ~/Trade_demo/logs/production/ -name "*.log" -mtime +30 -delete
```

---

## 📈 Performans Optimizasyonu

### CPU Limitleri
```bash
sudo nano /etc/systemd/system/genetix-bot-v2.service

# Ekle:
[Service]
CPUQuota=80%
```

### Memory Limitleri
```bash
[Service]
MemoryMax=2G
MemoryHigh=1.5G
```

### Restart Policy
```bash
[Service]
Restart=on-failure
RestartSec=10s
StartLimitBurst=5
StartLimitIntervalSec=300
```

**Reload:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart genetix-bot-v2
```

---

## 📊 Beklenen Performans

### Validation Results
- **Win Rate**: 48.39%
- **Sharpe Ratio**: 2.95
- **Max Drawdown**: 28.04%
- **Consistency**: 89.54%
- **Average Trade**: +2.2%

### Resource Usage
- **CPU**: ~5-15% (normal)
- **Memory**: ~500MB - 1.5GB
- **Disk**: ~100MB (logs + results)
- **Network**: Minimal (WebSocket + API calls)

---

## 🎯 Deployment Checklist

### Pre-Deployment
- [x] Sunucu portları kontrol edildi (8080 boş ✅)
- [x] Python 3.9+ kurulu
- [x] Git kurulu
- [x] Systemd mevcut
- [x] Yeterli disk space (min 10GB)
- [x] Yeterli RAM (min 2GB)

### Installation
- [ ] Repository klonlandı
- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar kuruldu (requirements.txt)
- [ ] TA-Lib kuruldu
- [ ] Dry run test yapıldı
- [ ] Dashboard test edildi

### Service Setup
- [ ] Service file path'leri güncellendi
- [ ] Systemd service kuruldu
- [ ] Service enable edildi
- [ ] Service başlatıldı
- [ ] Status GREEN

### Verification
- [ ] Bot çalışıyor (systemctl status)
- [ ] Dashboard erişilebilir (http://localhost:8080)
- [ ] API endpoints çalışıyor (/api/stats)
- [ ] Loglar yazılıyor
- [ ] Binance API bağlantısı OK
- [ ] İlk sinyaller bekleniyor

### Monitoring
- [ ] Systemd journal izleniyor
- [ ] Log dosyaları kontrol ediliyor
- [ ] Dashboard periyodik kontrol
- [ ] Resource usage monitoring
- [ ] Alert sistemi aktif (opsiyonel)

---

## 🆘 Acil Durum

### Bot'u Durdur
```bash
# Graceful shutdown
sudo systemctl stop genetix-bot-v2

# Force kill (son çare)
sudo killall -9 python3
```

### Pozisyonları Manuel Kapat
```bash
# Binance UI'dan manuel kapatabilirsiniz:
https://testnet.binancefuture.com

# veya API ile:
python -c "
from testnet.src.binance_futures_api import BinanceFuturesTestnetAPI
api = BinanceFuturesTestnetAPI('config/production_config.json')
api.close_all_positions()
"
```

### Rollback
```bash
cd ~/Trade_demo/deploy
sudo ./safe_deploy.sh rollback
```

---

## 📞 Destek

### Loglar
```bash
# Tüm logları topla
tar -czf ~/genetix-logs-$(date +%Y%m%d).tar.gz ~/Trade_demo/logs/
```

### GitHub Issues
https://github.com/yusufcmg/Trade_demo/issues

### Documentation
- README.md
- DEPLOYMENT_GUIDE.md
- PRODUCTION_READY.md

---

## 🚀 Hızlı Deployment (1 Komut)

```bash
ssh yusuf@161.35.76.27 '
cd ~ &&
git clone https://github.com/yusufcmg/Trade_demo.git &&
cd Trade_demo &&
python3 -m venv venv &&
source venv/bin/activate &&
pip install --upgrade pip &&
pip install -r requirements.txt &&
cd deploy &&
chmod +x safe_deploy.sh &&
sudo ./safe_deploy.sh install &&
sudo ./safe_deploy.sh deploy_service &&
sudo ./safe_deploy.sh start &&
echo "✅ Deployment complete! Check status: sudo systemctl status genetix-bot-v2"
'
```

**Not**: TA-Lib manuel kurulum gerekebilir (yukarıdaki adım 4'e bakın).

---

**🤖 GenetiX Production Bot v2.3.0**  
**Frankfurt Sunucu**: 161.35.76.27  
**Port**: 8080  
**Status**: Ready for Deployment ✅  

**Next Step**: SSH ile bağlan ve deployment'a başla! 🚀
