# ⚡ Production Bot - Hızlı Başlangıç

## 🚀 5 Dakikada Başla

### 1️⃣ Kurulum (Ubuntu)
```bash
cd production
chmod +x deploy/deploy.sh
./deploy/deploy.sh install
```

### 2️⃣ API Keys Ekle
```bash
# .env dosyası oluştur
cp .env.example .env
nano .env
```

**Ekle:**
```env
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_testnet_secret
```

### 3️⃣ Config Kontrol
```bash
nano config/production_config.json
```

**Önemli ayarlar:**
- `symbols_to_trade`: ["BTCUSDT", "ETHUSDT"]
- `position_size_percent`: 10.0
- `leverage`: 5

### 4️⃣ Başlat
```bash
./deploy/deploy.sh start
./deploy/deploy.sh logs
```

### 5️⃣ Dashboard Aç
```
http://localhost:8080/dashboard.html
```

---

## 🧪 Test Modu

İlk önce dry-run ile test et:
```bash
source ../venv/bin/activate
python production_bot.py --dry-run
```

---

## 📊 Komutlar

```bash
./deploy/deploy.sh start     # Başlat
./deploy/deploy.sh stop      # Durdur
./deploy/deploy.sh restart   # Yeniden başlat
./deploy/deploy.sh status    # Durum
./deploy/deploy.sh logs      # Log izle
```

---

## ✅ Kontrol Listesi

- [ ] Ubuntu 20.04+ kurulu
- [ ] Python 3.10+ yüklü
- [ ] Binance Testnet hesabı var
- [ ] API key ve secret alındı
- [ ] .env dosyası oluşturuldu
- [ ] Config düzenlendi
- [ ] Dry-run test yapıldı
- [ ] Dashboard açıldı
- [ ] Log'lar kontrol edildi

---

## 🆘 Sorun mu var?

1. **Log kontrol:**
   ```bash
   ./deploy/deploy.sh logs
   ```

2. **Status kontrol:**
   ```bash
   ./deploy/deploy.sh status
   ```

3. **Manuel test:**
   ```bash
   python production_bot.py --dry-run
   ```

4. **Detaylı dokümantasyon:**
   ```bash
   cat README.md
   ```

---

## 📞 Yardım

- 📖 **README.md** - Detaylı kılavuz
- 📁 **STRUCTURE.md** - Klasör yapısı
- 🔧 **config/** - Ayar örnekleri

**🎉 İyi tradinglar!**
