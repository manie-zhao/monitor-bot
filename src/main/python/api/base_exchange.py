"""
Base exchange wrapper for market data fetching
Provides common interface for all exchanges using ccxt
"""
import asyncio
import ccxt.async_support as ccxt
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from src.main.python.models.market_data import MarketSnapshot


class BaseExchange(ABC):
    """
    Abstract base class for exchange wrappers
    """

    def __init__(self, exchange_id: str, config: dict):
        """
        Initialize exchange connection

        Args:
            exchange_id: Exchange identifier (e.g., 'binance', 'bybit')
            config: Exchange configuration dictionary
        """
        self.exchange_id = exchange_id
        self.config = config
        self.exchange: Optional[ccxt.Exchange] = None

    async def initialize(self):
        """Initialize the exchange connection"""
        exchange_class = getattr(ccxt, self.exchange_id)
        self.exchange = exchange_class(self.config)
        await self.exchange.load_markets()

    async def close(self):
        """Close the exchange connection"""
        if self.exchange:
            await self.exchange.close()

    @abstractmethod
    async def fetch_market_snapshot(
        self,
        symbol: str,
        market_type: Optional[str] = None
    ) -> Optional[MarketSnapshot]:
        """
        Fetch current market snapshot for a symbol

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            market_type: Market type (for exchanges with multiple markets)

        Returns:
            MarketSnapshot object or None if fetch fails
        """
        pass

    async def fetch_ticker(self, symbol: str) -> Optional[dict]:
        """
        Fetch ticker data for a symbol

        Args:
            symbol: Trading pair symbol

        Returns:
            Ticker dictionary or None if fetch fails
        """
        try:
            return await asyncio.wait_for(
                self.exchange.fetch_ticker(symbol),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print(f"Timeout fetching ticker for {symbol} on {self.exchange_id}")
            return None
        except Exception as e:
            print(f"Error fetching ticker for {symbol} on {self.exchange_id}: {e}")
            return None

    async def fetch_open_interest(self, symbol: str) -> Optional[dict]:
        """
        Fetch open interest data for a symbol

        Args:
            symbol: Trading pair symbol

        Returns:
            Open interest dictionary or None if fetch fails
        """
        try:
            # Use exchange's open interest method if available
            if hasattr(self.exchange, 'fetch_open_interest'):
                return await asyncio.wait_for(
                    self.exchange.fetch_open_interest(symbol),
                    timeout=10.0
                )
            return None
        except asyncio.TimeoutError:
            print(f"Timeout fetching OI for {symbol} on {self.exchange_id}")
            return None
        except Exception as e:
            print(f"Error fetching OI for {symbol} on {self.exchange_id}: {e}")
            return None
