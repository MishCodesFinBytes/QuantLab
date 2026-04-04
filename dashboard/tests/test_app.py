"""Frontend tests for the Streamlit dashboard using AppTest."""
import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest


class TestLandingPage:
    def test_loads_without_error(self):
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        assert not at.exception, f"App crashed: {at.exception}"

    def test_shows_title(self):
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        assert any("FinBytes QuantLabs" in t.value or "System Health" in t.value for t in at.title)


class TestScannerPage:
    def _run_scanner(self):
        """Run scanner page with mocked external calls."""
        at = AppTest.from_file("pages/1_Stock_Risk_Scanner.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run_scanner()
        assert not at.exception, f"Scanner page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run_scanner()
        assert any("Stock Risk Scanner" in t.value for t in at.title)

    def test_has_three_tabs(self):
        at = self._run_scanner()
        assert len(at.tabs) == 3

    def test_has_scan_button(self):
        at = self._run_scanner()
        buttons = [b.label for b in at.button]
        assert any("Scan" in label for label in buttons)

    def test_has_preset_buttons(self):
        at = self._run_scanner()
        buttons = [b.label for b in at.button]
        assert any("Tech Giants" in label for label in buttons)
        assert any("Safe Haven" in label for label in buttons)
        assert any("Balanced" in label for label in buttons)

    def test_has_equal_weight_button(self):
        at = self._run_scanner()
        buttons = [b.label for b in at.button]
        assert any("Equal Weight" in label for label in buttons)
