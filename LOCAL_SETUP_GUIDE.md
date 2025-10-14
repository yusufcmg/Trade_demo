# 🖥️ Lokal PC'de Bot Çalıştırma Rehberi

## ✅ DURUM: Bot Lokal'de Başarıyla Test Edildi! (14 Ekim 2025 - 18:58)

```
✅ BTCUSDT: 200 candles loaded
✅ ETHUSDT: 200 candles loaded
✅ BNBUSDT: 200 candles loaded
✅ ADAUSDT: 200 candles loaded
✅ DOTUSDT: 200 candles loaded
✅ LINKUSDT: 200 candles loaded
✅ LTCUSDT: 200 candles loaded
✅ SOLUSDT: 200 candles loaded
✅ Bot initialized successfully!
✅ Main trading loop starting...
```

**🎉 BUGLAR DÜZELTİLDİ!**
- ✅ IndexError "list index out of range" → **FIXED**
- ✅ UnboundLocalError "response variable" → **FIXED**
- ✅ Tüm semboller başarıyla yükleniyor (8/8)
- ✅ Rate limiting düzgün çalışıyor

**Detaylar:** `BUGFIX_INDEX_ERROR.md` dosyasına bakın

---

## 📋 Lokal PC'de Çalıştırma (Windows/WSL)

### Yöntem 1: Terminalden Çalıştırma (ÖNERİLEN)

```bash
# 1. Dizine git
cd /mnt/c/masaustu/genetix/evrimx/production

# 2. Virtual environment aktif et
source venv/bin/activate

# 3. Bot'u başlat (DRY RUN - test modu)
python production_bot_v2.py --dry-run
```

**Beklenen Çıktı:**
```
🤖 GenetiX Production Trading Bot v2.3.0
✅ Binance API connected!
📊 BTCUSDT: 200 candles loaded
🤖 Bot initialized successfully!
🔄 Main trading loop starting...
💰 Balance: $5,000.00
```

**Dashboard:** http://localhost:8080

---

### Yöntem 2: Arka Planda Çalıştırma (nohup)

```bash
cd /mnt/c/masaustu/genetix/evrimx/production
source venv/bin/activate
nohup python production_bot_v2.py --dry-run > bot.log 2>&1 &

# Process ID'yi kaydet
echo $! > bot.pid

# Logları izle
tail -f bot.log

# Bot'u durdur
kill $(cat bot.pid)
```

---

### Yöntem 3: Screen ile Çalıştırma (Kalıcı Terminal)

```bash
# Screen kur (eğer yoksa)
sudo apt-get install screen

# Screen session başlat
screen -S genetix-bot

# Bot'u başlat
cd /mnt/c/masaustu/genetix/evrimx/production
source venv/bin/activate
python production_bot_v2.py --dry-run

# Screen'den çık (bot çalışmaya devam eder)
Ctrl+A, sonra D tuşlarına bas

# Geri dön
screen -r genetix-bot

# Screen'i tamamen kapat
screen -X -S genetix-bot quit
```

---

## 🎛️ Bot Kontrol Komutları

### Process Kontrolü

```bash
# Bot çalışıyor mu?
ps aux | grep production_bot_v2.py

# Port kullanımı (Dashboard)
lsof -i :8080

# Bot'u durdur
pkill -f production_bot_v2.py
```

### Log İzleme

```bash
# Canlı log takibi
tail -f logs/production/bot_$(date +%Y%m%d).log

# Son 100 satır
tail -n 100 logs/production/bot_$(date +%Y%m%d).log

# Hata arama
grep ERROR logs/production/bot_$(date +%Y%m%d).log
```

### Dashboard Erişimi

**Tarayıcıda aç:**
- http://localhost:8080
- http://127.0.0.1:8080

**API Endpoints:**
```bash
# Durum
curl http://localhost:8080/api/status

# Pozisyonlar
curl http://localhost:8080/api/positions

# İşlem geçmişi
curl http://localhost:8080/api/trades

# Performans
curl http://localhost:8080/api/performance
```

---

## 🔧 Sorun Giderme

