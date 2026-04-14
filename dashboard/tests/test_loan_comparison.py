"""Frontend tests for Loan Comparison page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestLoanComparison:
    def _run(self):
        at = AppTest.from_file("pages/12_Loan_Comparison.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Loan Comparison" in markdown_blobs

    def test_has_expected_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_radio_mode_selector(self):
        at = self._run()
        assert len(at.radio) >= 1
        labels = [r.label for r in at.radio]
        assert any("compare" in lbl.lower() for lbl in labels)

    def test_has_number_inputs(self):
        at = self._run()
        input_labels = [n.label for n in at.number_input]
        label_text = " ".join(input_labels).lower()
        assert "principal" in label_text
        assert "rate" in label_text

    def test_has_selectbox_for_terms(self):
        at = self._run()
        assert len(at.selectbox) >= 1
        labels = [s.label for s in at.selectbox]
        assert any("term" in lbl.lower() or "year" in lbl.lower() for lbl in labels)

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 4

    def test_switch_to_rate_sensitivity_mode(self):
        """Switching to rate sensitivity mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "Same loan at different rates (rate sensitivity)"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
