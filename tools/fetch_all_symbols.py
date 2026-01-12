#!/usr/bin/env python3
"""
Fetch all available futures symbols from Binance and Bybit
Generates a comprehensive watchlist for monitor-bot
"""
import sys
import asyncio
sys.path.insert(0, '.')

from src.main.python.api.binance_exchange import BinanceExchange
from src.main.python.api.bybit_exchange import BybitExchange
from src.main.resources.config import settings


async def fetch_all_symbols():
    """Fetch all available USDT futures symbols from both exchanges"""

    print("\n" + "="*80)
    print("🔍 FETCHING ALL AVAILABLE FUTURES SYMBOLS")
    print("="*80)

    # Initialize exchanges
    binance_config = settings.get_exchange_config("binance")
    bybit_config = settings.get_exchange_config("bybit")

    binance = BinanceExchange(binance_config)
    bybit = BybitExchange(bybit_config)

    try:
        # Initialize exchanges
        print("\n1️⃣ Connecting to Binance Futures...")
        await binance.initialize()
        print("   ✅ Connected to Binance")

        print("\n2️⃣ Connecting to Bybit Futures...")
        await bybit.initialize()
        print("   ✅ Connected to Bybit")

        # Get all markets
        print("\n3️⃣ Fetching available symbols...")

        # Binance futures symbols
        binance_markets = binance.exchange.markets
        binance_symbols = set()
        for symbol, market in binance_markets.items():
            if market.get('quote') == 'USDT' and market.get('active') and market.get('type') == 'swap':
                binance_symbols.add(symbol)

        print(f"   📊 Binance Futures: {len(binance_symbols)} USDT pairs")

        # Bybit linear (USDT) futures symbols
        bybit.exchange.options['defaultType'] = 'linear'
        bybit_markets = bybit.exchange.markets
        bybit_symbols = set()
        for symbol, market in bybit_markets.items():
            if market.get('quote') == 'USDT' and market.get('active') and market.get('linear'):
                bybit_symbols.add(symbol)

        print(f"   📊 Bybit Linear Futures: {len(bybit_symbols)} USDT pairs")

        # Find common symbols (available on both exchanges)
        common_symbols = binance_symbols.intersection(bybit_symbols)
        print(f"   🎯 Common symbols (both exchanges): {len(common_symbols)}")

        # Symbols only on Binance
        binance_only = binance_symbols - bybit_symbols
        print(f"   🔸 Binance only: {len(binance_only)}")

        # Symbols only on Bybit
        bybit_only = bybit_symbols - binance_symbols
        print(f"   🔸 Bybit only: {len(bybit_only)}")

        # All unique symbols
        all_symbols = binance_symbols.union(bybit_symbols)
        print(f"   📈 Total unique symbols: {len(all_symbols)}")

        # Sort symbols
        common_sorted = sorted(list(common_symbols))
        all_sorted = sorted(list(all_symbols))

        # Display results
        print("\n" + "="*80)
        print("📋 SYMBOL LISTS")
        print("="*80)

        print("\n🎯 RECOMMENDED: Common symbols (available on both exchanges)")
        print("─" * 80)
        print(f"Total: {len(common_sorted)} symbols")
        print("\nTop 50 by market cap (estimated):")
        # Show first 50
        for i, symbol in enumerate(common_sorted[:50], 1):
            print(f"  {i:2d}. {symbol}")

        if len(common_sorted) > 50:
            print(f"\n  ... and {len(common_sorted) - 50} more")

        print("\n" + "─" * 80)
        print("💡 For .env file (Common symbols only):")
        print("─" * 80)
        symbols_string = ','.join(common_sorted)
        print(f"SYMBOLS={symbols_string}")

        print("\n" + "─" * 80)
        print("💡 For .env file (All symbols - includes exchange-specific):")
        print("─" * 80)
        all_symbols_string = ','.join(all_sorted)
        print(f"SYMBOLS={all_symbols_string}")

        # Performance considerations
        print("\n" + "="*80)
        print("⚠️  PERFORMANCE CONSIDERATIONS")
        print("="*80)
        print(f"\nWith {len(all_sorted)} symbols:")
        print(f"  • Estimated scan time: {len(all_sorted) * 0.5:.1f}-{len(all_sorted) * 1:.1f} seconds per exchange")
        print(f"  • Total per scan: {len(all_sorted) * 1:.1f}-{len(all_sorted) * 2:.1f} seconds")
        print(f"  • Recommended minimum scan interval: {max(300, len(all_sorted) * 2):.0f} seconds")

        if len(all_sorted) > 100:
            print("\n💡 RECOMMENDATIONS:")
            print("  1. Consider filtering by 24h volume or market cap")
            print("  2. Start with common symbols only for better stability")
            print("  3. Monitor fewer symbols initially, then expand")
            print("  4. Increase SCAN_INTERVAL to avoid rate limiting")

        # Save to files
        print("\n" + "="*80)
        print("💾 SAVING SYMBOL LISTS")
        print("="*80)

        # Save common symbols
        with open('output/symbols_common.txt', 'w') as f:
            f.write(','.join(common_sorted))
        print("  ✅ Saved: output/symbols_common.txt")

        # Save all symbols
        with open('output/symbols_all.txt', 'w') as f:
            f.write(','.join(all_sorted))
        print("  ✅ Saved: output/symbols_all.txt")

        # Save detailed list
        with open('output/symbols_detailed.txt', 'w') as f:
            f.write("BINANCE AND BYBIT FUTURES SYMBOLS\n")
            f.write("="*80 + "\n\n")

            f.write(f"Common Symbols ({len(common_sorted)}):\n")
            f.write("-" * 80 + "\n")
            for symbol in common_sorted:
                f.write(f"{symbol}\n")

            f.write(f"\nBinance Only ({len(binance_only)}):\n")
            f.write("-" * 80 + "\n")
            for symbol in sorted(binance_only):
                f.write(f"{symbol}\n")

            f.write(f"\nBybit Only ({len(bybit_only)}):\n")
            f.write("-" * 80 + "\n")
            for symbol in sorted(bybit_only):
                f.write(f"{symbol}\n")

        print("  ✅ Saved: output/symbols_detailed.txt")

        print("\n" + "="*80)
        print("✅ SYMBOL FETCH COMPLETE")
        print("="*80)
        print("\n📝 Next steps:")
        print("  1. Review the symbol lists in output/ directory")
        print("  2. Copy desired SYMBOLS line to your .env file")
        print("  3. Restart the bot: pkill -f main.py && PYTHONPATH=. python3 src/main/python/main.py")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await binance.close()
        await bybit.close()


if __name__ == "__main__":
    asyncio.run(fetch_all_symbols())
