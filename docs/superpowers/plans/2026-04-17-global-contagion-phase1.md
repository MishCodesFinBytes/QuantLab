# Global Contagion Command Center — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Streamlit dashboard at `/Global_Contagion` that replays two historical conflict periods on a 3D globe, fed by a committed parquet snapshot of market data.

**Architecture:** Offline ETL script (`scripts/fetch_contagion_data.py`) fetches yfinance + FRED CSV data and writes `dashboard/data/contagion/events.parquet`. A new `dashboard/lib/contagion/` package exposes a loader, rolling-correlation helper, and pydeck arc-layer builder. The Streamlit page composes these into a period toggle + timeline + globe + side-panel layout. A new *Geopolitics & Risk* category is added to the project registry so the sidebar and landing card render automatically.

**Tech Stack:** Python 3.11+, Streamlit, pandas, pyarrow, pydeck (`GlobeView`), yfinance, requests (for FRED CSV). All tests with pytest + `streamlit.testing.v1.AppTest`.

---

## File Structure

```
quant_lab/
├── scripts/
│   └── fetch_contagion_data.py                         (new — ETL)
└── dashboard/
    ├── data/
    │   └── contagion/
    │       ├── events.parquet                          (new — committed artifact)
    │       └── README.md                               (new — re-run instructions)
    ├── lib/
    │   ├── contagion/
    │   │   ├── __init__.py                             (new — public API)
    │   │   ├── constants.py                            (new — tickers, cities, date ranges)
    │   │   ├── loader.py                               (new — parquet IO + caching)
    │   │   ├── correlations.py                         (new — rolling corr + ME index)
    │   │   └── globe.py                                (new — pydeck layer builders)
    │   └── projects.py                                 (modify — add category + entry)
    ├── pages/
    │   └── 70_Global_Contagion.py                      (new — Streamlit page)
    └── tests/
        ├── test_contagion_constants.py                 (new)
        ├── test_contagion_correlations.py              (new)
        ├── test_contagion_loader.py                    (new)
        ├── test_contagion_globe.py                     (new)
        └── test_global_contagion.py                    (new — page smoke)
```

Each file has one responsibility. `constants.py` is pure data (no logic — trivially tested via assertion). `correlations.py` is pure math (fully unit-tested). `loader.py` does IO + cache (tested with a tmp parquet). `globe.py` builds pydeck layer configs (tested by asserting on the returned dict/object). The page file is a thin composer.

---

## Task 1: Constants module (tickers, cities, date ranges)

**Files:**
- Create: `dashboard/lib/contagion/__init__.py`
- Create: `dashboard/lib/contagion/constants.py`
- Test: `dashboard/tests/test_contagion_constants.py`

- [ ] **Step 1: Write the failing test**

Write `dashboard/tests/test_contagion_constants.py`:

```python
"""Unit tests for contagion constants module."""
from datetime import date

from lib.contagion import constants


def test_periods_cover_expected_date_ranges():
    assert constants.PERIODS["2020_us_iran"]["start"] == date(2019, 11, 1)
    assert constants.PERIODS["2020_us_iran"]["end"] == date(2020, 3, 15)
    assert constants.PERIODS["2024_hormuz"]["start"] == date(2024, 1, 1)
    # End is today-ish; just assert after 2026-01-01 so the test is stable.
    assert constants.PERIODS["2024_hormuz"]["end"] >= date(2026, 1, 1)


def test_every_ticker_has_a_role():
    valid_roles = {"epicenter", "contagion", "safe_haven", "energy", "fear"}
    for ticker, role in constants.TICKER_ROLES.items():
        assert role in valid_roles, f"{ticker} has invalid role {role}"


def test_destination_cities_include_all_five():
    expected = {"IN", "TR", "DE", "US", "GB"}
    assert set(constants.DESTINATION_CITIES.keys()) == expected


def test_epicenter_origin_is_strait_of_hormuz():
    lon, lat = constants.EPICENTER_LONLAT
    assert 55 < lon < 57, "Longitude should be ~56 (Strait of Hormuz)"
    assert 25 < lat < 27, "Latitude should be ~26 (Strait of Hormuz)"
```

- [ ] **Step 2: Run test to verify it fails**

Run from `dashboard/`:
```bash
cd dashboard && pytest tests/test_contagion_constants.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion'`.

- [ ] **Step 3: Create the package init**

Write `dashboard/lib/contagion/__init__.py`:

```python
"""Global Contagion Command Center — data + viz helpers."""
```

- [ ] **Step 4: Write the constants module**

Write `dashboard/lib/contagion/constants.py`:

