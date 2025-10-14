# 🤖 GenetiX Bot - Hızlı Kullanım Kılavuzu

## 🚀 Bot'u Başlatma

```bash
cd /mnt/c/masaustu/genetix/evrimx/production
./run_bot.sh
```

**Çıktı:**
```
✅ Bot başlatıldı!
📊 Process ID: 71997
📝 Log dosyası: logs/production/nohup_20251014_191249.log
🌐 Dashboard: http://localhost:8080
```

---

## 🔍 Bot Durumunu Kontrol Etme

```bash
./check_bot.sh
```

**Ne gösterir:**
- ✅ Bot çalışıyor mu?
- 📊 PID ve kaynak kullanımı
- 🌐 Dashboard durumu
- 📝 Son log kayıtları
- 💼 İşlem sayısı
- 📈 Hata/Uyarı/Sinyal istatistikleri

---

## 🛑 Bot'u Durdurma

```bash
./stop_bot.sh
```

**Veya:**
```bash
kill $(cat bot.pid)
```

---

## 📊 İşlemleri İzleme

### 1️⃣ **Canlı Log İzleme**
```bash
# Tüm loglar
tail -f logs/production/nohup_*.log

# Sadece işlemler
tail -f logs/production/nohup_*.log | grep "DRY RUN"

# Sadece hatalar
tail -f logs/production/nohup_*.log | grep "ERROR"
```

### 2️⃣ **Dashboard'u Aç**
Tarayıcıda: **http://localhost:8080**

**Dashboard özellikleri:**
- 💰 Bakiye ve P&L
- 📊 Açık pozisyonlar
- 📈 İşlem geçmişi
- 🎯 Performans metrikleri
- 🔔 Son sinyaller

### 3️⃣ **API Endpoints**
```bash
# Genel durum
curl http://localhost:8080/api/status

# Pozisyonlar
curl http://localhost:8080/api/positions

# İşlem geçmişi
curl http://localhost:8080/api/trades

# Performans
curl http://localhost:8080/api/performance
```

### 4️⃣ **Results Dosyası**
```bash
# Son results dosyasını görüntüle
cat results/production/results_$(date +%Y%m%d).json | jq '.'

# İşlem sayısı
cat results/production/results_*.json | grep -o '"trades"' | wc -l
```

---

## 🔔 İşlem Bildirimleri

### **DRY RUN Modunda** (Şu anda aktif)
```
19:06:34 | INFO | 🧪 DRY RUN: LINKUSDT BUY 0.7 @ $18.91 (Conf: 75.0%)
```

**Anlamı:**
- 🧪 **DRY RUN**: Gerçek işlem YOK, sadece test
- **LINKUSDT**: Coin
- **BUY**: Alım sinyali (LONG pozisyon)
- **0.7**: Miktar (LINK)
- **$18.91**: Giriş fiyatı
- **75.0%**: Sinyal güveni (confidence)

### **Gerçek Modda** (dry_run: false)
```
19:06:34 | INFO | ✅ POSITION OPENED: LINKUSDT LONG 0.7 @ $18.91
```

---

## 📈 Performans Takibi

### **Terminal'den:**
```bash
# Son 24 saat istatistikleri
grep "Balance:" logs/production/nohup_*.log | tail -1

# Sinyal sayısı
grep -c "DRY RUN" logs/production/nohup_*.log

# Hata sayısı
grep -c "ERROR" logs/production/nohup_*.log

# Health check'ler
grep "Health check OK" logs/production/nohup_*.log | tail -5
```

### **Dashboard'dan:**
http://localhost:8080 → Tüm metrikler grafiklerle

---

## ⚙️ Konfigürasyon Değişiklikleri

### **DRY RUN → Gerçek İşlem**
```bash
nano config/production_config.json
```

Değiştir:
```json
"testnet": {
  "enabled": true,  ← false yap (mainnet için)
  "dry_run": true   ← false yap (gerçek işlemler için)
}
```

