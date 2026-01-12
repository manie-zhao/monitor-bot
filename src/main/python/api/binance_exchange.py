"""
Binance Futures exchange wrapper
Handles market data fetching from Binance Futures
"""
from typing import Optional
from datetime import datetime
from src.main.python.api.base_exchange import BaseExchange
from src.main.python.models.market_data import MarketSnapshot


class BinanceExchange(BaseExchange):
    """
    Binance Futures exchange wrapper
    """

    def __init__(self, config: dict):
        super().__init__("binance", config)

    async def fetch_market_snapshot(
        self,
        symbol: str,
        market_type: Optional[str] = None
    ) -> Optional[MarketSnapshot]:
        """
        Fetch current market snapshot from Binance Futures

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            market_type: Not used for Binance (always futures)

        Returns:
            MarketSnapshot object or None if fetch fails
        """
        try:
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

            # Open interest is returned in contract units, convert to USD
            # For USDT futures, openInterestAmount is already in USD
            open_interest_usd = float(oi_data.get('openInterestAmount', 0))

            # If openInterestAmount is not available, calculate from contracts
            if open_interest_usd == 0:
                open_interest_contracts = float(oi_data.get('openInterest', 0))
                open_interest_usd = open_interest_contracts * price

            return MarketSnapshot(
                symbol=symbol,
                exchange="binance",
                price=price,
                open_interest=open_interest_usd,
                volume_24h=volume_24h,
                timestamp=datetime.utcnow(),
                market_type="futures"
            )

        except Exception as e:
            print(f"Error fetching market snapshot for {symbol} on Binance: {e}")
            return None
