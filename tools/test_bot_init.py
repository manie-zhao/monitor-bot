"""
Quick bot test - checks if everything initializes correctly
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.abspath('.'))

print("="*60)
print("🧪 MONITOR-BOT INITIALIZATION TEST")
print("="*60)

# Test 1: Load configuration
print("\n1️⃣ Loading configuration...")
try:
    from src.main.resources.config import settings
    print(f"   ✅ Configuration loaded")
    print(f"   Bot Token: {settings.TELEGRAM_TOKEN[:20]}...")
    print(f"   Chat ID: {settings.CHAT_ID}")
    print(f"   Symbols: {', '.join(settings.SYMBOLS)}")
    print(f"   Thresholds: Price {settings.PRICE_THRESHOLD}%, OI {settings.OI_THRESHOLD}%")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 2: Validate configuration
print("\n2️⃣ Validating configuration...")
try:
    if settings.validate_config():
        print("   ✅ Configuration valid")
    else:
        print("   ❌ Configuration invalid")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 3: Import models
print("\n3️⃣ Importing data models...")
try:
    from src.main.python.models.market_data import MarketSnapshot, Alert, MarketBias
    print("   ✅ Models imported")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 4: Import services
print("\n4️⃣ Importing services...")
try:
    from src.main.python.services.telegram_service import TelegramService
    from src.main.python.services.market_data_service import MarketDataService
    print("   ✅ Services imported")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Test 5: Import monitoring engine
print("\n5️⃣ Importing monitoring engine...")
try:
    from src.main.python.core.monitoring_engine import MonitoringEngine
    print("   ✅ Monitoring engine imported")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL COMPONENTS LOADED SUCCESSFULLY!")
print("="*60)
print("\n🚀 Your bot is ready to run!")
print("\n📝 To start the bot:")
print("   PYTHONPATH=. python3 src/main/python/main.py")
print("\n⚠️  Note: Due to SSL certificate issues on your system,")
print("   the bot may have trouble connecting to exchanges.")
print("   This can be fixed by installing SSL certificates.")
print("="*60 + "\n")
