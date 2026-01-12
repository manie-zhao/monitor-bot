"""
Standalone dry-run test script for monitor-bot
Tests bot logic with simulated market data without external dependencies
"""
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


# Inline minimal versions of our models for testing
@dataclass
class MarketSnapshot:
    symbol: str
    exchange: str
    price: float
    open_interest: float
    volume_24h: float
    timestamp: datetime
    market_type: Optional[str] = None


@dataclass
class PriceOIChange:
    symbol: str
    exchange: str
    price_change_pct: float
    oi_change_pct: float
    current_price: float
    previous_price: float
    current_oi: float
    previous_oi: float
    volume_24h: float
    timestamp: datetime

    def meets_threshold(self, price_threshold: float, oi_threshold: float) -> bool:
        return (
            abs(self.price_change_pct) >= price_threshold
            and abs(self.oi_change_pct) >= oi_threshold
        )


# Calculation functions
def calculate_percentage_change(old_value: float, new_value: float) -> float:
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def compare_snapshots(previous: MarketSnapshot, current: MarketSnapshot) -> Optional[PriceOIChange]:
    if previous.symbol != current.symbol or previous.exchange != current.exchange:
        return None

    price_change_pct = calculate_percentage_change(previous.price, current.price)
    oi_change_pct = calculate_percentage_change(previous.open_interest, current.open_interest)

    return PriceOIChange(
        symbol=current.symbol,
        exchange=current.exchange,
        price_change_pct=price_change_pct,
        oi_change_pct=oi_change_pct,
        current_price=current.price,
        previous_price=previous.price,
        current_oi=current.open_interest,
        previous_oi=previous.open_interest,
        volume_24h=current.volume_24h,
        timestamp=current.timestamp
    )


# Market bias calculation
def calculate_bias(price_change_pct: float, oi_change_pct: float) -> tuple:
    price_up = price_change_pct > 0
    oi_up = oi_change_pct > 0

    if price_up and oi_up:
        return ("long_inflow", "🔥 多头进场 (Long Inflow)", "New longs are opening")
    elif not price_up and oi_up:
        return ("short_inflow", "📉 空头进场 (Short Inflow)", "New shorts are opening")
    elif price_up and not oi_up:
        return ("short_squeeze", "⚡ 空头挤压 (Short Squeeze)", "Shorts are covering/liquidating")
    else:
        return ("long_liquidation", "🌊 多头洗盘 (Long Liquidation)", "Longs are selling/liquidating")


# Test scenarios
def setup_test_scenarios():
    scenarios = []

    # Scenario 1: Long Inflow
    scenarios.append({
        "name": "Long Inflow - Both thresholds met",
        "previous": MarketSnapshot("BTC/USDT", "binance", 45000.0, 1200000000.0, 8500000000.0, datetime.utcnow()),
        "current": MarketSnapshot("BTC/USDT", "binance", 46575.0, 1266000000.0, 8500000000.0, datetime.utcnow()),
        "should_alert": True,
        "expected_bias": "long_inflow"
    })

    # Scenario 2: Short Inflow
    scenarios.append({
        "name": "Short Inflow - Both thresholds met",
        "previous": MarketSnapshot("ETH/USDT", "binance", 3000.0, 500000000.0, 2000000000.0, datetime.utcnow()),
        "current": MarketSnapshot("ETH/USDT", "binance", 2895.0, 527500000.0, 2000000000.0, datetime.utcnow()),
        "should_alert": True,
        "expected_bias": "short_inflow"
    })

    # Scenario 3: Short Squeeze
    scenarios.append({
        "name": "Short Squeeze - Both thresholds met",
        "previous": MarketSnapshot("SOL/USDT", "bybit", 100.0, 150000000.0, 500000000.0, datetime.utcnow(), "linear"),
        "current": MarketSnapshot("SOL/USDT", "bybit", 104.0, 141000000.0, 500000000.0, datetime.utcnow(), "linear"),
        "should_alert": True,
        "expected_bias": "short_squeeze"
    })

    # Scenario 4: Long Liquidation
    scenarios.append({
        "name": "Long Liquidation - Both thresholds met",
        "previous": MarketSnapshot("BNB/USDT", "binance", 400.0, 200000000.0, 800000000.0, datetime.utcnow()),
        "current": MarketSnapshot("BNB/USDT", "binance", 380.0, 186000000.0, 800000000.0, datetime.utcnow()),
        "should_alert": True,
        "expected_bias": "long_liquidation"
    })

    # Scenario 5: No Alert - Only price threshold met
    scenarios.append({
        "name": "No Alert - Only price threshold met",
        "previous": MarketSnapshot("BTC/USDT", "binance", 45000.0, 1200000000.0, 8500000000.0, datetime.utcnow()),
        "current": MarketSnapshot("BTC/USDT", "binance", 46575.0, 1212000000.0, 8500000000.0, datetime.utcnow()),
        "should_alert": False,
        "expected_bias": None
    })

    # Scenario 6: No Alert - Only OI threshold met
    scenarios.append({
        "name": "No Alert - Only OI threshold met",
        "previous": MarketSnapshot("ETH/USDT", "binance", 3000.0, 500000000.0, 2000000000.0, datetime.utcnow()),
        "current": MarketSnapshot("ETH/USDT", "binance", 3045.0, 527500000.0, 2000000000.0, datetime.utcnow()),
        "should_alert": False,
        "expected_bias": None
    })

    return scenarios


