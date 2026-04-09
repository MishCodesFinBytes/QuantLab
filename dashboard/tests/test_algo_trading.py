"""Frontend tests for Algorithmic Trading Backtest page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestAlgoTrading:
    def _run(self):
        at = AppTest.from_file("pages/37_Algo_Trading.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Algorithmic Trading Backtest" in t.value for t in at.title)

    def test_has_two_tabs(self):
        at = self._run()
        assert len(at.tabs) == 3, f"Expected 3 tabs, got {len(at.tabs)}"

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"

    def test_has_strategy_radio(self):
        at = self._run()
        radios = [r for r in at.radio if "SMA Crossover" in r.options]
        assert radios, "Expected a strategy radio (SMA Crossover / Momentum)"

    def test_has_sma_sliders(self):
        """In SMA Crossover mode, should have fast and slow SMA window sliders."""
        at = self._run()
        fast = [s for s in at.slider if s.min == 5 and s.max == 50]
        slow = [s for s in at.slider if s.min == 20 and s.max == 200]
        assert fast, "Expected a fast SMA window slider (5-50)"
        assert slow, "Expected a slow SMA window slider (20-200)"

    def test_momentum_mode(self):
        """Switch to Momentum and verify lookback slider appears."""
        at = AppTest.from_file("pages/37_Algo_Trading.py", default_timeout=15)
        at.run()
        for r in at.radio:
            if "SMA Crossover" in r.options:
                r.set_value("Momentum")
                break
        at.run()
        assert not at.exception, f"Page crashed in Momentum mode: {at.exception}"
        lookback = [s for s in at.slider if s.min == 5 and s.max == 60]
        assert lookback, "Expected a momentum lookback slider (5-60)"
