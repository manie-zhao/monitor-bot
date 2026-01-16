"""
Symbol discovery service
Dynamically fetches available symbols from exchanges
"""
import asyncio
from typing import List, Set
from src.main.python.api.binance_exchange import BinanceExchange
from src.main.python.api.bybit_exchange import BybitExchange


class SymbolService:
    """
    Service for discovering and managing trading symbols across exchanges
    """

    def __init__(self, binance_config: dict, bybit_config: dict):
        """
        Initialize symbol service

        Args:
            binance_config: Binance exchange configuration
            bybit_config: Bybit exchange configuration
        """
        self.binance_config = binance_config
        self.bybit_config = bybit_config

    async def fetch_all_available_symbols(self) -> List[str]:
        """
        Fetch all active USDT perpetual futures symbols from both exchanges

        Returns:
            List of unique symbol strings (e.g., ['BTC/USDT', 'ETH/USDT', ...])
            Returns empty list if fetching fails
        """
        binance = BinanceExchange(self.binance_config)
        bybit = BybitExchange(self.bybit_config)

        try:
            # Initialize exchanges
            print("🔌 Connecting to exchanges for symbol discovery...")
            await binance.initialize()
            await bybit.initialize()
            print("✅ Connected to exchanges")

            # Fetch Binance symbols
            binance_symbols = await self._fetch_binance_symbols(binance)
            print(f"📊 Binance Futures: {len(binance_symbols)} USDT pairs")

            # Fetch Bybit symbols
            bybit_symbols = await self._fetch_bybit_symbols(bybit)
            print(f"📊 Bybit Linear Futures: {len(bybit_symbols)} USDT pairs")

            # Combine all unique symbols
            all_symbols = binance_symbols.union(bybit_symbols)
            symbols_list = sorted(list(all_symbols))

            print(f"📈 Total unique symbols: {len(symbols_list)}")

            return symbols_list

        except Exception as e:
            print(f"❌ Error fetching symbols: {e}")
            return []
        finally:
            await binance.close()
            await bybit.close()

    async def _fetch_binance_symbols(self, binance: BinanceExchange) -> Set[str]:
        """
        Fetch active USDT perpetual futures symbols from Binance

        Args:
            binance: Initialized BinanceExchange instance

        Returns:
            Set of symbol strings
        """
        try:
            markets = binance.exchange.markets
            symbols = set()

            for symbol, market in markets.items():
                # Filter for USDT perpetual futures (swap type)
                if (market.get('quote') == 'USDT' and
                    market.get('active') and
                    market.get('type') == 'swap'):
                    symbols.add(symbol)

            return symbols
        except Exception as e:
            print(f"⚠️ Error fetching Binance symbols: {e}")
            return set()

    async def _fetch_bybit_symbols(self, bybit: BybitExchange) -> Set[str]:
        """
        Fetch active USDT linear perpetual futures symbols from Bybit

        Args:
            bybit: Initialized BybitExchange instance

        Returns:
            Set of symbol strings
        """
        try:
            # Set to linear market type for USDT perpetuals
            bybit.exchange.options['defaultType'] = 'linear'
            markets = bybit.exchange.markets
            symbols = set()

            for symbol, market in markets.items():
                # Filter for USDT linear perpetual futures
                if (market.get('quote') == 'USDT' and
                    market.get('active') and
                    market.get('linear')):
                    symbols.add(symbol)

            return symbols
        except Exception as e:
            print(f"⚠️ Error fetching Bybit symbols: {e}")
            return set()
