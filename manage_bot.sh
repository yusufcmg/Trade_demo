#!/bin/bash
#
# GenetiX Bot - Service Yönetim Script'i
# Bot'u kolayca yönetmek için
#

SERVICE_NAME="genetix-bot.service"

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_usage() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🤖 GenetiX Bot - Service Yönetimi"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "KULLANIM: ./manage_bot.sh [komut]"
    echo ""
    echo "KOMUTLAR:"
    echo "  start       - Bot'u başlat"
    echo "  stop        - Bot'u durdur"
    echo "  restart     - Bot'u yeniden başlat"
    echo "  status      - Bot durumunu göster"
    echo "  logs        - Canlı logları göster (Ctrl+C ile çık)"
    echo "  logs-tail   - Son 100 satır log"
    echo "  enable      - Otomatik başlatmayı aç"
    echo "  disable     - Otomatik başlatmayı kapat"
    echo "  update      - Git pull + restart"
    echo "  health      - Sağlık kontrolü"
    echo ""
}

check_service_exists() {
    if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        echo -e "${RED}❌ Service bulunamadı!${NC}"
        echo "   Önce install_service.sh çalıştırın."
        exit 1
    fi
}

case "$1" in
    start)
        check_service_exists
        echo -e "${BLUE}🚀 Bot başlatılıyor...${NC}"
        sudo systemctl start $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
        
    stop)
        check_service_exists
        echo -e "${YELLOW}🛑 Bot durduruluyor...${NC}"
        sudo systemctl stop $SERVICE_NAME
        sleep 1
        echo -e "${GREEN}✅ Bot durduruldu${NC}"
        ;;
        
    restart)
        check_service_exists
        echo -e "${BLUE}🔄 Bot yeniden başlatılıyor...${NC}"
        sudo systemctl restart $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
        
    status)
        check_service_exists
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
        
    logs)
        check_service_exists
        echo -e "${BLUE}📋 Canlı loglar (Ctrl+C ile çıkış)${NC}"
        echo ""
        sudo journalctl -u $SERVICE_NAME -f
        ;;
        
    logs-tail)
        check_service_exists
        echo -e "${BLUE}📋 Son 100 satır log:${NC}"
        echo ""
        sudo journalctl -u $SERVICE_NAME -n 100 --no-pager
        ;;
        
    enable)
        check_service_exists
        echo -e "${GREEN}✅ Otomatik başlatma aktif${NC}"
        sudo systemctl enable $SERVICE_NAME
        ;;
        
    disable)
        check_service_exists
        echo -e "${YELLOW}⚠️  Otomatik başlatma kapatıldı${NC}"
        sudo systemctl disable $SERVICE_NAME
        ;;
        
    update)
        check_service_exists
        echo -e "${BLUE}📥 Kod güncelleniyor...${NC}"
        git pull origin main
        echo ""
        echo -e "${BLUE}🔄 Bot yeniden başlatılıyor...${NC}"
        sudo systemctl restart $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
        
    health)
        check_service_exists
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🏥 Sağlık Kontrolü"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Service durumu
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo -e "${GREEN}✅ Service: ÇALIŞIYOR${NC}"
        else
            echo -e "${RED}❌ Service: DURDURULMUŞ${NC}"
        fi
        
        # Otomatik başlatma
        if systemctl is-enabled --quiet $SERVICE_NAME; then
            echo -e "${GREEN}✅ Otomatik başlatma: AKTİF${NC}"
        else
            echo -e "${YELLOW}⚠️  Otomatik başlatma: KAPALI${NC}"
        fi
        
        # Memory kullanımı
        MEM=$(systemctl show $SERVICE_NAME -p MemoryCurrent --value 2>/dev/null)
        if [ -n "$MEM" ] && [ "$MEM" != "[not set]" ]; then
            MEM_MB=$((MEM / 1024 / 1024))
            echo -e "${BLUE}📊 Memory: ${MEM_MB} MB${NC}"
        fi
        
        # Uptime
        UPTIME=$(systemctl show $SERVICE_NAME -p ActiveEnterTimestamp --value 2>/dev/null)
        if [ -n "$UPTIME" ]; then
            echo -e "${BLUE}⏱️  Başlangıç: ${UPTIME}${NC}"
        fi
        
        # Son restart
        LAST_RESTART=$(systemctl show $SERVICE_NAME -p NRestarts --value 2>/dev/null)
        if [ -n "$LAST_RESTART" ]; then
            echo -e "${BLUE}🔄 Restart sayısı: ${LAST_RESTART}${NC}"
        fi
        
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Son hatalar
        ERROR_COUNT=$(sudo journalctl -u $SERVICE_NAME --since "10 minutes ago" | grep -c "ERROR" || true)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Son 10 dakikada ${ERROR_COUNT} hata${NC}"
            echo "   Son hataları görmek için: ./manage_bot.sh logs-tail"
        else
            echo -e "${GREEN}✅ Son 10 dakikada hata yok${NC}"
        fi
        
        echo ""
        ;;
        
    *)
        show_usage
        exit 1
        ;;
esac
