"""Tests for London House Prices page."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest


class TestLondonHousePricesPage:
    def _run(self):
        at = AppTest.from_file("pages/42_London_House_Prices.py", default_timeout=30)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "London House Prices" in markdown_blobs


@pytest.fixture
def sample_ppd():
    """Small London PPD DataFrame for testing."""
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=100, freq="W")
    districts = np.random.choice(["SW11", "E14", "N1", "SE1", "W1"], 100)
    prices = np.random.randint(200000, 800000, 100)
    types = np.random.choice(["F", "T", "S", "D"], 100)
    return pd.DataFrame({
        "price": prices,
        "date": dates,
        "postcode": [f"{d} {np.random.randint(1,9)}AA" for d in districts],
        "postcode_district": districts,
        "property_type": types,
        "new_build": np.random.choice(["Y", "N"], 100),
    })


class TestHousePriceHelpers:
    def test_load_ppd_returns_dataframe(self, sample_ppd):
        with patch("pandas.read_parquet", return_value=sample_ppd):
            from lib.house_prices import load_ppd
            df = load_ppd()
            assert isinstance(df, pd.DataFrame)
            assert "postcode_district" in df.columns

    def test_aggregate_by_district_year(self, sample_ppd):
        from lib.house_prices import aggregate_by_district_year
        result = aggregate_by_district_year(sample_ppd, "SW11")
        assert "year" in result.columns
        assert "avg_price" in result.columns

    def test_aggregate_empty_district(self, sample_ppd):
        from lib.house_prices import aggregate_by_district_year
        result = aggregate_by_district_year(sample_ppd, "ZZ99")
        assert len(result) == 0

    def test_get_all_districts_summary(self, sample_ppd):
        from lib.house_prices import get_all_districts_summary
        result = get_all_districts_summary(sample_ppd)
        assert "postcode_district" in result.columns
        assert "avg_price" in result.columns

    def test_query_overpass_returns_list(self):
        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.json.return_value = {
            "elements": [
                {"lat": 51.5, "lon": -0.1, "tags": {"name": "Waitrose"}},
                {"type": "way", "center": {"lat": 51.51, "lon": -0.12}, "tags": {"name": "Waitrose"}},
            ]
        }
        with patch("requests.get", return_value=fake_resp):
            from lib.house_prices import query_brand_locations
            locs = query_brand_locations("Waitrose")
            assert len(locs) == 2
            assert "lat" in locs[0]
            assert "lon" in locs[0]
