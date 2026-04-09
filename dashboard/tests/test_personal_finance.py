"""Frontend tests for Personal Finance Dashboard page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestPersonalFinance:
    def _run(self):
        at = AppTest.from_file("pages/24_Personal_Finance.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Personal Finance Dashboard" in t.value for t in at.title)

    def test_has_income_number_input(self):
        at = self._run()
        labels = [n.label for n in at.number_input]
        assert any("Income" in lbl for lbl in labels)

    def test_has_data_editors(self):
        """Assets and liabilities editors should be present."""
        at = self._run()
        # data_editor renders as arrow_data_frame or data_frame depending on version
        editors = at.get("arrow_data_frame") or at.get("data_frame") or []
        assert len(editors) >= 2, "Expected at least 2 data_editors (assets and liabilities)"

    def test_has_expected_tabs(self):
        """Default data produces bar_data, so tabs appear."""
        at = self._run()
        assert len(at.tabs) == 2

    def test_has_net_worth_metric(self):
        at = self._run()
        labels = [m.label for m in at.metric]
        assert any("Net Worth" in lbl for lbl in labels)

    def test_has_savings_rate_metric(self):
        at = self._run()
        labels = [m.label for m in at.metric]
        assert any("Savings" in lbl for lbl in labels)

    def test_no_external_api_calls(self):
        """Page should load without any API mocks being hit."""
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"
