# 🚀 GenetiX Production Trading Bot v2.3.0# 🚀 GenetiX Production Trading Bot v2.3.0



**Professional Multi-Timeframe (MTF) Cryptocurrency Trading Bot** with Genetic Algorithm-optimized strategy validated at **89.54% consistency** (3.6x better than industry standard).**Professional Multi-Timeframe (MTF) Cryptocurrency Trading Bot** with Genetic Algorithm-optimized strategy validated at **89.54% consistency** (3.6x better than industry standard).



## 📊 Performance Highlights## � Performance Highlights



### Validated Strategy Results### Validated Strategy Results

- **Training Performance**: 76.29% fitness, 2.76 Sharpe Ratio, 45.18% win rate- **Training Performance**: 76.29% fitness, 2.76 Sharpe Ratio, 45.18% win rate

- **Validation Performance**: 68.31% fitness, 2.95 Sharpe Ratio, 48.39% win rate- **Validation Performance**: 68.31% fitness, 2.95 Sharpe Ratio, 48.39% win rate

- **Consistency Score**: 89.54% (target: 25%, achieved: **3.6x better**)- **Consistency Score**: 89.54% (target: 25%, achieved: **3.6x better**)

- **Maximum Drawdown**: 28.04%- **Maximum Drawdown**: 28.04%

- **Total Trades**: 31 (validation period)- **Total Trades**: 31 (validation period)



### Strategy Features### Strategy Features

- ✅ Multi-Timeframe Analysis (1h, 4h, 1d)- ✅ Multi-Timeframe Analysis (1h, 4h, 1d)

- ✅ Portfolio-weighted position sizing- ✅ Portfolio-weighted position sizing

- ✅ Advanced risk management with circuit breaker- ✅ Advanced risk management with circuit breaker

- ✅ Real-time monitoring dashboard- ✅ Real-time monitoring dashboard

- ✅ 3-level logging system- ✅ 3-level logging system

- ✅ Graceful shutdown and error handling- ✅ Graceful shutdown and error handling

- ✅ Zero-downtime deployment script- ✅ Zero-downtime deployment script



## 🏗️ System Architecture## 🏗️ System Architecture



``````

Production Bot v2.3.0Production Bot v2.3.0

├── Bot Engine (production_bot_v2.py)├── Bot Engine (production_bot_v2.py)

│   ├── MTF Strategy Engine│   ├── MTF Strategy Engine

│   ├── Portfolio Manager│   ├── Portfolio Manager

│   ├── Risk Manager│   ├── Risk Manager

│   ├── Circuit Breaker│   ├── Circuit Breaker

│   └── WebSocket Price Monitor│   └── WebSocket Price Monitor

├── Web Dashboard (dashboard.html)├── Web Dashboard (dashboard.html)

│   ├── Real-time Stats│   ├── Real-time Stats

│   ├── Position Monitor│   ├── Position Monitor

│   └── Activity Log│   └── Activity Log

├── Configuration (config/production_config.json)├── Configuration (config/production_config.json)

│   ├── API Credentials│   ├── API Credentials

│   ├── Trading Parameters│   ├── Trading Parameters

│   ├── Risk Settings│   ├── Risk Settings

│   └── Precision Settings│   └── Precision Settings

└── Deployment (deploy/safe_deploy.sh)└── Deployment (deploy/safe_deploy.sh)

    ├── Zero-downtime deployment    ├── Zero-downtime deployment

    ├── Port/process isolation    ├── Port/process isolation

    └── Automatic rollback    └── Automatic rollback

``````



## 🎯 Trading Symbols (8 Pairs)## 🎯 Trading Symbols (8 Pairs)



| Symbol | Portfolio Weight | Leverage | Min Notional || Symbol | Portfolio Weight | Leverage | Min Notional |

|--------|-----------------|----------|--------------||--------|-----------------|----------|--------------|

| BTCUSDT | 40% | 5x | $5 || BTCUSDT | 40% | 5x | $5 |

