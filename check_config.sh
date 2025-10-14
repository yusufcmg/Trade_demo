#!/bin/bash
# GenetiX Bot - Config Doğrulama

# Script'in bulunduğu dizine git
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔍 GenetiX Bot - Konfigürasyon Kontrolü"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

CONFIG_FILE="config/production_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config dosyası bulunamadı: $CONFIG_FILE"
    exit 1
fi

echo "📄 Config Dosyası: $CONFIG_FILE"
echo ""

# Dry run durumu
DRY_RUN=$(cat $CONFIG_FILE | grep -A2 '"testnet"' | grep '"dry_run"' | awk -F': ' '{print $2}' | tr -d ',')
TESTNET_ENABLED=$(cat $CONFIG_FILE | grep -A2 '"testnet"' | grep '"enabled"' | awk -F': ' '{print $2}' | tr -d ',')

echo "🔴 İŞLEM MODU:"
if [ "$DRY_RUN" = "false" ]; then
    echo "   ✅ dry_run: false → GERÇEK İŞLEMLER AÇILACAK!"
else
    echo "   🧪 dry_run: true → Test modu (emir gönderilmez)"
fi
echo ""

echo "🌐 NETWORK:"
if [ "$TESTNET_ENABLED" = "true" ]; then
    echo "   ✅ Testnet AKTIF (https://testnet.binancefuture.com)"
    echo "   💡 Gerçek para kullanılmıyor, testnet paraları"
else
    echo "   🔴 MAINNET AKTIF (Gerçek para!)"
fi
echo ""

# Risk ayarları
echo "⚙️  RİSK YÖNETİMİ:"
cat $CONFIG_FILE | grep -A8 '"trading_config"' | tail -7 | while read line; do
    echo "   $line"
done
echo ""

echo "🛡️  KORUNMA AYARLARI:"
cat $CONFIG_FILE | grep -A12 '"risk_management"' | tail -11 | while read line; do
    echo "   $line"
done
echo ""

# Semboller
echo "📊 TİCARET SEMBOLLERI:"
SYMBOLS=$(cat $CONFIG_FILE | grep -A10 '"symbols_to_trade"' | grep 'USDT' | tr -d '", ' | head -8)
COUNT=0
for symbol in $SYMBOLS; do
    COUNT=$((COUNT + 1))
    echo "   $COUNT. $symbol"
done
echo ""

# Özet
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📋 ÖZET"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ "$DRY_RUN" = "false" ] && [ "$TESTNET_ENABLED" = "true" ]; then
    echo "🟢 DURUM: TESTNET GERÇEK İŞLEM MODU"
    echo "   ✅ Emirler Binance Testnet'e gönderilecek"
    echo "   ✅ Gerçek para riski YOK"
    echo "   ✅ Canlı piyasa verileri kullanılacak"
    echo "   ⚠️  İşlemler gerçek gibi takip edilecek"
elif [ "$DRY_RUN" = "false" ] && [ "$TESTNET_ENABLED" = "false" ]; then
    echo "🔴 DİKKAT: MAINNET GERÇEK İŞLEM MODU!"
    echo "   ⚠️  Gerçek para kullanılıyor!"
    echo "   ⚠️  Kayıp riski var!"
    echo "   🚨 Çok dikkatli olun!"
elif [ "$DRY_RUN" = "true" ]; then
    echo "🧪 DURUM: DRY RUN TEST MODU"
    echo "   ✅ Hiçbir emir gönderilmeyecek"
    echo "   ✅ Sadece simülasyon"
    echo "   💡 Gerçek işlem için: dry_run: false yapın"
fi

echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Onay
if [ "$DRY_RUN" = "false" ]; then
    echo "⚠️  GERÇEK İŞLEM MODU AKTİF!"
    echo "   Başlatmak için: ./run_bot_live.sh"
    echo "   İptal için: Ctrl+C"
else
    echo "✅ Güvenli test modu aktif"
    echo "   Başlatmak için: ./run_bot.sh"
fi

echo ""