def test_scenario(scenario: dict, price_threshold: float, oi_threshold: float):
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
    meets_threshold = change.meets_threshold(price_threshold, oi_threshold)

    print(f"\nThreshold Check:")
    print(f"  Price Threshold (≥{price_threshold}%): {'✅' if abs(change.price_change_pct) >= price_threshold else '❌'}")
    print(f"  OI Threshold (≥{oi_threshold}%): {'✅' if abs(change.oi_change_pct) >= oi_threshold else '❌'}")
    print(f"  Should Alert: {'✅ YES' if meets_threshold else '❌ NO'}")

    # Verify expectation
    if meets_threshold != scenario["should_alert"]:
        print(f"\n❌ FAILED: Expected should_alert={scenario['should_alert']}, got {meets_threshold}")
        return False

    if meets_threshold:
        # Calculate market bias
        bias_type, bias_indicator, bias_description = calculate_bias(
            change.price_change_pct,
            change.oi_change_pct
        )

        print(f"\nMarket Bias:")
        print(f"  Type: {bias_type}")
        print(f"  Indicator: {bias_indicator}")
        print(f"  Description: {bias_description}")

        # Verify bias type
        if bias_type != scenario["expected_bias"]:
            print(f"\n❌ FAILED: Expected bias={scenario['expected_bias']}, got {bias_type}")
            return False

        # Format alert preview
        price_sign = "+" if change.price_change_pct > 0 else ""
        oi_sign = "+" if change.oi_change_pct > 0 else ""

        alert_emoji_map = {
            "long_inflow": "🔥",
            "short_inflow": "📉",
            "short_squeeze": "⚡",
            "long_liquidation": "🌊",
        }
        alert_emoji = alert_emoji_map.get(bias_type, "⚠️")

        print(f"\nTelegram Message Preview:")
        print("─" * 80)
        print(f"""
{alert_emoji} *ALERT: {change.symbol}* | {change.exchange.capitalize()}

*Market Bias: {bias_indicator}*

*Price:* ${change.current_price:,.2f} | {price_sign}{change.price_change_pct:.2f}%
*OI:* ${change.current_oi / 1_000_000:.2f}M USD | {oi_sign}{change.oi_change_pct:.2f}%
*Volume (24h):* ${change.volume_24h / 1_000_000:.2f}M

⏰ {change.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC
""".strip())
        print("─" * 80)

    print(f"\n✅ PASSED: {scenario['name']}")
    return True


def main():
    price_threshold = 3.0
    oi_threshold = 5.0

    print("\n" + "="*80)
    print("🧪 MONITOR-BOT DRY RUN TEST SUITE")
    print("="*80)
    print(f"Configuration:")
    print(f"  Price Threshold: {price_threshold}%")
    print(f"  OI Threshold: {oi_threshold}%")

    scenarios = setup_test_scenarios()
    print(f"  Total Scenarios: {len(scenarios)}")

    results = []
    for scenario in scenarios:
        result = test_scenario(scenario, price_threshold, oi_threshold)
        results.append(result)

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

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
