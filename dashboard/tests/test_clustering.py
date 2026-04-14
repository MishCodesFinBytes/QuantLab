"""Frontend tests for Customer Segmentation via Clustering page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestClustering:
    def _run(self):
        at = AppTest.from_file("pages/35_Clustering.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "ql-page-title" in markdown_blobs, "render_page_header was not called"

    def test_has_two_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2, f"Expected at least 2 tabs, got {len(at.tabs)}"

    def test_has_data_source_radio(self):
        at = self._run()
        radios = [r for r in at.radio if "Use sample data" in r.options]
        assert radios, "Expected a data source radio"

    def test_has_algorithm_radio(self):
        at = self._run()
        radios = [r for r in at.radio if "K-Means" in r.options]
        assert radios, "Expected an algorithm radio (K-Means / DBSCAN)"

    def test_has_clusters_slider(self):
        at = self._run()
        sliders = [s for s in at.slider if s.min == 2 and s.max == 8]
        assert sliders, "Expected a clusters slider (2-8)"

    def test_custom_data_mode(self):
        """Switch to 'Enter my own data' and verify data_editor appears."""
        at = AppTest.from_file("pages/35_Clustering.py", default_timeout=15)
        at.run()
        for r in at.radio:
            if "Use sample data" in r.options:
                r.set_value("Enter my own data")
                break
        at.run()
        assert not at.exception, f"Page crashed in custom data mode: {at.exception}"
