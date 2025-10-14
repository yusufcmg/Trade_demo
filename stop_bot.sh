#!/bin/bash
# GenetiX Bot Durdurma Scripti
# Kullanım: ./stop_bot.sh

echo "🛑 GenetiX Bot durduruluyor..."

# PID dosyasından process ID'yi al
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "📊 Process ID: $BOT_PID"
    
    # Process'i durdur
    kill $BOT_PID 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Bot durduruldu (PID: $BOT_PID)"
        rm bot.pid
    else
        echo "⚠️  Process bulunamadı (muhtemelen zaten durdu)"
        rm bot.pid
    fi
else
    echo "⚠️  bot.pid dosyası bulunamadı"
    echo "🔍 Tüm bot process'leri durduruluyor..."
    pkill -f "production_bot_v2.py"
    
    if [ $? -eq 0 ]; then
        echo "✅ Bot process'leri durduruldu"
    else
        echo "✅ Çalışan bot process'i bulunamadı"
    fi
fi

echo ""
echo "📋 Kontrol:"
ps aux | grep production_bot_v2 | grep -v grep
