# Testing Guide for monitor-bot

This guide covers all aspects of testing the monitoring bot.

## Quick Start

```bash
# 1. Run dry-run test (no live API calls)
python tools/dry_run_test.py

# 2. Run unit tests
pytest src/test/unit/

# 3. Run with live data (requires .env setup)
python src/main/python/main.py
```

## Test Suite Overview

### 1. Dry-Run Tests (`tools/dry_run_test.py`)

Simulates market data and tests bot logic without making live API calls.

**What it tests:**
- Price & OI change calculations
- Threshold validation (AND logic)
- Market bias detection (4 scenarios)
- Alert generation
- Telegram message formatting

**Run it:**
```bash
python tools/dry_run_test.py
```

**Expected output:**
```
🧪 MONITOR-BOT DRY RUN TEST SUITE
════════════════════════════════════════════════════════════
Configuration:
  Price Threshold: 3.0%
  OI Threshold: 5.0%
  Total Scenarios: 6

Testing: Long Inflow - Both thresholds met
... (test details)
✅ PASSED

📊 TEST SUMMARY
════════════════════════════════════════════════════════════
Total Tests: 6
✅ Passed: 6
❌ Failed: 0

🎉 All tests passed! Bot logic is working correctly.
```

### 2. Unit Tests (`src/test/unit/`)

Tests individual components in isolation.

**Test Files:**
- `test_calculators.py` - Calculation utilities
- `test_models.py` - Data models and structures

**Run all unit tests:**
```bash
pytest src/test/unit/ -v
```

**Run specific test file:**
```bash
pytest src/test/unit/test_calculators.py -v
```

**Run with coverage:**
```bash
pytest src/test/unit/ --cov=src/main/python --cov-report=html
```

**Expected output:**
```
================================ test session starts =================================
collected 25 items

src/test/unit/test_calculators.py::TestCalculatePercentageChange::test_positive_change PASSED [  4%]
src/test/unit/test_calculators.py::TestCalculatePercentageChange::test_negative_change PASSED [  8%]
...
src/test/unit/test_models.py::TestAlert::test_telegram_message_format PASSED [ 100%]

================================ 25 passed in 0.15s ==================================
```

### 3. Integration Tests (Coming Soon)

Will test services with mock exchanges:
- Market data service
- Telegram service
- Monitoring engine

## Test Scenarios Explained

### Scenario 1: Long Inflow 🔥
- **Price**: ↑ 3.5%
- **OI**: ↑ 5.5%
- **Interpretation**: New long positions opening
- **Should Alert**: ✅ YES

### Scenario 2: Short Inflow 📉
- **Price**: ↓ 3.5%
- **OI**: ↑ 5.5%
- **Interpretation**: New short positions opening
- **Should Alert**: ✅ YES

### Scenario 3: Short Squeeze ⚡
- **Price**: ↑ 4%
- **OI**: ↓ 6%
- **Interpretation**: Shorts covering/liquidating
- **Should Alert**: ✅ YES

### Scenario 4: Long Liquidation 🌊
- **Price**: ↓ 5%
- **OI**: ↓ 7%
- **Interpretation**: Longs selling/liquidating
- **Should Alert**: ✅ YES

### Scenario 5: No Alert - Price Only
- **Price**: ↑ 3.5% ✅
- **OI**: ↑ 1% ❌
- **Should Alert**: ❌ NO (OI threshold not met)

### Scenario 6: No Alert - OI Only
- **Price**: ↑ 1.5% ❌
- **OI**: ↑ 5.5% ✅
- **Should Alert**: ❌ NO (Price threshold not met)

## Manual Testing with Live Data

### Prerequisites

1. **Setup .env file** with your credentials:
```bash
cp .env.example .env
# Edit .env with your Telegram token and chat ID
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Test Telegram connection**:
```bash
python -c "
import asyncio
from src.main.python.services.telegram_service import TelegramService
from src.main.resources.config import settings

async def test():
    service = TelegramService(settings.TELEGRAM_TOKEN, settings.CHAT_ID)
    success = await service.test_connection()
    if success:
        await service.send_message('✅ Test successful!')

