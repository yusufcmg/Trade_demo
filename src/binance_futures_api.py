"""
Binance Futures Testnet API Bağlantı Modülü
Futures trading için özelleştirilmiş API client
Dokümantasyon: https://developers.binance.com/docs/derivatives

FEATURES:
- Automatic retry with exponential backoff
- Rate limiting protection
- Specific error handling (NetworkError, RateLimitError, etc.)
- Connection pooling
- Request/response logging
"""

import json
import hmac
import hashlib
import time
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import logging
from functools import wraps

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    import websocket
except ImportError as e:
    print(f"Required packages not installed: {e}")
    print("Please run: pip install requests websocket-client")
    raise


# Custom Exceptions
class BinanceAPIError(Exception):
    """Base exception for Binance API errors"""
    pass

class RateLimitError(BinanceAPIError):
    """Rate limit exceeded"""
    pass

class NetworkError(BinanceAPIError):
    """Network connectivity error"""
    pass

class InsufficientBalanceError(BinanceAPIError):
    """Insufficient balance for trade"""
    pass

class InvalidOrderError(BinanceAPIError):
    """Invalid order parameters"""
    pass

class BinanceFuturesTestnetAPI:
    """Binance Futures Testnet API client with retry and rate limiting"""
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 1200  # Binance limit
    REQUEST_WEIGHT_LIMIT = 2400     # Per minute
    
    def __init__(self, config_path: str = "config/testnet_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config["api_credentials"]["api_key"]
        self.secret_key = self.config["api_credentials"]["secret_key"]
        self.base_url = self.config["testnet_config"]["api_url"]
        self.ws_url = self.config["testnet_config"]["ws_url"]
        
        # Session with connection pooling and retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # 1, 2, 4 seconds
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        
        # Rate limiting tracking
        self.request_timestamps = []
        self.request_weights = []
        
        # WebSocket connections
        self.ws_connections = {}
        self.price_data = {}
        
        # Logging setup
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        
        # Eğer log_dir varsa kullan, yoksa basit logging
        handlers = [logging.StreamHandler()]
        if log_config.get("file_output", False):
            log_dir = log_config.get("log_dir", "logs")
            from pathlib import Path
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            log_file = Path(log_dir) / "binance_api.log"
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger(__name__)
        
    def _generate_signature(self, params: Dict) -> str:
        """API imzası oluştur"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _check_rate_limit(self, weight: int = 1):
        """Rate limit kontrolü ve bekleme"""
        now = time.time()
        
        # 1 dakikadan eski istekleri temizle (her iki listeyi de aynı anda filtrele)
        filtered_data = [(ts, w) for ts, w in zip(self.request_timestamps, self.request_weights) if now - ts < 60]
        if filtered_data:
            self.request_timestamps, self.request_weights = zip(*filtered_data)
            self.request_timestamps = list(self.request_timestamps)
            self.request_weights = list(self.request_weights)
        else:
            self.request_timestamps = []
            self.request_weights = []
        
        # Rate limit kontrolü
        if len(self.request_timestamps) >= self.MAX_REQUESTS_PER_MINUTE:
            sleep_time = 60 - (now - self.request_timestamps[0])
            if sleep_time > 0:
                self.logger.warning(f"⚠️ Rate limit yaklaşıldı, {sleep_time:.1f}s bekleniyor...")
                time.sleep(sleep_time)
        
        if sum(self.request_weights) + weight >= self.REQUEST_WEIGHT_LIMIT:
            sleep_time = 60 - (now - self.request_timestamps[0])
            if sleep_time > 0:
                self.logger.warning(f"⚠️ Weight limit yaklaşıldı, {sleep_time:.1f}s bekleniyor...")
                time.sleep(sleep_time)
        
        # İsteği kaydet
        self.request_timestamps.append(now)
        self.request_weights.append(weight)
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 signed: bool = False, weight: int = 1, retry_count: int = 3) -> Union[Dict, List]:
        """
        API isteği gönder (gelişmiş hata yönetimi ve retry)
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Signature gerekli mi
            weight: Request weight (rate limiting için)
            retry_count: Hata durumunda kaç kez tekrar deneneceği
        
        Returns:
            API response (dict veya list)
        
        Raises:
            RateLimitError: Rate limit aşıldı
            NetworkError: Ağ bağlantı hatası
            InvalidOrderError: Geçersiz emir parametreleri
            BinanceAPIError: Diğer API hataları
        """
        if params is None:
            params = {}
        
        # Rate limit kontrolü
        self._check_rate_limit(weight)
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        url = f"{self.base_url}{endpoint}"
        last_exception = None
        
        for attempt in range(retry_count):
            try:
                # HTTP request
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=10)
                elif method == "POST":
                    response = self.session.post(url, params=params, timeout=10)
                elif method == "DELETE":
                    response = self.session.delete(url, params=params, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Response kontrolü
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # HTTP hata kodlarını ayıkla
                if e.response.status_code == 429:
                    # Rate limit
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    self.logger.error(f"❌ Rate limit aşıldı! {retry_after}s bekleniyor...")
                    time.sleep(retry_after)
                    last_exception = RateLimitError(f"Rate limit exceeded: {e}")
                    
                elif e.response.status_code == 418:
                    # IP banned
                    self.logger.critical(f"🚫 IP BANNED! API erişimi engellendi!")
                    raise RateLimitError("IP banned by Binance")
                    
                elif e.response.status_code in [400, 401, 403]:
                    # Client error - retry yapma
                    error_data = e.response.json() if e.response.text else {}
                    error_msg = error_data.get('msg', str(e))
                    self.logger.error(f"❌ API Client Error [{e.response.status_code}]: {error_msg}")
                    
                    # Spesifik hatalar
                    if 'insufficient balance' in error_msg.lower():
                        raise InsufficientBalanceError(error_msg)
                    elif any(word in error_msg.lower() for word in ['order', 'quantity', 'price']):
                        raise InvalidOrderError(error_msg)
                    else:
                        raise BinanceAPIError(error_msg)
                        
                elif e.response.status_code >= 500:
                    # Server error - retry yap
                    self.logger.warning(f"⚠️ Server error [{e.response.status_code}], {attempt + 1}/{retry_count} deneme...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    last_exception = e
                else:
                    raise BinanceAPIError(f"HTTP {e.response.status_code}: {e}")
                    
            except requests.exceptions.ConnectionError as e:
                # Ağ bağlantı hatası
                self.logger.warning(f"⚠️ Ağ bağlantı hatası, {attempt + 1}/{retry_count} deneme...")
                time.sleep(2 ** attempt)
                last_exception = NetworkError(f"Connection error: {e}")
                
            except requests.exceptions.Timeout as e:
                # Timeout
                self.logger.warning(f"⚠️ Request timeout, {attempt + 1}/{retry_count} deneme...")
                time.sleep(2 ** attempt)
                last_exception = NetworkError(f"Timeout: {e}")
                
            except requests.exceptions.RequestException as e:
                # Diğer request hataları
                self.logger.error(f"❌ Request failed: {e}")
                last_exception = BinanceAPIError(str(e))
                break  # Retry yapma
        
        # Tüm denemeler başarısız
        if last_exception:
            raise last_exception
        raise BinanceAPIError("Request failed after all retries")
    
    def get_server_time(self) -> int:
        """Server zamanını al"""
        response = self._request("GET", "/v1/time")
        if isinstance(response, dict):
            return response["serverTime"]
        raise ValueError("Invalid response format")
    
    def get_account_info(self) -> Dict:
        """Futures hesap bilgilerini al"""
        response = self._request("GET", "/v2/account", signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def get_balance(self) -> List[Dict]:
        """Hesap bakiyelerini al"""
        account = self.get_account_info()
        return account.get("assets", [])
    
    def get_positions(self) -> List[Dict]:
        """Açık pozisyonları al"""
        response = self._request("GET", "/v2/positionRisk", signed=True)
        if isinstance(response, list):
            return response
        raise ValueError("Invalid response format")
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Sembol bilgilerini al"""
        response = self._request("GET", "/v1/exchangeInfo")
        if isinstance(response, dict):
            for s in response["symbols"]:
                if s["symbol"] == symbol:
                    return s
        raise ValueError(f"Symbol {symbol} not found")
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """
        Anlık fiyat al (güçlendirilmiş hata kontrolü ile)
        
        Returns:
            float: Geçerli fiyat
            None: Hata durumunda veya geçersiz veri
        """
        response = None  # Initialize to avoid UnboundLocalError
        try:
            response = self._request("GET", "/v1/ticker/price", {"symbol": symbol})
            
            # DEBUG: API yanıtını logla
            if response is None:
                self.logger.debug(f"API returned None for {symbol}")
            elif isinstance(response, list) and len(response) == 0:
                self.logger.debug(f"API returned empty list for {symbol}")
            else:
                self.logger.debug(f"API response for {symbol}: {type(response)} = {response}")
            
            # Response kontrolü - daha güvenli
            if response and isinstance(response, dict) and "price" in response:
                price_str = response.get("price")
                
                # Price değeri var mı ve geçerli mi kontrol et
                if price_str is not None:
                    try:
                        price = float(price_str)
                        
                        # Fiyat geçerliliği kontrolü
                        if price > 0:
                            return price
                        else:
                            self.logger.warning(f"⚠️  Invalid price value for {symbol}: {price}")
                            return None
                    except (ValueError, TypeError) as e:
                        self.logger.error(f"❌ Cannot convert price to float for {symbol}: {price_str} - {e}")
                        return None
                else:
                    self.logger.warning(f"⚠️  Price field is None for {symbol}")
                    return None
            
            # Response liste mi kontrol et (bazı API'ler liste döndürebilir)
            elif response and isinstance(response, list):
                if len(response) > 0:
                    # Liste ise ilk elemanı al
                    first_item = response[0]
                    if isinstance(first_item, dict) and "price" in first_item:
                        try:
                            price = float(first_item["price"])
                            if price > 0:
                                return price
                        except (ValueError, TypeError, IndexError) as e:
                            self.logger.error(f"❌ Error parsing price from list for {symbol}: {e}")
                            return None
                    else:
                        self.logger.warning(f"⚠️  Invalid list item format for {symbol}: {first_item}")
                        return None
                else:
                    self.logger.warning(f"⚠️  Ticker response is empty list for {symbol}")
                    return None
            else:
                self.logger.warning(f"⚠️  Invalid ticker response format for {symbol}: {type(response)} - {response}")
                return None
                
        except IndexError as e:
            # Liste index hatası - DETAYLI STACK TRACE
            import traceback
            self.logger.error(f"❌ List index out of range for {symbol}: {e}")
            self.logger.error("Stack trace:")
            self.logger.error(traceback.format_exc())
            self.logger.error(f"Response was: {response}")
            return None
        except (ValueError, TypeError, KeyError) as e:
            self.logger.error(f"❌ Price parsing error for {symbol}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error getting price for {symbol}: {e}")
            # Detaylı stack trace
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[List]:
        """
        Kline/Candlestick verisi al (güçlendirilmiş veri kontrolü ile)
        
        Returns:
            List[List]: Kline verisi (her kline en az 6 element içerir)
            []: Hata durumunda veya boş veri
        """
        try:
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            response = self._request("GET", "/v1/klines", params)
            
            # GÜÇLENDİRİLMİŞ KONTROL: Liste mi, boş değil mi, geçerli mi?
            if response and isinstance(response, list) and len(response) > 0:
                # Her kline'ın en az 6 element olduğundan emin ol
                valid_klines = []
                for kline in response:
                    if kline and isinstance(kline, list) and len(kline) >= 6:
                        valid_klines.append(kline)
                    else:
                        self.logger.warning(f"⚠️  Invalid kline format skipped for {symbol}")
                
                if len(valid_klines) > 0:
                    return valid_klines
                else:
                    self.logger.warning(f"⚠️  No valid klines found for {symbol}")
                    return []
            else:
                self.logger.warning(f"⚠️  Received empty or invalid kline data for {symbol}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error getting klines for {symbol}: {e}")
            return []
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """Leverage ayarla"""
        params = {
            "symbol": symbol,
            "leverage": leverage
        }
        response = self._request("POST", "/v1/leverage", params, signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def set_margin_type(self, symbol: str, margin_type: str) -> Dict:
        """Margin tipini ayarla (ISOLATED veya CROSSED)"""
        params = {
            "symbol": symbol,
            "marginType": margin_type
        }
        response = self._request("POST", "/v1/marginType", params, signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None, 
                   stop_price: Optional[float] = None, reduce_only: bool = False) -> Dict:
        """Futures emri ver"""
        params = {
            "symbol": symbol,
            "side": side,  # BUY veya SELL
            "type": order_type,  # MARKET, LIMIT, STOP, STOP_MARKET, etc.
            "quantity": quantity
        }
        
        if order_type == "LIMIT":
            params["timeInForce"] = "GTC"  # Good Till Cancel
            if price:
                params["price"] = price
        
        if order_type in ["STOP", "STOP_MARKET"] and stop_price:
            params["stopPrice"] = stop_price
            
        if reduce_only:
            params["reduceOnly"] = "true"
            
        response = self._request("POST", "/v1/order", params, signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Emri iptal et"""
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        response = self._request("DELETE", "/v1/order", params, signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def cancel_all_orders(self, symbol: str) -> Dict:
        """Sembol için tüm açık emirleri iptal et"""
        params = {"symbol": symbol}
        response = self._request("DELETE", "/v1/allOpenOrders", params, signed=True)
        if isinstance(response, dict):
            return response
        raise ValueError("Invalid response format")
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Açık emirleri al"""
        params = {}
        if symbol:
            params["symbol"] = symbol
        response = self._request("GET", "/v1/openOrders", params, signed=True)
        if isinstance(response, list):
            return response
        raise ValueError("Invalid response format")
    
    def get_order_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Emir geçmişini al"""
        params = {
            "symbol": symbol,
            "limit": limit
        }
        response = self._request("GET", "/v1/allOrders", params, signed=True)
        if isinstance(response, list):
            return response
        raise ValueError("Invalid response format")
    
    def close_position(self, symbol: str) -> Dict:
        """Pozisyonu market emriyle kapat"""
        # Önce mevcut pozisyonu kontrol et
        positions = self.get_positions()
        position = None
        
        for pos in positions:
            if pos["symbol"] == symbol and float(pos["positionAmt"]) != 0:
                position = pos
                break
        
        if not position:
            raise ValueError(f"No open position found for {symbol}")
        
        position_amt = float(position["positionAmt"])
        
        # Pozisyon kapatma emri (ters yönde)
        if position_amt > 0:  # Long pozisyon
            side = "SELL"
        else:  # Short pozisyon
            side = "BUY"
            position_amt = abs(position_amt)
        
        return self.place_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=position_amt,
            reduce_only=True
        )
    
    def start_price_stream(self, symbols: List[str]):
        """Futures fiyat akışını başlat"""
        def on_message(ws, message):
            data = json.loads(message)
            if 'data' in data:
                symbol = data['data']['s']
                price = float(data['data']['c'])
                self.price_data[symbol] = {
                    'price': price,
                    'timestamp': datetime.now(timezone.utc),
                    'volume': float(data['data']['v']),
                    'mark_price': float(data['data'].get('p', price))  # Mark price
                }
                self.logger.debug(f"{symbol}: ${price:.4f}")
        
        def on_error(ws, error):
            self.logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.logger.info("WebSocket connection closed")
        
        # Futures stream URL
        stream_names = [f"{symbol.lower()}@ticker" for symbol in symbols]
        stream_url = f"wss://fstream.binancefuture.com/stream?streams={'/'.join(stream_names)}"
        
        ws = websocket.WebSocketApp(
            stream_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # WebSocket'i ayrı thread'de başlat
        def run_ws():
            ws.run_forever()
            
        ws_thread = threading.Thread(target=run_ws, daemon=True)
        ws_thread.start()
        
        self.ws_connections['price_stream'] = ws
        self.logger.info(f"Futures price stream started for {len(symbols)} symbols")
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """En son fiyatı al (WebSocket'ten)"""
        if symbol in self.price_data:
            return self.price_data[symbol]['price']
        return None
    
    def get_funding_rate(self, symbol: str) -> Dict:
        """Funding rate bilgisini al"""
        params = {"symbol": symbol}
        response = self._request("GET", "/v1/premiumIndex", params)
        if isinstance(response, dict):
            return {
                'funding_rate': float(response.get('lastFundingRate', 0)),
                'next_funding_time': response.get('nextFundingTime', 0),
                'mark_price': float(response.get('markPrice', 0))
            }
        raise ValueError("Invalid response format")
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Belirli bir sembol için pozisyon bilgisi al"""
        positions = self.get_positions()
        for pos in positions:
            if pos["symbol"] == symbol and float(pos.get("positionAmt", 0)) != 0:
                return pos
        return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Anlık fiyat al (get_ticker_price'ın alias'ı)"""
        return self.get_ticker_price(symbol)
    
    def stop_all_streams(self):
        """Tüm WebSocket bağlantılarını kapat"""
        for ws in self.ws_connections.values():
            ws.close()
        self.ws_connections.clear()
        self.logger.info("All WebSocket streams stopped")


# Test fonksiyonu
if __name__ == "__main__":
    # Futures API'yi test et
    api = BinanceFuturesTestnetAPI()
    
    try:
        # Server zamanını kontrol et
        server_time = api.get_server_time()
        print(f"Server time: {datetime.fromtimestamp(server_time/1000)}")
        
        # Hesap bilgilerini kontrol et
        account = api.get_account_info()
        print(f"Account status: {account.get('canTrade', False)}")
        
        # Bakiyeleri kontrol et
        balances = api.get_balance()
        for balance in balances:
            if float(balance['walletBalance']) > 0:
                print(f"{balance['asset']}: {balance['walletBalance']}")
        
        # BTC fiyatını al
        btc_price = api.get_ticker_price("BTCUSDT")
        print(f"BTC Futures Price: ${btc_price:,.2f}")
        
        # Funding rate
        funding = api.get_funding_rate("BTCUSDT")
        print(f"BTC Funding Rate: {funding['funding_rate']:.6f}")
        
        # Leverage ayarla (test)
        try:
            leverage_result = api.set_leverage("BTCUSDT", 10)
            print(f"Leverage set: {leverage_result}")
        except Exception as e:
            print(f"Leverage setting (may already be set): {e}")
        
        # Pozisyonları kontrol et
        positions = api.get_positions()
        open_positions = [p for p in positions if float(p['positionAmt']) != 0]
        print(f"Open positions: {len(open_positions)}")
        
        # Fiyat akışını test et (5 saniye)
        print("Testing price stream for 5 seconds...")
        api.start_price_stream(["BTCUSDT", "ETHUSDT"])
        time.sleep(5)
        
        # En son fiyatları göster
        btc_latest = api.get_latest_price("BTCUSDT")
        eth_latest = api.get_latest_price("ETHUSDT")
        
        if btc_latest:
            print(f"Latest BTC: ${btc_latest:,.2f}")
        if eth_latest:
            print(f"Latest ETH: ${eth_latest:,.2f}")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        api.stop_all_streams()
