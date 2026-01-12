"""
Unit tests for market data models
Tests data structures, bias calculations, and alert formatting
"""
import pytest
from datetime import datetime
from src.main.python.models.market_data import (
    MarketSnapshot,
    PriceOIChange,
    MarketBias,
    Alert
)
from src.main.resources.config import settings


class TestMarketSnapshot:
    """Tests for MarketSnapshot model"""

    def test_create_snapshot(self):
        """Test creating a market snapshot"""
        snapshot = MarketSnapshot(
            symbol="BTC/USDT",
            exchange="binance",
            price=45000.0,
            open_interest=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

        assert snapshot.symbol == "BTC/USDT"
        assert snapshot.exchange == "binance"
        assert snapshot.price == 45000.0
        assert snapshot.open_interest == 1200000000.0
        assert snapshot.volume_24h == 8500000000.0
        assert snapshot.market_type is None

    def test_snapshot_with_market_type(self):
        """Test snapshot with market type"""
        snapshot = MarketSnapshot(
            symbol="BTC/USD",
            exchange="bybit",
            price=45000.0,
            open_interest=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow(),
            market_type="inverse"
        )

        assert snapshot.market_type == "inverse"


class TestPriceOIChange:
    """Tests for PriceOIChange model"""

    def test_create_change(self):
        """Test creating a PriceOIChange object"""
        change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=3.5,
            oi_change_pct=5.5,
            current_price=46575.0,
            previous_price=45000.0,
            current_oi=1266000000.0,
            previous_oi=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

        assert change.symbol == "BTC/USDT"
        assert change.price_change_pct == 3.5
        assert change.oi_change_pct == 5.5

    def test_meets_threshold_both_met(self):
        """Test meets_threshold when both are met"""
        change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=3.5,
            oi_change_pct=5.5,
            current_price=46575.0,
            previous_price=45000.0,
            current_oi=1266000000.0,
            previous_oi=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

        assert change.meets_threshold(3.0, 5.0) is True

    def test_meets_threshold_only_price(self):
        """Test meets_threshold when only price meets"""
        change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=3.5,
            oi_change_pct=4.0,
            current_price=46575.0,
            previous_price=45000.0,
            current_oi=1248000000.0,
            previous_oi=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

        assert change.meets_threshold(3.0, 5.0) is False

    def test_meets_threshold_negative_values(self):
        """Test meets_threshold with negative changes"""
        change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=-3.5,
            oi_change_pct=-5.5,
            current_price=43425.0,
            previous_price=45000.0,
            current_oi=1134000000.0,
            previous_oi=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime.utcnow()
        )

        assert change.meets_threshold(3.0, 5.0) is True


class TestMarketBias:
    """Tests for MarketBias calculation"""

    def test_long_inflow(self):
        """Test Long Inflow bias (Price ↑ & OI ↑)"""
        bias = MarketBias.calculate(
            price_change_pct=3.5,
            oi_change_pct=5.5,
            indicators=settings.BIAS_INDICATORS
        )

        assert bias.bias_type == "long_inflow"
        assert "Long Inflow" in bias.indicator
        assert "🔥" in bias.indicator

    def test_short_inflow(self):
        """Test Short Inflow bias (Price ↓ & OI ↑)"""
        bias = MarketBias.calculate(
            price_change_pct=-3.5,
            oi_change_pct=5.5,
            indicators=settings.BIAS_INDICATORS
        )

        assert bias.bias_type == "short_inflow"
        assert "Short Inflow" in bias.indicator
        assert "📉" in bias.indicator

    def test_short_squeeze(self):
        """Test Short Squeeze bias (Price ↑ & OI ↓)"""
        bias = MarketBias.calculate(
            price_change_pct=3.5,
            oi_change_pct=-5.5,
            indicators=settings.BIAS_INDICATORS
        )

        assert bias.bias_type == "short_squeeze"
        assert "Short Squeeze" in bias.indicator
        assert "⚡" in bias.indicator

    def test_long_liquidation(self):
        """Test Long Liquidation bias (Price ↓ & OI ↓)"""
        bias = MarketBias.calculate(
            price_change_pct=-3.5,
            oi_change_pct=-5.5,
            indicators=settings.BIAS_INDICATORS
        )

        assert bias.bias_type == "long_liquidation"
        assert "Long Liquidation" in bias.indicator
        assert "🌊" in bias.indicator


class TestAlert:
    """Tests for Alert model and Telegram formatting"""

    def create_test_alert(self):
        """Helper to create a test alert"""
        price_change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=3.45,
            oi_change_pct=5.67,
            current_price=45230.50,
            previous_price=43715.75,
            current_oi=1200000000.0,
            previous_oi=1135500000.0,
            volume_24h=8500000000.0,
            timestamp=datetime(2026, 1, 12, 14, 35, 0)
        )

        market_bias = MarketBias.calculate(
            price_change_pct=3.45,
            oi_change_pct=5.67,
            indicators=settings.BIAS_INDICATORS
        )

        return Alert(
            symbol="BTC/USDT",
            exchange="binance",
            market_bias=market_bias,
            price_change=price_change,
            timestamp=datetime(2026, 1, 12, 14, 35, 0)
        )

    def test_create_alert(self):
        """Test creating an alert"""
        alert = self.create_test_alert()

        assert alert.symbol == "BTC/USDT"
        assert alert.exchange == "binance"
        assert alert.market_bias.bias_type == "long_inflow"

    def test_telegram_message_format(self):
        """Test Telegram message formatting"""
        alert = self.create_test_alert()
        message = alert.format_telegram_message()

        # Check message contains key elements
        assert "BTC/USDT" in message
        assert "Binance" in message
        assert "Long Inflow" in message
        assert "45,230.50" in message
        assert "+3.45%" in message
        assert "1.20M" in message
        assert "+5.67%" in message
        assert "8.50M" in message
        assert "2026-01-12 14:35:00" in message

    def test_telegram_message_with_market_type(self):
        """Test Telegram message with market type"""
        alert = self.create_test_alert()
        alert.market_type = "linear"
        message = alert.format_telegram_message()

        assert "Bybit Linear" in message or "linear" in message.lower()

    def test_negative_changes_formatting(self):
        """Test formatting with negative changes"""
        price_change = PriceOIChange(
            symbol="BTC/USDT",
            exchange="binance",
            price_change_pct=-3.45,
            oi_change_pct=-5.67,
            current_price=43620.00,
            previous_price=45180.00,
            current_oi=1132000000.0,
            previous_oi=1200000000.0,
            volume_24h=8500000000.0,
            timestamp=datetime(2026, 1, 12, 14, 35, 0)
        )

        market_bias = MarketBias.calculate(
            price_change_pct=-3.45,
            oi_change_pct=-5.67,
            indicators=settings.BIAS_INDICATORS
        )

        alert = Alert(
            symbol="BTC/USDT",
            exchange="binance",
            market_bias=market_bias,
            price_change=price_change,
            timestamp=datetime(2026, 1, 12, 14, 35, 0)
        )

        message = alert.format_telegram_message()

        # Check negative signs are present
        assert "-3.45%" in message
        assert "-5.67%" in message
        assert "Long Liquidation" in message or "多头洗盘" in message
