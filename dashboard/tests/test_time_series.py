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
        assert any("Time Series Decomposition" in t.value for t in at.title)

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"

    def test_handles_insufficient_data(self):
        """Mock has 252 rows but page needs 260; should show error, not crash."""
        at = self._run()
        errors = [e.value for e in at.error]
        # Page should display an error about needing 260 days
        assert any("260" in e for e in errors), (
            "Expected an error message about needing 260 trading days"
        )

    def test_has_two_tabs_or_error(self):
        """If data is sufficient the page shows 2 tabs; otherwise stops early."""
        at = self._run()
        # With 252 rows the page stops before tabs, so tabs may be 0 or 2
        assert len(at.tabs) in (0, 2), (
            f"Expected 0 tabs (data error) or 2 tabs, got {len(at.tabs)}"
        )
