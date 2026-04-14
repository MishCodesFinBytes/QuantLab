"""Frontend tests for Currency Dashboard page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestCurrencyDashboard:
    def _run(self):
        at = AppTest.from_file("pages/20_Currency_Dashboard.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Currency Dashboard" in markdown_blobs

    def test_has_base_currency_selectbox(self):
        at = self._run()
        labels = [s.label for s in at.selectbox]
        assert any("Base Currency" in lbl for lbl in labels)

    def test_base_currency_options(self):
        at = self._run()
        base_sb = [s for s in at.selectbox if "Base Currency" in s.label][0]
        for cur in ["USD", "EUR", "GBP", "JPY", "CHF"]:
            assert cur in base_sb.options

    def test_has_target_multiselect(self):
        at = self._run()
        labels = [m.label for m in at.multiselect]
        assert any("Target" in lbl for lbl in labels)

    def test_has_amount_number_input(self):
        at = self._run()
        labels = [n.label for n in at.number_input]
        assert any("Amount" in lbl for lbl in labels)

    def test_has_expected_tabs_with_targets(self):
        """When targets are selected (default), two tabs are shown."""
        at = self._run()
        assert len(at.tabs) >= 2

    def test_shows_metrics_for_targets(self):
        """Default run has target currencies selected, so metrics appear."""
        at = self._run()
        assert len(at.metric) >= 1

    def test_error_on_fetch_failure(self, monkeypatch):
        """Page shows st.error and stops when exchange rate fetch fails."""
        monkeypatch.setattr(
            "data.fetch_exchange_rates", lambda *a, **kw: {}
        )
        at = self._run()
        assert len(at.error) >= 1
        assert any("exchange rates" in e.value.lower() for e in at.error)
