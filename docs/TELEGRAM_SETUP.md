# Telegram Bot Setup Guide

This guide will help you set up a Telegram bot to receive alerts from monitor-bot.

## Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a conversation** with BotFather
3. **Send the command**: `/newbot`
4. **Choose a name** for your bot (e.g., "My Crypto Monitor")
5. **Choose a username** (must end with 'bot', e.g., "my_crypto_monitor_bot")
6. **Copy the token** - BotFather will give you an HTTP API token like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```
7. **Save this token** - you'll need it for the `.env` file

## Step 2: Get Your Chat ID

### Method 1: Using @userinfobot (Easiest)

1. **Search for** `@userinfobot` in Telegram
2. **Start a conversation** and send any message
3. **Copy your Chat ID** (it will be a number like `123456789`)

### Method 2: Using the Telegram API

1. **Send a message** to your bot (the one you just created)
2. **Open this URL** in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. **Find your chat ID** in the JSON response under `result[0].message.chat.id`

Example response:
```json
{
  "ok": true,
  "result": [
    {
      "message": {
        "chat": {
          "id": 123456789,  // <-- This is your Chat ID
          "first_name": "Your Name"
        }
      }
    }
  ]
}
```

## Step 3: Configure Your .env File

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file** and add your credentials:
   ```bash
   # Telegram Bot Configuration
   TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   CHAT_ID=123456789

   # Optional: Exchange API Keys (for higher rate limits)
   BINANCE_API_KEY=
   BINANCE_API_SECRET=
   BYBIT_API_KEY=
   BYBIT_API_SECRET=

   # Monitoring Configuration
   SCAN_INTERVAL=300  # 5 minutes in seconds
   PRICE_THRESHOLD=3.0  # 3% price change
   OI_THRESHOLD=5.0  # 5% OI change

   # Symbols to monitor (comma-separated)
   SYMBOLS=BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT
   ```

3. **Save the file**

## Step 4: Test Your Telegram Connection

Run the test script to verify your Telegram setup:

```bash
python -c "
import asyncio
from src.main.python.services.telegram_service import TelegramService
from src.main.resources.config import settings

async def test():
    service = TelegramService(settings.TELEGRAM_TOKEN, settings.CHAT_ID)
    if await service.test_connection():
        print('✅ Telegram connection successful!')
        await service.send_message('🤖 Monitor-bot test message!')
    else:
        print('❌ Telegram connection failed!')

asyncio.run(test())
"
```

If successful, you should:
- See "✅ Telegram connection successful!" in the terminal
- Receive a test message from your bot in Telegram

## Step 5: Configure Bot Settings (Optional)

You can customize your bot's appearance in BotFather:

1. **Send** `/setdescription` to @BotFather
2. **Select your bot**
3. **Add a description**: "Crypto futures monitoring bot for Price & OI anomalies"

4. **Send** `/setabouttext` to @BotFather
5. **Add about text**: "Monitors Binance and Bybit futures markets"

6. **Send** `/setuserpic` to @BotFather
7. **Upload a profile picture** for your bot

## Troubleshooting

### Bot Token Not Working
- Make sure you copied the entire token (no spaces or line breaks)
- Token format should be: `NUMBER:ALPHANUMERIC`
- Regenerate token if needed: Send `/token` to @BotFather

### Chat ID Not Working
- Make sure you sent a message to your bot first
- Chat ID should be a plain number (positive or negative)
- For private chats, it's usually a positive number
- For groups, it's usually a negative number starting with `-100`

### Not Receiving Messages
- Check that your bot is not blocked
- Make sure your Chat ID matches the chat where you want to receive messages
- Verify the bot has permission to send messages (for groups)

### Rate Limiting
- If you're getting rate limit errors, add delays between messages
- The bot automatically adds 0.5s delay between alerts
- Consider using only one exchange if you're hitting limits

## Group Chat Setup (Optional)

To receive alerts in a Telegram group:

1. **Create a group** in Telegram
2. **Add your bot** to the group
3. **Make the bot an admin** (optional, but recommended)
4. **Get the group Chat ID**:
   - Send a message in the group
   - Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
   - Find the chat ID (will be negative, like `-1001234567890`)
5. **Update your .env** with the group Chat ID

## Security Tips

- **Never share** your bot token publicly
- **Never commit** your `.env` file to git (it's already in .gitignore)
- **Regenerate token** if accidentally exposed
- **Use environment variables** for production deployments
- **Consider using** a dedicated bot for production vs. testing

## Next Steps

Once your Telegram bot is configured:

1. **Run the dry-run test**: `python tools/dry_run_test.py`
2. **Run unit tests**: `pytest src/test/`
3. **Start the bot**: `python src/main/python/main.py`

You should receive a startup message in Telegram when the bot initializes!
