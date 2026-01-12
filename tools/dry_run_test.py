"""
Dry-run test script for monitor-bot
Tests bot logic with simulated market data without live API calls
"""
import asyncio
from datetime import datetime
from src.main.python.models.market_data import MarketSnapshot, PriceOIChange, MarketBias, Alert
from src.main.python.utils.calculators import compare_snapshots, is_significant_move
from src.main.resources.config import settings


class DryRunSimulator:
    """
    Simulates market data and tests bot logic
    """

    def __init__(self):
        self.test_scenarios = []
        self.setup_test_scenarios()

    def setup_test_scenarios(self):
        """Setup various test scenarios"""

        # Scenario 1: Long Inflow (Price ↑ 3.5%, OI ↑ 5.5%)
        self.test_scenarios.append({
            "name": "Long Inflow - Both thresholds met",
            "previous": MarketSnapshot(
                symbol="BTC/USDT",
                exchange="binance",
                price=45000.0,
                open_interest=1200000000.0,
                volume_24h=8500000000.0,
                timestamp=datetime.utcnow()
            ),
            "current": MarketSnapshot(
                symbol="BTC/USDT",
                exchange="binance",
                price=46575.0,  # +3.5%
                open_interest=1266000000.0,  # +5.5%
                volume_24h=8500000000.0,
                timestamp=datetime.utcnow()
            ),
            "should_alert": True,
            "expected_bias": "long_inflow"
        })

        # Scenario 2: Short Inflow (Price ↓ 3.5%, OI ↑ 5.5%)
        self.test_scenarios.append({
            "name": "Short Inflow - Both thresholds met",
            "previous": MarketSnapshot(
                symbol="ETH/USDT",
                exchange="binance",
                price=3000.0,
                open_interest=500000000.0,
                volume_24h=2000000000.0,
                timestamp=datetime.utcnow()
            ),
            "current": MarketSnapshot(
                symbol="ETH/USDT",
                exchange="binance",
                price=2895.0,  # -3.5%
                open_interest=527500000.0,  # +5.5%
                volume_24h=2000000000.0,
                timestamp=datetime.utcnow()
            ),
            "should_alert": True,
            "expected_bias": "short_inflow"
        })

        # Scenario 3: Short Squeeze (Price ↑ 4%, OI ↓ 6%)
        self.test_scenarios.append({
            "name": "Short Squeeze - Both thresholds met",
            "previous": MarketSnapshot(
                symbol="SOL/USDT",
                exchange="bybit",
                price=100.0,
                open_interest=150000000.0,
                volume_24h=500000000.0,
                timestamp=datetime.utcnow(),
                market_type="linear"
            ),
            "current": MarketSnapshot(
                symbol="SOL/USDT",
                exchange="bybit",
                price=104.0,  # +4%
                open_interest=141000000.0,  # -6%
                volume_24h=500000000.0,
                timestamp=datetime.utcnow(),
                market_type="linear"
            ),
            "should_alert": True,
            "expected_bias": "short_squeeze"
        })

        # Scenario 4: Long Liquidation (Price ↓ 5%, OI ↓ 7%)
        self.test_scenarios.append({
            "name": "Long Liquidation - Both thresholds met",
            "previous": MarketSnapshot(
                symbol="BNB/USDT",
                exchange="binance",
                price=400.0,
                open_interest=200000000.0,
                volume_24h=800000000.0,
                timestamp=datetime.utcnow()
            ),
            "current": MarketSnapshot(
                symbol="BNB/USDT",
                exchange="binance",
                price=380.0,  # -5%
                open_interest=186000000.0,  # -7%
                volume_24h=800000000.0,
                timestamp=datetime.utcnow()
            ),
            "should_alert": True,
            "expected_bias": "long_liquidation"
        })

        # Scenario 5: No Alert - Only price threshold met
        self.test_scenarios.append({
            "name": "No Alert - Only price threshold met",
            "previous": MarketSnapshot(
                symbol="BTC/USDT",
                exchange="binance",
                price=45000.0,
                open_interest=1200000000.0,
                volume_24h=8500000000.0,
                timestamp=datetime.utcnow()
            ),
            "current": MarketSnapshot(
                symbol="BTC/USDT",
                exchange="binance",
                price=46575.0,  # +3.5%
                open_interest=1212000000.0,  # +1% only
                volume_24h=8500000000.0,
                timestamp=datetime.utcnow()
            ),
            "should_alert": False,
            "expected_bias": None
        })

        # Scenario 6: No Alert - Only OI threshold met
        self.test_scenarios.append({
            "name": "No Alert - Only OI threshold met",
            "previous": MarketSnapshot(
                symbol="ETH/USDT",
                exchange="binance",
                price=3000.0,
                open_interest=500000000.0,
                volume_24h=2000000000.0,
                timestamp=datetime.utcnow()
            ),
            "current": MarketSnapshot(
                symbol="ETH/USDT",
                exchange="binance",
                price=3045.0,  # +1.5% only
                open_interest=527500000.0,  # +5.5%
                volume_24h=2000000000.0,
                timestamp=datetime.utcnow()
            ),
            "should_alert": False,
            "expected_bias": None
        })

    def test_scenario(self, scenario: dict):
        """Test a single scenario"""
        print(f"\n{'='*80}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*80}")

        previous = scenario["previous"]
        current = scenario["current"]

        print(f"\nPrevious State:")
        print(f"  Symbol: {previous.symbol} | Exchange: {previous.exchange}")
        print(f"  Price: ${previous.price:,.2f}")
        print(f"  OI: ${previous.open_interest:,.0f}")

        print(f"\nCurrent State:")
        print(f"  Symbol: {current.symbol} | Exchange: {current.exchange}")
        print(f"  Price: ${current.price:,.2f}")
        print(f"  OI: ${current.open_interest:,.0f}")

        # Compare snapshots
        change = compare_snapshots(previous, current)

        if not change:
            print("\n❌ ERROR: Failed to compare snapshots")
            return False

        print(f"\nCalculated Changes:")
        print(f"  Price Change: {change.price_change_pct:+.2f}%")
        print(f"  OI Change: {change.oi_change_pct:+.2f}%")

        # Check if thresholds are met
        meets_threshold = change.meets_threshold(
            settings.PRICE_THRESHOLD,
            settings.OI_THRESHOLD
        )

        print(f"\nThreshold Check:")
        print(f"  Price Threshold (≥{settings.PRICE_THRESHOLD}%): {'✅' if abs(change.price_change_pct) >= settings.PRICE_THRESHOLD else '❌'}")
        print(f"  OI Threshold (≥{settings.OI_THRESHOLD}%): {'✅' if abs(change.oi_change_pct) >= settings.OI_THRESHOLD else '❌'}")
        print(f"  Should Alert: {'✅ YES' if meets_threshold else '❌ NO'}")

        # Verify expectation
        if meets_threshold != scenario["should_alert"]:
            print(f"\n❌ FAILED: Expected should_alert={scenario['should_alert']}, got {meets_threshold}")
            return False

        if meets_threshold:
            # Calculate market bias
            bias = MarketBias.calculate(
                change.price_change_pct,
                change.oi_change_pct,
                settings.BIAS_INDICATORS
            )

            print(f"\nMarket Bias:")
            print(f"  Type: {bias.bias_type}")
            print(f"  Indicator: {bias.indicator}")
            print(f"  Description: {bias.description}")

            # Verify bias type
            if bias.bias_type != scenario["expected_bias"]:
                print(f"\n❌ FAILED: Expected bias={scenario['expected_bias']}, got {bias.bias_type}")
                return False

            # Create and format alert
            alert = Alert(
                symbol=change.symbol,
                exchange=change.exchange,
                market_bias=bias,
                price_change=change,
                timestamp=change.timestamp,
                market_type=current.market_type
            )

            print(f"\nTelegram Message Preview:")
            print("─" * 80)
            print(alert.format_telegram_message())
            print("─" * 80)

        print(f"\n✅ PASSED: {scenario['name']}")
        return True

    async def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*80)
        print("🧪 MONITOR-BOT DRY RUN TEST SUITE")
        print("="*80)
        print(f"Configuration:")
        print(f"  Price Threshold: {settings.PRICE_THRESHOLD}%")
        print(f"  OI Threshold: {settings.OI_THRESHOLD}%")
        print(f"  Total Scenarios: {len(self.test_scenarios)}")

        results = []
        for scenario in self.test_scenarios:
            result = self.test_scenario(scenario)
            results.append(result)
            await asyncio.sleep(0.1)  # Small delay between tests

        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        passed = sum(results)
        failed = len(results) - passed
        print(f"Total Tests: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")

        if failed == 0:
            print("\n🎉 All tests passed! Bot logic is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")

        print("="*80 + "\n")

        return failed == 0


async def main():
    """Main entry point for dry-run tests"""
    simulator = DryRunSimulator()
    success = await simulator.run_all_tests()

    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