asyncio.run(test())
"
```

### Running the Bot

**Start the bot:**
```bash
python src/main/python/main.py
```

**Expected startup output:**
```
================================================================
🤖 Monitor Bot v1.0.0
================================================================
⏰ Started at: 2026-01-12 14:30:00 UTC
================================================================
✅ Configuration validated
🔌 Initializing Telegram service...
✅ Telegram connection successful - Bot: @your_bot
🔌 Initializing market data service...
🔌 Initializing exchange connections...
✅ Exchange connections initialized
📸 Collecting initial market snapshots...
📊 Fetched 12 market snapshots
✅ Stored 12 initial snapshots
✅ All services initialized successfully!
================================================================
⚙️  Configuration
================================================================
Scan Interval: 300s (5 minutes)
Price Threshold: 3.0%
OI Threshold: 5.0%
Symbols: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT
Exchanges: binance, bybit
================================================================
```

**You should also receive a Telegram message:**
```
🤖 Monitor Bot Started

✅ Monitoring active
📊 Tracking Price & OI changes
⚡ Alert thresholds configured

The bot is now watching the markets!
```

### What to Expect

1. **First Scan (5 minutes)**: No alerts (establishing baseline)
2. **Subsequent Scans**: Alerts only when thresholds are met
3. **Console Output**: Detailed logging of each scan
4. **Telegram Alerts**: Professional formatted messages

### Sample Alert

When thresholds are met, you'll receive a Telegram message like:

```
🔥 ALERT: BTC/USDT | Binance

**Market Bias: 🔥 多头进场 (Long Inflow)**

Price: $45,230.50 | +3.45%
OI: $1.20M USD | +5.67%
Volume (24h): $8.50M

⏰ 2026-01-12 14:35:00 UTC
```

## Troubleshooting Tests

### Dry-Run Tests Failing

**Issue**: Import errors
```bash
ModuleNotFoundError: No module named 'src'
```

**Solution**: Run from project root
```bash
cd /path/to/monitor-bot
python tools/dry_run_test.py
```

### Unit Tests Failing

**Issue**: Missing pytest
```bash
bash: pytest: command not found
```

**Solution**: Install test dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Live Bot Not Connecting

**Issue**: Configuration errors
```bash
ERROR: TELEGRAM_TOKEN not set in .env file
```

**Solution**: Check .env file
```bash
# Ensure .env exists and contains:
TELEGRAM_TOKEN=your_token_here
CHAT_ID=your_chat_id_here
```

### No Market Data

**Issue**: Exchange connection failed
```bash
Error fetching ticker for BTC/USDT on binance
```

**Solution**: Check internet connection and exchange status
- Binance: https://www.binance.com/en/support/announcement
- Bybit: https://status.bybit.com/

### Rate Limiting

**Issue**: Too many requests
```bash
Error: Rate limit exceeded
```

**Solution**: Reduce monitored symbols or increase scan interval
```bash
# In .env
SCAN_INTERVAL=600  # 10 minutes instead of 5
SYMBOLS=BTC/USDT,ETH/USDT  # Monitor fewer symbols
```

## Performance Testing

### Memory Usage

Monitor memory consumption:
```bash
# Linux/Mac
ps aux | grep python

# Or use htop
htop
```

Expected memory: 50-100 MB for normal operation

### Response Time

Check scan duration in logs:
```
🔍 Scanning markets - 2026-01-12 14:35:00 UTC
📊 Fetched 12 market snapshots  # Should be < 5 seconds
✅ No significant movements detected
```

## Continuous Integration (Future)

To add CI/CD with GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest src/test/unit/
      - run: python tools/dry_run_test.py
```

## Best Practices

1. **Always run dry-run tests** before live testing
2. **Use unit tests** during development
3. **Test with small symbol lists** first
4. **Monitor logs** for errors
5. **Start with longer intervals** (10-15 minutes) during testing
6. **Keep test snapshots** for debugging

## Next Steps

1. ✅ Run dry-run test
2. ✅ Run unit tests
3. ✅ Setup Telegram bot
4. ✅ Test with live data (short period)
5. ✅ Monitor for 1-2 hours
6. ✅ Adjust thresholds if needed
7. ✅ Deploy for 24/7 monitoring

Happy testing! 🚀
