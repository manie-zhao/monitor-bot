"""
Main entry point for monitor-bot
Initializes services and runs the monitoring loop
"""
import asyncio
import signal
import sys
import logging
from datetime import datetime

# Import configuration
from src.main.resources.config import settings

# Import services
from src.main.python.services.market_data_service import MarketDataService
from src.main.python.services.telegram_service import TelegramService
from src.main.python.core.monitoring_engine import MonitoringEngine

# Import logging setup
from src.main.python.utils.logging_config import setup_logging


class MonitorBot:
    """
    Main bot class that coordinates all services
    """

    def __init__(self):
        self.running = False
        self.market_service = None
        self.telegram_service = None
        self.engine = None
        self.logger = setup_logging()

    async def initialize(self):
        """Initialize all services"""
        self.logger.info("="*60)
        self.logger.info(f"🤖 Monitor Bot v{settings.VERSION}")
        self.logger.info("="*60)
        self.logger.info(f"⏰ Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        self.logger.info("="*60)

        # Validate configuration
        if not settings.validate_config():
            self.logger.error("Configuration validation failed. Please check your .env file.")
            sys.exit(1)

        self.logger.info("✅ Configuration validated")

        # Initialize Telegram service
        self.logger.info("🔌 Initializing Telegram service...")
        self.telegram_service = TelegramService(
            token=settings.TELEGRAM_TOKEN,
            chat_id=settings.CHAT_ID
        )

        # Test Telegram connection
        if not await self.telegram_service.test_connection():
            self.logger.error("Telegram connection failed. Please check your bot token and chat ID.")
            sys.exit(1)

        # Initialize Market Data service
        self.logger.info("🔌 Initializing market data service...")
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
        self.logger.info("🔌 Initializing monitoring engine...")
        self.engine = MonitoringEngine(
            market_service=self.market_service,
            telegram_service=self.telegram_service,
            price_threshold=settings.PRICE_THRESHOLD,
            oi_threshold=settings.OI_THRESHOLD,
            bias_indicators=settings.BIAS_INDICATORS
        )

        self.logger.info("✅ All services initialized successfully!")

        # Send introduction message explaining how the bot works
        await self.telegram_service.send_introduction_message(
            symbols_count=len(settings.SYMBOLS),
            price_threshold=settings.PRICE_THRESHOLD,
            oi_threshold=settings.OI_THRESHOLD,
            scan_interval=settings.SCAN_INTERVAL
        )

        # Log configuration
        self.logger.info("="*60)
        self.logger.info("⚙️  Configuration")
        self.logger.info("="*60)
        self.logger.info(f"Scan Interval: {settings.SCAN_INTERVAL}s ({settings.SCAN_INTERVAL // 60} minutes)")
        self.logger.info(f"Price Threshold: {settings.PRICE_THRESHOLD}%")
        self.logger.info(f"OI Threshold: {settings.OI_THRESHOLD}%")
        self.logger.info(f"Symbols: {', '.join(settings.SYMBOLS)}")
        self.logger.info(f"Exchanges: {', '.join(settings.EXCHANGES)}")
        self.logger.info("="*60)

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
                self.logger.info(f"⏳ Waiting {settings.SCAN_INTERVAL}s until next scan...")
                self.logger.info("="*60)

                # Sleep with cancellation support
                for i in range(settings.SCAN_INTERVAL):
                    if not self.running:
                        break
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            self.logger.warning("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
            if self.telegram_service:
                await self.telegram_service.send_error_message(f"Fatal error: {str(e)}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown all services gracefully"""
        self.logger.info("🛑 Shutting down monitor-bot...")
        self.running = False

        if self.market_service:
            await self.market_service.close()

        if self.engine:
            stats = self.engine.get_statistics()
            self.logger.info("📊 Final Statistics:")
            self.logger.info(f"   Total Alerts Sent: {stats['total_alerts']}")
            self.logger.info(f"   Tracked Snapshots: {stats['tracked_snapshots']}")

        self.logger.info("✅ Monitor-bot shut down successfully")
        self.logger.info(f"⏰ Stopped at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    def handle_signal(self, sig, frame):
        """Handle shutdown signals"""
        self.logger.warning(f"Received signal {sig}, initiating shutdown...")
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
        bot.logger.warning("Keyboard interrupt received")
        await bot.shutdown()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
