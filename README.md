# monitor-bot

A high-performance Python-based monitoring bot that tracks Price and Open Interest (OI) anomalies for specific Altcoins on Binance Futures and Bybit Inverse/Linear Futures. The bot alerts users via Telegram when significant coordinated movements occur.

## 🎯 Project Overview

**monitor-bot** is a real-time cryptocurrency futures monitoring system that:
- Scans market data every **5 minutes**
- Tracks **Price** and **Open Interest (OI)** changes
- Alerts on coordinated movements: **Price ≥3%** AND **OI ≥5%**
- Analyzes market sentiment and categorizes bias
- Sends professional alerts via **Telegram**

## 🔥 Core Logic & Thresholds

An alert is triggered **ONLY** when **BOTH** conditions are met (AND logic):

1. **Price Change**: ≥ 3% (absolute value) within 5-minute interval
2. **Open Interest Change**: ≥ 5% (absolute value) within 5-minute interval

## 📊 Market Sentiment Analysis (The "Bias")

Every alert categorizes the movement based on Price & OI relationship:

| Price | OI | Bias | Meaning |
|-------|----|----|---------|
| ↑ | ↑ | 🔥 多头进场 (Long Inflow) | New longs opening |
| ↓ | ↑ | 📉 空头进场 (Short Inflow) | New shorts opening |
| ↑ | ↓ | ⚡ 空头挤压 (Short Squeeze) | Shorts covering/liquidating |
| ↓ | ↓ | 🌊 多头洗盘 (Long Liquidation) | Longs selling/liquidating |

## 🛠️ Technical Stack

- **Language**: Python 3.10+
- **Libraries**:
  - `ccxt` (Asynchronous) - Exchange connectivity
  - `python-telegram-bot` or `httpx` - Telegram API
- **Data Handling**: In-memory dictionary for snapshots (no database)
- **Concurrency**: `asyncio` for handling multiple symbols and exchanges

## 📱 Telegram Message Format

```
🔥 ALERT: BTC/USDT | Binance Futures

**Market Bias: 🔥 多头进场 (Long Inflow)**

Price: $45,230.50 | +3.45%
OI: $1.2B USD | +5.67%
Volume (24h): $8.5B

⏰ 2026-01-12 14:35:00 UTC
```

## 📂 Project Structure

```
monitor-bot/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # This file
├── .env                   # Environment variables (TELEGRAM_TOKEN, CHAT_ID)
├── .gitignore             # Git ignore patterns
├── requirements.txt       # Python dependencies
├── src/                   # Source code
│   ├── main/              # Main application code
│   │   ├── python/        # Python source code
│   │   │   ├── core/      # Core monitoring engine
│   │   │   ├── utils/     # Helper functions
│   │   │   ├── models/    # Data models
│   │   │   ├── services/  # Market data & Telegram services
│   │   │   ├── api/       # Exchange API integration
│   │   │   └── main.py    # Entry point
│   │   └── resources/     # Configuration files
│   │       └── config/    # Settings and symbol lists
│   └── test/              # Test code
│       ├── unit/          # Unit tests
│       └── integration/   # Integration tests
├── docs/                  # Documentation
├── tools/                 # Development scripts
├── examples/              # Usage examples
└── output/                # Logs and output files
```

## 🚀 Implementation Steps

### 1. Environment Setup
```bash
# Create .env file
TELEGRAM_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
BINANCE_API_KEY=optional
BINANCE_API_SECRET=optional
BYBIT_API_KEY=optional
BYBIT_API_SECRET=optional
```

### 2. Market Data Engine
- Async loop to fetch `ticker` and `open_interest` data
- Support for multiple altcoin symbols
- Handle Binance Futures + Bybit Inverse/Linear Futures

### 3. Calculation Module
- Compare current data with previous 5-minute snapshot
- Calculate percentage changes for Price and OI
- Store snapshots in-memory dictionary

### 4. Directional Algorithm
- Implement Price/OI matrix logic
- Categorize market bias (4 scenarios)
- Format bias with emoji indicators

### 5. Notification Module
- Format Markdown-style Telegram messages
- Send alerts only when both thresholds are met
- Include timestamp and exchange context

## 📋 Getting Started

### Prerequisites
```bash
# Python 3.10 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Create `.env` file with your Telegram credentials
2. Configure symbol watchlist in `src/main/resources/config/settings.py`
3. Set exchange preferences (Binance/Bybit)

### Running the Bot
```bash
# Run the monitoring bot
python -m src.main.python.main

# Or with Python path set
PYTHONPATH=. python src/main/python/main.py
```

## 🧪 Testing
```bash
# Run all tests
python -m pytest src/test/

# Run unit tests only
python -m pytest src/test/unit/

# Run integration tests
python -m pytest src/test/integration/
```

## 📖 Development Guidelines

### Before Starting Any Task
1. **Read CLAUDE.md first** - Contains essential development rules
2. Follow pre-task compliance checklist
3. Search for existing implementations before creating new files
4. Use proper module structure under `src/main/python/`
5. Commit after every completed task

### Code Organization
- **core/**: Monitoring engine, alert logic, main loop
- **utils/**: Helper functions, formatters, calculators
- **models/**: Data models for Price, OI, Alert structures
- **services/**: Market data service, Telegram service
- **api/**: Exchange API wrappers (Binance, Bybit)
- **resources/config/**: Configuration files, symbol lists

### Development Workflow
1. Search existing code before adding new functionality
2. Extend existing modules when possible
3. Use Task agents for operations >30 seconds
4. Single source of truth for all functionality
5. Commit after each feature/fix
6. Push to GitHub: `git push origin main`

## 🔐 Security Notes

- Never commit `.env` file to git
- Store API keys securely in environment variables
- Use read-only API keys when possible
- Rate limit API calls to avoid bans

## 📊 Performance Considerations

- Use `asyncio` for concurrent exchange requests
- In-memory data storage (no database overhead)
- Efficient 5-minute scan intervals
- Batch processing for multiple symbols

## 🐛 Troubleshooting

- **No alerts received**: Check threshold settings and market volatility
- **Telegram not working**: Verify `TELEGRAM_TOKEN` and `CHAT_ID` in `.env`
- **Exchange errors**: Check API rate limits and permissions
- **Missing data**: Ensure symbol format matches exchange requirements

---

**🎯 Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
**📺 Tutorial: https://youtu.be/8Q1bRZaHH24**