### **Sembol Ekle/Çıkar**
```bash
nano config/production_config.json
```

```json
"symbols": [
  "BTCUSDT",
  "ETHUSDT",
  "YENI_COIN_USDT"  ← Ekle
]
```

### **Risk Ayarları**
```json
"risk_management": {
  "max_position_size": 0.02,    ← Pozisyon büyüklüğü (balance'ın %2'si)
  "max_positions": 5,            ← Maksimum eşzamanlı pozisyon
  "stop_loss_pct": 0.02,        ← Stop loss (%2)
  "take_profit_pct": 0.04        ← Take profit (%4)
}
```

**Değişiklikten sonra:**
```bash
./stop_bot.sh
./run_bot.sh
```

---

## 🆘 Sorun Giderme

### **Bot Çalışmıyor**
```bash
./check_bot.sh  # Durumu kontrol et

# Manuel başlatma
cd /mnt/c/masaustu/genetix/evrimx/production
python production_bot_v2.py --dry-run
```

### **Port 8080 Kullanımda**
```bash
# Portu kullanan process'i bul
lsof -i :8080

# Kill et
kill -9 <PID>

# Veya config'de portu değiştir
nano config/production_config.json
```

### **API Hatası**
```bash
# API test et
curl https://testnet.binancefuture.com/fapi/v1/time

# Config kontrolü
cat config/production_config.json | grep -A5 api_credentials
```

### **Loglar Görünmüyor**
```bash
# Log dizini oluştur
mkdir -p logs/production results/production

# İzinleri düzelt
chmod -R 755 logs results
```

---

## 📋 Günlük Kontrol Listesi

### **Her Gün:**
- [ ] `./check_bot.sh` - Bot çalışıyor mu?
- [ ] `tail -20 logs/production/nohup_*.log` - Hata var mı?
- [ ] http://localhost:8080 - Dashboard kontrolü
- [ ] `grep "DRY RUN" logs/production/nohup_*.log | tail -10` - Sinyaller

### **Her Hafta:**
- [ ] `git pull origin main` - Kod güncellemesi
- [ ] `pip install --upgrade -r requirements.txt` - Paket güncellemesi
- [ ] `./stop_bot.sh && ./run_bot.sh` - Bot restart
- [ ] Performans analizi (win rate, Sharpe, drawdown)

### **Her Ay:**
- [ ] Log dosyalarını arşivle: `tar -czf logs_$(date +%Y%m).tar.gz logs/`
- [ ] Eski logları sil: `find logs -name "*.log" -mtime +30 -delete`
- [ ] Strateji performansını değerlendir

---

## 🎯 Hedefler ve Metrikler

### **İyi Performans:**
- ✅ Win Rate: >55%
- ✅ Sharpe Ratio: >1.5
- ✅ Max Drawdown: <15%
- ✅ Profit Factor: >1.5
- ✅ Uptime: >98%

### **Kötü Performans (Durdur!):**
- ❌ Win Rate: <45%
- ❌ Max Drawdown: >25%
- ❌ 3 gün üst üste zarar
- ❌ Sık API hataları

---

## 📞 Hızlı Referans

| Komut | Açıklama |
|-------|----------|
| `./run_bot.sh` | Bot'u başlat |
| `./stop_bot.sh` | Bot'u durdur |
| `./check_bot.sh` | Durum kontrolü |
| `tail -f logs/production/nohup_*.log` | Canlı log |
| `grep "DRY RUN" logs/production/*.log` | İşlemleri göster |
| http://localhost:8080 | Dashboard |
| `cat bot.pid` | PID göster |
| `ps aux \| grep production_bot` | Process kontrolü |

---

**💡 İpucu:** İlk kez kullanıyorsan, önce 24 saat DRY RUN modunda test et!

---

**Hazırlayan:** GenetiX AI  
**Tarih:** 14 Ekim 2025  
**Bot Versiyonu:** v2.3.0
