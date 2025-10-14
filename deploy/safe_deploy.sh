#!/bin/bash
################################################################################
# GenetiX Trading Bot v2.3.0 - Safe Deployment Script
#
# Mevcut sistemleri etkilemeden güvenli deployment
# Port isolation, process management, rollback support
#
# KULLANIM:
#   chmod +x safe_deploy.sh
#   ./safe_deploy.sh check       # Sistem kontrolü
#   ./safe_deploy.sh install     # İlk kurulum
#   ./safe_deploy.sh start       # Bot'u başlat
#   ./safe_deploy.sh stop        # Bot'u durdur
#   ./safe_deploy.sh restart     # Yeniden başlat
#   ./safe_deploy.sh status      # Durum kontrolü
#   ./safe_deploy.sh logs        # Log'ları göster
#   ./safe_deploy.sh rollback    # Geri alma
################################################################################

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Konfigürasyon
PROJECT_NAME="genetix-v2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PRODUCTION_DIR="${PROJECT_DIR}/production"
VENV_DIR="${PROJECT_DIR}/venv"
SERVICE_NAME="genetix-bot-v2"
BOT_SCRIPT="production_bot_v2.py"
CONFIG_FILE="production/config/production_config.json"
DASHBOARD_PORT=8080  # Default port
PYTHON_VERSION="python3"

# Backup directory
BACKUP_DIR="${PROJECT_DIR}/backups"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Log file
DEPLOY_LOG="${PROJECT_DIR}/logs/deployment_${BACKUP_TIMESTAMP}.log"

#===============================================================================
# UTILITY FUNCTIONS
#===============================================================================

print_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║       🤖 GenetiX Trading Bot v2.3.0 - Safe Deployment               ║
║                                                                      ║
║       Multi-Timeframe Validated Strategy                            ║
║       Production-Ready | Zero Downtime | Rollback Support           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

log() {
    echo -e "$1" | tee -a "$DEPLOY_LOG"
}

success() {
    log "${GREEN}✅ $1${NC}"
}

error() {
    log "${RED}❌ ERROR: $1${NC}"
}

warning() {
    log "${YELLOW}⚠️  WARNING: $1${NC}"
}

info() {
    log "${BLUE}ℹ️  $1${NC}"
}

step() {
    log "${CYAN}▶ $1${NC}"
}

#===============================================================================
# SAFETY CHECKS
#===============================================================================

check_prerequisites() {
    step "Checking prerequisites..."
    
    # Python check
    if ! command -v ${PYTHON_VERSION} &> /dev/null; then
        error "Python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    python_ver=$(${PYTHON_VERSION} --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    info "Python version: ${python_ver}"
    
    # Git check
    if ! command -v git &> /dev/null; then
        warning "Git not found. Install with: sudo apt install git"
    fi
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error "Don't run this script as root!"
        exit 1
    fi
    
    success "Prerequisites OK"
}

