"""Frontend tests for Loan Default Prediction page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestLoanDefault:
    def _run(self):
        at = AppTest.from_file("pages/34_Loan_Default.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Loan Default Prediction" in t.value for t in at.title)

    def test_has_two_tabs(self):
        at = self._run()
        assert len(at.tabs) == 3, f"Expected 3 tabs, got {len(at.tabs)}"

    def test_has_model_radio(self):
        at = self._run()
        radios = [r for r in at.radio if "Logistic Regression" in r.options]
        assert radios, "Expected a model radio (Logistic Regression / Random Forest)"

    def test_has_test_size_slider(self):
        at = self._run()
        sliders = [s for s in at.slider if s.min == 10 and s.max == 40]
        assert sliders, "Expected a test size slider (10-40)"

    def test_has_five_number_inputs(self):
        at = self._run()
        # Page has number_inputs for income, credit score, debt ratio, loan amount, employment years
        assert len(at.number_input) >= 5, (
            f"Expected at least 5 number_inputs, got {len(at.number_input)}"
        )

    def test_random_forest_mode(self):
        """Switch to Random Forest and verify no crash."""
        at = AppTest.from_file("pages/34_Loan_Default.py", default_timeout=15)
        at.run()
        for r in at.radio:
            if "Logistic Regression" in r.options:
                r.set_value("Random Forest")
                break
        at.run()
        assert not at.exception, f"Page crashed in Random Forest mode: {at.exception}"
