#!/usr/bin/env python3
"""
🤖 GenetiX Production Trading Bot v2.3.0
Multi-Timeframe Validated Strategy ile çalışır
Ubuntu sunucuda 7/24, validated parametreler, portfolio weighting

KULLANIM:
    python production_bot_v2.py                      # Normal başlatma
    python production_bot_v2.py --dry-run            # Test modu
    python production_bot_v2.py --background         # Background mode
"""

import sys
import os
import json
import time
import asyncio
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import signal
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import traceback
from decimal import Decimal, ROUND_DOWN
from colorama import init, Fore, Back, Style
from threading import Thread
from flask import Flask, jsonify, send_file
from flask_cors import CORS


class CustomJSONEncoder(json.JSONEncoder):
    """Custom encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Colorama initialize
init(autoreset=True)

# Flask app for dashboard API
app = Flask(__name__)
CORS(app)

# Global bot instance for API access
bot_instance = None


# Dashboard API Endpoints
@app.route('/')
def index():
    """Serve dashboard HTML"""
    try:
        return send_file('dashboard.html')
    except:
        return "<h1>GenetiX Trading Bot</h1><p>Dashboard not found. Use API endpoints: /api/stats, /api/positions, /api/activity</p>"


@app.route('/api/stats')
def api_stats():
    """Get bot statistics"""
    if not bot_instance:
        return jsonify({"error": "Bot not initialized"}), 503
    
    try:
        win_rate = (bot_instance.stats['wins'] / bot_instance.stats['trades_closed'] * 100) if bot_instance.stats['trades_closed'] > 0 else 0
        
        return jsonify({
            "balance": round(bot_instance.account_balance, 2),
            "daily_pnl": round(bot_instance.daily_pnl, 2),
            "total_pnl": round(bot_instance.account_balance - bot_instance.initial_balance, 2),
            "total_pnl_percent": round((bot_instance.account_balance - bot_instance.initial_balance) / bot_instance.initial_balance * 100, 2) if bot_instance.initial_balance > 0 else 0,
            "positions": len(bot_instance.positions),
            "trades": bot_instance.stats['trades_closed'],
            "win_rate": round(win_rate, 2),
            "status": "running" if bot_instance.is_running else "stopped"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/status')
def api_status():
    """Get bot status (alias for /api/stats)"""
    return api_stats()


@app.route('/api/positions')
def api_positions():
    """Get open positions"""
    if not bot_instance:
        return jsonify({"error": "Bot not initialized"}), 503
    
    try:
        positions_list = []
        for symbol, pos in bot_instance.positions.items():
            positions_list.append({
                "symbol": symbol,
                "side": pos.get('side', 'LONG'),
                "entry_price": pos.get('entry_price', 0),
                "current_price": pos.get('current_price', 0),
                "quantity": pos.get('quantity', 0),
                "leverage": pos.get('leverage', 5),
                "pnl": pos.get('pnl', 0),
                "pnl_percent": pos.get('pnl_percent', 0),
                "duration": pos.get('duration', 0)
            })
        
        return jsonify({"positions": positions_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/activity')
def api_activity():
    """Get recent activity log"""
    if not bot_instance:
        return jsonify({"error": "Bot not initialized"}), 503
    
    try:
        # Get last 10 trade history items
        recent_trades = bot_instance.trade_history[-10:] if bot_instance.trade_history else []
        
        activity = []
        for trade in reversed(recent_trades):
            activity.append({
                "timestamp": trade.get('timestamp', datetime.now().isoformat()),
                "type": trade.get('type', 'trade'),
                "symbol": trade.get('symbol', ''),
                "action": trade.get('action', ''),
                "message": trade.get('message', '')
            })
        
        return jsonify({"activity": activity})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_dashboard_server(port=8080):
    """Start Flask dashboard server in background thread"""
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    
    dashboard_thread = Thread(target=run_server, daemon=True)
    dashboard_thread.start()
    return dashboard_thread

# Proje root path ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'evrim-strateji'))

# İmportlar
try:
    from src.binance_futures_api import (
        BinanceFuturesTestnetAPI,
        BinanceAPIError,
        RateLimitError,
        NetworkError,
        InsufficientBalanceError,
        InvalidOrderError
    )
except ImportError:
    print(f"{Fore.RED}❌ Binance API modülü bulunamadı!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Lütfen src/ klasörünün mevcut olduğundan emin olun.{Style.RESET_ALL}")
    sys.exit(1)


class ColoredFormatter(logging.Formatter):
    """Colored console logging"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname:8}{Style.RESET_ALL}"
        return super().format(record)