```python
"""Static configuration for the Global Contagion dashboard.

Tickers, asset roles, date ranges, and geographic coordinates live here
so the ETL script, loader, and Streamlit page share one source of truth.
"""
from __future__ import annotations

from datetime import date, datetime


# ──────────────────────────────────────────────────────────────
# Conflict periods. Dates are inclusive on both ends.
# "end" for the 2024 Hormuz period is today, re-evaluated at import time
# so the parquet's cut-off is obvious in logs.
# ──────────────────────────────────────────────────────────────
PERIODS: dict = {
    "2020_us_iran": {
        "start": date(2019, 11, 1),
        "end": date(2020, 3, 15),
        "label": "2020 US-Iran escalation",
    },
    "2024_hormuz": {
        "start": date(2024, 1, 1),
        "end": datetime.today().date(),
        "label": "2024-2026 Strait of Hormuz tensions",
    },
}


# ──────────────────────────────────────────────────────────────
# Ticker → asset role map. yfinance symbols unless annotated.
# FRED CSV tickers are prefixed with `FRED:` and resolved by the ETL.
# ──────────────────────────────────────────────────────────────
TICKER_ROLES: dict = {
    # Epicenter — Middle East sovereign risk (best-effort via ETFs/proxies)
    "EIS": "epicenter",      # iShares MSCI Israel
    "KSA": "epicenter",      # iShares MSCI Saudi Arabia
    "UAE": "epicenter",      # iShares MSCI UAE
    # Contagion — energy-dependent economies (10Y yields via FRED)
    "FRED:IRLTLT01INM156N": "contagion",   # India 10Y yield, monthly (ffilled)
    "FRED:IRLTLT01TRM156N": "contagion",   # Turkey 10Y yield
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
EPICENTER_LONLAT: tuple = (56.0, 26.0)   # Strait of Hormuz

DESTINATION_CITIES: dict = {
    "IN": {"label": "Delhi",    "lonlat": (77.21, 28.61), "ticker": "FRED:IRLTLT01INM156N"},
    "TR": {"label": "Istanbul", "lonlat": (28.98, 41.01), "ticker": "FRED:IRLTLT01TRM156N"},
    "DE": {"label": "Frankfurt","lonlat": ( 8.68, 50.11), "ticker": "FRED:IRLTLT01DEM156N"},
    "US": {"label": "New York", "lonlat": (-74.01, 40.71),"ticker": "^TNX"},
    "GB": {"label": "London",   "lonlat": (-0.13, 51.51), "ticker": "^TNX"},  # proxy: use TNX for UK too
}


# ──────────────────────────────────────────────────────────────
# Rolling correlation window (trading days).
# ──────────────────────────────────────────────────────────────
CORRELATION_WINDOW = 7
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd dashboard && pytest tests/test_contagion_constants.py -v
```
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add dashboard/lib/contagion/__init__.py dashboard/lib/contagion/constants.py dashboard/tests/test_contagion_constants.py
git commit -m "feat(contagion): add package scaffold + constants module"
```

---

## Task 2: Rolling correlation + Middle East Risk Index

**Files:**
- Create: `dashboard/lib/contagion/correlations.py`
- Test: `dashboard/tests/test_contagion_correlations.py`

- [ ] **Step 1: Write the failing test**

Write `dashboard/tests/test_contagion_correlations.py`:

```python
"""Unit tests for rolling correlation and epicenter aggregation."""
import numpy as np
import pandas as pd
import pytest

from lib.contagion import correlations


def test_rolling_corr_of_identical_series_is_one():
    s = pd.Series(np.random.RandomState(0).rand(30), name="x")
    corr = correlations.rolling_corr(s, s, window=7)
    # First (window-1) are NaN; after that, identical series correlate to 1.
    assert corr.iloc[-1] == pytest.approx(1.0)


def test_rolling_corr_of_opposite_series_is_negative_one():
    s1 = pd.Series(np.arange(20, dtype=float))
    s2 = -s1
    corr = correlations.rolling_corr(s1, s2, window=7)
    assert corr.iloc[-1] == pytest.approx(-1.0)


def test_rolling_corr_output_bounded():
    rng = np.random.RandomState(1)
    s1 = pd.Series(rng.rand(50))
    s2 = pd.Series(rng.rand(50))
    corr = correlations.rolling_corr(s1, s2, window=7).dropna()
    assert corr.min() >= -1.0 - 1e-9
    assert corr.max() <= 1.0 + 1e-9


def test_middle_east_index_averages_epicenter_tickers():
    # Long-format events DF: one row per (date, ticker)
    events = pd.DataFrame({
        "date": pd.to_datetime(["2020-01-01", "2020-01-01", "2020-01-01",
                                "2020-01-02", "2020-01-02", "2020-01-02"]),
        "ticker": ["EIS", "KSA", "UAE", "EIS", "KSA", "UAE"],
        "asset_role": ["epicenter"] * 6,
        "close": [10.0, 20.0, 30.0, 11.0, 21.0, 31.0],
    })
    idx = correlations.middle_east_index(events)
    assert len(idx) == 2
    assert idx.loc[pd.Timestamp("2020-01-01")] == pytest.approx(20.0)  # mean(10,20,30)
    assert idx.loc[pd.Timestamp("2020-01-02")] == pytest.approx(21.0)  # mean(11,21,31)
```

- [ ] **Step 2: Run to verify fails**

```bash
cd dashboard && pytest tests/test_contagion_correlations.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion.correlations'`.

- [ ] **Step 3: Implement**

Write `dashboard/lib/contagion/correlations.py`:

