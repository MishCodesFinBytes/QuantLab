"""Frontend tests for Retirement Calculator page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestRetirementCalculator:
    def _run(self):
        at = AppTest.from_file("pages/13_Retirement_Calculator.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "Retirement Calculator" in markdown_blobs

    def test_has_top_level_tabs(self):
        at = self._run()
        assert len(at.tabs) >= 2

    def test_has_radio_mode_selector(self):
        at = self._run()
        assert len(at.radio) >= 1
        labels = [r.label for r in at.radio]
        assert any("calculate" in lbl.lower() for lbl in labels)

    def test_has_number_inputs(self):
        at = self._run()
        input_labels = [n.label for n in at.number_input]
        label_text = " ".join(input_labels).lower()
        assert "age" in label_text
        assert "savings" in label_text
        assert "return" in label_text

    def test_has_monte_carlo_checkbox(self):
        at = self._run()
        assert len(at.checkbox) >= 1
        labels = [c.label for c in at.checkbox]
        assert any("monte carlo" in lbl.lower() for lbl in labels)

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 2

    def test_switch_to_target_mode(self):
        """Switching to target-savings mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "How much should I save monthly to hit a target?"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
