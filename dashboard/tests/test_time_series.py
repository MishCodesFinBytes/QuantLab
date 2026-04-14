"""Frontend tests for Time Series Decomposition page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestTimeSeries:
    def _run(self):
        at = AppTest.from_file("pages/31_Time_Series.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        # The page requires >=260 rows but mock provides 252.
        # It should show an error message rather than crash.
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "ql-page-title" in markdown_blobs, "render_page_header was not called"

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"

    def test_loads_data_successfully(self):
        """Mock has 252 rows which is enough (adaptive decompose period)."""
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_has_tabs(self):
        """Page should show top-level App/Tests tabs plus chart sub-tabs."""
        at = self._run()
        assert len(at.tabs) >= 2, (
            f"Expected at least 2 tabs, got {len(at.tabs)}"
        )
