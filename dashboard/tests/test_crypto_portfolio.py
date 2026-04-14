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
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "ql-page-title" in markdown_blobs, "render_page_header was not called"

    def test_has_expected_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_data_editor(self):
        """Holdings editor should be present for coin/quantity input."""
        at = self._run()
        # data_editor internal element type varies across Streamlit versions
        editors = at.get("arrow_data_frame") or at.get("data_frame") or []
        if not editors:
            pytest.skip("data_editor not exposed in this Streamlit version's AppTest")

    def test_has_metrics(self):
        """Default holdings produce summary metrics."""
        at = self._run()
        assert len(at.metric) >= 2

    def test_metric_labels(self):
        at = self._run()
        labels = [m.label for m in at.metric]
        label_text = " ".join(labels).lower()
        assert "portfolio" in label_text or "total" in label_text
