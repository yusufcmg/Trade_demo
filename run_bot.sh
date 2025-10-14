#!/bin/bash
# GenetiX Bot Başlatma Scripti
# Kullanım: ./run_bot.sh

# Script'in bulunduğu dizine git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 GenetiX Bot başlatılıyor..."
echo "📁 Dizin: $(pwd)"
echo "🕐 Zaman: $(date)"
echo ""

# Virtual environment aktif et (eğer varsa)
if [ -d "venv" ]; then
    echo "🐍 Virtual environment aktif ediliyor..."
    source venv/bin/activate
fi

# Eski bot process'ini durdur
echo "🛑 Eski bot process'leri kontrol ediliyor..."
pkill -f "production_bot_v2.py" 2>/dev/null
sleep 2

# Log dizinini oluştur
mkdir -p logs/production results/production

# Bot'u arka planda başlat
echo "🚀 Bot arka planda başlatılıyor..."
nohup python production_bot_v2.py --dry-run > logs/production/nohup_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Process ID'yi kaydet
BOT_PID=$!
echo $BOT_PID > bot.pid

echo ""
echo "✅ Bot başlatıldı!"
echo "📊 Process ID: $BOT_PID"
echo "📝 Log dosyası: logs/production/nohup_$(date +%Y%m%d_%H%M%S).log"
echo "🌐 Dashboard: http://localhost:8080"
echo ""
echo "📋 Kontrol komutları:"
echo "   Logları izle:     tail -f logs/production/nohup_*.log"
echo "   Bot durumu:       ps aux | grep production_bot_v2"
echo "   Bot'u durdur:     kill $BOT_PID   veya   ./stop_bot.sh"
echo ""
