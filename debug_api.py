#!/usr/bin/env python3
"""
Binance Testnet API Debug Script
API'nin ne döndürdüğünü görmek için basit test
"""

import requests
import json

# Binance Testnet Futures API
BASE_URL = "https://testnet.binancefuture.com/fapi"

def test_endpoints():
    print("=" * 60)
    print("🔍 Binance Testnet Futures API Test")
    print("=" * 60)
    
    # Test 1: Server Time
    print("\n1️⃣ Test: Server Time")
    try:
        response = requests.get(f"{BASE_URL}/v1/time", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Exchange Info (kontrol için)
    print("\n2️⃣ Test: Exchange Info (BTCUSDT)")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/exchangeInfo",
            params={"symbol": "BTCUSDT"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "symbols" in data:
            print(f"   Symbol count: {len(data['symbols'])}")
            if data['symbols']:
                symbol_info = data['symbols'][0]
                print(f"   Symbol: {symbol_info.get('symbol')}")
                print(f"   Status: {symbol_info.get('status')}")
        else:
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Ticker Price (SORUN BURDA!)
    print("\n3️⃣ Test: Ticker Price")
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    for symbol in test_symbols:
        print(f"\n   Testing {symbol}:")
        try:
            response = requests.get(
                f"{BASE_URL}/v1/ticker/price",
                params={"symbol": symbol},
                timeout=5
            )
            print(f"      Status: {response.status_code}")
            print(f"      Response Type: {type(response.json())}")
            print(f"      Response: {response.json()}")
            
            # Yanıt tipine göre işle
            data = response.json()
            if isinstance(data, dict):
                print(f"      ✅ DICT - Price: {data.get('price', 'N/A')}")
            elif isinstance(data, list):
                print(f"      ⚠️  LIST - Length: {len(data)}")
                if data:
                    print(f"      First item: {data[0]}")
            else:
                print(f"      ❌ UNKNOWN TYPE: {type(data)}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Test 4: Ticker Price (tüm semboller)
    print("\n4️⃣ Test: All Ticker Prices (parametre yok)")
    try:
        response = requests.get(f"{BASE_URL}/v1/ticker/price", timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response Type: {type(data)}")
        if isinstance(data, list):
            print(f"   Total tickers: {len(data)}")
            print(f"   First 3 items:")
            for item in data[:3]:
                print(f"      {item}")
        else:
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Klines (tarihsel veri)
    print("\n5️⃣ Test: Klines (Historical Data)")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": "1h",
                "limit": 5
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response Type: {type(data)}")
        if isinstance(data, list):
            print(f"   Klines count: {len(data)}")
            if data:
                print(f"   First kline: {data[0]}")
        else:
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test tamamlandı!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
