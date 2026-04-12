"""Frontend tests for Plotting Libraries page."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


@pytest.fixture
def sample_ohlcv():
    """Small OHLCV DataFrame for chart builder tests."""
    dates = pd.bdate_range("2026-01-02", periods=30)
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(30) * 2)
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.random.randint(1_000_000, 5_000_000, 30),
        },
        index=dates,
    )


class TestPlotlyCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_line_chart

        fig = plotly_line_chart(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1

    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_candlestick

        fig = plotly_candlestick(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_volume_bar

        fig = plotly_volume_bar(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_returns_histogram

        fig = plotly_returns_histogram(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1


class TestMatplotlibCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_line_chart

        fig = matplotlib_line_chart(sample_ohlcv)
        assert fig is not None
        assert len(fig.get_axes()) >= 1

    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_candlestick

        fig = matplotlib_candlestick(sample_ohlcv)
        assert fig is not None
        assert len(fig.get_axes()) >= 1

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_volume_bar

        fig = matplotlib_volume_bar(sample_ohlcv)
        assert fig is not None

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_returns_histogram

        fig = matplotlib_returns_histogram(sample_ohlcv)
        assert fig is not None
