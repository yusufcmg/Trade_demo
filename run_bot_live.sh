#!/bin/bash
# GenetiX Bot - GERÇEK İŞLEM MODU BAŞLATMA
# ⚠️  DİKKAT: Bu script GERÇEK işlem açacak!

# Script'in bulunduğu dizine git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Config dosyasından ayarları dinamik olarak oku
CONFIG_FILE="config/production_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ HATA: Config dosyası bulunamadı: $CONFIG_FILE"
    exit 1
fi

# jq komutunun varlığını kontrol et
if ! command -v jq &> /dev/null; then
    echo "❌ HATA: 'jq' komutu bulunamadı. Lütfen 'sudo apt install jq -y' ile kurun."
    exit 1
fi

# Ayarları config'den al
MAX_POS=$(jq -r '.trading_config.max_positions' "$CONFIG_FILE")
BASE_PERCENT=$(jq -r '.trading_config.base_position_percent' "$CONFIG_FILE")
LEVERAGE=$(jq -r '.trading_config.leverage' "$CONFIG_FILE")
STOP_LOSS=$(jq -r '.trading_config.stop_loss_percent' "$CONFIG_FILE")
MAX_DAILY_LOSS=$(jq -r '.risk_management.max_daily_loss_usd' "$CONFIG_FILE")
CIRCUIT_BREAKER=$(jq -r '.risk_management.circuit_breaker.max_consecutive_losses' "$CONFIG_FILE")

echo "═══════════════════════════════════════════════════════════════════════════"
echo "⚠️  GenetiX Bot - GERÇEK İŞLEM MODU"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "🔴 DİKKAT: Bot GERÇEK işlem açacak şekilde yapılandırıldı!"
echo ""
echo "📋 Mevcut Ayarlar (config.json'dan okundu):"
echo "   • Testnet: AKTIF (https://testnet.binancefuture.com)"
echo "   • Dry Run: KAPALI (Gerçek emirler gönderilecek)"
echo "   • Maksimum Pozisyon: $MAX_POS"
echo "   • Pozisyon Büyüklüğü: Balance'ın %$BASE_PERCENT'i"
echo "   • Leverage: ${LEVERAGE}x"
echo "   • Stop Loss: %$STOP_LOSS"
echo "   • Max Daily Loss: $$MAX_DAILY_LOSS"
echo "   • Circuit Breaker: $CIRCUIT_BREAKER ardışık zarar"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Kullanıcıdan onay al
read -p "🤔 Devam etmek istediğinize EMİN MİSİNİZ? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ İşlem iptal edildi."
    exit 1
fi

echo ""
read -p "🔐 İkinci onay: 'START' yazın: " second_confirm

if [ "$second_confirm" != "START" ]; then
    echo "❌ İşlem iptal edildi."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚀 Bot başlatılıyor..."
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Eski bot'u durdur
echo "🛑 Eski bot process'leri durduruluyor..."
pkill -f "production_bot_v2.py" 2>/dev/null
sleep 2

# Virtual environment aktif et
if [ -d "venv" ]; then
    echo "🐍 Virtual environment aktif ediliyor..."
    source venv/bin/activate
fi

# Log dizinini oluştur
mkdir -p logs/production results/production

# Bot'u başlat
echo "🔴 LIVE TRADING MODU başlatılıyor..."
echo ""
nohup python production_bot_v2.py > logs/production/nohup_live_$(date +%Y%m%d_%H%M%S).log 2>&1 &

BOT_PID=$!
echo $BOT_PID > bot.pid

sleep 3

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ Bot başlatıldı!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Process ID: $BOT_PID"
echo "📝 Log: logs/production/nohup_live_$(date +%Y%m%d_%H%M%S).log"
echo "🌐 Dashboard: http://161.35.76.27:8443"
echo ""
echo "⚠️  ÖNEMLİ HATIRLATMA:"
echo "   • Bot GERÇEK emirler gönderecek!"
echo "   • Sürekli izleyin: ./check_bot.sh"
echo "   • İlk 30 dakika yakın takip edin!"
echo "   • Beklenmedik davranış görürseniz: ./stop_bot.sh"
echo ""
echo "📋 İzleme Komutları:"
echo "   tail -f logs/production/nohup_live_*.log    # Canlı log"
echo "   ./check_bot.sh                               # Durum kontrolü"
echo "   curl http://localhost:8443/api/positions     # Açık pozisyonlar"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"