| ETHUSDT | 30% | 5x | $5 || ETHUSDT | 30% | 5x | $5 |

| BNBUSDT | 15% | 5x | $5 || BNBUSDT | 15% | 5x | $5 |

| ADAUSDT | 3% | 5x | $5 || ADAUSDT | 3% | 5x | $5 |

| DOTUSDT | 3% | 5x | $5 || DOTUSDT | 3% | 5x | $5 |

| LINKUSDT | 3% | 5x | $5 || LINKUSDT | 3% | 5x | $5 |

| LTCUSDT | 3% | 5x | $5 || LTCUSDT | 3% | 5x | $5 |

| SOLUSDT | 3% | 5x | $5 || SOLUSDT | 3% | 5x | $5 |



## 🚀 Quick Start## 🚀 Quick Start



### Prerequisites### Prerequisites

- Ubuntu 20.04+ (recommended) or any Linux distribution- Ubuntu 20.04+ (recommended) or any Linux distribution

- Python 3.9+- Python 3.9+

- Binance Futures Testnet account- Binance Futures Testnet account

- 2GB RAM minimum- 2GB RAM minimum

- 10GB disk space- 10GB disk space



### 1. Clone Repository### 1. Clone Repository

```bash```bash

git clone https://github.com/yusufcmg/Trade_demo.gitgit clone https://github.com/yusufcmg/Trade_demo.git

cd Trade_democd Trade_demo

``````



### 2. Install Dependencies### 2. Install Dependencies

```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

``````



### 3. Configure API Credentials### 3. Configure API Credentials



**⚠️ IMPORTANT**: The repository contains **Binance Testnet** API credentials for demo purposes. **⚠️ IMPORTANT**: The repository contains **Binance Testnet** API credentials for demo purposes. 



**For production deployment**, update `config/production_config.json`:**For production deployment**, update `config/production_config.json`:

```json```json

{{

    "api_credentials": {    "api_credentials": {

        "api_key": "YOUR_PRODUCTION_API_KEY",        "api_key": "YOUR_PRODUCTION_API_KEY",

        "secret_key": "YOUR_PRODUCTION_SECRET_KEY"        "secret_key": "YOUR_PRODUCTION_SECRET_KEY"

    }    }

}}

``````



**Testnet Configuration** (default):**Testnet Configuration** (default):

- Base URL: `https://testnet.binancefuture.com`- Base URL: `https://testnet.binancefuture.com`

- Testnet funds: Virtual $10,000 USDT- Testnet funds: Virtual $10,000 USDT

- No real money involved- No real money involved



### 4. Deploy Bot (Zero-Downtime)### 4. Deploy Bot (Zero-Downtime)

```bash```bash

cd deploycd deploy

chmod +x safe_deploy.shchmod +x safe_deploy.sh

sudo ./safe_deploy.sh installsudo ./safe_deploy.sh install

sudo ./safe_deploy.sh deploy_servicesudo ./safe_deploy.sh deploy_service

sudo ./safe_deploy.sh startsudo ./safe_deploy.sh start

``````



### 5. Monitor Dashboard### 5. Monitor Dashboard

Open browser: `http://localhost:8080`Open browser: `http://localhost:8080`



### 6. Check Logs### 6. Check Logs

```bash```bash

# Real-time monitoring# Real-time monitoring

sudo journalctl -u genetix-bot-v2 -fsudo journalctl -u genetix-bot-v2 -f



# Bot logs# Bot logs

tail -f logs/production/bot_$(date +%Y%m%d).logtail -f logs/production/bot_$(date +%Y%m%d).log



# Trade logs# Trade logs

tail -f logs/production/trades_$(date +%Y%m%d).logtail -f logs/production/trades_$(date +%Y%m%d).log



# Error logs# Error logs

tail -f logs/production/errors_$(date +%Y%m%d).logtail -f logs/production/errors_$(date +%Y%m%d).log

``````



## ⚙️ Configuration## 🔒 Güvenlik



### Strategy Parameters (Validated)### API Keys Yönetimi

