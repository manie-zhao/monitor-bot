"""
Core monitoring engine
Coordinates market data collection, analysis, and alerting
"""
import asyncio
from typing import List
from datetime import datetime
from src.main.python.services.market_data_service import MarketDataService
from src.main.python.services.telegram_service import TelegramService
from src.main.python.models.market_data import Alert, MarketBias, PriceOIChange
from src.main.python.utils.calculators import is_significant_move


class MonitoringEngine:
    """
    Core engine that monitors markets and sends alerts
    """

    def __init__(
        self,
        market_service: MarketDataService,
        telegram_service: TelegramService,
        price_threshold: float,
        oi_threshold: float,
        bias_indicators: dict
    ):
        """
        Initialize monitoring engine

        Args:
            market_service: Market data service instance
            telegram_service: Telegram service instance
            price_threshold: Price change threshold (e.g., 3.0 for 3%)
            oi_threshold: OI change threshold (e.g., 5.0 for 5%)
            bias_indicators: Dictionary of bias indicators with emojis
        """
        self.market_service = market_service
        self.telegram_service = telegram_service
        self.price_threshold = price_threshold
        self.oi_threshold = oi_threshold
        self.bias_indicators = bias_indicators
        self.alert_count = 0

    async def analyze_changes(self, changes: List[PriceOIChange]) -> List[Alert]:
        """
        Analyze price/OI changes and generate alerts for significant moves

        Args:
            changes: List of PriceOIChange objects

        Returns:
            List of Alert objects for significant moves
        """
        alerts = []

        for change in changes:
            # Check if change meets both thresholds (AND logic)
            if change.meets_threshold(self.price_threshold, self.oi_threshold):
                # Calculate market bias
                market_bias = MarketBias.calculate(
                    change.price_change_pct,
                    change.oi_change_pct,
                    self.bias_indicators
                )

                # Create alert
                alert = Alert(
                    symbol=change.symbol,
                    exchange=change.exchange,
                    market_bias=market_bias,
                    price_change=change,
                    timestamp=change.timestamp,
                    market_type=None  # Will be set if available from snapshot
                )

                alerts.append(alert)

                print(f"🚨 Alert generated: {alert.symbol} on {alert.exchange} - {market_bias.bias_type}")

        return alerts

    async def send_alerts(self, alerts: List[Alert]):
        """
        Send alerts via Telegram

        Args:
            alerts: List of Alert objects to send
        """
        for alert in alerts:
            success = await self.telegram_service.send_alert(alert)
            if success:
                self.alert_count += 1
                print(f"✅ Alert #{self.alert_count} sent: {alert.symbol} ({alert.exchange})")
            else:
                print(f"❌ Failed to send alert: {alert.symbol} ({alert.exchange})")

            # Small delay between alerts to avoid rate limiting
            await asyncio.sleep(0.5)

    async def scan_markets(self):
        """
        Perform a single market scan:
        1. Fetch current market data
        2. Compare with previous snapshots
        3. Analyze for significant changes
        4. Send alerts if thresholds are met
        """
        print(f"\n{'='*60}")
        print(f"🔍 Scanning markets - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"{'='*60}")

        try:
            # Get price/OI changes
            changes = await self.market_service.get_changes()
            print(f"📊 Analyzed {len(changes)} market pairs")

            if not changes:
                print("ℹ️  No changes to analyze (first scan or no data)")
                return

            # Analyze changes for significant moves
            alerts = await self.analyze_changes(changes)

            if alerts:
                print(f"🚨 {len(alerts)} significant movements detected!")
                await self.send_alerts(alerts)
            else:
                print("✅ No significant movements detected")

        except Exception as e:
            print(f"❌ Error during market scan: {e}")
            await self.telegram_service.send_error_message(f"Market scan error: {str(e)}")

    async def run_scan_cycle(self):
        """
        Run a single scan cycle:
        1. Scan markets
        2. Generate alerts if needed
        """
        await self.scan_markets()

    def get_statistics(self) -> dict:
        """
        Get monitoring statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "total_alerts": self.alert_count,
            "tracked_snapshots": self.market_service.get_snapshot_count(),
            "price_threshold": self.price_threshold,
            "oi_threshold": self.oi_threshold
        }

    async def print_statistics(self):
        """Print current monitoring statistics"""
        stats = self.get_statistics()
        print(f"\n{'='*60}")
        print("📈 Monitoring Statistics")
        print(f"{'='*60}")
        print(f"Total Alerts Sent: {stats['total_alerts']}")
        print(f"Tracked Snapshots: {stats['tracked_snapshots']}")
        print(f"Price Threshold: {stats['price_threshold']}%")
        print(f"OI Threshold: {stats['oi_threshold']}%")
        print(f"{'='*60}\n")
