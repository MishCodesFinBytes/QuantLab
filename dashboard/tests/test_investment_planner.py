"""Frontend tests for Investment Planner page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestInvestmentPlanner:
    def _run(self):
        at = AppTest.from_file("pages/14_Investment_Planner.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        markdown_blobs = " ".join(m.value for m in at.markdown)
        assert "ql-page-title" in markdown_blobs, "render_page_header was not called"

    def test_has_expected_tabs(self):
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
        assert "initial" in label_text or "investment" in label_text
        assert "return" in label_text

    def test_has_sliders(self):
        at = self._run()
        assert len(at.slider) >= 1
        labels = [s.label for s in at.slider]
        label_text = " ".join(labels).lower()
        assert "horizon" in label_text or "year" in label_text or "return" in label_text

    def test_has_metrics(self):
        at = self._run()
        assert len(at.metric) >= 2

    def test_switch_to_goal_mode(self):
        """Switching to goal mode should not crash."""
        at = self._run()
        at.radio[0].set_value(
            "How much should I invest monthly to reach a goal?"
        ).run()
        assert not at.exception, f"Page crashed after mode switch: {at.exception}"
