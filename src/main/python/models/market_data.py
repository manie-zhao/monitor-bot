"""
Data models for market monitoring
Defines structures for snapshots, alerts, and market data
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MarketSnapshot:
    """
    Represents a snapshot of market data at a specific point in time
    """
    symbol: str
    exchange: str
    price: float
    open_interest: float  # OI in USD
    volume_24h: float  # 24h trading volume
    timestamp: datetime
    market_type: Optional[str] = None  # For Bybit: 'linear' or 'inverse'

    def __repr__(self) -> str:
        return (
            f"MarketSnapshot(symbol={self.symbol}, exchange={self.exchange}, "
            f"price={self.price:.2f}, oi={self.open_interest:.2f}, "
            f"timestamp={self.timestamp.isoformat()})"
        )


@dataclass
class PriceOIChange:
    """
    Represents calculated changes in price and OI between two snapshots
    """
    symbol: str
    exchange: str
    price_change_pct: float  # Percentage change
    oi_change_pct: float  # Percentage change
    volume_change_pct: float  # Percentage change
    current_price: float
    previous_price: float
    current_oi: float
    previous_oi: float
    volume_24h: float
    previous_volume: float
    timestamp: datetime

    def meets_threshold(self, price_threshold: float, oi_threshold: float) -> bool:
        """
        Check if changes meet either threshold (OR logic)
        Alert if price change >= threshold OR OI change >= threshold
        """
        return (
            abs(self.price_change_pct) >= price_threshold
            or abs(self.oi_change_pct) >= oi_threshold
        )

    def __repr__(self) -> str:
        return (
            f"PriceOIChange(symbol={self.symbol}, "
            f"price_change={self.price_change_pct:.2f}%, "
            f"oi_change={self.oi_change_pct:.2f}%, "
            f"volume_change={self.volume_change_pct:.2f}%)"
        )


@dataclass
class MarketBias:
    """
    Represents the calculated market bias based on Price & OI movement
    """
    bias_type: str  # 'long_inflow', 'short_inflow', 'short_squeeze', 'long_liquidation'
    indicator: str  # Formatted string with emoji
    description: str  # Human-readable description

    @staticmethod
    def calculate(price_change_pct: float, oi_change_pct: float, indicators: dict) -> "MarketBias":
        """
        Calculate market bias based on price and OI direction

        Logic:
        - Price ↑ & OI ↑: Long Inflow (new longs opening)
        - Price ↓ & OI ↑: Short Inflow (new shorts opening)
        - Price ↑ & OI ↓: Short Squeeze (shorts covering/liquidating)
        - Price ↓ & OI ↓: Long Liquidation (longs selling/liquidating)
        """
        price_up = price_change_pct > 0
        oi_up = oi_change_pct > 0

        if price_up and oi_up:
            bias_type = "long_inflow"
            description = "New longs are opening"
        elif not price_up and oi_up:
            bias_type = "short_inflow"
            description = "New shorts are opening"
        elif price_up and not oi_up:
            bias_type = "short_squeeze"
            description = "Shorts are covering/liquidating"
        else:  # not price_up and not oi_up
            bias_type = "long_liquidation"
            description = "Longs are selling/liquidating"

        indicator = indicators.get(bias_type, bias_type)

        return MarketBias(
            bias_type=bias_type,
            indicator=indicator,
            description=description
        )


@dataclass
class Alert:
    """
    Represents a complete alert with all necessary information
    """
    symbol: str
    exchange: str
    market_bias: MarketBias
    price_change: PriceOIChange
    timestamp: datetime
    market_type: Optional[str] = None

    def format_telegram_message(self) -> str:
        """
        Format alert as a Telegram message with Markdown
        """
        # Determine alert emoji based on bias
        alert_emoji_map = {
            "long_inflow": "🔥",
            "short_inflow": "📉",
            "short_squeeze": "⚡",
            "long_liquidation": "🌊",
        }
        alert_emoji = alert_emoji_map.get(self.market_bias.bias_type, "⚠️")

        # Format exchange name
        exchange_name = self.exchange.capitalize()
        if self.market_type:
            exchange_name += f" {self.market_type.capitalize()}"

        # Format price change with + or - sign
        price_sign = "+" if self.price_change.price_change_pct > 0 else ""
        oi_sign = "+" if self.price_change.oi_change_pct > 0 else ""
        volume_sign = "+" if self.price_change.volume_change_pct > 0 else ""

        message = f"""
{alert_emoji} *ALERT: {self.symbol}* | {exchange_name}

*Market Bias: {self.market_bias.indicator}*

*Price:* ${self.price_change.current_price:,.2f} | {price_sign}{self.price_change.price_change_pct:.2f}%
*OI:* ${self.price_change.current_oi / 1_000_000:.2f}M USD | {oi_sign}{self.price_change.oi_change_pct:.2f}%
*Volume (24h):* ${self.price_change.volume_24h / 1_000_000:.2f}M | {volume_sign}{self.price_change.volume_change_pct:.2f}%

⏰ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        return message.strip()

    def __repr__(self) -> str:
        return (
            f"Alert(symbol={self.symbol}, exchange={self.exchange}, "
            f"bias={self.market_bias.bias_type})"
        )