class MTFTradingStrategy:
    """Multi-Timeframe Validated Strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.strategy_params = config['validated_strategy']['parameters']
        self.price_history = {symbol: [] for symbol in config['symbols_to_trade']}
        
        # İndikatör parametreleri
        self.sma_short = int(self.strategy_params['sma_short'])
        self.sma_long = int(self.strategy_params['sma_long'])
        self.rsi_oversold = self.strategy_params['rsi_oversold']
        self.rsi_overbought = self.strategy_params['rsi_overbought']
        self.bb_period = int(self.strategy_params['bollinger_period'])
        self.bb_std = self.strategy_params['bollinger_std']
        self.macd_fast = int(self.strategy_params['macd_fast'])
        self.macd_slow = int(self.strategy_params['macd_slow'])
        self.macd_signal = int(self.strategy_params['macd_signal'])
        self.volume_threshold = self.strategy_params['volume_threshold']
        self.trend_strength = self.strategy_params['trend_strength']
        self.confluence_weight = self.strategy_params['confluence_weight']
        
    def update_price(self, symbol: str, price: float, volume: float = None):
        """Fiyat verisini güncelle"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'volume': volume or 0,
            'timestamp': datetime.now()
        })
        
        # Son 500 veriyi tut
        if len(self.price_history[symbol]) > 500:
            self.price_history[symbol] = self.price_history[symbol][-500:]
    
    def calculate_sma(self, symbol: str, period: int) -> Optional[float]:
        """SMA hesapla"""
        try:
            if symbol not in self.price_history or len(self.price_history[symbol]) < period:
                return None
            
            prices = [p['price'] for p in self.price_history[symbol][-period:]]
            if len(prices) < period:
                return None
                
            return sum(prices) / period
        except (KeyError, IndexError, ZeroDivisionError):
            return None
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """RSI hesapla"""
        try:
            if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
                return None
            
            prices = [p['price'] for p in self.price_history[symbol][-(period+1):]]
            if len(prices) < period + 1:
                return None
            
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except (KeyError, IndexError, ZeroDivisionError):
            return None
    
    def calculate_bollinger_bands(self, symbol: str) -> Optional[Tuple[float, float, float]]:
        """Bollinger Bands hesapla"""
        try:
            if symbol not in self.price_history or len(self.price_history[symbol]) < self.bb_period:
                return None
            
            prices = [p['price'] for p in self.price_history[symbol][-self.bb_period:]]
            if len(prices) < self.bb_period:
                return None
            
            sma = sum(prices) / self.bb_period
            
            variance = sum([(p - sma) ** 2 for p in prices]) / self.bb_period
            std = variance ** 0.5
            
            upper = sma + (std * self.bb_std)
            lower = sma - (std * self.bb_std)
            
            return upper, sma, lower
        except (KeyError, IndexError, ZeroDivisionError):
            return None
    
    def generate_signal(self, symbol: str, current_price: float) -> Dict:
        """Trading sinyali üret"""
        # Yeterli veri var mı kontrol
        if symbol not in self.price_history or len(self.price_history[symbol]) < max(self.sma_long, 200):
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}
        
        # İndikatörleri hesapla
        sma_short = self.calculate_sma(symbol, self.sma_short)
        sma_long = self.calculate_sma(symbol, self.sma_long)
        rsi = self.calculate_rsi(symbol)
        bb = self.calculate_bollinger_bands(symbol)
        
        if not all([sma_short, sma_long, rsi, bb]):
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'Indicator calculation failed'}
        
        # None check for type safety
        if sma_short is None or sma_long is None or rsi is None or bb is None:
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'Indicator calculation failed'}
        
        bb_upper, bb_middle, bb_lower = bb
        
        # Confluence scoring
        bullish_signals = 0.0
        bearish_signals = 0.0
        total_weight = 0.0
        
        # SMA trend (weight: 2.0)
        if sma_short > sma_long:
            bullish_signals += 2.0
        else:
            bearish_signals += 2.0
        total_weight += 2.0
        
        # RSI (weight: 1.5)
        if rsi < self.rsi_oversold:
            bullish_signals += 1.5
        elif rsi > self.rsi_overbought:
            bearish_signals += 1.5
        total_weight += 1.5
        
        # Bollinger Bands (weight: 1.0)
        if current_price < bb_lower:
            bullish_signals += 1.0
        elif current_price > bb_upper:
            bearish_signals += 1.0
        total_weight += 1.0
        
        # Price vs SMA (weight: 1.5)
        if current_price > sma_short:
            bullish_signals += 1.5
        else:
            bearish_signals += 1.5
        total_weight += 1.5
        
        # Confluence score hesapla
        if bullish_signals > bearish_signals:
            confluence = (bullish_signals / total_weight) * 10
            action = 'BUY'
        elif bearish_signals > bullish_signals:
            confluence = (bearish_signals / total_weight) * 10
            action = 'SELL'
        else:
            return {'action': 'HOLD', 'confidence': 0.5, 'reason': 'Neutral signals'}
        
        # Confidence hesapla (0-1 range)
        confidence = min(confluence / 10, 1.0)
        
        # Minimum confluence kontrolü
        min_confluence = self.config['risk_management'].get('min_confluence_score', 6.0)
        if confluence < min_confluence:
            return {
                'action': 'HOLD',
                'confidence': confidence,
                'confluence': confluence,
                'reason': f'Low confluence ({confluence:.2f} < {min_confluence})'
            }
        
        return {
            'action': action,
            'confidence': confidence,
            'confluence': confluence,
            'indicators': {
                'sma_short': sma_short,
                'sma_long': sma_long,
                'rsi': rsi,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'price': current_price
            },
            'reason': f'Confluence {confluence:.2f}, RSI {rsi:.1f}'
        }


