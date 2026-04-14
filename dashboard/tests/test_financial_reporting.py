"""Frontend tests for Financial Reporting page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestFinancialReporting:
    def _run(self):
        at = AppTest.from_file("pages/26_Financial_Reporting.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Financial Reporting" in markdown_blobs

    def test_has_expected_tabs(self):
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

    def test_has_download_buttons(self):
        """Two download buttons: price data CSV and summary stats CSV."""
        at = self._run()
        buttons = at.get("download_button")
        assert len(buttons) == 2, (
            f"Expected 2 download buttons, got {len(buttons)}"
        )

    def test_download_button_labels(self):
        at = self._run()
        labels = [b.label for b in at.get("download_button")]
        label_text = " ".join(labels).lower()
        assert "price" in label_text or "data" in label_text
        assert "stats" in label_text or "summary" in label_text

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 3

    def test_metric_labels(self):
        at = self._run()
        labels = [m.label for m in at.metric]
        label_text = " ".join(labels).lower()
        assert "return" in label_text
        assert "sharpe" in label_text or "volatility" in label_text
