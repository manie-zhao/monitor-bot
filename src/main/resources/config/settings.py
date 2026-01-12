"""
Configuration module for monitor-bot
Handles environment variables, thresholds, and symbol management
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application metadata
APP_NAME = "monitor-bot"
VERSION = "1.0.0"

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

# Exchange API Keys (Optional - for higher rate limits)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

# Monitoring Configuration
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))  # 5 minutes in seconds
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD", "3.0"))  # 3% price change
OI_THRESHOLD = float(os.getenv("OI_THRESHOLD", "5.0"))  # 5% OI change

# Symbols to monitor
SYMBOLS_RAW = os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT")
SYMBOLS: List[str] = [s.strip() for s in SYMBOLS_RAW.split(",") if s.strip()]

# Exchange Configuration
EXCHANGES = ["binance", "bybit"]  # Exchanges to monitor

# Bybit market types to monitor
BYBIT_MARKET_TYPES = ["linear", "inverse"]  # Linear and Inverse futures

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Market Bias Indicators (Emojis)
BIAS_INDICATORS = {
    "long_inflow": "🔥 多头进场 (Long Inflow)",
    "short_inflow": "📉 空头进场 (Short Inflow)",
    "short_squeeze": "⚡ 空头挤压 (Short Squeeze)",
    "long_liquidation": "🌊 多头洗盘 (Long Liquidation)",
}


def validate_config() -> bool:
    """
    Validate required configuration settings
    Returns True if valid, False otherwise
    """
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set in .env file")
        return False

    if not CHAT_ID:
        print("ERROR: CHAT_ID not set in .env file")
        return False

    if not SYMBOLS:
        print("ERROR: No symbols configured in .env file")
        return False

    return True


def get_exchange_config(exchange: str) -> dict:
    """
    Get exchange-specific configuration
    Only includes API keys if they are actually set (non-empty)
    """
    binance_config = {
        "enableRateLimit": True,
        "options": {
            "defaultType": "future",  # Use futures market
        }
    }

    # Only add API keys if they're actually set
    if BINANCE_API_KEY and BINANCE_API_SECRET:
        binance_config["apiKey"] = BINANCE_API_KEY
        binance_config["secret"] = BINANCE_API_SECRET

    bybit_config = {
        "enableRateLimit": True,
    }

    # Only add API keys if they're actually set
    if BYBIT_API_KEY and BYBIT_API_SECRET:
        bybit_config["apiKey"] = BYBIT_API_KEY
        bybit_config["secret"] = BYBIT_API_SECRET

    configs = {
        "binance": binance_config,
        "bybit": bybit_config
    }

    return configs.get(exchange, {})
