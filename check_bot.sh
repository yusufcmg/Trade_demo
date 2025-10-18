#!/bin/bash
# GenetiX Bot Durum Kontrolü
# Kullanım: ./check_bot.sh

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔍 GenetiX Bot Durum Kontrolü"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# 1. Process kontrolü
echo "📊 Process Durumu:"
if ps aux | grep -v grep | grep production_bot_v2.py > /dev/null; then
    echo "✅ Bot ÇALIŞIYOR"
    ps aux | grep -v grep | grep production_bot_v2.py | awk '{print "   PID: " $2 " | CPU: " $3 "% | MEM: " $4 "% | Uptime: " $10}'
else
    echo "❌ Bot ÇALIŞMIYOR"
fi
echo ""

# 2. PID dosyası kontrolü
echo "📄 PID Dosyası:"
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "✅ bot.pid mevcut (PID: $BOT_PID)"
    
    # PID hala çalışıyor mu?
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "✅ Process aktif"
    else
        echo "⚠️  PID dosyası var ama process çalışmıyor"
    fi
else
    echo "❌ bot.pid bulunamadı"
fi
echo ""

# 3. Dashboard kontrolü
echo "🌐 Dashboard Durumu:"
if lsof -i :8443 > /dev/null 2>&1; then
    echo "✅ Dashboard AKTIF (http://localhost:8443)"
    lsof -i :8443 | grep LISTEN | awk '{print "   Port 8443: " $1 " (PID: " $2 ")"}'
else
    echo "❌ Dashboard kapalı (Port 8443 boş)"
fi
echo ""

# 4. Son log kayıtları
echo "📝 Son Log Kayıtları (son 10 satır):"
LOG_FILE=$(ls -t logs/production/*.log 2>/dev/null | head -1)
if [ -n "$LOG_FILE" ]; then
    echo "   Dosya: $LOG_FILE"
    echo "   ─────────────────────────────────────────────────────────────────"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
else
    echo "❌ Log dosyası bulunamadı"
fi
echo ""

# 5. Son işlem kontrolü
echo "💼 Son İşlemler:"
RESULT_FILE=$(ls -t results/production/*.json 2>/dev/null | head -1)
if [ -n "$RESULT_FILE" ]; then
    TRADE_COUNT=$(cat "$RESULT_FILE" | grep -o '"trades"' | wc -l)
    echo "✅ Results dosyası: $RESULT_FILE"
    echo "   İşlem sayısı: ~$TRADE_COUNT"
else
    echo "❌ Results dosyası bulunamadı"
fi
echo ""

# 6. Hızlı istatistikler
echo "📈 Hızlı İstatistikler:"
if [ -n "$LOG_FILE" ]; then
    ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
    WARNING_COUNT=$(grep -c "WARNING" "$LOG_FILE" 2>/dev/null || echo "0")
    SIGNAL_COUNT=$(grep -c "DRY RUN:" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo "   ✅ INFO kayıtları: $(grep -c "INFO" "$LOG_FILE" 2>/dev/null || echo "0")"
    echo "   ⚠️  WARNING: $WARNING_COUNT"
    echo "   ❌ ERROR: $ERROR_COUNT"
    echo "   🎯 Sinyal sayısı: $SIGNAL_COUNT"
fi
echo ""

# 7. Komutlar
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📋 Yardımcı Komutlar:"
echo "   Bot'u başlat:     ./run_bot.sh"
echo "   Bot'u durdur:     ./stop_bot.sh"
echo "   Logları izle:     tail -f $LOG_FILE"
echo "   Dashboard:        http://localhost:8443"
echo "═══════════════════════════════════════════════════════════════════════════"