```python
"""Rolling correlation and epicenter aggregation helpers.

Kept deliberately pure (no Streamlit imports) so tests are fast and
the logic is reusable from notebooks.
"""
from __future__ import annotations

import pandas as pd


def rolling_corr(
    s1: pd.Series, s2: pd.Series, window: int = 7
) -> pd.Series:
    """Pearson rolling correlation between two aligned series."""
    return s1.rolling(window=window).corr(s2)


def middle_east_index(events: pd.DataFrame) -> pd.Series:
    """Daily simple mean of the epicenter-tagged closing values.

    Assumes `events` is the long-format DataFrame returned by the loader
    (columns: date, ticker, asset_role, close). Returns a Series indexed
    by date.
    """
    epi = events[events["asset_role"] == "epicenter"]
    # Pivot → one column per ticker → row-mean → Series
    wide = epi.pivot_table(index="date", columns="ticker", values="close")
    return wide.mean(axis=1)
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && pytest tests/test_contagion_correlations.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/correlations.py dashboard/tests/test_contagion_correlations.py
git commit -m "feat(contagion): add rolling correlation + ME index helpers"
```

---

## Task 3: Parquet loader with Streamlit cache

**Files:**
- Create: `dashboard/lib/contagion/loader.py`
- Test: `dashboard/tests/test_contagion_loader.py`

- [ ] **Step 1: Write the failing test**

Write `dashboard/tests/test_contagion_loader.py`:

```python
"""Unit tests for contagion loader."""
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from lib.contagion import loader


def _write_fixture(path: Path) -> None:
    """Write a small synthetic events parquet for testing."""
    rows = [
        (date(2020, 1, 1), "2020_us_iran", "EIS", "epicenter", "IL", 10.0),
        (date(2020, 1, 1), "2020_us_iran", "^TNX", "safe_haven", "US", 1.8),
        (date(2024, 1, 1), "2024_hormuz", "EIS", "epicenter", "IL", 15.0),
    ]
    df = pd.DataFrame(
        rows, columns=["date", "period", "ticker", "asset_role", "country", "close"]
    )
    df.to_parquet(path, index=False)


def test_load_events_returns_all_rows_when_no_period(tmp_path):
    p = tmp_path / "events.parquet"
    _write_fixture(p)
    df = loader.load_events(path=p)
    assert len(df) == 3


def test_load_events_filters_by_period(tmp_path):
    p = tmp_path / "events.parquet"
    _write_fixture(p)
    df = loader.load_events(path=p, period="2020_us_iran")
    assert len(df) == 2
    assert set(df["period"].unique()) == {"2020_us_iran"}


def test_load_events_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        loader.load_events(path=tmp_path / "missing.parquet")
```

- [ ] **Step 2: Run to verify fails**

```bash
cd dashboard && pytest tests/test_contagion_loader.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion.loader'`.

- [ ] **Step 3: Implement**

Write `dashboard/lib/contagion/loader.py`:

```python
"""Load the committed contagion events parquet.

Kept minimal and side-effect-free; the Streamlit page wraps this in
`@st.cache_data` at the page layer to avoid importing Streamlit here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "contagion" / "events.parquet"


def load_events(
    *, path: Optional[Path] = None, period: Optional[str] = None
) -> pd.DataFrame:
    """Return the events DataFrame, optionally filtered by period.

    Columns: date, period, ticker, asset_role, country, close.
    """
    p = Path(path) if path is not None else DEFAULT_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Events parquet not found at {p}. Run "
            f"`python scripts/fetch_contagion_data.py` to generate it."
        )
    df = pd.read_parquet(p)
    if period is not None:
        df = df[df["period"] == period].reset_index(drop=True)
    return df
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && pytest tests/test_contagion_loader.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/loader.py dashboard/tests/test_contagion_loader.py
git commit -m "feat(contagion): add parquet loader with period filter"
```

---

## Task 4: pydeck globe layer builder

**Files:**
- Create: `dashboard/lib/contagion/globe.py`
- Test: `dashboard/tests/test_contagion_globe.py`

- [ ] **Step 1: Write the failing test**

Write `dashboard/tests/test_contagion_globe.py`:

```python
"""Unit tests for pydeck globe layer builder."""
import pytest

from lib.contagion import globe


def test_correlation_to_color_red_at_plus_one():
    r, g, b, a = globe.correlation_to_color(1.0)
    assert r >= 180 and g < 50 and b < 50


def test_correlation_to_color_green_at_minus_one():
    r, g, b, a = globe.correlation_to_color(-1.0)
    assert g >= 100 and r < 50 and b < 50


def test_correlation_to_color_gray_at_zero():
    r, g, b, a = globe.correlation_to_color(0.0)
    # Midpoint: should be near mid-gray (roughly equal channels)
    assert abs(r - g) < 40 and abs(g - b) < 40


def test_correlation_to_color_clips_out_of_range():
    assert globe.correlation_to_color(2.0) == globe.correlation_to_color(1.0)
    assert globe.correlation_to_color(-2.0) == globe.correlation_to_color(-1.0)


def test_build_arc_layer_returns_one_arc_per_destination():
    arcs = globe.build_arc_rows(
        correlations_by_country={"IN": 0.8, "TR": -0.3, "DE": 0.1, "US": -0.7, "GB": 0.5}
    )
    assert len(arcs) == 5
    countries = {arc["dest_country"] for arc in arcs}
    assert countries == {"IN", "TR", "DE", "US", "GB"}
    for arc in arcs:
        assert len(arc["source"]) == 2   # [lon, lat]
        assert len(arc["target"]) == 2
        assert len(arc["color"]) == 4    # RGBA
```

