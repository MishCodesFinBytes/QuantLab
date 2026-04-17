"""Offline ETL: fetch prices for the Global Contagion dashboard.

Run manually whenever you want to refresh the committed snapshot:

    python scripts/fetch_contagion_data.py

Writes to `dashboard/data/contagion/events.parquet`.
"""
from __future__ import annotations

import io
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

# Make `lib.contagion` importable when this script is run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard" / "lib"))

from contagion.constants import PERIODS, TICKER_ROLES  # noqa: E402

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "dashboard"
    / "data"
    / "contagion"
    / "events.parquet"
)

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def _country_for_ticker(ticker: str) -> str | None:
    """Shallow mapping; None for non-geographic (commodities/indices)."""
    mapping = {
        "EIS": "IL", "KSA": "SA", "UAE": "AE",
        "TUR": "TR",
        "FRED:INDIRLTLT01STM": "IN",
        "FRED:IRLTLT01DEM156N": "DE",
        "^TNX": "US",
    }
    return mapping.get(ticker)


def _fetch_yfinance(ticker: str, start: date, end: date) -> pd.Series:
    df = yf.download(
        ticker, start=start.isoformat(), end=end.isoformat(),
        progress=False, auto_adjust=False,
    )
    if df.empty:
        print(f"  WARNING: yfinance returned empty for {ticker}", file=sys.stderr)
        return pd.Series(dtype=float)
    close = df["Close"]
    # yfinance ≥1.0 returns MultiIndex columns (Price, Ticker) for single tickers too;
    # squeeze to a plain Series.
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    return close.rename(ticker)


def _fetch_fred(series_id: str, start: date, end: date, retries: int = 3) -> pd.Series:
    url = FRED_CSV_URL.format(series_id=series_id)
    for attempt in range(retries):
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            break
        print(f"  FRED {series_id} returned {r.status_code}, retrying…", file=sys.stderr)
        time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"FRED fetch failed after {retries} attempts: {series_id}")
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"observation_date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    value_col = [c for c in df.columns if c != "date"][0]
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
    return df.loc[mask].set_index("date")[value_col].rename(f"FRED:{series_id}")


def _fetch_ticker(ticker: str, start: date, end: date) -> pd.Series:
    if ticker.startswith("FRED:"):
        return _fetch_fred(ticker.split(":", 1)[1], start, end)
    return _fetch_yfinance(ticker, start, end)


def _build_long_frame(period_key: str, start: date, end: date) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for ticker, role in TICKER_ROLES.items():
        print(f"  {ticker} ({role})…", file=sys.stderr)
        s = _fetch_ticker(ticker, start, end)
        if s.empty:
            continue
        df = s.to_frame(name="close").reset_index()
        df.columns = ["date", "close"]
        df["period"] = period_key
        df["ticker"] = ticker
        df["asset_role"] = role
        df["country"] = _country_for_ticker(ticker)
        rows.append(df[["date", "period", "ticker", "asset_role", "country", "close"]])
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main() -> None:
    frames: list[pd.DataFrame] = []
    for period_key, meta in PERIODS.items():
        print(f"Fetching period {period_key} ({meta['start']} → {meta['end']})…", file=sys.stderr)
        frames.append(_build_long_frame(period_key, meta["start"], meta["end"]))
    events = pd.concat(frames, ignore_index=True)
    events["date"] = pd.to_datetime(events["date"]).dt.date
    events = events.dropna(subset=["close"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {len(events)} rows to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
