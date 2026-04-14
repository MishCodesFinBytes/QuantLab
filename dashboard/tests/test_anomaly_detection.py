"""Frontend tests for Return Anomaly Detection page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestAnomalyDetection:
    def _run(self):
        at = AppTest.from_file("pages/33_Anomaly_Detection.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
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

    def test_has_method_radio(self):
        at = self._run()
        radios = [r for r in at.radio if "Z-Score" in r.options]
        assert radios, "Expected a radio with Z-Score / Isolation Forest options"

    def test_has_threshold_slider(self):
        at = self._run()
        sliders = [s for s in at.slider if s.min == 1.5 and s.max == 4.0]
        assert sliders, "Expected a Z-Score threshold slider (1.5-4.0)"

    def test_isolation_forest_mode(self):
        """Switch to Isolation Forest and verify no crash."""
        at = AppTest.from_file("pages/33_Anomaly_Detection.py", default_timeout=15)
        at.run()
        for r in at.radio:
            if "Z-Score" in r.options:
                r.set_value("Isolation Forest")
                break
        at.run()
        assert not at.exception, f"Page crashed in Isolation Forest mode: {at.exception}"
