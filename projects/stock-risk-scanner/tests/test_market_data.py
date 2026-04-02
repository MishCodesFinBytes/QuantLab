import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


class TestFetchPrices:
    @patch("src.scanner.market_data.yf.download")
    def test_successful_fetch(self, mock_download):
        from src.scanner.market_data import fetch_prices

        # Simulate yfinance returning a MultiIndex DataFrame for 2 tickers
        dates = pd.date_range("2024-01-01", periods=5)
        mock_data = pd.DataFrame(
            {
                ("Close", "AAPL"): [150.0, 151.0, 152.0, 153.0, 154.0],
                ("Close", "MSFT"): [300.0, 301.0, 302.0, 303.0, 304.0],
            },
            index=dates,
        )
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_download.return_value = mock_data

        result = fetch_prices(["AAPL", "MSFT"], period="5d")
        assert list(result.columns) == ["AAPL", "MSFT"]
        assert len(result) == 5
        assert result["AAPL"].iloc[0] == 150.0

    @patch("src.scanner.market_data.yf.download")
    def test_empty_data_raises(self, mock_download):
        from src.scanner.market_data import fetch_prices

        mock_download.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No price data"):
            fetch_prices(["INVALID"], period="1y")
