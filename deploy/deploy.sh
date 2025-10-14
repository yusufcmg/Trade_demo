#!/bin/bash
################################################################################
# GenetiX Trading Bot - Ubuntu Deployment Script
# 
# Bu script Ubuntu sunucuda production bot'u kurar ve başlatır
#
# KULLANIM:
#   chmod +x deploy.sh
#   ./deploy.sh install      # İlk kurulum
#   ./deploy.sh update       # Güncelleme
#   ./deploy.sh start        # Bot'u başlat
#   ./deploy.sh stop         # Bot'u durdur
#   ./deploy.sh restart      # Bot'u yeniden başlat
#   ./deploy.sh status       # Durum kontrolü
#   ./deploy.sh logs         # Log'ları göster
################################################################################

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Proje ayarları
PROJECT_NAME="genetix"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PRODUCTION_DIR="${PROJECT_DIR}/production"
VENV_DIR="${PROJECT_DIR}/venv"
SERVICE_NAME="genetix-bot"
PYTHON_VERSION="3.10"

# Fonksiyonlar
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          🤖 GenetiX Production Bot Deployment               ║"
    echo "║              Ubuntu Server Installation                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Bu scripti root olarak çalıştırmayın!"
        print_info "Kullanım: ./deploy.sh [command]"
        exit 1
    fi
}

check_ubuntu() {
    if [[ ! -f /etc/lsb-release ]]; then
        print_error "Bu script sadece Ubuntu için tasarlandı"
        exit 1
    fi
    
    source /etc/lsb-release
    print_info "Ubuntu ${DISTRIB_RELEASE} tespit edildi"
}

install_system_dependencies() {
    print_info "Sistem bağımlılıkları kuruluyor..."
    
    sudo apt update
    sudo apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python3-pip \
        git \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        wget \
        curl \
        htop \
        screen
    
    print_success "Sistem bağımlılıkları kuruldu"
}

install_talib() {
    print_info "TA-Lib kuruluyor..."
    
    # TA-Lib C library
    if [[ ! -f /usr/local/lib/libta_lib.so ]]; then
        cd /tmp
        wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
        tar -xzf ta-lib-0.4.0-src.tar.gz
        cd ta-lib/
        ./configure --prefix=/usr
        make
        sudo make install
        cd ..
        rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
        
        print_success "TA-Lib kuruldu"
    else
        print_warning "TA-Lib zaten kurulu"
    fi
}

setup_project() {
    print_info "Proje dizini hazırlanıyor..."
    
    # Proje dizini oluştur
    if [[ ! -d "$PROJECT_DIR" ]]; then
        mkdir -p "$(dirname $PROJECT_DIR)"
        
        print_info "Git reposu klonlanıyor..."
        git clone https://github.com/yusufcmg/NEW--GenetiX-Trading-System.git "$(dirname $PROJECT_DIR)/${PROJECT_NAME}"
        
        print_success "Proje klonlandı"
    else
        print_warning "Proje dizini zaten mevcut"
    fi
    
    cd "$PROJECT_DIR"
}

setup_venv() {
    print_info "Virtual environment oluşturuluyor..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python${PYTHON_VERSION} -m venv "$VENV_DIR"
        print_success "Virtual environment oluşturuldu"
    else
        print_warning "Virtual environment zaten mevcut"
    fi
    
    # Activate venv
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Pip güncellendi"
}

install_python_deps() {
    print_info "Python bağımlılıkları kuruluyor..."
    
    source "${VENV_DIR}/bin/activate"
    
    cd "$PROJECT_DIR"
    
    # Requirements install
    if [[ -f requirements.txt ]]; then
        pip install -r requirements.txt
        print_success "Requirements kuruldu"
    fi
    
    # TA-Lib Python wrapper
    pip install TA-Lib
    
    print_success "Python bağımlılıkları kuruldu"
}

setup_config() {
    print_info "Konfigürasyon hazırlanıyor..."
    
    CONFIG_DIR="${PROJECT_DIR}/config"
    mkdir -p "$CONFIG_DIR"
    
    if [[ ! -f "${CONFIG_DIR}/production_config.json" ]]; then
        print_warning "production_config.json bulunamadı"
        print_info "Lütfen API credentials'larınızı config/production_config.json dosyasına ekleyin"
        
        # İlk çalıştırmada otomatik oluşturulacak
        print_info "Bot ilk çalıştırıldığında template oluşturulacak"
    else
        print_success "Config dosyası mevcut"
    fi
}

