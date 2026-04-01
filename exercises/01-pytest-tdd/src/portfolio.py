import numpy as np


def daily_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate daily percentage returns from a price series.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        1D array of daily returns (length = len(prices) - 1).

    Raises:
        ValueError: If any price is zero (can't compute return from zero).
    """
    if np.any(prices == 0):
        raise ValueError("Price series contains zero — cannot compute returns from zero price")
    if len(prices) <= 1:
        return np.array([])
    return np.diff(prices) / prices[:-1]


def cumulative_return(prices: np.ndarray) -> float:
    """Total return from first price to last price.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        Cumulative return as a decimal (e.g. 0.10 for 10%).
    """
    if len(prices) == 0:
        raise ValueError("Price series is empty")
    return float((prices[-1] - prices[0]) / prices[0])


def max_drawdown(prices: np.ndarray) -> float:
    """Maximum peak-to-trough decline as a negative decimal.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        Max drawdown as negative decimal (e.g. -0.25 for 25% drop). 0.0 if no drawdown.
    """
    running_max = np.maximum.accumulate(prices)
    drawdowns = (prices - running_max) / running_max
    return float(drawdowns.min())
