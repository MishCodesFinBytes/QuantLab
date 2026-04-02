import yfinance as yf
import pandas as pd


def fetch_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f"No price data returned for {tickers}")

    # yfinance returns MultiIndex columns for multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        # Single ticker — no MultiIndex
        prices = data[["Close"]].rename(columns={"Close": tickers[0]})

    # Drop rows where all values are NaN, forward-fill remaining gaps
    prices = prices.dropna(how="all").ffill()

    if prices.empty:
        raise ValueError(f"No price data returned for {tickers}")

    return prices
