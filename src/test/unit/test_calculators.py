"""
Unit tests for calculation utilities
Tests percentage change calculations, snapshot comparisons, and threshold validation
"""
import pytest
from datetime import datetime
from src.main.python.utils.calculators import (
    calculate_percentage_change,
    compare_snapshots,
    format_large_number,
    is_significant_move
)
from src.main.python.models.market_data import MarketSnapshot


class TestCalculatePercentageChange:
    """Tests for calculate_percentage_change function"""

    def test_positive_change(self):
        """Test positive percentage change"""
        result = calculate_percentage_change(100, 103)
        assert result == 3.0

    def test_negative_change(self):
        """Test negative percentage change"""
        result = calculate_percentage_change(100, 95)
        assert result == -5.0

    def test_zero_change(self):
        """Test zero change"""
        result = calculate_percentage_change(100, 100)
        assert result == 0.0

    def test_large_change(self):
        """Test large percentage change"""
        result = calculate_percentage_change(100, 200)
        assert result == 100.0

    def test_zero_old_value(self):
        """Test with zero old value"""
        result = calculate_percentage_change(0, 100)
        assert result == 0.0

    def test_decimal_values(self):
        """Test with decimal values"""
        result = calculate_percentage_change(45230.50, 46791.57)
        assert pytest.approx(result, rel=0.01) == 3.45


class TestCompareSnapshots:
    """Tests for compare_snapshots function"""

    def create_snapshot(self, symbol="BTC/USDT", exchange="binance", price=45000.0, oi=1200000000.0):
        """Helper to create test snapshot"""
        return MarketSnapshot(
            symbol=symbol,
            exchange=exchange,
            price=price,
            open_interest=oi,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

    def test_valid_comparison(self):
        """Test valid snapshot comparison"""
        previous = self.create_snapshot(price=45000.0, oi=1200000000.0)
        current = self.create_snapshot(price=46545.0, oi=1268040000.0)

        result = compare_snapshots(previous, current)

        assert result is not None
        assert result.symbol == "BTC/USDT"
        assert result.exchange == "binance"
        assert pytest.approx(result.price_change_pct, rel=0.01) == 3.43
        assert pytest.approx(result.oi_change_pct, rel=0.01) == 5.67

    def test_mismatched_symbols(self):
        """Test comparison with different symbols"""
        previous = self.create_snapshot(symbol="BTC/USDT")
        current = self.create_snapshot(symbol="ETH/USDT")

        result = compare_snapshots(previous, current)
        assert result is None

    def test_mismatched_exchanges(self):
        """Test comparison with different exchanges"""
        previous = self.create_snapshot(exchange="binance")
        current = self.create_snapshot(exchange="bybit")

        result = compare_snapshots(previous, current)
        assert result is None

    def test_negative_changes(self):
        """Test with negative price and OI changes"""
        previous = self.create_snapshot(price=45000.0, oi=1200000000.0)
        current = self.create_snapshot(price=43650.0, oi=1140000000.0)

        result = compare_snapshots(previous, current)

        assert result is not None
        assert result.price_change_pct < 0
        assert result.oi_change_pct < 0


class TestFormatLargeNumber:
    """Tests for format_large_number function"""

    def test_billions(self):
        """Test billion formatting"""
        result = format_large_number(2500000000)
        assert result == "2.50B"

    def test_millions(self):
        """Test million formatting"""
        result = format_large_number(1500000)
        assert result == "1.50M"

    def test_thousands(self):
        """Test thousand formatting"""
        result = format_large_number(5500)
        assert result == "5.50K"

    def test_small_numbers(self):
        """Test small numbers"""
        result = format_large_number(500)
        assert result == "500.00"

    def test_custom_decimals(self):
        """Test custom decimal places"""
        result = format_large_number(1234567, decimals=1)
        assert result == "1.2M"


class TestIsSignificantMove:
    """Tests for is_significant_move function"""

    def test_both_thresholds_met(self):
        """Test when both thresholds are met"""
        result = is_significant_move(
            price_change_pct=3.5,
            oi_change_pct=5.5,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is True

    def test_only_price_threshold_met(self):
        """Test when only price threshold is met"""
        result = is_significant_move(
            price_change_pct=3.5,
            oi_change_pct=4.0,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is False

    def test_only_oi_threshold_met(self):
        """Test when only OI threshold is met"""
        result = is_significant_move(
            price_change_pct=2.0,
            oi_change_pct=6.0,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is False

    def test_neither_threshold_met(self):
        """Test when neither threshold is met"""
        result = is_significant_move(
            price_change_pct=2.0,
            oi_change_pct=4.0,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is False

    def test_negative_changes_above_threshold(self):
        """Test with negative changes that meet thresholds"""
        result = is_significant_move(
            price_change_pct=-3.5,
            oi_change_pct=-5.5,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is True

    def test_exact_thresholds(self):
        """Test with values exactly at thresholds"""
        result = is_significant_move(
            price_change_pct=3.0,
            oi_change_pct=5.0,
            price_threshold=3.0,
            oi_threshold=5.0
        )
        assert result is True
