"""
Main entry point for monitor-bot
Initializes services and runs the monitoring loop
"""
import asyncio
import signal
import sys
from datetime import datetime

# Import configuration
from src.main.resources.config import settings

# Import services
from src.main.python.services.market_data_service import MarketDataService
from src.main.python.services.telegram_service import TelegramService
from src.main.python.core.monitoring_engine import MonitoringEngine


class MonitorBot:
    """
    Main bot class that coordinates all services
    """

    def __init__(self):
        self.running = False
        self.market_service = None
        self.telegram_service = None
        self.engine = None

    async def initialize(self):
        """Initialize all services"""
        print(f"\n{'='*60}")
        print(f"🤖 Monitor Bot v{settings.VERSION}")
        print(f"{'='*60}")
        print(f"⏰ Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"{'='*60}\n")

        # Validate configuration
        if not settings.validate_config():
            print("❌ Configuration validation failed. Please check your .env file.")
            sys.exit(1)

        print("✅ Configuration validated")

        # Initialize Telegram service
        print("🔌 Initializing Telegram service...")
        self.telegram_service = TelegramService(
            token=settings.TELEGRAM_TOKEN,
            chat_id=settings.CHAT_ID
        )

        # Test Telegram connection
        if not await self.telegram_service.test_connection():
            print("❌ Telegram connection failed. Please check your bot token and chat ID.")
            sys.exit(1)

        # Initialize Market Data service
        print("🔌 Initializing market data service...")
        binance_config = settings.get_exchange_config("binance")
        bybit_config = settings.get_exchange_config("bybit")

        self.market_service = MarketDataService(
            binance_config=binance_config,
            bybit_config=bybit_config,
            symbols=settings.SYMBOLS
        )

        await self.market_service.initialize()

        # Collect initial snapshots
        await self.market_service.get_initial_snapshots()

        # Initialize Monitoring Engine
        print("🔌 Initializing monitoring engine...")
        self.engine = MonitoringEngine(
            market_service=self.market_service,
            telegram_service=self.telegram_service,
            price_threshold=settings.PRICE_THRESHOLD,
            oi_threshold=settings.OI_THRESHOLD,
            bias_indicators=settings.BIAS_INDICATORS
        )

        print("\n✅ All services initialized successfully!\n")

        # Send startup notification
        await self.telegram_service.send_startup_message()

        # Print configuration
        print(f"{'='*60}")
        print("⚙️  Configuration")
        print(f"{'='*60}")
        print(f"Scan Interval: {settings.SCAN_INTERVAL}s ({settings.SCAN_INTERVAL // 60} minutes)")
        print(f"Price Threshold: {settings.PRICE_THRESHOLD}%")
        print(f"OI Threshold: {settings.OI_THRESHOLD}%")
        print(f"Symbols: {', '.join(settings.SYMBOLS)}")
        print(f"Exchanges: {', '.join(settings.EXCHANGES)}")
        print(f"{'='*60}\n")

    async def run(self):
        """Run the main monitoring loop"""
        self.running = True

        try:
            while self.running:
                # Run scan cycle
                await self.engine.run_scan_cycle()

                # Print statistics periodically
                await self.engine.print_statistics()

                # Wait for next scan interval
                print(f"⏳ Waiting {settings.SCAN_INTERVAL}s until next scan...")
                print(f"{'='*60}\n")

                # Sleep with cancellation support
                for i in range(settings.SCAN_INTERVAL):
                    if not self.running:
                        break
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            print("\n🛑 Monitoring loop cancelled")
        except Exception as e:
            print(f"\n❌ Unexpected error in monitoring loop: {e}")
            await self.telegram_service.send_error_message(f"Fatal error: {str(e)}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown all services gracefully"""
        print("\n🛑 Shutting down monitor-bot...")
        self.running = False

        if self.market_service:
            await self.market_service.close()

        if self.engine:
            stats = self.engine.get_statistics()
            print(f"\n📊 Final Statistics:")
            print(f"   Total Alerts Sent: {stats['total_alerts']}")
            print(f"   Tracked Snapshots: {stats['tracked_snapshots']}")

        print("\n✅ Monitor-bot shut down successfully")
        print(f"⏰ Stopped at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

    def handle_signal(self, sig, frame):
        """Handle shutdown signals"""
        print(f"\n⚠️  Received signal {sig}, initiating shutdown...")
        self.running = False


async def main():
    """Main entry point"""
    bot = MonitorBot()

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, bot.handle_signal)
    signal.signal(signal.SIGTERM, bot.handle_signal)

    try:
        await bot.initialize()
        await bot.run()
    except KeyboardInterrupt:
        print("\n⚠️  Keyboard interrupt received")
        await bot.shutdown()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