- [ ] **Step 2: Run to verify fails**

```bash
cd dashboard && pytest tests/test_contagion_globe.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion.globe'`.

- [ ] **Step 3: Implement**

Write `dashboard/lib/contagion/globe.py`:

```python
"""pydeck globe arc-layer builders.

Returns plain-dict arc rows so the Streamlit page can pass them straight
into `pdk.Layer("ArcLayer", data=arcs, ...)`. Keeping this dict-shaped
(not a pydeck object) makes tests trivial and avoids pulling pydeck
into the unit-test import path.
"""
from __future__ import annotations

from typing import Dict, List

from .constants import DESTINATION_CITIES, EPICENTER_LONLAT


def correlation_to_color(corr: float) -> tuple:
    """Diverging color ramp: green (-1) → gray (0) → red (+1)."""
    c = max(-1.0, min(1.0, float(corr)))
    # Anchors
    green = (20, 160, 60)
    gray = (128, 128, 128)
    red = (200, 30, 30)
    if c >= 0:
        t = c
        r = int(gray[0] + t * (red[0] - gray[0]))
        g = int(gray[1] + t * (red[1] - gray[1]))
        b = int(gray[2] + t * (red[2] - gray[2]))
    else:
        t = -c
        r = int(gray[0] + t * (green[0] - gray[0]))
        g = int(gray[1] + t * (green[1] - gray[1]))
        b = int(gray[2] + t * (green[2] - gray[2]))
    return (r, g, b, 220)


def build_arc_rows(
    correlations_by_country: Dict[str, float]
) -> List[dict]:
    """Build arc dicts for pydeck ArcLayer.

    Args:
        correlations_by_country: e.g. {"IN": 0.8, "TR": -0.3, ...}

    Returns:
        List of dicts with keys: source, target, color, dest_country,
        dest_label, correlation. Ready to be passed as the ArcLayer `data`.
    """
    rows: List[dict] = []
    for country_code, meta in DESTINATION_CITIES.items():
        corr = correlations_by_country.get(country_code, 0.0)
        rows.append({
            "source": list(EPICENTER_LONLAT),
            "target": list(meta["lonlat"]),
            "color": list(correlation_to_color(corr)),
            "dest_country": country_code,
            "dest_label": meta["label"],
            "correlation": float(corr),
        })
    return rows
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && pytest tests/test_contagion_globe.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/globe.py dashboard/tests/test_contagion_globe.py
git commit -m "feat(contagion): add arc-layer builder + correlation color ramp"
```

---

## Task 5: ETL script + data-quality test + manual run to generate parquet

This task is half-code, half-operations. The ETL hits live yfinance + FRED, so we don't unit-test the network; we test the pure helpers, write a **data-quality test** that asserts on parquet completeness, and then run the script and ensure the committed artifact passes the quality gate. CI will re-run this test on every PR to catch silent regressions (e.g. if someone re-runs the ETL on a bad-data day).

**Files:**
- Create: `scripts/fetch_contagion_data.py`
- Create: `dashboard/data/contagion/README.md`
- Create: `dashboard/tests/test_contagion_data_quality.py`
- Generate: `dashboard/data/contagion/events.parquet` (via script run)

- [ ] **Step 1: Write the ETL script**

Write `scripts/fetch_contagion_data.py`:

```python
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
        "FRED:IRLTLT01INM156N": "IN",
        "FRED:IRLTLT01TRM156N": "TR",
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
    return df["Close"].rename(ticker)


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
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {len(events)} rows to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the data directory README**

Write `dashboard/data/contagion/README.md`:

```markdown
# Contagion events parquet

`events.parquet` is a committed snapshot of market data for the Global
Contagion dashboard. Regenerate with:

```bash
python scripts/fetch_contagion_data.py
```

## Schema

| column | dtype | notes |
|---|---|---|
| date | date | trading day |
| period | string | `2020_us_iran` or `2024_hormuz` |
| ticker | string | yfinance symbol or `FRED:<series_id>` |
| asset_role | string | `epicenter` / `contagion` / `safe_haven` / `energy` / `fear` |
| country | string \| null | ISO-2 for geographic tickers, null for commodities/indices |
| close | float64 | closing price or yield |

## Sources

- yfinance: ETF + futures closing prices
- FRED public CSV endpoints (no API key): long-term government bond yields

## Notes

Israel / Saudi / UAE 10Y yield series are not cleanly available via free
yfinance or FRED, so the ETL substitutes the country ETFs (`EIS`, `KSA`,
`UAE`) as a proxy for sovereign risk. The blog post should document this
substitution.
```

- [ ] **Step 3: Write the failing data-quality test**

Write `dashboard/tests/test_contagion_data_quality.py`:

```python
"""Data-quality gate for the committed contagion parquet.

Runs against dashboard/data/contagion/events.parquet. Skips if the
parquet doesn't exist yet (fresh clone before ETL has been run), so
this doesn't break CI on a checkout that hasn't materialised the data.
Otherwise it asserts on completeness so regressions surface on PR.
"""
from pathlib import Path

import pandas as pd
import pytest

from lib.contagion import constants, loader


PARQUET_PATH = Path(__file__).resolve().parents[1] / "data" / "contagion" / "events.parquet"

