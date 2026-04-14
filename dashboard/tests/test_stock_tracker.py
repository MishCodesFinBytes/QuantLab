"""Frontend tests for Stock Tracker page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestStockTracker:
    def _run(self):
        at = AppTest.from_file("pages/21_Stock_Tracker.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Stock Tracker" in markdown_blobs

    def test_has_top_level_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_ticker_text_input(self):
        at = self._run()
        labels = [t.label for t in at.text_input]
        assert any("Ticker" in lbl for lbl in labels)

    def test_ticker_default_value(self):
        at = self._run()
        ticker_input = [t for t in at.text_input if "Ticker" in t.label][0]
        assert ticker_input.value == "AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Period" in lbl for lbl in labels)

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 3

    def test_error_on_empty_data(self, mock_empty_data):
        """Page shows st.error and stops when yfinance returns no data."""
        at = self._run()
        assert len(at.error) >= 1
