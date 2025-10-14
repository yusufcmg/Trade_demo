#!/bin/bash
#
# GenetiX Bot - systemd Service Kurulum Script'i
# Terminal kapansa bile bot çalışmaya devam eder
#

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 GenetiX Trading Bot - systemd Service Kurulumu"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Root kontrolü
if [ "$EUID" -eq 0 ]; then 
    echo "❌ Bu script'i root olarak çalıştırmayın!"
    echo "   Normal kullanıcı ile çalıştırın, sudo şifresi istenecek."
    exit 1
fi

# Dizin kontrolü
if [ ! -f "production_bot_v2.py" ]; then
    echo "❌ Hata: production_bot_v2.py bulunamadı!"
    echo "   Lütfen Trade_demo dizininde çalıştırın."
    exit 1
fi

BOT_DIR=$(pwd)
SERVICE_FILE="deploy/genetix-bot.service"
SERVICE_NAME="genetix-bot.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "📂 Bot dizini: $BOT_DIR"
echo "📄 Service dosyası: $SERVICE_FILE"
echo ""

# Service dosyası kontrolü
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service dosyası bulunamadı: $SERVICE_FILE"
    exit 1
fi

# Log dizini oluştur
echo "📁 Log dizini oluşturuluyor..."
mkdir -p logs/production
chmod 755 logs/production

# Service dosyasını kopyala
echo "📋 Service dosyası kopyalanıyor..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"

# systemd reload
echo "🔄 systemd yeniden yükleniyor..."
sudo systemctl daemon-reload

# Service'i etkinleştir (boot'ta otomatik başlasın)
echo "✅ Service etkinleştiriliyor..."
sudo systemctl enable $SERVICE_NAME

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Kurulum tamamlandı!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 KULLANIM:"
echo ""
echo "   # Bot'u başlat"
echo "   sudo systemctl start genetix-bot"
echo ""
echo "   # Bot durumunu kontrol et"
echo "   sudo systemctl status genetix-bot"
echo ""
echo "   # Logları görüntüle (son 50 satır)"
echo "   sudo journalctl -u genetix-bot -n 50 -f"
echo ""
echo "   # Bot'u durdur"
echo "   sudo systemctl stop genetix-bot"
echo ""
echo "   # Bot'u yeniden başlat"
echo "   sudo systemctl restart genetix-bot"
echo ""
echo "   # Bot'u devre dışı bırak (boot'ta başlamasın)"
echo "   sudo systemctl disable genetix-bot"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚙️  ÖNEMLİ NOTLAR:"
echo ""
echo "   • Terminal kapatıldığında bot ÇALIŞMAYA DEVAM EDER"
echo "   • Sunucu yeniden başladığında bot OTOMATİK BAŞLAR"
echo "   • Bot crash olursa 10 saniye sonra OTOMATİK YENİDEN BAŞLAR"
echo "   • Loglar: logs/production/ dizininde"
echo "   • Dashboard: http://161.35.76.27:8080"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Şimdi bot'u başlatmak ister misiniz? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Bot başlatılıyor..."
    sudo systemctl start genetix-bot
    sleep 2
    sudo systemctl status genetix-bot
fi
