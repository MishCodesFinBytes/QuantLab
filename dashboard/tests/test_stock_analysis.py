"""Frontend tests for Stock Analysis (Technical Analysis) page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestStockAnalysis:
    def _run(self):
        at = AppTest.from_file("pages/22_Stock_Analysis.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "ql-page-title" in markdown_blobs, "render_page_header was not called"

    def test_has_top_level_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_ticker_text_input(self):
        at = self._run()
        labels = [t.label for t in at.text_input]
        assert any("Ticker" in lbl for lbl in labels)

    def test_has_period_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Period" in lbl for lbl in labels)

    def test_has_sma_checkbox(self):
        at = self._run()
        labels = [c.label for c in at.checkbox]
        assert any("SMA" in lbl for lbl in labels)

    def test_has_ema_checkbox(self):
        at = self._run()
        labels = [c.label for c in at.checkbox]
        assert any("EMA" in lbl for lbl in labels)

    def test_has_bollinger_checkbox(self):
        at = self._run()
        labels = [c.label for c in at.checkbox]
        assert any("Bollinger" in lbl for lbl in labels)

    def test_has_rsi_checkbox(self):
        at = self._run()
        labels = [c.label for c in at.checkbox]
        assert any("RSI" in lbl for lbl in labels)

    def test_has_macd_checkbox(self):
        at = self._run()
        labels = [c.label for c in at.checkbox]
        assert any("MACD" in lbl for lbl in labels)

    def test_sma_checked_by_default(self):
        at = self._run()
        sma_cb = [c for c in at.checkbox if "SMA" in c.label][0]
        assert sma_cb.value is True

    def test_rsi_checked_by_default(self):
        at = self._run()
        rsi_cb = [c for c in at.checkbox if "RSI" in c.label][0]
        assert rsi_cb.value is True

    def test_macd_checked_by_default(self):
        at = self._run()
        macd_cb = [c for c in at.checkbox if "MACD" in c.label][0]
        assert macd_cb.value is True
