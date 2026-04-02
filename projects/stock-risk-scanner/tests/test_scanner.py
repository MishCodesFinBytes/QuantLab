import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


class TestScan:
    @patch("src.scanner.scanner.RiskNarrator")
    @patch("src.scanner.scanner.fetch_prices")
    def test_full_pipeline(self, mock_fetch, mock_narrator_cls):
        from src.scanner.models import ScanRequest
        from src.scanner.scanner import scan

        # Mock fetch_prices to return synthetic price data with realistic noise
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=252)
        aapl_noise = np.cumsum(np.random.normal(0.0005, 0.02, 252))
        msft_noise = np.cumsum(np.random.normal(0.0005, 0.02, 252))
        mock_fetch.return_value = pd.DataFrame(
            {
                "AAPL": 150 * np.exp(aapl_noise),
                "MSFT": 300 * np.exp(msft_noise),
            },
            index=dates,
        )

        # Mock narrator
        mock_narrator = mock_narrator_cls.return_value
        mock_narrator.generate.return_value = "Portfolio looks healthy."

        request = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        result = scan(request)

        assert result.tickers == ["AAPL", "MSFT"]
        assert result.weights == [0.6, 0.4]
        assert result.metrics.var_pct < 0  # VaR should be negative
        assert result.metrics.volatility_pct > 0
        assert result.narrative == "Portfolio looks healthy."
        assert result.generated_at is not None

        mock_fetch.assert_called_once_with(["AAPL", "MSFT"], "1y")
        mock_narrator.generate.assert_called_once()