# Minimum rows per ticker for the shorter 2020 period. Dailies should
# yield ~90 trading days; monthly FRED series ≥4 rows. Thresholds are
# intentionally loose so a slightly short window doesn't trip CI.
MIN_ROWS_DAILY_2020 = 30
MIN_ROWS_FRED_2020 = 3
MIN_ROWS_DAILY_2024 = 200   # 2024→today, ~500 trading days available
MIN_ROWS_FRED_2024 = 12     # monthly series

# Tickers that must be present in both periods; if these fail the
# dashboard is effectively non-functional.
CORE_TICKERS = {"^TNX", "^VIX", "BZ=F", "GC=F"}


@pytest.fixture(scope="module")
def events() -> pd.DataFrame:
    if not PARQUET_PATH.exists():
        pytest.skip(
            f"{PARQUET_PATH} not present — run "
            "`python scripts/fetch_contagion_data.py` first."
        )
    return loader.load_events()


def test_both_periods_present(events):
    got = set(events["period"].unique())
    expected = set(constants.PERIODS.keys())
    assert expected <= got, f"Missing periods: {expected - got}"


def test_all_asset_roles_present(events):
    got = set(events["asset_role"].unique())
    expected = {"epicenter", "contagion", "safe_haven", "energy", "fear"}
    assert expected <= got, f"Missing asset roles: {expected - got}"


def test_core_tickers_present_in_both_periods(events):
    for period in constants.PERIODS:
        got = set(events[events["period"] == period]["ticker"].unique())
        missing = CORE_TICKERS - got
        assert not missing, f"Period {period} missing core tickers: {missing}"


@pytest.mark.parametrize("period,min_daily,min_fred", [
    ("2020_us_iran", MIN_ROWS_DAILY_2020, MIN_ROWS_FRED_2020),
    ("2024_hormuz", MIN_ROWS_DAILY_2024, MIN_ROWS_FRED_2024),
])
def test_minimum_row_counts_per_ticker(events, period, min_daily, min_fred):
    slice_ = events[events["period"] == period]
    for ticker, role in constants.TICKER_ROLES.items():
        n = (slice_["ticker"] == ticker).sum()
        threshold = min_fred if ticker.startswith("FRED:") else min_daily
        # Epicenter ETFs (EIS/KSA/UAE) can be thin in the 2020 window;
        # don't block on those but still assert they have something.
        if role == "epicenter" and period == "2020_us_iran":
            assert n >= 1, f"{ticker} had zero rows in {period}"
            continue
        assert n >= threshold, (
            f"{ticker} ({role}) has {n} rows in {period}, "
            f"expected ≥{threshold}"
        )


def test_no_na_in_close_column(events):
    # Forward-fill happens at loader boundary if needed; raw parquet
    # should not carry NaN close values (ETL drops them).
    assert events["close"].notna().all(), "Found NaN values in close column"


def test_close_values_are_positive(events):
    # yields and prices are all positive; a negative would signal a
    # sign-flip bug somewhere.
    assert (events["close"] > 0).all(), "Found non-positive close values"
```

- [ ] **Step 4: Run data-quality test — expect skip (parquet not yet generated)**

```bash
cd dashboard && pytest tests/test_contagion_data_quality.py -v
```
Expected: all tests skipped with the "parquet not present" message. This confirms the test doesn't break CI on a fresh clone before ETL has run.

- [ ] **Step 5: Run the ETL**

```bash
cd c:/codebase/quant_lab && python scripts/fetch_contagion_data.py
```
Expected: stderr log lines like `Fetching period 2020_us_iran…` followed by per-ticker lines. Final: `Wrote N rows to …events.parquet` where N is in the thousands. Non-zero file on disk.

If any ticker prints a WARNING and returns empty, the script continues with the rest. Whether the outcome is good enough is decided by the data-quality test in Step 6, not by manual inspection.

- [ ] **Step 6: Re-run data-quality test — expect pass**

```bash
cd dashboard && pytest tests/test_contagion_data_quality.py -v
```
Expected: all tests pass. If any fails:
- **Missing role/period**: bug in the ETL — fix and re-run before committing
- **Core ticker missing**: yfinance/FRED outage; wait and re-run, or substitute ticker in `constants.py` if persistent
- **Row count below threshold**: either the ticker genuinely has limited history (document in `data/contagion/README.md` and lower that specific threshold with justification), or there's a fetching bug

Do **not** commit a parquet that fails the quality gate. The whole point of the test is to prevent that.

- [ ] **Step 7: Verify parquet stats (informational)**

```bash
python -c "import pandas as pd; df = pd.read_parquet('dashboard/data/contagion/events.parquet'); print(df.shape); print(df['period'].value_counts()); print(df['asset_role'].value_counts())"
```
Expected: shape like `(5000-30000, 6)`, both periods present, every asset role represented.

- [ ] **Step 8: Commit script + data + test**

```bash
git add scripts/fetch_contagion_data.py dashboard/data/contagion/events.parquet dashboard/data/contagion/README.md dashboard/tests/test_contagion_data_quality.py
git commit -m "feat(contagion): add ETL script, data-quality test, and initial parquet snapshot"
```

---

## Task 6: Register new Geopolitics & Risk category

**Files:**
- Modify: `dashboard/lib/projects.py`

- [ ] **Step 1: Locate the registry dict**

```bash
grep -n "PROJECTS_BY_CATEGORY" dashboard/lib/projects.py
```
Expected: a dict at module top level containing categories like `"Personal finance & property"`, `"Stocks & markets"`, `"Analytics & fintech"`.

- [ ] **Step 2: Add the new category + entry**

Add to `dashboard/lib/projects.py` — insert a new entry in `PROJECTS_BY_CATEGORY` at an appropriate position (order in the dict drives sidebar order). Pick a position after "Analytics & fintech":

```python
    "Geopolitics & risk": [
        Project(
            key="global_contagion",
            label="Global Contagion",
            description=(
                "Replay geopolitical shocks across a 3D globe — "
                "bond-yield contagion from Middle East to world markets"
            ),
            tech=["Python", "Streamlit", "pydeck", "pandas", "yfinance"],
            page_link="pages/70_Global_Contagion.py",
        ),
    ],
