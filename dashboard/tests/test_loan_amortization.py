"""Frontend tests for Loan Amortization page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestLoanAmortization:
    def _run(self):
        at = AppTest.from_file("pages/11_Loan_Amortization.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Loan Amortization Calculator" in t.value for t in at.title)

    def test_has_expected_tabs(self):
        at = self._run()
        assert len(at.tabs) == 3

    def test_has_radio_mode_selector(self):
        at = self._run()
        assert len(at.radio) >= 1
        labels = [r.label for r in at.radio]
        assert any("calculate" in lbl.lower() for lbl in labels)

    def test_has_number_inputs(self):
        at = self._run()
        input_labels = [n.label for n in at.number_input]
        label_text = " ".join(input_labels).lower()
        assert "principal" in label_text
        assert "rate" in label_text or "interest" in label_text

    def test_default_mode_has_term_selectbox(self):
        """Default (term) mode shows a selectbox for loan term."""
        at = self._run()
        assert len(at.selectbox) >= 1
        labels = [s.label for s in at.selectbox]
        assert any("term" in lbl.lower() or "year" in lbl.lower() for lbl in labels)

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 2

    def test_switch_to_budget_mode(self):
        """Switching to budget mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "I know my budget -- what loan can I afford?"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
