"""Frontend tests for Portfolio Optimization page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestPortfolioOptimization:
    def _run(self):
        at = AppTest.from_file("pages/36_Portfolio_Optimization.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Portfolio Optimization" in t.value for t in at.title)

    def test_has_multiselect_tickers(self):
        at = self._run()
        ms = [w for w in at.multiselect if "AAPL" in w.options]
        assert ms, "Expected a multiselect with ticker options including AAPL"
        # Should have 14 options
        assert len(ms[0].options) == 14, (
            f"Expected 14 ticker options, got {len(ms[0].options)}"
        )

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"

    def test_has_simulations_slider(self):
        at = self._run()
        sliders = [s for s in at.slider if s.min == 1000 and s.max == 50000]
        assert sliders, "Expected a simulations slider (1000-50000)"

    def test_has_risk_free_rate_input(self):
        at = self._run()
        ni = [w for w in at.number_input if w.min == 0.0 and w.max == 10.0]
        assert ni, "Expected a risk-free rate number_input (0.0-10.0)"