```json

{**❌ YAPMAYIN:**

    "sma_short": 16,```json

    "sma_long": 113,// Config'de plaintext API key

    "rsi_period": 24.61,{

    "rsi_oversold": 74.56,  "api_key": "abc123xyz"

    "bb_period": 19,}

    "bb_std": 1.83,```

    "macd_fast": 10,

    "macd_slow": 28,**✅ YAPIN:**

    "macd_signal": 9,```bash

    "volume_threshold": 1.47,# .env dosyası kullanın (git'e eklemeyin)

    "trend_strength": 0.60,echo "BINANCE_API_KEY=your_key" > .env

    "confluence_weight": 0.93echo "BINANCE_SECRET_KEY=your_secret" >> .env

}

```# .gitignore'a ekleyin

echo ".env" >> .gitignore

### Risk Management```

```json

{### Firewall

    "max_positions": 5,

    "position_size_pct": 10,```bash

    "leverage": 5,# Sadece gerekli portları açın

    "stop_loss_pct": 2.5,sudo ufw allow 22/tcp    # SSH

    "take_profit_pct": 5.0,sudo ufw allow 8080/tcp  # Dashboard (opsiyonel)

    "trailing_stop_pct": 1.5,sudo ufw enable

    "max_daily_loss_usd": 100,```

    "max_drawdown_pct": 15,

    "emergency_stop_loss_usd": 200,## 📊 Monitoring

    "min_confidence": 70,

    "min_confluence": 6.0### Dashboard

}

```Bot çalışırken dashboard'a erişin:

```

### Circuit Breakerhttp://YOUR_SERVER_IP:8080/dashboard.html

```json```

{

    "enabled": true,### Log Dosyaları

    "consecutive_losses": 5,

    "cooldown_minutes": 60```bash

}# Bot log'ları

```tail -f logs/production/production_bot_$(date +%Y%m%d).log



## 📈 Dashboard Features# Systemd journal

sudo journalctl -u genetix-bot -f

### Stats Cards

- 💰 **Account Balance**: Real-time USDT balance# Sonuçlar

- 📊 **Daily P&L**: Today's profit/losscat results/production/results_$(date +%Y%m%d).json | jq .

- 💵 **Total P&L**: Cumulative profit/loss```

- 📍 **Open Positions**: Current position count

- 📝 **Total Trades**: Trade count### Performance Metrics

- ✅ **Win Rate**: Success percentage

```bash

### Position Monitor# Günlük sonuçları göster

- Symbol, Entry Price, Current Pricecat results/production/results_$(date +%Y%m%d).json | jq '{

- P&L (amount and percentage)  balance: .account_balance,

- Position size and leverage  pnl: .total_pnl,

- Duration tracking  pnl_percent: .total_pnl_percent,

  trades: .total_trades,

### Activity Log  open_positions: .open_positions

- Last 10 events}'

- Timestamps```

- Event types (trade, signal, error)

- Real-time updates every 5 seconds## ⚙️ Konfigürasyon Detayları



## 🛠️ Deployment Commands### Trading Ayarları



```bash```json

# Install (first time){

sudo ./deploy/safe_deploy.sh install  "trading_config": {

    "max_positions": 3,              // Aynı anda max 3 pozisyon

# Deploy systemd service    "position_size_percent": 10.0,   // Her pozisyon bakiyenin %10'u

sudo ./deploy/safe_deploy.sh deploy_service    "leverage": 5,                   // 5x kaldıraç

    "stop_loss_percent": 2.5,        // %2.5 stop-loss

# Start bot    "take_profit_percent": 5.0,      // %5 take-profit

sudo ./deploy/safe_deploy.sh start    "trailing_stop_percent": 1.5     // %1.5 trailing stop

  }

# Stop bot}

sudo ./deploy/safe_deploy.sh stop```



# Restart bot### Risk Limitleri

sudo ./deploy/safe_deploy.sh restart

```json

# Check status{

