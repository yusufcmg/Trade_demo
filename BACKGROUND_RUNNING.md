# 🚀 Terminal Kapansa Bile Bot Çalıştırma Rehberi

Bot'u terminal kapandığında bile arka planda çalıştırmak için 4 farklı yöntem.

---

## ⭐ YÖNTEM 1: systemd Service (ÖNERİLEN)

**Avantajları:**
- ✅ Terminal kapansa bile çalışır
- ✅ Sunucu yeniden başlayınca otomatik başlar
- ✅ Crash olursa otomatik yeniden başlar
- ✅ Profesyonel log yönetimi
- ✅ Resource limiting (CPU, RAM)
- ✅ Kolay yönetim (start/stop/restart)

### Kurulum:

```bash
# 1. Service dosyasını kopyala
cd ~/Trade_demo
chmod +x deploy/install_service.sh
./deploy/install_service.sh

# 2. Bot'u başlat
sudo systemctl start genetix-bot

# 3. Durumu kontrol et
sudo systemctl status genetix-bot

# 4. Logları izle
sudo journalctl -u genetix-bot -f
```

### Yönetim:

```bash
# Kolay yönetim için
chmod +x manage_bot.sh

# Bot'u başlat
./manage_bot.sh start

# Durumu kontrol et
./manage_bot.sh status

# Logları izle
./manage_bot.sh logs

# Kod güncelle + restart
./manage_bot.sh update

# Sağlık kontrolü
./manage_bot.sh health
```

### Service Özellikleri:

- **Restart Policy:** `always` - Her durumda yeniden başlar
- **Restart Delay:** 10 saniye
- **Memory Limit:** 2GB
- **CPU Quota:** 150%
- **Log Location:** `logs/production/systemd_stdout.log`
- **Watchdog:** 120 saniye (yanıt vermezse restart)

---

## 🔄 YÖNTEM 2: screen (Basit & Hızlı)

**Avantajları:**
- ✅ Kurulumu çok kolay
- ✅ Terminal kapansa bile çalışır
- ✅ Birden fazla session yönetimi

**Dezavantajları:**
- ❌ Sunucu yeniden başlayınca kapanır
- ❌ Crash olursa otomatik başlamaz

### Kurulum:

```bash
# screen kur (genelde yüklü)
sudo apt install screen -y
```

### Kullanım:

```bash
# 1. Yeni screen session oluştur
screen -S genetix

# 2. Bot'u başlat
cd ~/Trade_demo
python production_bot_v2.py --dry-run

# 3. Screen'den ayrıl (bot çalışmaya devam eder)
# Ctrl+A sonra D tuşlarına bas

# 4. Screen'e geri dön
screen -r genetix

# 5. Tüm screen'leri listele
screen -ls

# 6. Screen'i tamamen kapat (bot'u durdur)
screen -X -S genetix quit
```

### Screen Komutları:

```bash
# Yeni session
screen -S bot_ismi

# Mevcut session'a bağlan
screen -r bot_ismi

# Detach (çıkış ama çalışmaya devam)
Ctrl+A sonra D

# Liste
screen -ls

# Session'ı kapat
screen -X -S bot_ismi quit
```

---

## 🌙 YÖNTEM 3: nohup (En Basit)

**Avantajları:**
- ✅ Ekstra kurulum gerektirmez
- ✅ Terminal kapansa bile çalışır

**Dezavantajları:**
- ❌ Process yönetimi zor
- ❌ Sunucu yeniden başlayınca kapanır
- ❌ Log yönetimi kötü

### Kullanım:

```bash
# Bot'u başlat (arka planda)
cd ~/Trade_demo
nohup python production_bot_v2.py --dry-run > bot.log 2>&1 &

# Process ID'yi kaydet
echo $! > bot.pid

# Logları izle
tail -f bot.log

# Bot'u durdur
kill $(cat bot.pid)

# Zorla durdur
kill -9 $(cat bot.pid)
```

### Temizlik Script'i:

```bash
#!/bin/bash
# start_bot_nohup.sh

cd ~/Trade_demo

# Eski process varsa durdur
if [ -f bot.pid ]; then
    kill $(cat bot.pid) 2>/dev/null || true
    rm bot.pid
fi

# Yeni bot başlat
nohup python production_bot_v2.py --dry-run > logs/nohup.log 2>&1 &
echo $! > bot.pid

echo "Bot başlatıldı! PID: $(cat bot.pid)"
echo "Loglar: tail -f logs/nohup.log"
```

---

## 🐳 YÖNTEM 4: tmux (Modern Alternatif)

**screen'e benzer ama daha güçlü**

### Kurulum:

```bash
sudo apt install tmux -y
```

### Kullanım:

```bash
# 1. Yeni tmux session
tmux new -s genetix

# 2. Bot'u başlat
cd ~/Trade_demo
python production_bot_v2.py --dry-run

# 3. Detach (çıkış)
Ctrl+B sonra D

# 4. Attach (geri dön)
tmux attach -t genetix

# 5. Liste
tmux ls

# 6. Session'ı kapat
tmux kill-session -t genetix
```

