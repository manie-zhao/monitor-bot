"""
Bybit exchange wrapper
Handles market data fetching from Bybit Linear and Inverse Futures
"""
from typing import Optional
from datetime import datetime
from src.main.python.api.base_exchange import BaseExchange
from src.main.python.models.market_data import MarketSnapshot


class BybitExchange(BaseExchange):
    """
    Bybit exchange wrapper for Linear and Inverse Futures
    """

    def __init__(self, config: dict):
        super().__init__("bybit", config)

    async def fetch_market_snapshot(
        self,
        symbol: str,
        market_type: str = "linear"
    ) -> Optional[MarketSnapshot]:
        """
        Fetch current market snapshot from Bybit

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT', 'BTC/USD')
            market_type: 'linear' for USDT-settled or 'inverse' for coin-settled

        Returns:
            MarketSnapshot object or None if fetch fails
        """
        try:
            # Set the market type in exchange options
            if market_type == "inverse":
                self.exchange.options['defaultType'] = 'inverse'
            else:
                self.exchange.options['defaultType'] = 'linear'

            # Fetch ticker for price and volume
            ticker = await self.fetch_ticker(symbol)
            if not ticker:
                return None

            # Fetch open interest
            oi_data = await self.fetch_open_interest(symbol)
            if not oi_data:
                return None

            # Extract data
            price = ticker.get('last') or ticker.get('close') or 0
            if price is None:
                price = 0
            price = float(price)

            volume_24h = ticker.get('quoteVolume') or 0
            if volume_24h is None:
                volume_24h = 0
            volume_24h = float(volume_24h)

            # Open interest handling for Bybit
            # Bybit returns openInterestAmount (in base currency) but openInterestValue is None
            # We need to calculate USD value ourselves
            open_interest_amount = oi_data.get('openInterestAmount') or 0
            if open_interest_amount is None:
                open_interest_amount = 0
            open_interest_amount = float(open_interest_amount)

            # Calculate OI in USD by multiplying amount by current price
            if open_interest_amount > 0 and price > 0:
                open_interest_usd = open_interest_amount * price
            else:
                open_interest_usd = 0

            return MarketSnapshot(
                symbol=symbol,
                exchange="bybit",
                price=price,
                open_interest=open_interest_usd,
                volume_24h=volume_24h,
                timestamp=datetime.utcnow(),
                market_type=market_type
            )

        except Exception as e:
            print(f"Error fetching market snapshot for {symbol} ({market_type}) on Bybit: {e}")
            return None

    async def fetch_linear_snapshot(self, symbol: str) -> Optional[MarketSnapshot]:
        """
        Fetch snapshot from Bybit Linear (USDT-settled) Futures
        """
        return await self.fetch_market_snapshot(symbol, market_type="linear")

    async def fetch_inverse_snapshot(self, symbol: str) -> Optional[MarketSnapshot]:
        """
        Fetch snapshot from Bybit Inverse (coin-settled) Futures
        """
        return await self.fetch_market_snapshot(symbol, market_type="inverse")
