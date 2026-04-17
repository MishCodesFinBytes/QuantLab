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
    assert events["close"].notna().all(), "Found NaN values in close column"


def test_close_values_are_positive(events):
    # Bond yields (FRED series) can legitimately be negative (e.g. German Bund 2019-2020).
    # Only assert positivity for price-type assets (ETFs, futures, indices).
    non_fred = events[~events["ticker"].str.startswith("FRED:")]
    assert (non_fred["close"] > 0).all(), "Found non-positive close values in price assets"