### tmux Avantajları:

- Split panes (ekran bölme)
- Daha modern
- Scriptable
- Session paylaşımı

---

## 📊 YÖNTEMLER KARŞILAŞTIRMA

| Özellik | systemd | screen | nohup | tmux |
|---------|---------|--------|-------|------|
| Kurulum | Orta | Kolay | Yok | Kolay |
| Terminal bağımsız | ✅ | ✅ | ✅ | ✅ |
| Sunucu restart sonrası | ✅ | ❌ | ❌ | ❌ |
| Auto-restart (crash) | ✅ | ❌ | ❌ | ❌ |
| Log yönetimi | ✅ | ✅ | ⚠️ | ✅ |
| Resource limit | ✅ | ❌ | ❌ | ❌ |
| Profesyonellik | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 HANGİSİNİ SEÇMELİ?

### Production (Frankfurt Server): **systemd** ✅
- Profesyonel
- Güvenilir
- Otomatik yönetim

### Development/Test: **screen** veya **tmux**
- Hızlı başlatma/durdurma
- Kolay debug

### Geçici Testler: **nohup**
- Tek seferlik işler
- Hızlı test

---

## 🚀 ÖNERİLEN KURULUM (Frankfurt)

```bash
# 1. SSH bağlan
ssh yusuf@161.35.76.27

# 2. Repo güncelle
cd ~/Trade_demo
git pull origin main

# 3. systemd service kur
chmod +x deploy/install_service.sh
./deploy/install_service.sh

# 4. Bot'u başlat
sudo systemctl start genetix-bot

# 5. Durum kontrol et
./manage_bot.sh status

# 6. Logları izle (Ctrl+C ile çık)
./manage_bot.sh logs

# 7. Terminal'i kapat
exit

# 8. Yeniden bağlan ve kontrol et
ssh yusuf@161.35.76.27
./manage_bot.sh status
# Bot hala çalışıyor olmalı! ✅
```

---

## 📋 FAYDALΙ KOMUTLAR

### systemd ile:

```bash
# Başlat/Durdur/Restart
sudo systemctl start genetix-bot
sudo systemctl stop genetix-bot
sudo systemctl restart genetix-bot

# Durum
sudo systemctl status genetix-bot

# Loglar (son 100 satır)
sudo journalctl -u genetix-bot -n 100

# Canlı loglar
sudo journalctl -u genetix-bot -f

# Otomatik başlatma
sudo systemctl enable genetix-bot   # Aç
sudo systemctl disable genetix-bot  # Kapat

# Service yeniden yükle (değişiklikten sonra)
sudo systemctl daemon-reload
sudo systemctl restart genetix-bot
```

### screen ile:

```bash
# Oluştur ve başlat
screen -S genetix
cd ~/Trade_demo && python production_bot_v2.py --dry-run

# Detach (Ctrl+A D)

# Attach
screen -r genetix

# Liste
screen -ls

# Kapat
screen -X -S genetix quit
```

---

## 🔧 SORUN GİDERME

### systemd loglarında hata var:

```bash
# Son 50 satır hataları göster
sudo journalctl -u genetix-bot -n 50 --no-pager | grep ERROR

# Service'i restart et
sudo systemctl restart genetix-bot
```

### Bot çalışmıyor:

```bash
# 1. Service durumunu kontrol et
sudo systemctl status genetix-bot

# 2. Detaylı logları incele
sudo journalctl -u genetix-bot -n 200

# 3. Config dosyasını kontrol et
cat config/production_config.json

# 4. Manuel çalıştır (debug)
cd ~/Trade_demo
python production_bot_v2.py --dry-run
```

### Memory aşımı:

```bash
# Service memory limitini artır
sudo nano /etc/systemd/system/genetix-bot.service

# MemoryMax=2G -> MemoryMax=4G

# Reload ve restart
sudo systemctl daemon-reload
sudo systemctl restart genetix-bot
```

---

## ✅ BAŞARI KONTROLÜ

Bot doğru çalışıyorsa:

```bash
# 1. Service aktif
sudo systemctl is-active genetix-bot
# Output: active

# 2. Dashboard erişilebilir
curl http://localhost:8080/api/stats
# Output: JSON data

# 3. Loglar akıyor
sudo journalctl -u genetix-bot -n 5
# Output: Son 5 satır log

# 4. Process çalışıyor
ps aux | grep production_bot_v2.py
# Output: python process
```

---

## 📚 EK KAYNAKLAR

- systemd docs: `man systemd.service`
- screen docs: `man screen`
- tmux docs: `man tmux`
- Binance API status: https://testnet.binancefuture.com

---

**Son Güncelleme:** 14 Ekim 2025  
**Version:** v2.5.1  
**Durum:** Production Ready ✅
