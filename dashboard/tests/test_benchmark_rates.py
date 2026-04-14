"""Frontend tests for Benchmark Rates Dashboard page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestBenchmarkRates:
    def _run(self):
        at = AppTest.from_file("pages/40_Benchmark_Rates.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Benchmark Rates" in markdown_blobs

    def test_has_top_level_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_currency_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Currency" in lbl for lbl in labels)

    def test_has_notional_input(self):
        at = self._run()
        labels = [n.label for n in at.number_input]
        assert any("Notional" in lbl for lbl in labels)

    def test_has_fixed_rate_input(self):
        at = self._run()
        labels = [n.label for n in at.number_input]
        assert any("Fixed Rate" in lbl for lbl in labels)

    def test_has_position_radio(self):
        at = self._run()
        assert len(at.radio) >= 1

    def test_has_rate_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Rate" in lbl for lbl in labels)

    def test_has_period_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Period" in lbl for lbl in labels)

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 4