class ProductionTradingBot:
    """Production Trading Bot v2.3.0"""
    
    def __init__(self, config_path: str = "config/production_config.json", 
                 dry_run: bool = False, background: bool = False):
        """
        Args:
            config_path: Config dosyası yolu
            dry_run: Test modu (emir vermez)
            background: Background mode (minimal console output)
        """
        self.config_path = Path(config_path)
        self.dry_run = dry_run
        self.background = background
        self.is_running = False
        self.shutdown_requested = False
        
        # Logging setup
        self.setup_logging()
        
        # Config yükle
        self.load_config()
        
        # API
        self.logger.info(f"🔌 Binance Futures Testnet API bağlanıyor...")
        self.api = BinanceFuturesTestnetAPI(str(self.config_path))
        
        # Strategy
        self.logger.info(f"🧬 MTF Validated Strategy yükleniyor...")
        self.strategy = MTFTradingStrategy(self.config)
        
        # Bot state
        self.positions = {}  # {symbol: position_data}
        self.trade_history = []
        self.account_balance = 0.0
        self.initial_balance = 0.0
        self.daily_pnl = 0.0
        self.daily_start_balance = 0.0
        self.symbols = self.config['symbols_to_trade']
        self.portfolio_weights = self.config['portfolio_weights']
        
        # Statistics
        self.stats = {
            'trades_opened': 0,
            'trades_closed': 0,
            'wins': 0,
            'losses': 0,
            'consecutive_losses': 0
        }
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_banner()
        self.logger.info("✅ Production Bot v2.3.0 hazır!")
    
    def print_banner(self):
        """Başlangıç banner'ı"""
        if not self.background:
            banner = f"""
{Fore.CYAN}{'='*80}
{Fore.GREEN}🤖 GenetiX Production Trading Bot v2.3.0{Style.RESET_ALL}
{Fore.CYAN}{'='*80}
{Fore.YELLOW}Strategy:{Style.RESET_ALL} Multi-Timeframe Validated (89.54% consistency)
{Fore.YELLOW}Mode:{Style.RESET_ALL}     {'🧪 DRY RUN' if self.dry_run else '🔴 LIVE TRADING'}
{Fore.YELLOW}Symbols:{Style.RESET_ALL}  {len(self.symbols)} coins (BTC, ETH, BNB, ADA, DOT, LINK, LTC, SOL)
{Fore.YELLOW}Config:{Style.RESET_ALL}   {self.config_path}
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
"""
            print(banner)
    
    def setup_logging(self):
        """
        Advanced logging system with rotation
        - Console: Colored output for INFO+ (if not background)
        - Main log: All logs, rotates daily, keeps 30 days
        - Trade log: Trade-specific logs, rotates at 10MB
        - Error log: ERROR+ only
        """
        # Log directory
        log_dir = PROJECT_ROOT / "logs" / "production"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate log files
        main_log = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        trade_log = log_dir / "trades.log"  # Rotating, not dated
        error_log = log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Root logger
        self.logger = logging.getLogger('ProductionBot')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()  # Clear existing handlers
        
        # Console handler (colored)
        if not self.background:
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(logging.INFO)
            console_fmt = ColoredFormatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console.setFormatter(console_fmt)
            self.logger.addHandler(console)
        
        # Main file handler (time-based rotation: daily, keeps 30 days)
        main_handler = TimedRotatingFileHandler(
            main_log,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        main_fmt = logging.Formatter(
            '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(main_fmt)
        self.logger.addHandler(main_handler)
        
        # Error handler (size-based rotation: 50MB, keeps 5 files)
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(main_fmt)
        self.logger.addHandler(error_handler)
        
        # Trade logger (size-based rotation: 10MB, keeps 10 files)
        self.trade_logger = logging.getLogger('Trades')
        self.trade_logger.setLevel(logging.INFO)
        self.trade_logger.handlers.clear()
        trade_handler = RotatingFileHandler(
            trade_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        trade_handler.setFormatter(main_fmt)
        self.trade_logger.addHandler(trade_handler)
        
        self.logger.info("="*80)
        self.logger.info("🚀 GenetiX Production Bot Starting...")
        self.logger.info("="*80)
    
    def load_config(self):
        """Config yükle"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"✅ Config loaded: {self.config_path}")
            
            # Dry run ayarını config'den oku (eğer belirtilmemişse mevcut değeri kullan)
            if 'testnet' in self.config and 'dry_run' in self.config['testnet']:
                config_dry_run = self.config['testnet']['dry_run']
                if self.dry_run != config_dry_run:
                    self.logger.warning(f"⚙️  Config dry_run override: {self.dry_run} → {config_dry_run}")
                    self.dry_run = config_dry_run
                    
        except FileNotFoundError:
            self.logger.error(f"❌ Config not found: {self.config_path}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Graceful shutdown"""
        sig_name = signal.Signals(signum).name
        self.logger.warning(f"📡 Shutdown signal received: {sig_name}")
        self.shutdown_requested = True
    
    async def initialize(self):
        """Bot başlat (gelişmiş hata yönetimi ile)"""
        global bot_instance
        bot_instance = self  # Global instance için
        
        try:
            self.logger.info("🔧 Initializing bot...")
            
            # API Health Check - Binance'e erişim var mı?
            self.logger.info("🔍 Checking Binance API connection...")
            try:
                server_time = self.api.get_server_time()
                if server_time:
                    from datetime import datetime
                    server_dt = datetime.fromtimestamp(server_time / 1000)
                    self.logger.info(f"✅ Binance API connected! Server time: {server_dt}")
                else:
                    self.logger.warning("⚠️  API responded but server time is None")
            except Exception as e:
                self.logger.error(f"❌ Binance API connection failed: {e}")
                self.logger.error("Please check:")
                self.logger.error("  1. Internet connection")
                self.logger.error("  2. Binance Testnet API status (https://testnet.binancefuture.com)")
                self.logger.error("  3. API credentials in config")
                raise NetworkError(f"Cannot connect to Binance API: {e}")
            
            # Dashboard server başlat
            dashboard_port = self.config.get('dashboard', {}).get('port', 8080)
            try:
                self.dashboard_thread = start_dashboard_server(dashboard_port)
                self.logger.info(f"🌐 Dashboard server started on port {dashboard_port}")
                self.logger.info(f"📊 Dashboard: http://localhost:{dashboard_port}")
            except Exception as e:
                self.logger.warning(f"⚠️  Dashboard server error: {e}")
            
            # Hesap bakiyesi (retry ile)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    balances = self.api.get_balance()
                    for bal in balances:
                        if bal['asset'] == 'USDT':
                            self.account_balance = float(bal['walletBalance'])
                            self.initial_balance = self.account_balance
                            self.daily_start_balance = self.account_balance
                            break
                    self.logger.info(f"💰 Account Balance: ${self.account_balance:,.2f} USDT")
                    break
                    
                except NetworkError as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"⚠️  Network error, retrying ({attempt + 1}/{max_retries})...")
                        await asyncio.sleep(5)
                    else:
                        raise
                        
                except BinanceAPIError as e:
                    self.logger.error(f"❌ API error getting balance: {e}")
                    raise
            
            if self.dry_run:
                self.logger.warning(f"{Fore.YELLOW}⚠️  DRY RUN MODE - No real orders!{Style.RESET_ALL}")
            
            # Açık pozisyonları yükle
            await self.load_positions()
            
            # İlk fiyat verilerini topla
            await self.collect_initial_data()
            
            self.is_running = True
            self.logger.info(f"{Fore.GREEN}✅ Bot initialized successfully!{Style.RESET_ALL}")
            
        except RateLimitError as e:
            self.logger.critical(f"🚫 Rate limit error during initialization: {e}")
            self.logger.info("Waiting 60 seconds before retry...")
            await asyncio.sleep(60)
            raise
            
        except NetworkError as e:
            self.logger.error(f"❌ Network error during initialization: {e}")
            self.logger.info("Check your internet connection and Binance API status")
            raise
            
        except Exception as e:
            self.logger.error(f"❌ Initialization error: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    async def load_positions(self):
        """Açık pozisyonları yükle"""
        try:
            for symbol in self.symbols:
                pos = self.api.get_position(symbol)
                if pos and float(pos.get('positionAmt', 0)) != 0:
                    amt = float(pos['positionAmt'])
                    self.positions[symbol] = {
                        'size': amt,
                        'side': 'LONG' if amt > 0 else 'SHORT',
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unRealizedProfit']),
                        'entry_time': datetime.now()  # Gerçek time bilinmiyor
                    }
                    self.logger.info(f"📍 Position loaded: {symbol} {self.positions[symbol]['side']}")
        except Exception as e:
            self.logger.warning(f"⚠️  Position load error: {e}")
    
    async def collect_initial_data(self):
        """İlk market verilerini topla (güvenli veri kontrolü ile)"""
        self.logger.info("📥 Collecting initial market data...")
        
        for symbol in self.symbols:
            try:
                # Son 200 candle (1m interval)
                klines = self.api.get_klines(symbol, '1m', limit=200)
                
                # GÜÇLENDIRILMIŞ KONTROL: Liste boş mu, geçerli mi?
                if klines and isinstance(klines, list) and len(klines) > 0:
                    loaded_count = 0
                    for kline in klines:
                        # Her kline'ın en az 6 element olduğundan emin ol
                        if kline and len(kline) >= 6:
                            try:
                                price = float(kline[4])  # Close
                                volume = float(kline[5])
                                self.strategy.update_price(symbol, price, volume)
                                loaded_count += 1
                            except (ValueError, TypeError, IndexError) as e:
                                self.logger.warning(f"⚠️  Invalid kline data for {symbol}: {e}")
                                continue
                    
                    if loaded_count > 0:
                        self.logger.info(f"✅ {symbol}: {loaded_count} candles loaded")
                    else:
                        self.logger.warning(f"⚠️  {symbol}: No valid candles found")
                else:
                    # Liste boş veya geçersiz
                    self.logger.warning(f"⚠️  Received empty or invalid candle data for {symbol}. Skipping.")
                
            except Exception as e:
                self.logger.error(f"❌ {symbol} data load error: {e}")
                self.logger.error(traceback.format_exc())
        
        # Biraz bekle
        await asyncio.sleep(2)
    
    async def run(self):
        """Ana trading loop"""
        self.logger.info("🔄 Main trading loop starting...")
        
        iteration = 0
        last_save = time.time()
        last_health_check = time.time()
        last_status_display = time.time()
        
        save_interval = self.config['monitoring']['save_results_interval']
        health_interval = self.config['monitoring']['health_check_interval']
        status_display_interval = 30  # Her 30 saniyede durum göster
        
        while self.is_running and not self.shutdown_requested:
            try:
                iteration += 1
                current_time = time.time()
                
                # Tüm sembolleri işle
                for symbol in self.symbols:
                    await self.process_symbol(symbol)
                
                # Periyodik kayıt
                if current_time - last_save >= save_interval:
                    await self.save_results()
                    last_save = current_time
                
                # Health check
                if current_time - last_health_check >= health_interval:
                    await self.health_check()
                    last_health_check = current_time
                
                # Status display (console)
                if not self.background and current_time - last_status_display >= status_display_interval:
                    self.display_status()
                    last_status_display = current_time
                
                # 30 saniye bekle
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Main loop error: {e}")
                self.logger.error(traceback.format_exc())
                await asyncio.sleep(60)
        
        self.logger.info("🛑 Main loop terminating...")
        await self.shutdown()
    
    async def process_symbol(self, symbol: str):
        """Tek symbol için trading logic (güvenli fiyat kontrolü ile)"""
        try:
            # Güncel fiyat al - GÜÇLENDİRİLMİŞ KONTROL
            current_price = self.api.get_current_price(symbol)
            
            # Fiyat geçerli mi kontrol et
            if current_price is None:
                self.logger.warning(f"⚠️  {symbol}: Price is None, skipping cycle")
                return
            
            if not isinstance(current_price, (int, float)) or current_price <= 0:
                self.logger.warning(f"⚠️  {symbol}: Invalid price value ({current_price}), skipping cycle")
                return
            
            # Price history'ye ekle
            self.strategy.update_price(symbol, current_price)
            
            # Yeterli veri var mı kontrol et (minimum 200 data point)
            if symbol not in self.strategy.price_history or len(self.strategy.price_history[symbol]) < 200:
                # İlk başlatmada henüz yeterli veri yok, sadece bilgi ver
                if len(self.strategy.price_history.get(symbol, [])) % 50 == 0:  # Her 50 data'da bir log
                    self.logger.info(f"📊 {symbol}: Building history ({len(self.strategy.price_history.get(symbol, []))} / 200)")
                return
            
            # Açık pozisyon varsa yönet
            if symbol in self.positions:
                await self.manage_position(symbol, current_price)
                return
            
            # Yeni sinyal üret
            signal = self.strategy.generate_signal(symbol, current_price)
            
            if signal['action'] == 'HOLD':
                return
            
            # Risk kontrolü
            if not self.check_risk_limits():
                self.logger.warning("⚠️  Risk limits exceeded, no new positions")
                return
            
            # Confidence kontrolü
            min_conf = self.config['risk_management']['min_confidence']
            if signal['confidence'] < min_conf:
                return
            
            # Pozisyon aç
            await self.open_position(symbol, signal, current_price)
            
        except Exception as e:
            self.logger.error(f"❌ Process error {symbol}: {e}")
            self.logger.error(traceback.format_exc())
    
    def calculate_position_size(self, symbol: str, current_price: float) -> float:
        """Portfolio-weighted position size hesapla"""
        # Portfolio weight
        weight = self.portfolio_weights.get(symbol, 0.05)
        
        # Toplam allocation
        total_allocation = self.account_balance * (self.config['trading_config']['base_position_percent'] / 100)
        
        # Symbol allocation
        symbol_allocation = total_allocation * weight
        
        # Quantity hesapla
        quantity = symbol_allocation / current_price
        
        # Precision'a göre yuvarla
        precision = self.config['precision'][symbol]['quantity']
        quantity = float(Decimal(str(quantity)).quantize(
            Decimal(10) ** -precision,
            rounding=ROUND_DOWN
        ))
        
        # Min/max kontrolü
        max_usd = self.config['trading_config']['max_position_usd']
        min_usd = self.config['trading_config']['min_position_usd']
        
        position_usd = quantity * current_price
        
        if position_usd > max_usd:
            quantity = max_usd / current_price
            quantity = float(Decimal(str(quantity)).quantize(
                Decimal(10) ** -precision,
                rounding=ROUND_DOWN
            ))
        elif position_usd < min_usd:
            self.logger.warning(f"⚠️  Position too small for {symbol}: ${position_usd:.2f}")
            return 0.0
        
        return quantity
    
    async def open_position(self, symbol: str, signal: Dict, current_price: float):
        """Pozisyon aç (gelişmiş hata yönetimi ile)"""
        side = 'BUY' if signal['action'] == 'BUY' else 'SELL'
        
        try:
            # Position size hesapla
            quantity = self.calculate_position_size(symbol, current_price)
            
            if quantity == 0:
                return
            
            if self.dry_run:
                self.logger.info(f"🧪 DRY RUN: {symbol} {side} {quantity} @ ${current_price:,.2f} (Conf: {signal['confidence']:.1%})")
                return
            
            # Leverage ayarla (hata yönetimi ile)
            try:
                leverage = self.config['trading_config']['leverage']
                self.api.set_leverage(symbol, leverage)
            except BinanceAPIError as e:
                # Leverage zaten ayarlanmış olabilir, devam et
                self.logger.debug(f"Leverage setting info: {e}")
            
            # Emir ver (MARKET order) - Retry mekanizması ile
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    order = self.api.place_order(
                        symbol=symbol,
                        side=side,
                        order_type="MARKET",
                        quantity=quantity
                    )
                    
                    if order:
                        self.positions[symbol] = {
                            'size': quantity if side == 'BUY' else -quantity,
                            'side': 'LONG' if side == 'BUY' else 'SHORT',
                            'entry_price': current_price,
                            'entry_time': datetime.now(),
                            'signal': signal,
                            'order_id': order.get('orderId')
                        }
                        
                        self.stats['trades_opened'] += 1
                        
                        self.logger.info(f"{Fore.GREEN}✅ Position OPENED: {symbol} {side} {quantity} @ ${current_price:,.2f}{Style.RESET_ALL}")
                        self.trade_logger.info(f"OPEN | {symbol} | {side} | {quantity} | ${current_price:,.2f} | Conf: {signal['confidence']:.1%} | Confluence: {signal['confluence']:.2f}")
                        
                        self.trade_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol,
                            'action': 'OPEN',
                            'side': side,
                            'quantity': quantity,
                            'price': current_price,
                            'confidence': signal['confidence'],
                            'confluence': signal['confluence'],
                            'order_id': order.get('orderId')
                        })
                        
                        return
                    break
                    
                except InsufficientBalanceError as e:
                    self.logger.error(f"❌ Insufficient balance for {symbol}: {e}")
                    return  # Retry yapma
                    
                except InvalidOrderError as e:
                    self.logger.error(f"❌ Invalid order for {symbol}: {e}")
                    return  # Retry yapma
                    
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"⚠️  Rate limit, waiting 10s...")
                        await asyncio.sleep(10)
                    else:
                        self.logger.error(f"❌ Rate limit exceeded for {symbol}")
                        return
                        
                except NetworkError as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"⚠️  Network error, retrying...")
                        await asyncio.sleep(3)
                    else:
                        self.logger.error(f"❌ Network error opening position: {e}")
                        return
                        
        except Exception as e:
            self.logger.error(f"❌ Error opening position {symbol}: {e}")
            self.logger.error(traceback.format_exc())
    
    async def manage_position(self, symbol: str, current_price: float):
        """Pozisyon yönetimi (SL/TP)"""
        try:
            pos = self.positions[symbol]
            entry_price = pos['entry_price']
            side = pos['side']
            
            # P&L hesapla
            if side == 'LONG':
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            sl_percent = self.config['trading_config']['stop_loss_percent']
            tp_percent = self.config['trading_config']['take_profit_percent']
            
            # Stop Loss
            if pnl_percent <= -sl_percent:
                self.logger.warning(f"🛑 STOP LOSS: {symbol} (P&L: {pnl_percent:.2f}%)")
                await self.close_position(symbol, current_price, 'STOP_LOSS')
                return
            
            # Take Profit
            if pnl_percent >= tp_percent:
                self.logger.info(f"🎯 TAKE PROFIT: {symbol} (P&L: {pnl_percent:.2f}%)")
                await self.close_position(symbol, current_price, 'TAKE_PROFIT')
                return
            
        except Exception as e:
            self.logger.error(f"❌ Manage position error {symbol}: {e}")
    
    async def close_position(self, symbol: str, current_price: float, reason: str):
        """Pozisyonu kapat"""
        try:
            pos = self.positions[symbol]
            side = 'SELL' if pos['side'] == 'LONG' else 'BUY'
            quantity = abs(pos['size'])
            
            if self.dry_run:
                self.logger.info(f"🧪 DRY RUN: CLOSE {symbol} {side} {quantity} @ ${current_price:,.2f}")
                del self.positions[symbol]
                return
            
            # Emir ver (MARKET order - pozisyon kapatma)
            order = self.api.place_order(
                symbol=symbol,
                side=side,
                order_type="MARKET",
                quantity=quantity,
                reduce_only=True
            )
            
            if order:
                # P&L hesapla
                if pos['side'] == 'LONG':
                    pnl = (current_price - pos['entry_price']) * quantity
                else:
                    pnl = (pos['entry_price'] - current_price) * quantity
                
                pnl_percent = (pnl / self.account_balance) * 100
                
                # İstatistik
                self.stats['trades_closed'] += 1
                if pnl > 0:
                    self.stats['wins'] += 1
                    self.stats['consecutive_losses'] = 0
                    icon = "🟢"
                else:
                    self.stats['losses'] += 1
                    self.stats['consecutive_losses'] += 1
                    icon = "🔴"
                
                self.logger.info(f"{icon} Position CLOSED: {symbol} | {reason} | P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
                self.trade_logger.info(f"CLOSE | {symbol} | {reason} | ${pnl:,.2f} | {pnl_percent:+.2f}% | Entry: ${pos['entry_price']:.2f} | Exit: ${current_price:.2f}")
                
                self.trade_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'CLOSE',
                    'side': side,
                    'quantity': quantity,
                    'price': current_price,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'reason': reason
                })
                
                del self.positions[symbol]
                self.account_balance += pnl
                self.daily_pnl += pnl
                
        except Exception as e:
            self.logger.error(f"❌ Close position error {symbol}: {e}")
    
    def check_risk_limits(self) -> bool:
        """Risk limitleri kontrol"""
        # Max pozisyon sayısı
        if len(self.positions) >= self.config['trading_config']['max_positions']:
            return False
        
        # Günlük kayıp limiti (USD)
        max_daily_loss = self.config['risk_management']['max_daily_loss_usd']
        if self.daily_pnl <= -max_daily_loss:
            self.logger.error(f"🚨 Daily loss limit hit: ${self.daily_pnl:,.2f}")
            return False
        
        # Günlük kayıp limiti (%)
        daily_loss_percent = (self.daily_pnl / self.daily_start_balance) * 100
        max_daily_percent = self.config['risk_management']['max_daily_loss_percent']
        if daily_loss_percent <= -max_daily_percent:
            self.logger.error(f"🚨 Daily loss % limit hit: {daily_loss_percent:.2f}%")
            return False
        
        # Circuit breaker
        if self.config['risk_management']['circuit_breaker']['enabled']:
            max_consecutive = self.config['risk_management']['circuit_breaker']['max_consecutive_losses']
            if self.stats['consecutive_losses'] >= max_consecutive:
                self.logger.error(f"🚨 Circuit breaker: {self.stats['consecutive_losses']} consecutive losses")
                return False
        
        return True
    
    def display_status(self):
        """Console'da durum göster"""
        try:
            win_rate = (self.stats['wins'] / max(self.stats['trades_closed'], 1)) * 100
            daily_pnl_percent = (self.daily_pnl / self.daily_start_balance) * 100
            total_pnl = self.account_balance - self.initial_balance
            total_pnl_percent = (total_pnl / self.initial_balance) * 100
            
            status = f"""
{Fore.CYAN}{'─'*80}{Style.RESET_ALL}
{Fore.YELLOW}💰 Balance:{Style.RESET_ALL} ${self.account_balance:,.2f} | {Fore.YELLOW}Daily P&L:{Style.RESET_ALL} ${self.daily_pnl:+,.2f} ({daily_pnl_percent:+.2f}%) | {Fore.YELLOW}Total P&L:{Style.RESET_ALL} ${total_pnl:+,.2f} ({total_pnl_percent:+.2f}%)
{Fore.YELLOW}📊 Positions:{Style.RESET_ALL} {len(self.positions)}/{self.config['trading_config']['max_positions']} | {Fore.YELLOW}Trades:{Style.RESET_ALL} {self.stats['trades_closed']} | {Fore.YELLOW}Win Rate:{Style.RESET_ALL} {win_rate:.1f}% ({self.stats['wins']}W/{self.stats['losses']}L)
{Fore.CYAN}{'─'*80}{Style.RESET_ALL}
"""
            print(status, end='')
            
        except Exception as e:
            self.logger.error(f"❌ Display status error: {e}")
    
    async def save_results(self):
        """Sonuçları kaydet"""
        try:
            results_dir = PROJECT_ROOT / "results" / "production"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            results_file = results_dir / f"results_{datetime.now().strftime('%Y%m%d')}.json"
            
            win_rate = (self.stats['wins'] / max(self.stats['trades_closed'], 1)) * 100
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'account_balance': self.account_balance,
                'initial_balance': self.initial_balance,
                'daily_pnl': self.daily_pnl,
                'daily_start_balance': self.daily_start_balance,
                'total_pnl': self.account_balance - self.initial_balance,
                'total_pnl_percent': ((self.account_balance - self.initial_balance) / self.initial_balance) * 100,
                'statistics': {
                    'trades_opened': self.stats['trades_opened'],
                    'trades_closed': self.stats['trades_closed'],
                    'wins': self.stats['wins'],
                    'losses': self.stats['losses'],
                    'win_rate': win_rate,
                    'consecutive_losses': self.stats['consecutive_losses']
                },
                'open_positions': len(self.positions),
                'positions': self.positions,
                'recent_trades': self.trade_history[-50:]  # Son 50
            }
            
            with open(results_file, 'w') as f:
                json.dump(results, f)
            
            self.logger.debug(f"💾 Results saved: {results_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Save results error: {e}")
    
    async def health_check(self):
        """Health check"""
        try:
            # API connectivity
            balances = self.api.get_balance()
            if not balances:
                self.logger.error("🚨 API connection lost!")
                return
            
            # Bakiye güncelle
            for bal in balances:
                if bal['asset'] == 'USDT':
                    self.account_balance = float(bal['walletBalance'])
                    break
            
            self.logger.debug(f"💚 Health check OK | Balance: ${self.account_balance:,.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Shutting down...")
        
        try:
            # Son sonuçları kaydet
            await self.save_results()
            
            final_pnl = self.account_balance - self.initial_balance
            final_pnl_percent = (final_pnl / self.initial_balance) * 100
            
            self.logger.info(f"💰 Final Balance: ${self.account_balance:,.2f}")
            self.logger.info(f"📊 Total P&L: ${final_pnl:+,.2f} ({final_pnl_percent:+.2f}%)")
            self.logger.info(f"📍 Open Positions: {len(self.positions)}")
            self.logger.info("✅ Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown error: {e}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='GenetiX Production Bot v2.3.0')
    parser.add_argument('--config', type=str, 
                       default='config/production_config.json',
                       help='Config file path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode (no real orders)')
    parser.add_argument('--background', action='store_true',
                       help='Background mode (minimal console output)')
    
    args = parser.parse_args()
    
    bot = ProductionTradingBot(
        config_path=args.config,
        dry_run=args.dry_run,
        background=args.background
    )
    
    try:
        await bot.initialize()
        await bot.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Keyboard interrupt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        traceback.print_exc()
    finally:
        if bot.is_running:
            await bot.shutdown()


if __name__ == "__main__":
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🤖 GenetiX Production Trading Bot v2.3.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    asyncio.run(main())
