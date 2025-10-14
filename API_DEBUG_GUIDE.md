# 🔍 API Debug Rehberi

## 🎯 Sorun

Bot şu hatayı veriyor:
```
❌ List index out of range for BTCUSDT: list index out of range
This usually means API returned empty data. Check Binance API status.
```

**Sebep:** API yanıt formatı beklenenden farklı olabilir.

## 📋 Frankfurt Sunucusunda Debug

### Adım 1: Kodu Güncelle

```bash
cd ~/Trade_demo
git pull origin main
```

### Adım 2: Debug Script'i Çalıştır

```bash
python debug_api.py
```

**Bu script şunları test eder:**
1. ✅ Server Time (API erişilebilir mi?)
2. ✅ Exchange Info (Semboller aktif mi?)
3. ❓ Ticker Price (TEK sembol) - **SORUN BURDA**
4. ✅ All Ticker Prices (TÜM semboller)
5. ✅ Klines (Tarihsel veri)

### Beklenen Çıktı

**EĞER API ÇALIŞIYORSA:**
```
3️⃣ Test: Ticker Price
   Testing BTCUSDT:
      Status: 200
      Response Type: <class 'dict'>
      Response: {'symbol': 'BTCUSDT', 'price': '67850.50'}
      ✅ DICT - Price: 67850.50
```

**EĞER API SORUNLUYSA:**
```
3️⃣ Test: Ticker Price
   Testing BTCUSDT:
      Status: 200
      Response Type: <class 'list'>
      Response: []  ← BOŞ LİSTE!
      ⚠️  LIST - Length: 0
```

---

## 🔧 Muhtemel Sorunlar ve Çözümleri

### Sorun 1: API Endpoint Yanlış

**Belirti:**
```
Status: 404
❌ Error: Not Found
```

**Çözüm:**
API endpoint'i kontrol et. Binance Futures için:
- ✅ DOĞRU: `/fapi/v1/ticker/price`
- ❌ YANLIŞ: `/api/v1/ticker/price` (Spot API)
- ❌ YANLIŞ: `/v1/ticker/price` (Prefix eksik)

**Config'de kontrol:**
```bash
cat config/production_config.json | grep api_url
```

Şu çıkmalı:
```json
"api_url": "https://testnet.binancefuture.com/fapi"
```

### Sorun 2: API Boş Liste Döndürüyor

**Belirti:**
```
Response Type: <class 'list'>
Response: []
```

**Muhtemel Sebepler:**
1. Testnet bakımda
2. Sembol testnet'te desteklenmiyor
3. API versiyonu değişmiş

**Çözüm:**
Alternatif endpoint kullan:

```bash
# Manuel test
curl "https://testnet.binancefuture.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
```

### Sorun 3: API Timeout

**Belirti:**
```
❌ Error: Connection timeout
```

**Çözüm:**
```bash
# İnternet bağlantısı kontrol
ping -c 3 testnet.binancefuture.com

# DNS kontrol
nslookup testnet.binancefuture.com

# Firewall kontrol (gerekirse)
sudo ufw status
```

### Sorun 4: Rate Limit

**Belirti:**
```
Status: 429
❌ Error: Too many requests
```

**Çözüm:**
1-2 dakika bekle, tekrar dene.

---

## 💡 Eğer Debug Script Sorun Bulduysa

### 1. API Endpoint Değiştir

**Eğer `/v1/ticker/price` çalışmıyorsa:**

```bash
# Alternatif 1: 24hr Ticker (daha detaylı)
# src/binance_futures_api.py dosyasında
# "/v1/ticker/price" → "/v1/ticker/24hr"

# Alternatif 2: Premium Index
# "/v1/ticker/price" → "/v1/premiumIndex"
```

### 2. Kod Düzeltmesi

**Eğer API liste döndürüyorsa:**

`src/binance_futures_api.py` dosyasında `get_ticker_price()` metodunu düzelt:

```python
# ŞU ANKİ KOD (336. satır civarı):
elif response and isinstance(response, list):
    if len(response) > 0:
        first_item = response[0]
        ...
    else:
        self.logger.warning(f"⚠️  Ticker response is empty list for {symbol}")
        return None

# DÜZELTME:
elif response and isinstance(response, list):
    # BOŞ LİSTE İSE: Tüm ticker'ları çek, symbol'ü filtrele
    if len(response) == 0:
        self.logger.warning(f"⚠️  Empty list response, trying alternative method...")
        
        # Alternatif: Tüm ticker'ları çek
        all_response = self._request("GET", "/v1/ticker/price", {})
        if all_response and isinstance(all_response, list):
            for item in all_response:
                if item.get("symbol") == symbol:
                    return float(item["price"])
        
        self.logger.error(f"❌ Could not find {symbol} in all tickers")
        return None
    else:
        # Liste dolu ise normal devam et
        first_item = response[0]
        ...
```

---

## 🎯 Hızlı Düzeltme (Eğer API Çalışmıyorsa)

### Yöntem 1: Alternative Endpoint Kullan

**24hr Ticker kullan (daha güvenilir):**

```bash
# src/binance_futures_api.py'yi düzenle
nano src/binance_futures_api.py
```

`get_ticker_price()` metodunda (305. satır):
```python
# ÖNCE
response = self._request("GET", "/v1/ticker/price", {"symbol": symbol})

# SONRA
response = self._request("GET", "/v1/ticker/24hr", {"symbol": symbol})
# Response format: {"symbol": "BTCUSDT", "lastPrice": "67850.50", ...}
# lastPrice kullan!
```

Sonra `price` yerine `lastPrice` kullan:
```python
# ÖNCE
if response and isinstance(response, dict) and "price" in response:
    price_str = response.get("price")

# SONRA  
if response and isinstance(response, dict) and "lastPrice" in response:
    price_str = response.get("lastPrice")
```

### Yöntem 2: Mark Price Kullan

```python
# Mark price daha stabil
response = self._request("GET", "/v1/premiumIndex", {"symbol": symbol})
# Response: {"symbol": "BTCUSDT", "markPrice": "67850.50", ...}
```

---

## ✅ Test Sonrası

### 1. Bot'u Yeniden Başlat

```bash
# Düzeltme yaptıysan
sudo systemctl restart genetix-bot

# Logları izle
./manage_bot.sh logs
```

### 2. Başarı Kontrolü

**Beklenen log:**
```
✅ Binance API connected! Server time: ...
📊 BTCUSDT: 200 candles loaded
📊 ETHUSDT: 200 candles loaded
🤖 Bot başlatıldı - 8 sembol izleniyor
```

**HATA OLMAMALI:**
```
❌ List index out of range  ← BU OLMAMALI!
```

### 3. Dashboard Kontrolü

```bash
curl http://localhost:8080/api/status
```

Beklenen:
```json
{
  "status": "running",
  "symbols": 8,
  "active_positions": 0,
  "uptime_seconds": 120
}
```

---

## 📞 Yardım

### Eğer debug script başarılıysa ama bot hata veriyorsa:

```bash
# 1. Log seviyesini DEBUG'a çevir
nano config/production_config.json
# "level": "INFO" → "level": "DEBUG"

# 2. Bot'u restart et
sudo systemctl restart genetix-bot

# 3. Logları izle
tail -f logs/production/bot_$(date +%Y%m%d).log | grep "API response"
```

### Eğer debug script de başarısızsa:

**API erişilemiyor demektir. Kontrol et:**

1. ✅ İnternet: `ping 8.8.8.8`
2. ✅ DNS: `nslookup testnet.binancefuture.com`
3. ✅ Binance Status: https://www.binance.com/en/support/announcement
4. ✅ Testnet Status: https://testnet.binancefuture.com

---

## 🚀 Özet

```bash
# 1. Debug script'i çalıştır
cd ~/Trade_demo
git pull origin main
python debug_api.py

# 2. Sorun varsa yukarıdaki çözümleri uygula

# 3. Bot'u restart et
sudo systemctl restart genetix-bot

# 4. Logları kontrol et
./manage_bot.sh logs
```

**Hedef:** `list index out of range` hatasını ortadan kaldırmak!

---

**Hazırlayan:** GenetiX AI Agent  
**Tarih:** 14 Ekim 2025  
**Commit:** 25b708b
