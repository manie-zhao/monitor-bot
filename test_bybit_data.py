#!/usr/bin/env python3
"""Test script to inspect Bybit API response structure"""

import asyncio
import ccxt.async_support as ccxt
from src.main.resources.config.settings import get_exchange_config


async def test_bybit_data():
    """Test fetching data for a specific symbol from Bybit"""

    # Initialize Bybit exchange
    config = get_exchange_config('bybit')
    exchange = ccxt.bybit(config)

    try:
        await exchange.load_markets()

        # Test with a common symbol
        test_symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ATOM/USDT:USDT']

        for symbol in test_symbols:
            print(f"\n{'='*60}")
            print(f"Testing symbol: {symbol}")
            print(f"{'='*60}")

            try:
                # Fetch ticker
                print("\n1. Fetching ticker...")
                ticker = await exchange.fetch_ticker(symbol)
                print(f"Ticker keys: {ticker.keys()}")
                print(f"  - last: {ticker.get('last')} (type: {type(ticker.get('last'))})")
                print(f"  - quoteVolume: {ticker.get('quoteVolume')} (type: {type(ticker.get('quoteVolume'))})")
                print(f"  - baseVolume: {ticker.get('baseVolume')} (type: {type(ticker.get('baseVolume'))})")

                # Fetch open interest
                print("\n2. Fetching open interest...")
                if hasattr(exchange, 'fetch_open_interest'):
                    oi_data = await exchange.fetch_open_interest(symbol)
                    print(f"OI data keys: {oi_data.keys()}")
                    print(f"  - openInterest: {oi_data.get('openInterest')} (type: {type(oi_data.get('openInterest'))})")
                    print(f"  - openInterestValue: {oi_data.get('openInterestValue')} (type: {type(oi_data.get('openInterestValue'))})")
                    print(f"Full OI data: {oi_data}")
                else:
                    print("Exchange doesn't support fetch_open_interest")

            except Exception as e:
                print(f"❌ Error for {symbol}: {type(e).__name__}: {e}")

    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(test_bybit_data())
