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
