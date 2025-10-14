#!/usr/bin/env python3
"""
🤖 GenetiX Production Trading Bot
Ubuntu sunucuda 7/24 çalışacak, otomatik restart ve logging ile
Canlı testnet'te çalışır, sonuçları kaydeder

KULLANIM:
    python production_bot.py                    # Normal başlatma
    python production_bot.py --config custom.json  # Özel config
    python production_bot.py --dry-run          # Test modu (emir vermez)
"""

import sys
import os
import json
import time
import asyncio
import logging
import signal
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import traceback

# Proje root path ekle
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'testnet' / 'src'))

from testnet.src.binance_futures_api import BinanceFuturesTestnetAPI
from testnet.src.enhanced_strategy import EnhancedTradingStrategy
from testnet.src.notifications import NotificationManager
from testnet.src.dashboard_server import DashboardServer
from testnet.src.performance_tracker import PerformanceTracker


class ProductionTradingBot:
    """7/24 Çalışacak Production Trading Bot"""
    
    def __init__(self, config_path: str = "config/production_config.json", dry_run: bool = False):
        """
        Args:
            config_path: Konfigürasyon dosyası yolu
            dry_run: True ise gerçek emir vermez (test modu)
        """
        self.config_path = config_path
        self.dry_run = dry_run
        self.is_running = False
        self.shutdown_requested = False
        
        # Logging setup
        self.setup_logging()
        
        # Konfigürasyon yükle
        self.load_config()
        
        # API bağlantısı
        self.logger.info(f"🔌 API bağlantısı kuruluyor... (Dry Run: {dry_run})")
        self.api = BinanceFuturesTestnetAPI(config_path)
        
        # Strateji
        self.logger.info("🧬 Enhanced trading stratejisi yükleniyor...")
        self.strategy = EnhancedTradingStrategy(self.config)
        
        # Performance tracker
        self.tracker = PerformanceTracker(
            results_dir=PROJECT_ROOT / "results" / "production",
            save_interval=300  # Her 5 dakikada kaydet
        )
        
        # Notification manager (opsiyonel)
        try:
            self.notifier = NotificationManager(self.config)
            self.logger.info("📱 Telegram bildirimleri aktif")
        except Exception as e:
            self.notifier = None
            self.logger.warning(f"⚠️  Telegram bildirimleri devre dışı: {e}")
        
        # Dashboard server
        try:
            dashboard_port = self.config.get("dashboard_port", 8080)
            self.dashboard = DashboardServer(port=dashboard_port)
            self.logger.info(f"📊 Dashboard hazır: http://localhost:{dashboard_port}")
        except Exception as e:
            self.dashboard = None
            self.logger.warning(f"⚠️  Dashboard başlatılamadı: {e}")
        
        # Bot durumu
        self.positions = {}  # {symbol: position_data}
        self.trade_history = []
        self.account_balance = 0.0
        self.initial_balance = 0.0
        self.symbols = self.config.get("symbols_to_trade", ["BTCUSDT", "ETHUSDT"])
        
        # Signal handlers (graceful shutdown)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("✅ Production bot hazır!")
        
    def setup_logging(self):
        """Logging yapılandırması"""
        # Log dizini oluştur
        log_dir = PROJECT_ROOT / "logs" / "production"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log dosyası adı (tarihli)
        log_file = log_dir / f"production_bot_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Logging config
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 80)
        self.logger.info("🚀 GenetiX Production Trading Bot Starting...")
        self.logger.info("=" * 80)
    
    def load_config(self):
        """Konfigürasyonu yükle"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"✅ Config yüklendi: {self.config_path}")
        except FileNotFoundError:
            self.logger.error(f"❌ Config dosyası bulunamadı: {self.config_path}")
            self.logger.info("📝 Default config oluşturuluyor...")
            self.create_default_config()
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
    
    def create_default_config(self):
        """Default konfigürasyon oluştur"""
        default_config = {
            "api_credentials": {
                "api_key": "YOUR_BINANCE_TESTNET_API_KEY",
                "secret_key": "YOUR_BINANCE_TESTNET_SECRET_KEY"
            },
            "testnet_config": {
                "api_url": "https://testnet.binancefuture.com",
                "ws_url": "wss://stream.binancefuture.com"
            },
            "symbols_to_trade": [
                "BTCUSDT",
                "ETHUSDT",
                "BNBUSDT"
            ],
            "trading_config": {
                "max_positions": 3,
                "position_size_percent": 10.0,
                "leverage": 5,
                "stop_loss_percent": 2.5,
                "take_profit_percent": 5.0,
                "trailing_stop_percent": 1.5
            },
            "risk_management": {
                "max_daily_loss": 100.0,
                "max_drawdown_percent": 15.0,
                "emergency_stop_loss": 20.0,
                "min_confidence": 0.65
            },
            "strategy_type": "enhanced",
            "dashboard_port": 8080,
            "telegram": {
                "enabled": false,
                "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
                "chat_id": "YOUR_TELEGRAM_CHAT_ID"
            },
            "save_interval_minutes": 5,
            "health_check_interval": 60
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.logger.info(f"✅ Default config oluşturuldu: {self.config_path}")
        self.logger.warning("⚠️  API credentials'ları düzenlemeyi unutmayın!")
    
    def signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        self.logger.info(f"📡 Shutdown sinyali alındı: {signal.Signals(signum).name}")
        self.shutdown_requested = True
    
    async def initialize(self):
        """Bot'u başlat"""
        try:
            self.logger.info("🔧 Bot başlatılıyor...")
            
            # Hesap bilgilerini al
            balances = self.api.get_balance()
            for balance in balances:
                if balance["asset"] == "USDT":
                    self.account_balance = float(balance["walletBalance"])
                    if self.initial_balance == 0:
                        self.initial_balance = self.account_balance
                    break
            
            self.logger.info(f"💰 Hesap Bakiyesi: ${self.account_balance:,.2f} USDT")
            
            if self.dry_run:
                self.logger.warning("⚠️  DRY RUN MODE: Gerçek emir verilmeyecek!")
            
            # Açık pozisyonları yükle
            await self.load_existing_positions()
            
            # Dashboard başlat
            if self.dashboard:
                if self.dashboard.start():
                    self.logger.info(f"📊 Dashboard başlatıldı: http://localhost:{self.config.get('dashboard_port', 8080)}")
            
            # Fiyat stream'i başlat
            self.logger.info("📡 WebSocket stream başlatılıyor...")
            self.api.start_price_stream(self.symbols)
            
            # İlk veri toplama
            await self.collect_initial_data()
            
            # Telegram bildirim gönder
            if self.notifier:
                await self.notifier.send_message(
                    f"🤖 Production Bot Başlatıldı\n"
                    f"💰 Bakiye: ${self.account_balance:,.2f}\n"
                    f"📊 Symbols: {', '.join(self.symbols)}\n"
                    f"⚙️  Mode: {'DRY RUN' if self.dry_run else 'LIVE'}"
                )
            
            self.is_running = True
            self.logger.info("✅ Bot başarıyla başlatıldı!")
            
        except Exception as e:
            self.logger.error(f"❌ Bot başlatma hatası: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    async def load_existing_positions(self):
        """Mevcut açık pozisyonları yükle"""
        try:
            for symbol in self.symbols:
                position_data = self.api.get_position(symbol)
                if position_data and float(position_data.get('positionAmt', 0)) != 0:
                    self.positions[symbol] = {
                        'size': float(position_data['positionAmt']),
                        'entry_price': float(position_data['entryPrice']),
                        'unrealized_pnl': float(position_data['unRealizedProfit']),
                        'side': 'LONG' if float(position_data['positionAmt']) > 0 else 'SHORT'
                    }
                    self.logger.info(f"📍 Açık pozisyon yüklendi: {symbol} {self.positions[symbol]['side']}")
        except Exception as e:
            self.logger.warning(f"⚠️  Pozisyon yükleme hatası: {e}")
    
    async def collect_initial_data(self):
        """Başlangıç verilerini topla"""
        self.logger.info("📥 İlk market verisi toplanıyor...")
        
        for symbol in self.symbols:
            try:
                # Son 24 saatlik veri al
                klines = self.api.get_klines(symbol, "1m", limit=1440)
                
                for kline in klines[-200:]:  # Son 200 veri
                    timestamp = datetime.fromtimestamp(kline[0]/1000)
                    price = float(kline[4])  # Close price
                    volume = float(kline[5])
                    self.strategy.add_price_data(symbol, price, timestamp, volume)
                
                self.logger.info(f"✅ {symbol}: {len(klines)} veri noktası yüklendi")
                
            except Exception as e:
                self.logger.warning(f"⚠️  {symbol} veri yükleme hatası: {e}")
        
        # WebSocket verisi için bekle
        await asyncio.sleep(5)
    
    async def run(self):
        """Ana trading döngüsü"""
        self.logger.info("🔄 Ana trading döngüsü başlıyor...")
        
        iteration = 0
        last_save_time = time.time()
        last_health_check = time.time()
        
        save_interval = self.config.get("save_interval_minutes", 5) * 60
        health_interval = self.config.get("health_check_interval", 60)
        
        while self.is_running and not self.shutdown_requested:
            try:
                iteration += 1
                current_time = time.time()
                
                # Her symbol için işlem yap
                for symbol in self.symbols:
                    await self.process_symbol(symbol)
                
                # Periyodik kaydetme
                if current_time - last_save_time >= save_interval:
                    await self.save_results()
                    last_save_time = current_time
                
                # Health check
                if current_time - last_health_check >= health_interval:
                    await self.health_check()
                    last_health_check = current_time
                
                # Her 30 saniyede bir çalış
                await asyncio.sleep(30)
                
                # Her 100 iterasyonda log
                if iteration % 100 == 0:
                    self.logger.info(f"🔄 İterasyon: {iteration}, Bakiye: ${self.account_balance:,.2f}")
                
            except Exception as e:
                self.logger.error(f"❌ Ana döngü hatası: {e}")
                self.logger.error(traceback.format_exc())
                await asyncio.sleep(60)  # Hata durumunda bekle
        
        self.logger.info("🛑 Ana döngü sonlandırılıyor...")
        await self.shutdown()
    
    async def process_symbol(self, symbol: str):
        """Tek bir symbol için trading logic"""
        try:
            # Güncel fiyatı al
            current_price = self.api.get_current_price(symbol)
            if not current_price:
                return
            
            # Açık pozisyon varsa yönet
            if symbol in self.positions:
                await self.manage_position(symbol, current_price)
                return
            
            # Yeni sinyal üret
            signal = self.strategy.generate_signal(symbol, current_price, datetime.now())
            
            if not signal or signal['action'] == 'HOLD':
                return
            
            # Risk kontrolü
            if not self.check_risk_limits():
                self.logger.warning(f"⚠️  Risk limitleri aşıldı, yeni pozisyon açılmıyor")
                return
            
            # Pozisyon aç
            if signal['confidence'] >= self.config['risk_management']['min_confidence']:
                await self.open_position(symbol, signal, current_price)
                
        except Exception as e:
            self.logger.error(f"❌ {symbol} işlem hatası: {e}")
    
    async def open_position(self, symbol: str, signal: Dict, current_price: float):
        """Yeni pozisyon aç"""
        try:
            side = 'BUY' if signal['action'] == 'BUY' else 'SELL'
            
            # Pozisyon büyüklüğünü hesapla
            position_size_usd = self.account_balance * (self.config['trading_config']['position_size_percent'] / 100)
            quantity = position_size_usd / current_price
            
            # Quantity'yi düzenle (minimum lot size vs.)
            quantity = round(quantity, 3)
            
            if self.dry_run:
                self.logger.info(f"🧪 DRY RUN: {symbol} {side} {quantity} @ ${current_price:,.2f}")
                return
            
            # Emri ver
            order = self.api.place_order(symbol, side, quantity)
            
            if order:
                self.positions[symbol] = {
                    'size': quantity if side == 'BUY' else -quantity,
                    'entry_price': current_price,
                    'side': 'LONG' if side == 'BUY' else 'SHORT',
                    'entry_time': datetime.now(),
                    'signal': signal
                }
                
                self.logger.info(f"✅ Pozisyon açıldı: {symbol} {side} {quantity} @ ${current_price:,.2f}")
                
                # Telegram bildirim
                if self.notifier:
                    await self.notifier.send_message(
                        f"📈 Pozisyon Açıldı\n"
                        f"Symbol: {symbol}\n"
                        f"Side: {side}\n"
                        f"Quantity: {quantity}\n"
                        f"Price: ${current_price:,.2f}\n"
                        f"Confidence: {signal['confidence']:.1%}"
                    )
                
                # Trade history'ye ekle
                self.trade_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'OPEN',
                    'side': side,
                    'quantity': quantity,
                    'price': current_price,
                    'signal': signal
                })
                
        except Exception as e:
            self.logger.error(f"❌ Pozisyon açma hatası {symbol}: {e}")
    
    async def manage_position(self, symbol: str, current_price: float):
        """Açık pozisyonu yönet (SL/TP kontrol)"""
        try:
            position = self.positions[symbol]
            entry_price = position['entry_price']
            side = position['side']
            
            # P&L hesapla
            if side == 'LONG':
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            # Stop Loss kontrolü
            if pnl_percent <= -self.config['trading_config']['stop_loss_percent']:
                self.logger.warning(f"🛑 Stop Loss tetiklendi: {symbol} (P&L: {pnl_percent:.2f}%)")
                await self.close_position(symbol, current_price, "STOP_LOSS")
                return
            
            # Take Profit kontrolü
            if pnl_percent >= self.config['trading_config']['take_profit_percent']:
                self.logger.info(f"🎯 Take Profit tetiklendi: {symbol} (P&L: {pnl_percent:.2f}%)")
                await self.close_position(symbol, current_price, "TAKE_PROFIT")
                return
            
            # Trailing stop
            # TODO: Trailing stop logic eklenebilir
            
        except Exception as e:
            self.logger.error(f"❌ Pozisyon yönetim hatası {symbol}: {e}")
    
    async def close_position(self, symbol: str, current_price: float, reason: str):
        """Pozisyonu kapat"""
        try:
            position = self.positions[symbol]
            side = 'SELL' if position['side'] == 'LONG' else 'BUY'
            quantity = abs(position['size'])
            
            if self.dry_run:
                self.logger.info(f"🧪 DRY RUN: {symbol} CLOSE {side} {quantity} @ ${current_price:,.2f}")
                del self.positions[symbol]
                return
            
            # Emri ver
            order = self.api.place_order(symbol, side, quantity)
            
            if order:
                # P&L hesapla
                if position['side'] == 'LONG':
                    pnl = (current_price - position['entry_price']) * quantity
                else:
                    pnl = (position['entry_price'] - current_price) * quantity
                
                self.logger.info(f"✅ Pozisyon kapatıldı: {symbol} | Reason: {reason} | P&L: ${pnl:,.2f}")
                
                # Telegram bildirim
                if self.notifier:
                    await self.notifier.send_message(
                        f"📉 Pozisyon Kapatıldı\n"
                        f"Symbol: {symbol}\n"
                        f"Reason: {reason}\n"
                        f"P&L: ${pnl:,.2f} ({(pnl/self.account_balance)*100:.2f}%)"
                    )
                
                # Trade history'ye ekle
                self.trade_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'CLOSE',
                    'side': side,
                    'quantity': quantity,
                    'price': current_price,
                    'pnl': pnl,
                    'reason': reason
                })
                
                # Pozisyonu sil
                del self.positions[symbol]
                
                # Bakiyeyi güncelle
                self.account_balance += pnl
                
        except Exception as e:
            self.logger.error(f"❌ Pozisyon kapatma hatası {symbol}: {e}")
    
    def check_risk_limits(self) -> bool:
        """Risk limitlerini kontrol et"""
        # Maksimum pozisyon sayısı
        if len(self.positions) >= self.config['trading_config']['max_positions']:
            return False
        
        # Günlük kayıp limiti
        daily_pnl = self.account_balance - self.initial_balance
        if daily_pnl <= -self.config['risk_management']['max_daily_loss']:
            self.logger.error(f"🚨 Günlük kayıp limiti aşıldı: ${daily_pnl:,.2f}")
            return False
        
        # Drawdown kontrolü
        drawdown_percent = ((self.initial_balance - self.account_balance) / self.initial_balance) * 100
        if drawdown_percent >= self.config['risk_management']['max_drawdown_percent']:
            self.logger.error(f"🚨 Drawdown limiti aşıldı: {drawdown_percent:.2f}%")
            return False
        
        return True
    
    async def save_results(self):
        """Sonuçları kaydet"""
        try:
            results_dir = PROJECT_ROOT / "results" / "production"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Sonuç dosyası
            results_file = results_dir / f"results_{datetime.now().strftime('%Y%m%d')}.json"
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'account_balance': self.account_balance,
                'initial_balance': self.initial_balance,
                'total_pnl': self.account_balance - self.initial_balance,
                'total_pnl_percent': ((self.account_balance - self.initial_balance) / self.initial_balance) * 100,
                'open_positions': len(self.positions),
                'positions': self.positions,
                'total_trades': len(self.trade_history),
                'trade_history': self.trade_history[-100:]  # Son 100 trade
            }
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"💾 Sonuçlar kaydedildi: {results_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Sonuç kaydetme hatası: {e}")
    
    async def health_check(self):
        """Health check - sistem sağlığını kontrol et"""
        try:
            # API bağlantısı kontrolü
            balances = self.api.get_balance()
            if not balances:
                self.logger.error("🚨 API bağlantısı yok!")
                return
            
            # Bakiyeyi güncelle
            for balance in balances:
                if balance["asset"] == "USDT":
                    self.account_balance = float(balance["walletBalance"])
                    break
            
            self.logger.info(f"💚 Health Check OK | Bakiye: ${self.account_balance:,.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ Health check hatası: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Bot kapatılıyor...")
        
        try:
            # Açık pozisyonları kapat (opsiyonel)
            close_on_shutdown = self.config.get("close_positions_on_shutdown", False)
            
            if close_on_shutdown:
                self.logger.info("📍 Açık pozisyonlar kapatılıyor...")
                for symbol in list(self.positions.keys()):
                    current_price = self.api.get_current_price(symbol)
                    await self.close_position(symbol, current_price, "SHUTDOWN")
            
            # Son sonuçları kaydet
            await self.save_results()
            
            # Dashboard'u kapat
            if self.dashboard:
                self.dashboard.stop()
            
            # Telegram bildirim
            if self.notifier:
                await self.notifier.send_message(
                    f"🛑 Production Bot Kapatıldı\n"
                    f"💰 Final Bakiye: ${self.account_balance:,.2f}\n"
                    f"📊 Total P&L: ${self.account_balance - self.initial_balance:,.2f}\n"
                    f"📍 Açık Pozisyonlar: {len(self.positions)}"
                )
            
            self.logger.info("✅ Shutdown tamamlandı")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown hatası: {e}")


async def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='GenetiX Production Trading Bot')
    parser.add_argument('--config', type=str, default='config/production_config.json',
                       help='Config dosyası yolu')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test modu (gerçek emir vermez)')
    
    args = parser.parse_args()
    
    bot = ProductionTradingBot(
        config_path=args.config,
        dry_run=args.dry_run
    )
    
    try:
        await bot.initialize()
        await bot.run()
    except KeyboardInterrupt:
        print("\n⚠️  Keyboard interrupt alındı")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        if bot.is_running:
            await bot.shutdown()


if __name__ == "__main__":
    print("🚀 GenetiX Production Trading Bot v1.0")
    print("=" * 80)
    
    # Config kontrolü
    if not os.path.exists("config/production_config.json"):
        print("⚠️  Config dosyası bulunamadı, oluşturuluyor...")
    
    # Bot'u başlat
    asyncio.run(main())
