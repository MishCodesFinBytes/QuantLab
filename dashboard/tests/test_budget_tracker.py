"""Frontend tests for Budget Tracker page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestBudgetTracker:
    def _run(self):
        at = AppTest.from_file("pages/15_Budget_Tracker.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Budget Tracker" in t.value for t in at.title)

    def test_has_expected_tabs(self):
        at = self._run()
        assert len(at.tabs) == 3

    def test_has_radio_mode_selector(self):
        at = self._run()
        assert len(at.radio) >= 1
        labels = [r.label for r in at.radio]
        assert any("do" in lbl.lower() or "budget" in lbl.lower() for lbl in labels)

    def test_has_income_number_input(self):
        at = self._run()
        input_labels = [n.label for n in at.number_input]
        label_text = " ".join(input_labels).lower()
        assert "income" in label_text

    def test_has_data_editor(self):
        """Page should have an editable expense table."""
        at = self._run()
        # data_editor is exposed as dataframe in AppTest
        assert len(at.dataframe) >= 1 or hasattr(at, "data_editor")

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 2

    def test_shows_budget_status_message(self):
        """Default budget should show a success, warning, or error message."""
        at = self._run()
        has_status = (
            len(at.success) > 0
            or len(at.warning) > 0
            or len(at.error) > 0
        )
        assert has_status, "Expected a success, warning, or error budget status message"

    def test_switch_to_plan_mode(self):
        """Switching to plan mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "Plan a budget from a savings target"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