### Sorun 1: "ModuleNotFoundError: No module named 'xyz'"

**Çözüm:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Sorun 2: "Address already in use (Port 8080)"

**Çözüm:**
```bash
# Portı kullanan process'i bul
lsof -i :8080

# Kill et
kill -9 <PID>

# VEYA config'de portu değiştir
nano config/production_config.json
# "dashboard_port": 8080 → 8081
```

### Sorun 3: "Permission denied: logs/production"

**Çözüm:**
```bash
mkdir -p logs/production results
chmod -R 755 logs results
```

### Sorun 4: API Bağlantı Hatası

**Çözüm:**
```bash
# API'yi test et
python debug_api.py

# İnternet kontrolü
ping testnet.binancefuture.com

# Config kontrolü
cat config/production_config.json | grep api
```

---

## 📊 Başarı Kriterleri

✅ **Bot Başarıyla Çalışıyor:**

1. **Başlangıç logları:**
   ```
   ✅ Binance API connected!
   ✅ BTCUSDT: 200 candles loaded
   ✅ Bot initialized successfully!
   ```

2. **Ana döngü:**
   ```
   🔄 Main trading loop starting...
   💰 Balance: $5,000.00
   📊 Positions: 0/5
   ```

3. **Dashboard aktif:**
   - http://localhost:8080 açılıyor
   - `/api/status` JSON döndürüyor

4. **Hata YOK:**
   - ❌ "list index out of range" YOK
   - ❌ "Connection error" YOK
   - ❌ "API error" YOK

---

## 🚀 Prod Mode'a Geçiş (GERÇEK İŞLEM)

**⚠️ DİKKAT: Sadece testnet'te başarıyla çalıştıktan sonra!**

```bash
# 1. Config'i güncelle
nano config/production_config.json

# 2. Mainnet API keys ekle
{
  "api_credentials": {
    "api_key": "GERÇEK_MAINNET_KEY",
    "secret_key": "GERÇEK_MAINNET_SECRET"
  },
  "testnet": {
    "enabled": false  ← BU SATIRDA FALSE YAP
  }
}

# 3. --dry-run'sız başlat
python production_bot_v2.py
```

**ÖNEMLİ:** Mainnet öncesi:
- [ ] 7-14 gün testnet'te çalıştır
- [ ] Performansı doğrula (win rate, Sharpe, drawdown)
- [ ] Tüm senaryoları test et (long, short, stop loss, take profit)
- [ ] Küçük balance ile başla ($100-500)

---

## 💡 Öneriler

### Günlük Kontrol

```bash
# Her gün kontrol et:
1. Bot çalışıyor mu? → ps aux | grep production_bot
2. Hata var mı? → grep ERROR logs/production/bot_*.log
3. Performans nasıl? → curl http://localhost:8080/api/performance
4. Dashboard açılıyor mu? → http://localhost:8080
```

### Haftalık Bakım

```bash
# Her hafta:
1. Kodu güncelle → git pull origin main
2. Paketleri güncelle → pip install --upgrade -r requirements.txt
3. Bot'u restart et → pkill -f production_bot && python production_bot_v2.py --dry-run
4. Logları arşivle → tar -czf logs_$(date +%Y%m%d).tar.gz logs/
```

### Güvenlik

```bash
# API keys'i koru:
chmod 600 config/production_config.json

# Log dosyalarını düzenli temizle:
find logs -name "*.log" -mtime +30 -delete
```

---

## 🎯 Sonuç

✅ **Bot lokal PC'de başarıyla çalışıyor**  
✅ **Hiçbir "list index out of range" hatası yok**  
✅ **Dashboard aktif: http://localhost:8080**  
✅ **Tüm semboller yükleniyor (8/8)**  
✅ **API bağlantısı stabil**

**Tavsiye:** Lokal'de 24 saat test edin, sonra production'a geçin.

---

**Hazırlayan:** GenetiX AI Agent  
**Tarih:** 14 Ekim 2025  
**Platform:** Windows/WSL, Ubuntu  
**Commit:** 226a312
