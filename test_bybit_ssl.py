#!/usr/bin/env python3
"""Test script to diagnose Bybit SSL connection issues"""

import ssl
import urllib.request
import certifi

def test_bybit_connection():
    """Test different methods to connect to Bybit API"""

    print("=" * 60)
    print("Testing Bybit SSL Connection")
    print("=" * 60)

    # Test 1: Basic urllib with default SSL
    print("\n1. Testing urllib with default SSL context...")
    try:
        response = urllib.request.urlopen('https://api.bybit.com/v5/market/time', timeout=10)
        print(f"✅ SUCCESS - Status: {response.status}")
        print(f"   Response: {response.read()[:100]}")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {e}")

    # Test 2: urllib with certifi bundle
    print("\n2. Testing urllib with certifi SSL context...")
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        response = urllib.request.urlopen('https://api.bybit.com/v5/market/time',
                                         context=context,
                                         timeout=10)
        print(f"✅ SUCCESS - Status: {response.status}")
        print(f"   Response: {response.read()[:100]}")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {e}")

    # Test 3: urllib with unverified SSL (NOT RECOMMENDED, just for diagnosis)
    print("\n3. Testing urllib with unverified SSL (diagnostic only)...")
    try:
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen('https://api.bybit.com/v5/market/time',
                                         context=context,
                                         timeout=10)
        print(f"✅ SUCCESS - Status: {response.status}")
        print(f"   Response: {response.read()[:100]}")
        print("   NOTE: If this works, it's a certificate validation issue")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {e}")
        print("   NOTE: If this fails too, it's not a certificate issue")

    # Test 4: Test with requests library if available
    print("\n4. Testing with requests library...")
    try:
        import requests
        response = requests.get('https://api.bybit.com/v5/market/time', timeout=10)
        print(f"✅ SUCCESS - Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}")
    except ImportError:
        print("⚠️  SKIPPED - requests library not installed")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {e}")

    # Test 5: Check certifi location and version
    print("\n5. Certifi information...")
    print(f"   Certifi location: {certifi.where()}")
    print(f"   Certifi version: {certifi.__version__}")

    # Test 6: Compare with Binance (working)
    print("\n6. Testing Binance (for comparison)...")
    try:
        response = urllib.request.urlopen('https://api.binance.com/api/v3/ping', timeout=10)
        print(f"✅ Binance works - Status: {response.status}")
    except Exception as e:
        print(f"❌ Binance failed - {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_bybit_connection()
