"""
Telegram notification service
Handles sending formatted alerts to Telegram
"""
import httpx
from typing import Optional
from src.main.python.models.market_data import Alert


class TelegramService:
    """
    Service for sending notifications via Telegram Bot API
    """

    def __init__(self, token: str, chat_id: str):
        """
        Initialize Telegram service

        Args:
            token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message to Telegram

        Args:
            message: Message text to send
            parse_mode: Parsing mode ('Markdown' or 'HTML')

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": parse_mode,
                        "disable_web_page_preview": True
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    print(f"✅ Telegram alert sent successfully")
                    return True
                else:
                    print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False

    async def send_alert(self, alert: Alert) -> bool:
        """
        Send a formatted alert to Telegram

        Args:
            alert: Alert object to send

        Returns:
            True if alert sent successfully, False otherwise
        """
        message = alert.format_telegram_message()
        return await self.send_message(message)

    async def send_startup_message(self) -> bool:
        """
        Send a startup notification

        Returns:
            True if message sent successfully, False otherwise
        """
        message = """
🤖 *Monitor Bot Started*

✅ Monitoring active
📊 Tracking Price & OI changes
⚡ Alert thresholds configured

The bot is now watching the markets!
"""
        return await self.send_message(message.strip())

    async def send_error_message(self, error: str) -> bool:
        """
        Send an error notification

        Args:
            error: Error message to send

        Returns:
            True if message sent successfully, False otherwise
        """
        message = f"""
⚠️ *Monitor Bot Error*

{error}

Please check the logs for details.
"""
        return await self.send_message(message.strip())

    async def test_connection(self) -> bool:
        """
        Test the Telegram connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/getMe",
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    bot_name = data.get('result', {}).get('username', 'Unknown')
                    print(f"✅ Telegram connection successful - Bot: @{bot_name}")
                    return True
                else:
                    print(f"❌ Telegram connection failed: {response.status_code}")
                    return False

        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            return False
