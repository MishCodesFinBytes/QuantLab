"""Static configuration for the Global Contagion dashboard.

Tickers, asset roles, date ranges, and geographic coordinates live here
so the ETL script, loader, and Streamlit page share one source of truth.
"""
from __future__ import annotations

from datetime import date


# ──────────────────────────────────────────────────────────────
# Conflict periods. Dates are inclusive on both ends.
# "end" for the 2024 Hormuz period is today, re-evaluated at import time
# so the parquet's cut-off is obvious in logs.
# ──────────────────────────────────────────────────────────────
PERIODS: dict[str, dict[str, object]] = {
    "2020_us_iran": {
        "start": date(2019, 11, 1),
        "end": date(2020, 3, 15),
        "label": "2020 US-Iran escalation",
    },
    "2024_hormuz": {
        "start": date(2024, 1, 1),
        "end": date.today(),
        "label": "2024-2026 Strait of Hormuz tensions",
    },
}


# ──────────────────────────────────────────────────────────────
# Ticker → asset role map. yfinance symbols unless annotated.
# FRED CSV tickers are prefixed with `FRED:` and resolved by the ETL.
# ──────────────────────────────────────────────────────────────
TICKER_ROLES: dict[str, str] = {
    # Epicenter — Middle East sovereign risk (best-effort via ETFs/proxies)
    "EIS": "epicenter",      # iShares MSCI Israel
    "KSA": "epicenter",      # iShares MSCI Saudi Arabia
    "UAE": "epicenter",      # iShares MSCI UAE
    # Contagion — energy-dependent economies
    # India: INDIRLTLT01STM (replaces discontinued IRLTLT01INM156N)
    "FRED:INDIRLTLT01STM": "contagion",    # India 10Y yield, monthly (ffilled)
    # Turkey: IRLTLT01TRM156N is discontinued on FRED; use iShares MSCI Turkey ETF as proxy
    "TUR": "contagion",                    # iShares MSCI Turkey ETF (sovereign risk proxy)
    "FRED:IRLTLT01DEM156N": "contagion",   # Germany 10Y yield
    # Safe haven
    "^TNX": "safe_haven",    # CBOE 10Y Treasury Yield Index
    "GC=F": "safe_haven",    # Gold front-month future
    # Energy link
    "BZ=F": "energy",        # Brent front-month future
    "BDRY": "energy",        # Baltic Dry ETF proxy
    # Fear gauge
    "^VIX": "fear",
}


# ──────────────────────────────────────────────────────────────
# Globe geography: origin + 5 arc destinations.
# (longitude, latitude) pairs for pydeck.
# ──────────────────────────────────────────────────────────────
EPICENTER_LONLAT: tuple[float, float] = (56.0, 26.0)   # Strait of Hormuz

DESTINATION_CITIES: dict[str, dict[str, object]] = {
    "IN": {"label": "Delhi",    "lonlat": (77.21, 28.61), "ticker": "FRED:INDIRLTLT01STM"},
    "TR": {"label": "Istanbul", "lonlat": (28.98, 41.01), "ticker": "TUR"},
    "DE": {"label": "Frankfurt","lonlat": ( 8.68, 50.11), "ticker": "FRED:IRLTLT01DEM156N"},
    "US": {"label": "New York", "lonlat": (-74.01, 40.71),"ticker": "^TNX"},
    "GB": {"label": "London",   "lonlat": (-0.13, 51.51), "ticker": "^TNX"},  # proxy: use TNX for UK too
}


# ──────────────────────────────────────────────────────────────
# Rolling correlation window (trading days).
# ──────────────────────────────────────────────────────────────
CORRELATION_WINDOW: int = 7