```

- [ ] **Step 3: Smoke-test the registry**

```bash
cd dashboard && python -c "from lib.projects import PROJECTS_BY_CATEGORY, all_projects; assert 'Geopolitics & risk' in PROJECTS_BY_CATEGORY; p = [x for x in all_projects() if x.key == 'global_contagion']; assert len(p) == 1; print('OK')"
```
Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add dashboard/lib/projects.py
git commit -m "feat(contagion): register Geopolitics & Risk category + Global Contagion project"
```

---

## Task 7: Streamlit page scaffold — title + period toggle + slider

Build the page incrementally. This task gets the skeleton rendering without the globe yet; next task wires the globe in.

**Files:**
- Create: `dashboard/pages/70_Global_Contagion.py`
- Test: `dashboard/tests/test_global_contagion.py`

- [ ] **Step 1: Write the failing test**

Write `dashboard/tests/test_global_contagion.py`:

```python
"""Frontend tests for the Global Contagion page."""
from streamlit.testing.v1 import AppTest


class TestGlobalContagionPage:
    def _run(self):
        at = AppTest.from_file("pages/70_Global_Contagion.py", default_timeout=20)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        blobs = " ".join(m.value for m in at.markdown)
        assert "Global Contagion" in blobs

    def test_has_period_radio(self):
        at = self._run()
        # The page exposes a radio with two options.
        labels = [r.label for r in at.radio]
        assert any("period" in l.lower() or "conflict" in l.lower() for l in labels), (
            f"Expected a period radio; got labels: {labels}"
        )

    def test_has_timeline_slider(self):
        at = self._run()
        assert len(at.slider) >= 1, "Expected at least one slider for the timeline"
```

- [ ] **Step 2: Run to verify fails**

```bash
cd dashboard && pytest tests/test_global_contagion.py -v
```
Expected: errors about the missing page file.

- [ ] **Step 3: Create the page scaffold**

Write `dashboard/pages/70_Global_Contagion.py`:

```python
"""Global Contagion Command Center — replays geopolitical shocks on a 3D globe.

Phase 1: data + globe + timeline. Gesture control ships in Phase 2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from contagion import constants, loader  # noqa: E402
from nav import render_sidebar  # noqa: E402
from page_header import render_page_header  # noqa: E402


st.set_page_config(
    page_title="Global Contagion — QuantLabs",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()
render_page_header(
    "Global Contagion Command Center",
    "Replay geopolitical shocks across a 3D globe",
)


@st.cache_data(ttl=60 * 60 * 24)
def _load(period: str) -> pd.DataFrame:
    return loader.load_events(period=period)


# ──────────────────────────────────────────────────────────────
# Period toggle
# ──────────────────────────────────────────────────────────────
period_labels = {k: v["label"] for k, v in constants.PERIODS.items()}
period_key = st.radio(
    "Conflict period",
    options=list(period_labels.keys()),
    format_func=lambda k: period_labels[k],
    horizontal=True,
)

events = _load(period_key)

# ──────────────────────────────────────────────────────────────
# Timeline slider
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

selected_date = st.slider(
    "Date",
    min_value=dates[0],
    max_value=dates[-1],
    value=dates[-1],
    format="YYYY-MM-DD",
)

st.caption(f"Showing snapshot at **{selected_date}**")
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && pytest tests/test_global_contagion.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): scaffold page with period toggle + timeline slider"
```

---

## Task 8: Render the pydeck globe

Wire the loader → correlations → globe.py → `pydeck_chart` pipeline.

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py`

- [ ] **Step 1: Extend the page with globe rendering**

Append to `dashboard/pages/70_Global_Contagion.py` (after the `st.caption` line from Task 7):

```python
# ──────────────────────────────────────────────────────────────
# Globe — pydeck ArcLayer on GlobeView
# ──────────────────────────────────────────────────────────────
import pydeck as pdk  # noqa: E402

from contagion import correlations, globe  # noqa: E402


