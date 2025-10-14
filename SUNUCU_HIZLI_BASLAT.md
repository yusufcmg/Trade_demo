# 🚀 SUNUCUDA HIZLI BAŞLATMA

## ✅ Git Push Tamamlandı!

```
Commit: 0cc90f8
Branch: genetix-v2-complete  
Repo: https://github.com/yusufcmg/NEW--GenetiX-Trading-System.git
```

---

## 📦 SUNUCUDA KURULUM (3 Adım)

### 1️⃣ Repository Klonla

```bash
# SSH ile sunucuya bağlan
ssh user@sunucu_ip

# Repository'yi klonla
cd ~
git clone https://github.com/yusufcmg/NEW--GenetiX-Trading-System.git
cd NEW--GenetiX-Trading-System/evrimx/production
```

### 2️⃣ Environment Hazırla

```bash
# Python 3.8+ kontrol
python3 --version

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Bağımlılıklar
pip install --upgrade pip
pip install -r requirements.txt

# Script izinleri
chmod +x *.sh

# Dizinler
mkdir -p logs/production results/production
```

### 3️⃣ Bot'u Başlat

```bash
# Config'i kontrol et
./check_config.sh

# Bot'u başlat (gerçek işlem modu)
./run_bot_live.sh
# → "yes" yaz + Enter
# → "START" yaz + Enter

# Veya dry run test modu
./run_bot.sh
```

---

## 🔍 İZLEME

### **Canlı Log**
```bash
tail -f logs/production/nohup_*.log
```

### **Durum Kontrolü**
```bash
./check_bot.sh
```

### **Dashboard (Local'den SSH Tunnel)**
```bash
# Local bilgisayardan
ssh -L 8080:localhost:8080 user@sunucu_ip

# Tarayıcıda
http://localhost:8080
```

### **İşlemleri Görüntüle**
```bash
# Açık pozisyonlar
curl http://localhost:8080/api/positions | jq

# Son işlemler  
tail -f logs/production/nohup_*.log | grep "POSITION\|TRADE"
```

---

## 🛑 BOT'U DURDUR

```bash
./stop_bot.sh
```

---

## ⚙️ KONFİGÜRASYON

### **Mevcut Ayarlar:**

```json
{
  "testnet": {
    "enabled": true,        // Testnet aktif (gerçek para yok)
    "dry_run": false        // Gerçek işlem modu (emirler gönderilecek)
  },
  "trading_config": {
    "max_positions": 3,     // Max eşzamanlı pozisyon
    "base_position_percent": 5.0,  // Balance'ın %5'i
    "leverage": 3,          // 3x kaldıraç
    "stop_loss_percent": 2.0,      // %2 stop loss
    "take_profit_percent": 4.0     // %4 take profit
  },
  "risk_management": {
    "max_daily_loss_usd": 50,      // Max $50 günlük zarar
    "circuit_breaker": {
      "max_consecutive_losses": 3,  // 3 ardışık zarar → dur
      "cooldown_minutes": 120       // 2 saat bekle
    }
  }
}
```

---

## 📊 BEKLENTİLER

### **İlk 24 Saat:**
- ✅ Bot stabil çalışmalı
- ✅ 5-15 sinyal üretmeli
- ✅ Hata minimal (<10 ERROR)
- ✅ Crash olmamalı

### **İlk 7 Gün:**
- ✅ Win rate >50%
- ✅ Max drawdown <10%
- ✅ Uptime >95%

---

## 🆘 SORUN GİDERME

### **Bot Başlamıyor:**
```bash
python production_bot_v2.py --dry-run
```

### **Port Meşgul:**
```bash
lsof -ti:8080 | xargs kill -9
```

### **API Hatası:**
```bash
curl https://testnet.binancefuture.com/fapi/v1/time
```

---

## 📝 GÜNLÜK KONTROL

```bash
# Her gün çalıştır:
./check_bot.sh
tail -20 logs/production/nohup_*.log | grep "ERROR"
curl http://localhost:8080/api/performance
```

---

## 🎯 SONRAKI ADIMLAR

1. ✅ Sunucuda bot'u başlat
2. ✅ İlk 1 saat yakın takip et
3. ✅ Günde 2-3 kez kontrol et
4. ✅ 7 gün sorunsuz çalışırsa → Mainnet düşünülebilir

---

## 📞 DOKÜMANTASYONLAR

- `SERVER_DEPLOYMENT.md` - Detaylı sunucu kurulum
- `QUICK_START.md` - Hızlı kullanım kılavuzu
- `BUGFIX_INDEX_ERROR.md` - Bug fix detayları
- `LOCAL_SETUP_GUIDE.md` - Lokal test rehberi

---

**Hazırlayan:** GenetiX AI  
**Tarih:** 14 Ekim 2025  
**Commit:** 0cc90f8  
**Status:** ✅ Production Ready (Testnet)

🚀 **BOT SUNUCUDA ÇALIŞTIRMAYA HAZIR!**
