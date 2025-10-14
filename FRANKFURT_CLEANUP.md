# 🧹 Frankfurt Sunucu Temizleme Talimatları

## 🎯 Amaç

Frankfurt sunucusunda çalışan bot'u tamamen durdurup temizlemek.

## 📋 Frankfurt'ta Çalıştırılacak Komutlar

### Adım 1: Bot'u Durdur

```bash
# systemd servisi durdur
sudo systemctl stop genetix-bot

# Servis durumunu kontrol
sudo systemctl status genetix-bot
# Beklenen: "Active: inactive (dead)"

# Otomatik başlatmayı devre dışı bırak
sudo systemctl disable genetix-bot
```

### Adım 2: Process Kontrolü

```bash
# Çalışan bot process'i kontrol et
ps aux | grep production_bot

# Eğer hala çalışan process varsa, durdur:
pkill -f production_bot_v2.py

# Tekrar kontrol
ps aux | grep production_bot
# Hiçbir şey görmemeli (sadece grep komutu görünür)
```

### Adım 3: systemd Service Dosyasını Kaldır (Opsiyonel)

```bash
# Service dosyasını sil
sudo rm /etc/systemd/system/genetix-bot.service

# systemd'yi yeniden yükle
sudo systemctl daemon-reload

# Service'in kaldırıldığını kontrol et
systemctl list-units --type=service | grep genetix
# Hiçbir şey görmemeli
```

### Adım 4: Port Kontrolü (Opsiyonel)

```bash
# Dashboard portunu kontrol et (8080)
sudo lsof -i :8080

# Eğer bir şey kullanıyorsa, kill et
sudo fof -ti:8080 | xargs kill -9
```

### Adım 5: Log Temizliği (Opsiyonel)

```bash
# Log dosyalarını temizle (YEDEK ALDIYSAN)
cd ~/Trade_demo

# Sadece son logları sakla
find logs/production -name "*.log" -mtime +7 -delete

# VEYA tamamen sil
# rm -rf logs/production/*
```

### Adım 6: Final Kontrol

```bash
# Tüm kontroller
echo "=== Process Kontrolü ==="
ps aux | grep production_bot | grep -v grep

echo "=== Service Kontrolü ==="
sudo systemctl status genetix-bot 2>&1 | head -3

echo "=== Port Kontrolü ==="
sudo lsof -i :8080

echo ""
echo "✅ Eğer yukarıdaki komutlar boş/hata döndüyse, temizlik tamamlandı!"
```

---

## 🎯 Beklenen Sonuç

Tüm adımlardan sonra:

✅ **Process:** Hiçbir bot process'i çalışmıyor  
✅ **Service:** genetix-bot servisi yok veya inactive  
✅ **Port:** 8080 portu boş  
✅ **Logs:** Opsiyonel olarak temizlendi

---

## 💡 Not

Bot dosyalarını ve kodu silmiyoruz, sadece çalışan process'leri ve servisleri temizliyoruz. İleride tekrar başlatmak isterseniz:

```bash
cd ~/Trade_demo
git pull origin main
nohup python production_bot_v2.py --dry-run > bot.log 2>&1 &
```

---

## ✅ Temizlik Tamamlandı mı?

Şu komutu çalıştırın:

```bash
ps aux | grep -E "production_bot|genetix" | grep -v grep
```

**Hiçbir şey görmemelisiniz!**

---

**Tarih:** 14 Ekim 2025  
**Amaç:** Lokal PC'de test için Frankfurt'ı temizleme
