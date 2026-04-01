import numpy as np
import pytest
from portfolio import daily_returns, cumulative_return, max_drawdown


# --- daily_returns ---

class TestDailyReturns:
    def test_basic_returns(self):
        prices = np.array([100.0, 105.0, 103.0])
        result = daily_returns(prices)
        expected = np.array([0.05, -0.01904762])
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_single_price_returns_empty(self):
        prices = np.array([100.0])
        result = daily_returns(prices)
        assert len(result) == 0

    def test_zero_price_raises(self):
        prices = np.array([100.0, 0.0, 50.0])
        with pytest.raises(ValueError, match="zero"):
            daily_returns(prices)


# --- cumulative_return ---

class TestCumulativeReturn:
    @pytest.mark.parametrize("prices,expected", [
        (np.array([100.0, 110.0]), 0.10),
        (np.array([100.0, 90.0]), -0.10),
        (np.array([100.0, 100.0]), 0.0),
    ])
    def test_cumulative_return(self, prices, expected):
        assert cumulative_return(prices) == pytest.approx(expected, rel=1e-5)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            cumulative_return(np.array([]))


# --- max_drawdown ---

class TestMaxDrawdown:
    def test_no_drawdown(self):
        prices = np.array([100.0, 110.0, 120.0])
        assert max_drawdown(prices) == 0.0

    def test_simple_drawdown(self):
        prices = np.array([100.0, 120.0, 90.0, 110.0])
        # Peak 120, trough 90 → drawdown = -30/120 = -0.25
        assert max_drawdown(prices) == pytest.approx(-0.25)

    def test_drawdown_at_end(self):
        prices = np.array([100.0, 200.0, 100.0])
        assert max_drawdown(prices) == pytest.approx(-0.50)
