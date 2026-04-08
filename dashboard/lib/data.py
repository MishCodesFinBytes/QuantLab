"""Shared data fetching functions for dashboard pages."""

from __future__ import annotations

import pandas as pd
import yfinance as yf
import requests


def fetch_stock_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch OHLCV history from yfinance."""
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.index = pd.to_datetime(df.index)
    return df


def fetch_multiple_stocks(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """Fetch closing prices for multiple tickers."""
    df = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    df.index = pd.to_datetime(df.index)
    return df


def fetch_crypto_prices(coins: list[str], vs_currency: str = "usd") -> dict:
    """Fetch current crypto prices from CoinGecko (free, no key)."""
    ids = ",".join(coins)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={vs_currency}&include_24hr_change=true&include_market_cap=true"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def fetch_exchange_rates(base: str = "USD") -> dict:
    """Fetch exchange rates from a free API."""
    url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("rates", {})
    except Exception:
        return {}


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add SMA, EMA, RSI, MACD, Bollinger Bands to a price DataFrame."""
    df = df.copy()

    # Moving averages
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std

    return df


# Sample ESG data (no free API available)
SAMPLE_ESG_DATA = pd.DataFrame({
    "Company": ["Apple", "Microsoft", "Google", "Amazon", "Tesla",
                "JPMorgan", "Goldman Sachs", "ExxonMobil", "Chevron", "NextEra Energy"],
    "Ticker": ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
               "JPM", "GS", "XOM", "CVX", "NEE"],
    "Sector": ["Tech", "Tech", "Tech", "Tech", "Auto",
               "Finance", "Finance", "Energy", "Energy", "Energy"],
    "E_Score": [72, 78, 75, 55, 68, 52, 48, 35, 38, 85],
    "S_Score": [65, 80, 70, 45, 50, 60, 55, 42, 40, 70],
    "G_Score": [78, 85, 72, 60, 40, 75, 70, 65, 62, 80],
})
SAMPLE_ESG_DATA["ESG_Total"] = (
    SAMPLE_ESG_DATA["E_Score"] + SAMPLE_ESG_DATA["S_Score"] + SAMPLE_ESG_DATA["G_Score"]
) / 3
