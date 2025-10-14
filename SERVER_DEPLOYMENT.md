# 🚀 Sunucuda Bot Çalıştırma Rehberi

## 📋 Yapılan Değişiklikler (v2.3.1)

### ✅ Bug Fix'ler
1. **IndexError** düzeltildi (`_check_rate_limit` metodu)
2. **UnboundLocalError** düzeltildi (`get_ticker_price` metodu)

### ⚙️ Yeni Özellikler
1. **Gerçek işlem modu** eklendi (config'den kontrol edilebilir)
2. **Gelişmiş risk yönetimi:**
   - Max pozisyon: 3
   - Pozisyon büyüklüğü: %5
   - Leverage: 3x
   - Stop loss: %2
   - Max daily loss: $50
   - Circuit breaker: 3 ardışık zarar

### 📝 Yeni Dosyalar
- `run_bot.sh` - Arka planda bot başlatma
- `stop_bot.sh` - Bot'u güvenli durdurma
- `check_bot.sh` - Durum kontrolü
- `run_bot_live.sh` - Gerçek işlem modu başlatma (onay gerektirir)
- `check_config.sh` - Config doğrulama
- `QUICK_START.md` - Hızlı kullanım kılavuzu
- `BUGFIX_INDEX_ERROR.md` - Detaylı bug fix dokümantasyonu

---

## 🖥️ Sunucuda Kurulum

### 1️⃣ Repository'yi Klonla/Güncelle

```bash
# Yeni kurulum
cd ~
git clone https://github.com/yusufcmg/NEW--GenetiX-Trading-System.git
cd NEW--GenetiX-Trading-System/evrimx/production

# Veya mevcut repo'yu güncelle
cd ~/NEW--GenetiX-Trading-System
git pull origin genetix-v2-complete
cd evrimx/production
```

### 2️⃣ Python Environment Hazırla

```bash
# Python 3.8+ gerekli
python3 --version

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Konfigürasyon

```bash
# Config dosyasını kontrol et
./check_config.sh

# API credentials'ları güncelle (eğer farklı testnet hesabı kullanacaksan)
nano config/production_config.json
```

**Önemli ayarlar:**
```json
{
  "testnet": {
    "enabled": true,              // true = testnet, false = mainnet
    "base_url": "https://testnet.binancefuture.com",
    "dry_run": false              // false = gerçek işlem, true = simülasyon
  }
}
```

### 4️⃣ İzinleri Ayarla

```bash
# Script'lere çalıştırma izni ver
chmod +x *.sh

# Log ve results klasörlerini oluştur
mkdir -p logs/production results/production
```

---

## 🚀 Bot'u Başlatma

### **Seçenek 1: Test Modu (Önerilen - İlk Başlangıç)**

```bash
# Dry run modunda başlat (simülasyon, emir gönderilmez)
./run_bot.sh
```

**Kontrol:**
```bash
./check_bot.sh
tail -f logs/production/nohup_*.log
```

### **Seçenek 2: Gerçek İşlem Modu (Testnet)**

```bash
# Config'i kontrol et
./check_config.sh

# Gerçek işlem modunda başlat (onay gerektirir)
./run_bot_live.sh
```

**İlk başlatmada:**
1. "yes" yazıp Enter
2. "START" yazıp Enter
3. Bot başlayacak

---

## 📊 İzleme ve Kontrol

### **Durum Kontrolü**
```bash
./check_bot.sh
```

**Çıktı:**
- ✅ Bot çalışıyor mu?
- 📊 CPU/Memory kullanımı
- 🌐 Dashboard durumu
- 📝 Son loglar
- 🎯 Sinyal/hata istatistikleri

### **Canlı Log İzleme**
```bash
# Tüm loglar
tail -f logs/production/nohup_*.log

# Sadece işlemler
tail -f logs/production/nohup_*.log | grep -E "(POSITION|TRADE|BUY|SELL)"

# Sadece hatalar
tail -f logs/production/nohup_*.log | grep "ERROR"
```

### **Dashboard**
```bash
# Sunucu IP'sini öğren
hostname -I

# Dashboard'a eriş
http://<SUNUCU_IP>:8080
```

**Veya SSH tunnel ile:**
```bash
# Local bilgisayarından
ssh -L 8080:localhost:8080 user@sunucu_ip

# Sonra tarayıcıda
http://localhost:8080
```

### **API Endpoints**
```bash
# Durum
curl http://localhost:8080/api/status

# Açık pozisyonlar
curl http://localhost:8080/api/positions

# İşlem geçmişi
curl http://localhost:8080/api/trades

# Performans
curl http://localhost:8080/api/performance
```

---

## 🛑 Bot'u Durdurma

```bash
./stop_bot.sh
```

**Veya manuel:**
```bash
kill $(cat bot.pid)
```

---

## 🔄 Güncelleme (Yeni Kod Geldiğinde)

```bash
# Bot'u durdur
./stop_bot.sh

# Kodu güncelle
git pull origin genetix-v2-complete

# Bağımlılıkları güncelle (gerekirse)
pip install --upgrade -r requirements.txt

# Bot'u yeniden başlat
./run_bot.sh  # veya ./run_bot_live.sh
```

---

## 🆘 Sorun Giderme

### **Bot Başlamıyor**
```bash
# Manuel test
python production_bot_v2.py --dry-run

# Port kontrolü
lsof -i :8080

# Loglara bak
tail -50 logs/production/nohup_*.log
```

### **API Hatası**
```bash
# Testnet erişim testi
curl https://testnet.binancefuture.com/fapi/v1/time

# Config kontrolü
cat config/production_config.json | grep -A5 api_credentials
```

### **Process Takılı Kaldı**
```bash
# Tüm bot process'lerini durdur
pkill -9 -f production_bot_v2.py

# Port'u temizle
lsof -ti:8080 | xargs kill -9
```

---

## 📈 Performans Takibi

### **Günlük Kontrol (Her Gün)**
```bash
./check_bot.sh
grep "DRY RUN\|POSITION" logs/production/nohup_*.log | tail -20
curl http://localhost:8080/api/performance | jq
```

### **Haftalık Bakım (Her Hafta)**
```bash
# Bot'u restart et
./stop_bot.sh
./run_bot.sh

# Logları arşivle
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/
```

### **Metrikler**
```bash
# İşlem sayısı
grep -c "POSITION OPENED" logs/production/*.log

# Hata sayısı
grep -c "ERROR" logs/production/*.log

# Win rate hesaplama
# Dashboard'dan: http://localhost:8080
```

---

## 🔐 Güvenlik Tavsiyeleri

### **Testnet Başlangıç (Önerilen)**
1. ✅ İlk 24 saat DRY RUN modunda çalıştır
2. ✅ Sonra 7 gün testnet'te gerçek işlem modu
3. ✅ Performansı doğrula (win rate, drawdown, Sharpe)
4. ✅ Tüm senaryoları test et

### **Mainnet'e Geçiş (İleri Seviye)**
```bash
# Config düzenle
nano config/production_config.json

# Değiştir:
"testnet": {
  "enabled": false,        // Mainnet için false
  "dry_run": false         // Gerçek işlem için false
}

# ⚠️  DİKKAT: Mainnet API keys gerekli!
"api_credentials": {
  "api_key": "MAINNET_KEY",
  "secret_key": "MAINNET_SECRET"
}
```

**⚠️  Mainnet başlatmadan önce:**
- [ ] Testnet'te en az 7 gün sorunsuz çalıştı
- [ ] Win rate >55%
- [ ] Max drawdown <15%
- [ ] Circuit breaker test edildi
- [ ] Stop loss/Take profit test edildi

---

## 📋 Hızlı Komut Referansı

| Komut | Açıklama |
|-------|----------|
| `./run_bot.sh` | Bot'u başlat (dry run) |
| `./run_bot_live.sh` | Bot'u başlat (gerçek işlem) |
| `./stop_bot.sh` | Bot'u durdur |
| `./check_bot.sh` | Durum kontrolü |
| `./check_config.sh` | Config doğrulama |
| `tail -f logs/production/nohup_*.log` | Canlı log |
| `cat bot.pid` | Process ID |
| `ps aux \| grep production_bot` | Process kontrolü |

---

## 📞 Destek

- **Dokümantasyon:** `QUICK_START.md`
- **Bug Fix Detayları:** `BUGFIX_INDEX_ERROR.md`
- **Config Ayarları:** `config/production_config.json`
- **Log Dosyaları:** `logs/production/`

---

**Son Güncelleme:** 14 Ekim 2025  
**Bot Versiyonu:** v2.3.1  
**Status:** ✅ Production Ready (Testnet)

---

## 🎯 Beklenen Sonuçlar

### **İlk 24 Saat:**
- ✅ Bot stabil çalışmalı (crash yok)
- ✅ 5-15 sinyal üretmeli
- ✅ Hata sayısı minimal (<10 ERROR)
- ✅ Health check'ler başarılı

### **İlk 7 Gün:**
- ✅ Win rate >50%
- ✅ Sharpe ratio >1.0
- ✅ Max drawdown <10%
- ✅ Uptime >95%

**Bu metrikleri karşılarsa → Mainnet'e geçiş düşünülebilir**
