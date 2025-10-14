# 🚀 Frankfurt Server - Hızlı Başlangıç

Terminal kapansa bile bot çalışmaya devam etsin!

---

## 📋 HIZLI KURULUM

```bash
# 1. SSH bağlan
ssh yusuf@161.35.76.27

# 2. Güncel kodu çek
cd ~/Trade_demo
git pull origin main

# 3. Script'leri executable yap
chmod +x deploy/install_service.sh
chmod +x manage_bot.sh

# 4. systemd service kur
./deploy/install_service.sh

# ✅ Kurulum tamamlandı!
```

---

## ⚡ KULLANIM

### Kolay Yönetim (Önerilen):

```bash
# Bot'u başlat
./manage_bot.sh start

# Durumu kontrol et
./manage_bot.sh status

# Canlı logları izle (Ctrl+C ile çık)
./manage_bot.sh logs

# Sağlık kontrolü
./manage_bot.sh health

# Kod güncelle + restart
./manage_bot.sh update

# Bot'u durdur
./manage_bot.sh stop

# Yeniden başlat
./manage_bot.sh restart
```

### Manuel Yönetim:

```bash
# Başlat
sudo systemctl start genetix-bot

# Durdur
sudo systemctl stop genetix-bot

# Yeniden başlat
sudo systemctl restart genetix-bot

# Durum
sudo systemctl status genetix-bot

# Loglar
sudo journalctl -u genetix-bot -f
```

---

## ✅ TEST

```bash
# 1. Bot'u başlat
./manage_bot.sh start

# 2. Durumu kontrol et
./manage_bot.sh status
# Beklenen: active (running)

# 3. Birkaç saniye logları izle
./manage_bot.sh logs
# Beklenen: ✅ BTCUSDT: 200 candles loaded

# 4. Terminal'i kapat
exit

# 5. Yeniden bağlan
ssh yusuf@161.35.76.27

# 6. Bot hala çalışıyor mu?
./manage_bot.sh status
# ✅ Bot hala çalışıyor olmalı!

# 7. Dashboard'a eriş
# Tarayıcıda: http://161.35.76.27:8080
```

---

## 🎯 ÖNEMLİ NOTLAR

- ✅ Terminal kapansa bile bot çalışır
- ✅ Sunucu yeniden başlayınca bot otomatik başlar
- ✅ Bot crash olursa 10 saniyede yeniden başlar
- ✅ Loglar: `logs/production/` dizininde
- ✅ Dashboard: http://161.35.76.27:8080

---

## 🔧 SORUN GİDERME

### Bot başlamıyor:

```bash
# Detaylı hata logları
sudo journalctl -u genetix-bot -n 100

# Manuel çalıştırarak test et
cd ~/Trade_demo
python production_bot_v2.py --dry-run
```

### Logları göremiyorum:

```bash
# systemd logları
sudo journalctl -u genetix-bot -f

# Dosya logları
tail -f logs/production/bot_*.log
tail -f logs/production/errors_*.log
```

### Service yeniden yükle:

```bash
# Config değiştirdikten sonra
sudo systemctl daemon-reload
sudo systemctl restart genetix-bot
```

---

## 📊 MONITORING

```bash
# Sağlık kontrolü
./manage_bot.sh health

# Memory kullanımı
systemctl show genetix-bot -p MemoryCurrent

# Uptime
systemctl show genetix-bot -p ActiveEnterTimestamp

# Restart sayısı
systemctl show genetix-bot -p NRestarts

# Son hatalar (10 dakika)
sudo journalctl -u genetix-bot --since "10 minutes ago" | grep ERROR
```

---

## 🚀 SON ADIMLAR

1. ✅ Service kur: `./deploy/install_service.sh`
2. ✅ Bot başlat: `./manage_bot.sh start`
3. ✅ Durum kontrol: `./manage_bot.sh status`
4. ✅ Terminal kapat: `exit`
5. ✅ Yeniden bağlan ve kontrol et

**Bot artık kesintisiz çalışıyor! 🎉**