sudo ./deploy/safe_deploy.sh status  "risk_management": {

    "max_daily_loss": 100.0,         // Günlük max $100 kayıp

# Rollback to previous version    "max_drawdown_percent": 15.0,    // Max %15 drawdown

sudo ./deploy/safe_deploy.sh rollback    "emergency_stop_loss": 20.0,     // Acil durum stop

    "min_confidence": 0.65           // Min %65 sinyal güveni

# Update to new version  }

sudo ./deploy/safe_deploy.sh update}

``````



## 🔒 Security Features### Otomasyonlar



### Systemd Service Hardening```json

- `NoNewPrivileges=true`: Prevents privilege escalation{

- `ProtectSystem=strict`: Read-only system directories  "save_interval_minutes": 5,        // Her 5 dakikada sonuç kaydet

- `ProtectHome=true`: Isolates home directories  "health_check_interval": 60,       // Her 60 saniyede health check

- `PrivateTmp=true`: Private /tmp directory  "close_positions_on_shutdown": false  // Kapatırken pozisyonları kapat

}

### Resource Limits```

- CPU: 80% quota

- Memory: 2GB maximum## 🔧 Sorun Giderme

- Tasks: 512 maximum

### Bot Başlamıyor

### Restart Policy

- Auto-restart on failure```bash

- Max 5 restarts in 5 minutes# Service durumunu kontrol

- 120-second watchdog timersudo systemctl status genetix-bot



## 📊 Expected Performance# Log'ları kontrol

sudo journalctl -u genetix-bot -n 100

Based on validation results with 1d timeframe:

# Manuel başlatma ile test

| Metric | Value |cd /home/ubuntu/genetix/evrimx

|--------|-------|source venv/bin/activate

| Average Trade | +2.2% |python production_bot.py --dry-run

| Win Rate | 48.39% |```

| Sharpe Ratio | 2.95 |

| Max Drawdown | 28.04% |### API Bağlantı Hatası

| Profit Factor | 1.85 |

| Consistency | 89.54% |```bash

# Config'i kontrol et

**Note**: Past performance does not guarantee future results. Always use proper risk management.cat config/production_config.json | jq .api_credentials



## 🐛 Troubleshooting# API keys'i test et

curl -H "X-MBX-APIKEY: YOUR_API_KEY" \

### Bot Won't Start  https://testnet.binancefuture.com/fapi/v2/balance

```bash```

# Check prerequisites

sudo ./deploy/safe_deploy.sh check_prerequisites### Python Import Hatası



# Check logs```bash

sudo journalctl -u genetix-bot-v2 -n 50# Bağımlılıkları yeniden kur

source venv/bin/activate

# Verify API credentialspip install -r requirements.txt --upgrade

python3 -c "import json; print(json.load(open('config/production_config.json'))['api_credentials'])"```

```

## 📈 Performans İpuçları

### Port Already in Use

```bash1. **Başlangıç:**

# Find process using port 8080   - Dry-run mode ile test edin

sudo lsof -i :8080   - Küçük position size ile başlayın (%5-10)

   - Az sembol ile test edin (2-3 coin)

# Kill process

sudo kill -9 <PID>2. **Optimizasyon:**

   - Log'ları düzenli analiz edin

# Or let script find alternative port   - Win rate'i takip edin

sudo ./deploy/safe_deploy.sh install   - Drawdown'ı monitör edin

```

3. **Risk Yönetimi:**

### Dashboard Not Loading   - Günlük kayıp limitini aşmayın

```bash   - Position size'ı kademeli artırın

# Check if Flask is running   - Emergency stop'u aktif tutun

sudo systemctl status genetix-bot-v2

## 🔄 Güncelleme

# Test API endpoint

curl http://localhost:8080/api/stats```bash

# Deployment script ile

# Check firewall./deploy/deploy.sh update

sudo ufw status

sudo ufw allow 8080/tcp# Manuel