def _correlations_for_date(events: pd.DataFrame, target_date) -> dict:
    """For each destination country, compute rolling-corr(ME index, country_yield)
    and return the value at `target_date`."""
    me_idx = correlations.middle_east_index(events)
    out: dict = {}
    for country, meta in constants.DESTINATION_CITIES.items():
        ticker = meta["ticker"]
        country_series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if country_series.empty:
            out[country] = 0.0
            continue
        # Align on common dates
        aligned = pd.concat([me_idx, country_series], axis=1, join="inner").dropna()
        if len(aligned) < constants.CORRELATION_WINDOW:
            out[country] = 0.0
            continue
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1],
            window=constants.CORRELATION_WINDOW,
        )
        # Pick the correlation at target_date (or most recent ≤ target_date)
        corr = corr.dropna()
        mask = corr.index <= pd.Timestamp(target_date)
        out[country] = float(corr[mask].iloc[-1]) if mask.any() else 0.0
    return out


corr_by_country = _correlations_for_date(events, selected_date)
arc_rows = globe.build_arc_rows(corr_by_country)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width=3,
    great_circle=True,
    pickable=True,
)

view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=1.5,
    pitch=0,
    bearing=0,
)

deck = pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    views=[pdk.View(type="GlobeView", controller=True)],
    map_provider=None,   # GlobeView does not use map tiles
    tooltip={"text": "{dest_label}\nCorrelation: {correlation}"},
)

st.pydeck_chart(deck, use_container_width=True)

# Correlation read-out table under the globe
st.caption("Rolling 7-day correlation vs Middle East Risk Index")
st.dataframe(
    pd.DataFrame(
        [
            {"Country": constants.DESTINATION_CITIES[c]["label"], "Correlation": round(v, 3)}
            for c, v in corr_by_country.items()
        ]
    ),
    hide_index=True,
    use_container_width=True,
)
```

- [ ] **Step 2: Run tests — verify page still loads**

```bash
cd dashboard && pytest tests/test_global_contagion.py -v
```
Expected: 4 passed. (The existing tests don't assert on the globe — they just verify the page doesn't crash.)

- [ ] **Step 3: Smoke-test in Streamlit**

```bash
cd dashboard && streamlit run app.py
```
Navigate to `/Global_Contagion`. Expected: globe renders with 5 arcs; slider changes the arc colors as you drag across dates. Kill the server with Ctrl-C when satisfied.

- [ ] **Step 4: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py
git commit -m "feat(contagion): render pydeck GlobeView with correlation arcs"
```

---

## Task 9: Play/Pause timeline

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py`

- [ ] **Step 1: Extend the test**

Append to `dashboard/tests/test_global_contagion.py`:

```python
    def test_has_play_button(self):
        at = self._run()
        labels = [b.label for b in at.button]
        assert any("play" in l.lower() or "pause" in l.lower() for l in labels), (
            f"Expected a play/pause button; got: {labels}"
        )
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && pytest tests/test_global_contagion.py::TestGlobalContagionPage::test_has_play_button -v
```
Expected: AssertionError.

- [ ] **Step 3: Add play/pause logic**

Modify the slider block in `dashboard/pages/70_Global_Contagion.py` to:

```python
# ──────────────────────────────────────────────────────────────
# Timeline slider + play button
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

# Session state for playback + current cursor.
if "contagion_date_idx" not in st.session_state:
    st.session_state.contagion_date_idx = len(dates) - 1
if "contagion_playing" not in st.session_state:
    st.session_state.contagion_playing = False

col_slider, col_btn = st.columns([6, 1])
with col_slider:
    idx = st.slider(
        "Date",
        min_value=0,
        max_value=len(dates) - 1,
        value=st.session_state.contagion_date_idx,
        format="%d",
        label_visibility="collapsed",
    )
    st.session_state.contagion_date_idx = idx
with col_btn:
    btn_label = "⏸ Pause" if st.session_state.contagion_playing else "▶ Play"
    if st.button(btn_label, use_container_width=True):
        st.session_state.contagion_playing = not st.session_state.contagion_playing
        st.rerun()

selected_date = dates[st.session_state.contagion_date_idx]
st.caption(f"Showing snapshot at **{selected_date}**")

# Auto-advance while playing
if st.session_state.contagion_playing:
    import time as _time
    _time.sleep(0.15)
    if st.session_state.contagion_date_idx < len(dates) - 1:
        st.session_state.contagion_date_idx += 1
    else:
        st.session_state.contagion_playing = False   # stop at the end
    st.rerun()
```

- [ ] **Step 4: Run tests — expect all pass**

```bash
cd dashboard && pytest tests/test_global_contagion.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Smoke-test**

```bash
cd dashboard && streamlit run app.py
```
Navigate to `/Global_Contagion`, click ▶ Play. Expected: slider auto-advances one step every ~150ms; arcs change color as correlations update; button becomes ⏸ Pause; reaching the last date auto-stops.

- [ ] **Step 6: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): add play/pause timeline playback"
```

---

## Task 10: Side panel — sparklines + VIX

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py`

- [ ] **Step 1: Extend the test**

Append to `dashboard/tests/test_global_contagion.py`:

```python
    def test_side_panel_renders_four_metrics(self):
        at = self._run()
        # Each sparkline metric shows the ticker label as a subheader;
        # we just check that the page produced ≥4 line charts.
        assert len(at.line_chart) >= 4, (
            f"Expected ≥4 sparklines; got {len(at.line_chart)}"
        )
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && pytest tests/test_global_contagion.py::TestGlobalContagionPage::test_side_panel_renders_four_metrics -v
```
Expected: AssertionError.

- [ ] **Step 3: Add side panel rendering**