setup_directories() {
    print_info "Dizinler oluşturuluyor..."
    
    mkdir -p "${PROJECT_DIR}/logs/production"
    mkdir -p "${PROJECT_DIR}/results/production"
    mkdir -p "${PROJECT_DIR}/data"
    
    print_success "Dizinler oluşturuldu"
}

install_service() {
    print_info "Systemd service kuruluyor..."
    
    SERVICE_FILE="${PROJECT_DIR}/deploy/genetix-bot.service"
    
    if [[ ! -f "$SERVICE_FILE" ]]; then
        print_error "Service dosyası bulunamadı: $SERVICE_FILE"
        exit 1
    fi
    
    # Service dosyasını kopyala
    sudo cp "$SERVICE_FILE" "/etc/systemd/system/${SERVICE_NAME}.service"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable "${SERVICE_NAME}.service"
    
    print_success "Systemd service kuruldu"
}

setup_logrotate() {
    print_info "Log rotation kuruluyor..."
    
    LOGROTATE_CONFIG="/etc/logrotate.d/${SERVICE_NAME}"
    
    sudo tee "$LOGROTATE_CONFIG" > /dev/null <<EOF
${PROJECT_DIR}/logs/production/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload ${SERVICE_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF
    
    print_success "Log rotation kuruldu"
}

install_full() {
    print_header
    check_root
    check_ubuntu
    
    print_info "Tam kurulum başlıyor..."
    
    install_system_dependencies
    install_talib
    setup_project
    setup_venv
    install_python_deps
    setup_config
    setup_directories
    install_service
    setup_logrotate
    
    print_success "Kurulum tamamlandı!"
    echo ""
    print_info "Sonraki adımlar:"
    echo "  1. Config düzenle: nano ${PROJECT_DIR}/config/production_config.json"
    echo "  2. Bot'u başlat:    ./deploy.sh start"
    echo "  3. Durumu kontrol:  ./deploy.sh status"
    echo "  4. Log'ları izle:   ./deploy.sh logs"
}

update_project() {
    print_info "Proje güncelleniyor..."
    
    cd "$PROJECT_DIR"
    git pull origin main
    
    source "${VENV_DIR}/bin/activate"
    pip install -r requirements.txt --upgrade
    
    print_success "Proje güncellendi"
}

start_bot() {
    print_info "Bot başlatılıyor..."
    
    sudo systemctl start "${SERVICE_NAME}.service"
    sleep 2
    
    if sudo systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        print_success "Bot başarıyla başlatıldı"
        show_status
    else
        print_error "Bot başlatılamadı"
        sudo journalctl -u "${SERVICE_NAME}.service" -n 50 --no-pager
    fi
}

stop_bot() {
    print_info "Bot durduruluyor..."
    
    sudo systemctl stop "${SERVICE_NAME}.service"
    sleep 2
    
    if ! sudo systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        print_success "Bot durduruldu"
    else
        print_error "Bot durdurulamadı"
    fi
}

restart_bot() {
    print_info "Bot yeniden başlatılıyor..."
    
    sudo systemctl restart "${SERVICE_NAME}.service"
    sleep 2
    
    if sudo systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        print_success "Bot yeniden başlatıldı"
        show_status
    else
        print_error "Bot başlatılamadı"
    fi
}

show_status() {
    print_info "Bot durumu:"
    echo ""
    
    sudo systemctl status "${SERVICE_NAME}.service" --no-pager -l
    
    echo ""
    print_info "Son log girişleri:"
    sudo journalctl -u "${SERVICE_NAME}.service" -n 10 --no-pager
}

show_logs() {
    print_info "Bot log'ları (son 100 satır):"
    echo ""
    
    sudo journalctl -u "${SERVICE_NAME}.service" -n 100 --no-pager -f
}

show_help() {
    print_header
    echo "KULLANIM: ./deploy.sh [KOMUT]"
    echo ""
    echo "KOMUTLAR:"
    echo "  install     - Tam kurulum (ilk defa)"
    echo "  update      - Projeyi güncelle"
    echo "  start       - Bot'u başlat"
    echo "  stop        - Bot'u durdur"
    echo "  restart     - Bot'u yeniden başlat"
    echo "  status      - Durum kontrolü"
    echo "  logs        - Log'ları göster (real-time)"
    echo "  help        - Bu yardımı göster"
    echo ""
    echo "ÖRNEKLER:"
    echo "  ./deploy.sh install      # İlk kurulum"
    echo "  ./deploy.sh start        # Bot'u başlat"
    echo "  ./deploy.sh logs         # Log'ları izle"
}

# Ana fonksiyon
main() {
    case "${1:-help}" in
        install)
            install_full
            ;;
        update)
            update_project
            ;;
        start)
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Bilinmeyen komut: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Script başlat
main "$@"
