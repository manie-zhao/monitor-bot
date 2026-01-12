"""
Calculation utilities for market data analysis
Handles percentage changes and snapshot comparisons
"""
from typing import Optional
from datetime import datetime
from src.main.python.models.market_data import MarketSnapshot, PriceOIChange


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values

    Args:
        old_value: Previous value
        new_value: Current value

    Returns:
        Percentage change (positive or negative)

    Example:
        calculate_percentage_change(100, 103) -> 3.0
        calculate_percentage_change(100, 95) -> -5.0
    """
    if old_value == 0:
        return 0.0

    return ((new_value - old_value) / old_value) * 100


def compare_snapshots(
    previous: MarketSnapshot,
    current: MarketSnapshot
) -> Optional[PriceOIChange]:
    """
    Compare two market snapshots and calculate changes

    Args:
        previous: Previous snapshot
        current: Current snapshot

    Returns:
        PriceOIChange object with calculated changes, or None if incompatible
    """
    # Validate snapshots are for same symbol and exchange
    if previous.symbol != current.symbol or previous.exchange != current.exchange:
        return None

    # Calculate percentage changes
    price_change_pct = calculate_percentage_change(previous.price, current.price)
    oi_change_pct = calculate_percentage_change(
        previous.open_interest,
        current.open_interest
    )
    volume_change_pct = calculate_percentage_change(
        previous.volume_24h,
        current.volume_24h
    )

    return PriceOIChange(
        symbol=current.symbol,
        exchange=current.exchange,
        price_change_pct=price_change_pct,
        oi_change_pct=oi_change_pct,
        volume_change_pct=volume_change_pct,
        current_price=current.price,
        previous_price=previous.price,
        current_oi=current.open_interest,
        previous_oi=previous.open_interest,
        volume_24h=current.volume_24h,
        previous_volume=previous.volume_24h,
        timestamp=current.timestamp
    )


def format_large_number(value: float, decimals: int = 2) -> str:
    """
    Format large numbers with K, M, B suffixes

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string

    Example:
        format_large_number(1500000) -> "1.50M"
        format_large_number(2500000000) -> "2.50B"
    """
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


def is_significant_move(
    price_change_pct: float,
    oi_change_pct: float,
    price_threshold: float,
    oi_threshold: float
) -> bool:
    """
    Check if both price and OI changes meet thresholds (AND logic)

    Args:
        price_change_pct: Price change percentage
        oi_change_pct: OI change percentage
        price_threshold: Minimum price change threshold
        oi_threshold: Minimum OI change threshold

    Returns:
        True if both thresholds are met, False otherwise
    """
    return (
        abs(price_change_pct) >= price_threshold
        and abs(oi_change_pct) >= oi_threshold
    )
