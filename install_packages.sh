#!/bin/bash
# Eksik paketleri kurma scripti

echo "📦 Eksik Python paketlerini kuruyorum..."
echo ""

# Virtual environment aktif mi kontrol et
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment aktif değil!"
    echo "Aktif ediliyor..."
    source venv/bin/activate
fi

echo "🔧 Gerekli paketler kuruluyor..."
echo ""

# Temel paketler
pip install --upgrade pip

# Eksik paketler
pip install requests
pip install websocket-client
pip install flask
pip install flask-cors

# Tüm requirements
pip install -r requirements.txt

echo ""
echo "✅ Tüm paketler kuruldu!"
echo ""
echo "📋 Kurulu paketler:"
pip list | grep -E "(requests|websocket|flask|pandas|numpy|ta)"
echo ""
echo "🚀 Şimdi bot'u başlatabilirsin: ./run_bot_live.sh"
