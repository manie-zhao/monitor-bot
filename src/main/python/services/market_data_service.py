"""
Market data service
Manages snapshot collection, storage, and comparison across exchanges
"""
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.main.python.models.market_data import MarketSnapshot, PriceOIChange
from src.main.python.api.binance_exchange import BinanceExchange
from src.main.python.api.bybit_exchange import BybitExchange
from src.main.python.utils.calculators import compare_snapshots


class MarketDataService:
    """
    Service for collecting and managing market data snapshots
    """

    def __init__(self, binance_config: dict, bybit_config: dict, symbols: List[str]):
        """
        Initialize market data service

        Args:
            binance_config: Binance exchange configuration
            bybit_config: Bybit exchange configuration
            symbols: List of symbols to monitor
        """
        self.symbols = symbols
        self.binance = BinanceExchange(binance_config)
        self.bybit = BybitExchange(bybit_config)

        # In-memory storage for previous snapshots
        # Key format: "{exchange}:{symbol}:{market_type}"
        self.snapshots: Dict[str, MarketSnapshot] = {}

    async def initialize(self):
        """Initialize exchange connections"""
        print("🔌 Initializing exchange connections...")
        await self.binance.initialize()
        await self.bybit.initialize()
        print("✅ Exchange connections initialized")

    async def close(self):
        """Close exchange connections"""
        print("🔌 Closing exchange connections...")
        await self.binance.close()
        await self.bybit.close()
        print("✅ Exchange connections closed")

    def _get_snapshot_key(
        self,
        exchange: str,
        symbol: str,
        market_type: Optional[str] = None
    ) -> str:
        """
        Generate unique key for snapshot storage

        Args:
            exchange: Exchange name
            symbol: Trading pair symbol
            market_type: Market type (optional)

        Returns:
            Unique key string
        """
        if market_type:
            return f"{exchange}:{symbol}:{market_type}"
        return f"{exchange}:{symbol}"

    def _store_snapshot(self, snapshot: MarketSnapshot):
        """
        Store snapshot in memory

        Args:
            snapshot: Market snapshot to store
        """
        key = self._get_snapshot_key(
            snapshot.exchange,
            snapshot.symbol,
            snapshot.market_type
        )
        self.snapshots[key] = snapshot

    def _get_previous_snapshot(
        self,
        exchange: str,
        symbol: str,
        market_type: Optional[str] = None
    ) -> Optional[MarketSnapshot]:
        """
        Retrieve previous snapshot from memory

        Args:
            exchange: Exchange name
            symbol: Trading pair symbol
            market_type: Market type (optional)

        Returns:
            Previous snapshot or None if not found
        """
        key = self._get_snapshot_key(exchange, symbol, market_type)
        return self.snapshots.get(key)

    async def fetch_all_snapshots(self) -> List[MarketSnapshot]:
        """
        Fetch current snapshots from all exchanges and symbols

        Returns:
            List of market snapshots
        """
        try:
            tasks = []

            # Fetch from Binance
            for symbol in self.symbols:
                tasks.append(self.binance.fetch_market_snapshot(symbol))

            # Fetch from Bybit (both linear and inverse)
            for symbol in self.symbols:
                tasks.append(self.bybit.fetch_linear_snapshot(symbol))
                # For inverse, we need to convert symbol format (e.g., BTC/USDT -> BTC/USD)
                if symbol.endswith('/USDT'):
                    inverse_symbol = symbol.replace('/USDT', '/USD')
                    tasks.append(self.bybit.fetch_inverse_snapshot(inverse_symbol))

            # Execute all fetches concurrently with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=300.0  # 5 minute timeout for all fetches
            )

            # Filter out None values and exceptions
            snapshots = [
                r for r in results
                if isinstance(r, MarketSnapshot) and r is not None
            ]

            print(f"📊 Fetched {len(snapshots)} market snapshots")
            return snapshots

        except asyncio.TimeoutError:
            print(f"⚠️ Timeout fetching snapshots - returning empty list")
            return []
        except Exception as e:
            print(f"⚠️ Error fetching snapshots: {e}")
            return []

    async def get_changes(self) -> List[PriceOIChange]:
        """
        Fetch current snapshots and compare with previous ones

        Returns:
            List of PriceOIChange objects for all tracked pairs
        """
        current_snapshots = await self.fetch_all_snapshots()
        changes = []

        for current in current_snapshots:
            # Get previous snapshot
            previous = self._get_previous_snapshot(
                current.exchange,
                current.symbol,
                current.market_type
            )

            if previous:
                # Compare snapshots
                change = compare_snapshots(previous, current)
                if change:
                    changes.append(change)

            # Store current snapshot for next comparison
            self._store_snapshot(current)

        return changes

    async def get_initial_snapshots(self):
        """
        Fetch and store initial snapshots without comparing
        This should be called on first run to populate the snapshot storage
        """
        print("📸 Collecting initial market snapshots...")
        snapshots = await self.fetch_all_snapshots()

        for snapshot in snapshots:
            self._store_snapshot(snapshot)

        print(f"✅ Stored {len(snapshots)} initial snapshots")

    def get_snapshot_count(self) -> int:
        """
        Get the number of stored snapshots

        Returns:
            Number of snapshots in memory
        """
        return len(self.snapshots)