```cd /home/ubuntu/genetix

git pull origin main

### No Trading Signalssource evrimx/venv/bin/activate

This is **normal** if:pip install -r evrimx/requirements.txt --upgrade

- Market conditions don't meet strategy criteria (70% confidence, 6.0 confluence)sudo systemctl restart genetix-bot

- Circuit breaker is active (5 consecutive losses → 60min cooldown)```

- No valid MTF confluence detected

## 📞 Destek

Check logs:

```bash- **Issues:** [GitHub Issues](https://github.com/yusufcmg/NEW--GenetiX-Trading-System/issues)

tail -f logs/production/bot_$(date +%Y%m%d).log | grep "Signal"- **Docs:** `docs/` klasörü

```- **Logs:** `logs/production/` klasörü



### High Memory Usage## ⚠️ Disclaimer

```bash

# Check current usageBu bot testnet'te çalışır. Gerçek para ile trading yapmadan önce:

sudo systemctl status genetix-bot-v2- ✅ Kapsamlı testler yapın (minimum 2 hafta)

- ✅ Risk yönetimini anlayın

# Restart to clear memory- ✅ Kaybetmeyi göze alabileceğiniz sermaye kullanın

sudo ./deploy/safe_deploy.sh restart- ✅ Kripto trading risklerini bilin



# Adjust memory limit in service file**Mali kayıplardan yazılım sorumlu değildir.**

sudo nano /etc/systemd/system/genetix-bot-v2.service

# Change: MemoryMax=2G## 📄 Lisans

```

MIT License - Detaylar için `LICENSE` dosyasına bakın.

## 📚 Documentation

---

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Comprehensive 100+ page deployment manual

- **[PRODUCTION_READY.md](PRODUCTION_READY.md)**: Quick start and checklist**🤖 GenetiX Production Bot v1.0**  

- **[QUICKSTART.md](QUICKSTART.md)**: Fast setup guide**Hazırlayan:** Yusuf Çekmegil  

- **[STRUCTURE.md](STRUCTURE.md)**: Codebase structure**Tarih:** Ekim 2025

- **[CHANGES.md](CHANGES.md)**: Version history

## 🔄 Maintenance

### Daily Tasks
- ✅ Check dashboard (http://localhost:8080)
- ✅ Review trade logs
- ✅ Monitor P&L

### Weekly Tasks
- ✅ Analyze win rate trends
- ✅ Review error logs
- ✅ Check system resources
- ✅ Backup configuration

### Monthly Tasks
- ✅ Update dependencies
- ✅ Review strategy performance
- ✅ Optimize parameters if needed
- ✅ Clean old logs (30+ days)

## 🆘 Support

### Common Issues
1. **API Error 429**: Rate limit exceeded → Reduce API call frequency
2. **Insufficient Balance**: Add more testnet funds or adjust position sizes
3. **Invalid Symbol**: Check symbol precision in config
4. **WebSocket Timeout**: Network issue → Bot will auto-reconnect

### Logs Location
```
logs/
├── production/
│   ├── bot_20240114.log       # Main bot logs
│   ├── trades_20240114.log    # Trade execution logs
│   └── errors_20240114.log    # Error logs
```

### Health Checks
The bot performs automatic health checks every 60 seconds:
- ✅ API connectivity
- ✅ WebSocket connection
- ✅ Balance updates
- ✅ Position sync

## ⚠️ Disclaimer

**This software is provided for educational and research purposes.**

- Use at your own risk
- Past performance does not guarantee future results
- Cryptocurrency trading involves substantial risk
- Always test with demo/testnet accounts first
- Never invest more than you can afford to lose
- The authors are not responsible for any financial losses

**Default configuration uses Binance Testnet** with virtual funds. No real money is involved unless you explicitly configure production API credentials.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Credits

Developed with:
- **Genetic Algorithm** optimization
- **Multi-Timeframe** analysis
- **Professional risk management**
- **Industry best practices**

Validated strategy: **89.54% consistency** (3.6x better than 25% industry standard)

---

**Version**: 2.3.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅

For questions or support, open an issue on GitHub.
