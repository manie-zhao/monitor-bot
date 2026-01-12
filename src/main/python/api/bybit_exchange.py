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
            price = float(ticker.get('last', 0))
            volume_24h = float(ticker.get('quoteVolume', 0))  # 24h volume in quote currency

            # Open interest handling for Bybit
            # openInterestValue is in USD for linear, in contracts for inverse
            open_interest_value = float(oi_data.get('openInterestValue', 0))

            # For inverse contracts, convert to USD
            if market_type == "inverse":
                open_interest_contracts = float(oi_data.get('openInterest', 0))
                if open_interest_contracts > 0 and price > 0:
                    open_interest_usd = open_interest_contracts * price
                else:
                    open_interest_usd = open_interest_value
            else:
                # For linear, it's already in USD
                open_interest_usd = open_interest_value

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
