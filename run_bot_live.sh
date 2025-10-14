#!/bin/bash
# GenetiX Bot - GERÇEK İŞLEM MODU BAŞLATMA
# ⚠️  DİKKAT: Bu script GERÇEK işlem açacak!

# Script'in bulunduğu dizine git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "⚠️  GenetiX Bot - GERÇEK İŞLEM MODU"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "🔴 DİKKAT: Bot GERÇEK işlem açacak şekilde yapılandırıldı!"
echo ""
echo "📋 Mevcut Ayarlar:"
echo "   • Testnet: AKTIF (https://testnet.binancefuture.com)"
echo "   • Dry Run: KAPALI (Gerçek emirler gönderilecek)"
echo "   • Maksimum Pozisyon: 3"
echo "   • Pozisyon Büyüklüğü: Balance'ın %5'i"
echo "   • Leverage: 3x"
echo "   • Stop Loss: %2"
echo "   • Max Daily Loss: $50"
echo "   • Circuit Breaker: 3 ardışık zarar"
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
echo "🌐 Dashboard: http://localhost:8080"
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
echo "   curl http://localhost:8080/api/positions     # Açık pozisyonlar"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
