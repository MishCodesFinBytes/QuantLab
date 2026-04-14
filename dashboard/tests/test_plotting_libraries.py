"""Frontend tests for Plotting Libraries page."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class TestPlottingLibrariesPage:
    def _run(self):
        at = AppTest.from_file("pages/41_Plotting_Libraries.py", default_timeout=30)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Plotting Libraries" in markdown_blobs

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"


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


class TestAltairCharts:
    def test_line_chart_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_line_chart
        import altair as alt

        chart = altair_line_chart(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_candlestick_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_candlestick
        import altair as alt

        chart = altair_candlestick(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_volume_bar_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_volume_bar
        import altair as alt

        chart = altair_volume_bar(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_returns_histogram_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_returns_histogram
        import altair as alt

        chart = altair_returns_histogram(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))


class TestBokehCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_line_chart

        fig = bokeh_line_chart(sample_ohlcv)
        assert fig is not None

    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_candlestick

        fig = bokeh_candlestick(sample_ohlcv)
        assert fig is not None

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_volume_bar

        fig = bokeh_volume_bar(sample_ohlcv)
        assert fig is not None

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_returns_histogram

        fig = bokeh_returns_histogram(sample_ohlcv)
        assert fig is not None


class TestOutlierDetection:
    def test_no_outliers_in_clean_data(self, sample_ohlcv):
        from lib.plotting import detect_outliers

        result = detect_outliers(sample_ohlcv)
        assert result.sum().sum() < 3

    def test_detects_injected_outlier(self, sample_ohlcv):
        from lib.plotting import detect_outliers

        df = sample_ohlcv.copy()
        # Spike one Close value to 10x the mean
        df.iloc[15, df.columns.get_loc("Close")] = df["Close"].mean() * 10
        result = detect_outliers(df)
        assert result["Close"].iloc[15] == True

    def test_compute_daily_returns(self, sample_ohlcv):
        from lib.plotting import compute_daily_returns

        returns = compute_daily_returns(sample_ohlcv)
        assert len(returns) == len(sample_ohlcv) - 1
        assert returns.dtype == float