Append to `dashboard/pages/70_Global_Contagion.py`:

```python
# ──────────────────────────────────────────────────────────────
# Side panel: Brent / Baltic / Gold / VIX sparklines
# ──────────────────────────────────────────────────────────────
st.markdown("### Energy, Safe Haven & Fear")

panel_tickers = [
    ("BZ=F", "Brent Crude"),
    ("BDRY", "Baltic Dry (ETF)"),
    ("GC=F", "Gold"),
    ("^VIX", "VIX"),
]
cols = st.columns(4)
for (ticker, label), col in zip(panel_tickers, cols):
    with col:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        st.markdown(f"**{label}**")
        if series.empty:
            st.caption("no data")
            continue
        # Truncate to dates ≤ selected_date so the sparkline "plays along"
        series = series[series.index <= selected_date]
        st.line_chart(series, height=80)
        st.caption(f"Latest: {series.iloc[-1]:.2f}")
```

- [ ] **Step 4: Run tests — expect all pass**

```bash
cd dashboard && pytest tests/test_global_contagion.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Smoke-test**

```bash
cd dashboard && streamlit run app.py
```
Navigate to `/Global_Contagion`. Expected: below the globe and correlation table, four sparkline columns render with Brent / Baltic / Gold / VIX labels.

- [ ] **Step 6: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): add side panel with energy/safe-haven/VIX sparklines"
```

---

## Task 11: Full regression sweep + PR

- [ ] **Step 1: Run the full dashboard test suite**

```bash
cd dashboard && pytest tests/ -v
```
Expected: all existing tests still pass plus the 6 new contagion tests.

- [ ] **Step 2: Sanity-check the landing page**

```bash
cd dashboard && streamlit run app.py
```
Verify:
- The QuantLabs sidebar shows a new "Geopolitics & risk" section containing "Global Contagion"
- The landing page's category grids include a new "Geopolitics & risk" grid with the Global Contagion card
- Clicking the card navigates to `/Global_Contagion`

- [ ] **Step 3: Push to working**

```bash
git push origin working
```

- [ ] **Step 4: Open PR**

```bash
gh pr create --title "feat(contagion): Global Contagion Command Center (Phase 1)" --body "$(cat <<'EOF'
## Summary

Phase 1 of the Global Contagion Command Center. See spec: \`docs/superpowers/specs/2026-04-17-global-contagion-phase1-design.md\`.

### What's in
- Offline ETL (\`scripts/fetch_contagion_data.py\`) fetching yfinance + FRED CSV data for two conflict periods
- Committed parquet snapshot at \`dashboard/data/contagion/events.parquet\`
- New \`lib/contagion/\` package: loader, correlations, pydeck globe-layer builder
- Streamlit page at \`/Global_Contagion\` with period toggle, timeline slider + play/pause, pydeck GlobeView with 5 arcs, correlation read-out table, and Brent/Baltic/Gold/VIX side panel
- New "Geopolitics & risk" sidebar category

### What's out (Phase 2+)
- Hand gesture control (mediapipe, streamlit-webrtc) — Phase 2
- Drill-in, speed selector, key-event presets, VIX-driven glow — Phase 3
- Blog post on FinBytes — to follow once the page has screenshots

## Test plan
- [ ] Full \`pytest dashboard/tests/\` passes
- [ ] Landing page shows the new "Geopolitics & risk" grid + sidebar section
- [ ] \`/Global_Contagion\` loads; both periods produce data; play button auto-advances
- [ ] Globe arcs change color when correlations change
- [ ] Side panel sparklines truncate at the selected date

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review checklist (author notes)

**Spec coverage:**
- ETL script + parquet artifact → Task 5 ✓
- Raw-prices-only parquet schema → Task 5 (README.md) + Task 1 (constants) ✓
- Two periods with UI toggle → Task 1 + Task 7 ✓
- pydeck GlobeView, 5 arcs, aggregated ME origin → Task 4 + Task 8 ✓
- Diverging red/gray/green color ramp → Task 4 ✓
- Play/pause timeline at ~150ms/day → Task 9 ✓
- Side panel for Brent/Baltic/Gold/VIX → Task 10 ✓
- New "Geopolitics & Risk" category → Task 6 ✓
- Page at `/Global_Contagion` (`70_Global_Contagion.py`) → Task 7 ✓
- Tests for rolling corr in bounds → Task 2 ✓
- Tests for period toggle switching data — covered implicitly by `test_loads_without_error` + `test_has_period_radio`; explicit data-row-count test skipped (trivial verification on a committed parquet)
- **Data-quality gate on the committed parquet → Task 5 Step 3** ✓ (skips gracefully on fresh clone; asserts completeness on real runs so CI flags silent regressions)

**Placeholder scan:** none found.

**Type consistency:**
- `correlation_to_color` returns 4-tuple (RGBA); `build_arc_rows` wraps it in `list(...)` for pydeck JSON serialisation
- `correlations.middle_east_index` returns `pd.Series` indexed by date; `_correlations_for_date` in the page uses `.set_index("date")` to align — consistent
- `loader.load_events` accepts kwargs `path` and `period`; page uses `period=` kwarg — consistent

**Blog post:** spec flagged this as post-ship. Not a plan task; ships after Phase 1 is on master and we have screenshots to embed.