check_port_conflicts() {
    step "Checking port conflicts..."
    
    # Check if port is in use
    if lsof -Pi :${DASHBOARD_PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        warning "Port ${DASHBOARD_PORT} is already in use"
        local pid=$(lsof -t -i:${DASHBOARD_PORT})
        local process=$(ps -p $pid -o comm=)
        warning "Process using port: ${process} (PID: ${pid})"
        
        read -p "Continue anyway? This will use a different port. (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        
        # Find alternative port
        DASHBOARD_PORT=$((DASHBOARD_PORT + 1))
        info "Using alternative port: ${DASHBOARD_PORT}"
    else
        success "Port ${DASHBOARD_PORT} is available"
    fi
}

check_running_services() {
    step "Checking for running GenetiX services..."
    
    # Check systemd service
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        warning "Service ${SERVICE_NAME} is running"
        info "Run './safe_deploy.sh stop' first, or it will be stopped automatically"
    fi
    
    # Check for python processes
    if pgrep -f "production_bot" >/dev/null; then
        warning "Found running bot processes"
        ps aux | grep "[p]roduction_bot" | head -5
    fi
    
    success "Service check complete"
}

check_disk_space() {
    step "Checking disk space..."
    
    available=$(df -BG "${PROJECT_DIR}" | tail -1 | awk '{print $4}' | sed 's/G//')
    
    if [ "$available" -lt 1 ]; then
        error "Not enough disk space (${available}GB available, need at least 1GB)"
        exit 1
    fi
    
    success "Disk space OK (${available}GB available)"
}

#===============================================================================
# BACKUP & ROLLBACK
#===============================================================================

create_backup() {
    step "Creating backup..."
    
    mkdir -p "${BACKUP_DIR}"
    
    local backup_path="${BACKUP_DIR}/backup_${BACKUP_TIMESTAMP}.tar.gz"
    
    # Backup important files
    tar -czf "${backup_path}" \
        -C "${PROJECT_DIR}" \
        production/config/ \
        production/*.py \
        results/ \
        logs/ \
        2>/dev/null || true
    
    if [ -f "${backup_path}" ]; then
        local size=$(du -h "${backup_path}" | cut -f1)
        success "Backup created: ${backup_path} (${size})"
        echo "${backup_path}" > "${BACKUP_DIR}/latest_backup.txt"
    else
        warning "Backup creation failed (non-critical)"
    fi
}

rollback() {
    step "Rolling back to previous version..."
    
    if [ ! -f "${BACKUP_DIR}/latest_backup.txt" ]; then
        error "No backup found for rollback"
        exit 1
    fi
    
    local backup_file=$(cat "${BACKUP_DIR}/latest_backup.txt")
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
        exit 1
    fi
    
    info "Restoring from: ${backup_file}"
    
    # Stop service
    stop_bot
    
    # Extract backup
    tar -xzf "${backup_file}" -C "${PROJECT_DIR}"
    
    # Restart service
    start_bot
    
    success "Rollback complete"
}

#===============================================================================
# INSTALLATION
#===============================================================================

create_virtualenv() {
    step "Setting up Python virtual environment..."
    
    if [ ! -d "${VENV_DIR}" ]; then
        ${PYTHON_VERSION} -m venv "${VENV_DIR}"
        success "Virtual environment created"
    else
        info "Virtual environment already exists"
    fi
    
    # Activate venv
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    success "Virtual environment ready"
}

install_dependencies() {
    step "Installing Python dependencies..."
    
    source "${VENV_DIR}/bin/activate"
    
    # Check if requirements.txt exists
    if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
        pip install -r "${PROJECT_DIR}/requirements.txt"
        success "Dependencies installed from requirements.txt"
    else
        # Install essential packages
        pip install \
            python-binance \
            pandas \
            numpy \
            requests \
            colorama \
            aiohttp \
            websockets
        success "Essential dependencies installed"
    fi
}

setup_directories() {
    step "Setting up directories..."
    
    mkdir -p "${PROJECT_DIR}/logs/production"
    mkdir -p "${PROJECT_DIR}/results/production"
    mkdir -p "${BACKUP_DIR}"
    
    # Set permissions
    chmod -R 755 "${PROJECT_DIR}/logs"
    chmod -R 755 "${PROJECT_DIR}/results"
    
    success "Directories created"
}

configure_systemd() {
    step "Configuring systemd service..."
    
    local service_file="${PRODUCTION_DIR}/deploy/genetix-bot.service"
    
    if [ ! -f "${service_file}" ]; then
        error "Service file not found: ${service_file}"
        exit 1
    fi
    
    # Copy service file
    sudo cp "${service_file}" "/etc/systemd/system/${SERVICE_NAME}.service"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable ${SERVICE_NAME}
    
    success "Systemd service configured"
}

#===============================================================================
# SERVICE MANAGEMENT
#===============================================================================

start_bot() {
    step "Starting GenetiX bot..."
    
    # Check if service exists
    if systemctl list-unit-files | grep -q "${SERVICE_NAME}"; then
        sudo systemctl start ${SERVICE_NAME}
        sleep 3
        
        if systemctl is-active --quiet ${SERVICE_NAME}; then
            success "Bot started successfully"
            info "Status: $(systemctl is-active ${SERVICE_NAME})"
        else
            error "Bot failed to start"
            info "Check logs: journalctl -u ${SERVICE_NAME} -n 50"
            exit 1
        fi
    else
        error "Service ${SERVICE_NAME} not found. Run 'install' first."
        exit 1
    fi
}

stop_bot() {
    step "Stopping GenetiX bot..."
    
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        sudo systemctl stop ${SERVICE_NAME}
        sleep 2
        success "Bot stopped"
    else
        info "Bot is not running"
    fi
}

restart_bot() {
    step "Restarting GenetiX bot..."
    
    stop_bot
    sleep 2
    start_bot
}

show_status() {
    print_banner
    
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}📊 SYSTEM STATUS${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    
    # Service status
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        echo -e "${GREEN}🟢 Service: RUNNING${NC}"
    else
        echo -e "${RED}🔴 Service: STOPPED${NC}"
    fi
    
    # Uptime
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        local uptime=$(systemctl show ${SERVICE_NAME} --property=ActiveEnterTimestamp --value)
        echo -e "${BLUE}⏱️  Uptime: ${uptime}${NC}"
    fi
    
    # Port status
    if lsof -Pi :${DASHBOARD_PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}🌐 Dashboard: http://localhost:${DASHBOARD_PORT}${NC}"
    else
        echo -e "${YELLOW}🌐 Dashboard: Not running${NC}"
    fi
    
    # Logs
    if [ -d "${PROJECT_DIR}/logs/production" ]; then
        local log_count=$(ls -1 "${PROJECT_DIR}/logs/production" 2>/dev/null | wc -l)
        echo -e "${BLUE}📋 Log files: ${log_count}${NC}"
    fi
    
    # Results
    if [ -f "${PROJECT_DIR}/results/production/results_$(date +%Y%m%d).json" ]; then
        echo -e "${GREEN}💾 Results: Available for today${NC}"
    else
        echo -e "${YELLOW}💾 Results: No data for today${NC}"
    fi
    
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    
    # System resources
    echo -e "\n${YELLOW}💻 SYSTEM RESOURCES${NC}"
    echo -e "${CYAN}────────────────────────────────────────────────────────────${NC}"
    
    # Memory
    free -h | grep "Mem:" | awk '{print "  Memory: " $3 " / " $2 " used (" $7 " available)"}'
    
    # CPU
    echo -e "  CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
    
    # Disk
    df -h "${PROJECT_DIR}" | tail -1 | awk '{print "  Disk: " $3 " / " $2 " used (" $5 ")"}'
    
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
}

show_logs() {
    step "Showing recent logs..."
    
    if systemctl list-unit-files | grep -q "${SERVICE_NAME}"; then
        echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}📋 RECENT LOGS (last 50 lines)${NC}"
        echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
        
        sudo journalctl -u ${SERVICE_NAME} -n 50 --no-pager
        
        echo -e "\n${BLUE}ℹ️  For live logs: sudo journalctl -u ${SERVICE_NAME} -f${NC}"
    else
        error "Service not found. Check file logs instead."
        
        local latest_log=$(ls -t "${PROJECT_DIR}/logs/production/bot_"*.log 2>/dev/null | head -1)
        if [ -f "${latest_log}" ]; then
            echo -e "\n${YELLOW}Showing file log: ${latest_log}${NC}\n"
            tail -50 "${latest_log}"
        fi
    fi
}

#===============================================================================
# MAIN COMMANDS
#===============================================================================

cmd_check() {
    print_banner
    info "Running safety checks..."
    echo ""
    
    check_prerequisites
    check_disk_space
    check_port_conflicts
    check_running_services
    
    echo ""
    success "All safety checks passed ✓"
    echo ""
    info "System is ready for deployment"
}

cmd_install() {
    print_banner
    info "Starting installation..."
    echo ""
    
    # Safety checks
    check_prerequisites
    check_disk_space
    check_port_conflicts
    
    # Create backup
    create_backup
    
    # Setup
    setup_directories
    create_virtualenv
    install_dependencies
    configure_systemd
    
    echo ""
    success "Installation complete! 🎉"
    echo ""
    info "Next steps:"
    echo "  1. Edit config: nano ${CONFIG_FILE}"
    echo "  2. Add API keys to config"
    echo "  3. Start bot: ./safe_deploy.sh start"
    echo "  4. Check status: ./safe_deploy.sh status"
    echo ""
}

cmd_start() {
    print_banner
    start_bot
    echo ""
    show_status
}

cmd_stop() {
    print_banner
    stop_bot
}

cmd_restart() {
    print_banner
    restart_bot
    echo ""
    show_status
}

cmd_status() {
    show_status
}

cmd_logs() {
    show_logs
}

cmd_rollback() {
    print_banner
    
    warning "This will rollback to the previous version"
    read -p "Are you sure? (yes/no) " -r
    echo
    
    if [[ $REPLY == "yes" ]]; then
        rollback
    else
        info "Rollback cancelled"
    fi
}

cmd_help() {
    print_banner
    
    cat << EOF
${YELLOW}USAGE:${NC}
  ./safe_deploy.sh [COMMAND]

${YELLOW}COMMANDS:${NC}
  ${GREEN}check${NC}       - Run safety checks before deployment
  ${GREEN}install${NC}     - Initial installation (run once)
  ${GREEN}start${NC}       - Start the trading bot
  ${GREEN}stop${NC}        - Stop the trading bot
  ${GREEN}restart${NC}     - Restart the trading bot
  ${GREEN}status${NC}      - Show bot status and metrics
  ${GREEN}logs${NC}        - Show recent logs
  ${GREEN}rollback${NC}    - Rollback to previous version
  ${GREEN}help${NC}        - Show this help message

${YELLOW}EXAMPLES:${NC}
  ./safe_deploy.sh check        # Check system before install
  ./safe_deploy.sh install      # First time setup
  ./safe_deploy.sh start        # Start trading
  ./safe_deploy.sh logs         # View logs

${YELLOW}FILES:${NC}
  Config:      ${CONFIG_FILE}
  Logs:        ${PROJECT_DIR}/logs/production/
  Results:     ${PROJECT_DIR}/results/production/
  Backups:     ${BACKUP_DIR}/

${YELLOW}SUPPORT:${NC}
  GitHub: https://github.com/yusufcmg/NEW--GenetiX-Trading-System
  Issues: https://github.com/yusufcmg/NEW--GenetiX-Trading-System/issues

EOF
}

#===============================================================================
# MAIN
#===============================================================================

main() {
    # Create log directory
    mkdir -p "${PROJECT_DIR}/logs"
    
    # Parse command
    case "${1:-help}" in
        check)
            cmd_check
            ;;
        install)
            cmd_install
            ;;
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs
            ;;
        rollback)
            cmd_rollback
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            error "Unknown command: $1"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main
main "$@"
