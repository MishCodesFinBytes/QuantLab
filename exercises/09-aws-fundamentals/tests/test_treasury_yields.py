import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from treasury_yields import (
    TREASURY_SERIES,
    fetch_par_yields,
    format_yield_table,
    classify_curve_shape,
)


class TestTreasurySeries:
    def test_series_contains_expected_maturities(self):
        assert "DGS1MO" in TREASURY_SERIES
        assert "DGS10" in TREASURY_SERIES
        assert "DGS30" in TREASURY_SERIES
        assert len(TREASURY_SERIES) >= 11

    def test_series_values_are_maturity_labels(self):
        assert TREASURY_SERIES["DGS1MO"] == "1M"
        assert TREASURY_SERIES["DGS2"] == "2Y"
        assert TREASURY_SERIES["DGS30"] == "30Y"


class TestFetchParYields:
    @patch("treasury_yields.Fred")
    def test_returns_dict_of_maturities_and_rates(self, mock_fred_class):
        mock_fred = MagicMock()
        mock_fred_class.return_value = mock_fred

        import pandas as pd

        def mock_get_series(series_id, observation_start, observation_end):
            rates = {
                "DGS1MO": 5.25, "DGS3MO": 5.30, "DGS6MO": 5.20,
                "DGS1": 4.80, "DGS2": 4.50, "DGS3": 4.30,
                "DGS5": 4.20, "DGS7": 4.25, "DGS10": 4.30,
                "DGS20": 4.50, "DGS30": 4.45,
            }
            return pd.Series([rates[series_id]])

        mock_fred.get_series.side_effect = mock_get_series

        result = fetch_par_yields(api_key="fake-key")

        assert isinstance(result, dict)
        assert "1M" in result
        assert "10Y" in result
        assert "30Y" in result
        assert result["1M"] == 5.25
        assert result["10Y"] == 4.30

    @patch("treasury_yields.Fred")
    def test_handles_missing_maturity(self, mock_fred_class):
        mock_fred = MagicMock()
        mock_fred_class.return_value = mock_fred

        import pandas as pd

        def mock_get_series(series_id, observation_start, observation_end):
            if series_id == "DGS20":
                return pd.Series(dtype=float)  # empty — no data
            return pd.Series([4.0])

        mock_fred.get_series.side_effect = mock_get_series

        result = fetch_par_yields(api_key="fake-key")
        assert "20Y" not in result
        assert "10Y" in result


class TestFormatYieldTable:
    def test_formats_as_readable_table(self):
        yields = {"1M": 5.25, "3M": 5.30, "6M": 5.20, "1Y": 4.80, "2Y": 4.50}
        table = format_yield_table(yields)
        assert "1M" in table
        assert "5.25" in table
        assert "2Y" in table

    def test_empty_yields_returns_message(self):
        table = format_yield_table({})
        assert "No yield data" in table


class TestClassifyCurveShape:
    def test_normal_curve(self):
        # Short rates < long rates
        yields = {"1M": 3.0, "2Y": 3.5, "10Y": 4.5, "30Y": 5.0}
        assert classify_curve_shape(yields) == "normal"

    def test_inverted_curve(self):
        # Short rates > long rates
        yields = {"1M": 5.5, "2Y": 5.0, "10Y": 4.0, "30Y": 3.5}
        assert classify_curve_shape(yields) == "inverted"

    def test_flat_curve(self):
        # Short and long rates within 0.2% of each other
        yields = {"1M": 4.0, "2Y": 4.05, "10Y": 4.10, "30Y": 4.05}
        assert classify_curve_shape(yields) == "flat"

    def test_humped_curve(self):
        # Mid-term rates higher than both short and long
        yields = {"1M": 4.0, "2Y": 5.0, "10Y": 4.5, "30Y": 4.2}
        assert classify_curve_shape(yields) == "humped"
