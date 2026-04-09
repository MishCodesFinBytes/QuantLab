"""Frontend tests for Credit Card Calculator page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestCreditCardCalculator:
    def _run(self):
        at = AppTest.from_file("pages/10_Credit_Card_Calculator.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Credit Card Payoff Calculator" in t.value for t in at.title)

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
        assert "balance" in label_text
        assert "apr" in label_text

    def test_default_mode_shows_payment_input(self):
        """Default mode asks for monthly payment."""
        at = self._run()
        input_labels = [n.label for n in at.number_input]
        label_text = " ".join(input_labels).lower()
        assert "payment" in label_text or "months" in label_text

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 2

    def test_switch_to_target_mode(self):
        """Switching radio to target-months mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "I want to pay off in X months — what payment do I need?"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
