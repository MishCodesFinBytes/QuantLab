"""Frontend tests for VaR & CVaR page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestVaRCVaR:
    def _run(self):
        at = AppTest.from_file("pages/30_VaR_CVaR.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Value at Risk" in markdown_blobs

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"

    def test_has_confidence_slider(self):
        at = self._run()
        sliders = [s for s in at.slider if s.min == 90 and s.max == 99]
        assert sliders, "Expected a confidence slider with range 90-99"
