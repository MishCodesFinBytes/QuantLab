"""Frontend tests for Crypto Portfolio Tracker page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestCryptoPortfolio:
    def _run(self):
        at = AppTest.from_file("pages/23_Crypto_Portfolio.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Crypto Portfolio Tracker" in t.value for t in at.title)

    def test_has_expected_tabs(self):
        at = self._run()
        assert len(at.tabs) == 3

    def test_has_data_editor(self):
        """Holdings editor should be present for coin/quantity input."""
        at = self._run()
        # data_editor renders as arrow_data_frame or data_frame depending on version
        editors = at.get("arrow_data_frame") or at.get("data_frame") or []
        assert len(editors) >= 1, "Expected at least one data_editor for holdings"

    def test_has_metrics(self):
        """Default holdings produce summary metrics."""
        at = self._run()
        assert len(at.metric) >= 2

    def test_metric_labels(self):
        at = self._run()
        labels = [m.label for m in at.metric]
        label_text = " ".join(labels).lower()
        assert "portfolio" in label_text or "total" in label_text
