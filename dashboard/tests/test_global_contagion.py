"""Frontend tests for the Global Contagion page."""
from streamlit.testing.v1 import AppTest


class TestGlobalContagionPage:
    def _run(self):
        at = AppTest.from_file("pages/70_Global_Contagion.py", default_timeout=20)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        blobs = " ".join(m.value for m in at.markdown)
        assert "Global Contagion" in blobs

    def test_has_period_radio(self):
        at = self._run()
        # The page exposes a radio with two options.
        labels = [r.label for r in at.radio]
        assert any("period" in l.lower() or "conflict" in l.lower() for l in labels), (
            f"Expected a period radio; got labels: {labels}"
        )

    def test_has_timeline_slider(self):
        at = self._run()
        assert len(at.slider) >= 1, "Expected at least one slider for the timeline"

    def test_has_play_button(self):
        at = self._run()
        labels = [b.label for b in at.button]
        assert any("play" in l.lower() or "pause" in l.lower() for l in labels), (
            f"Expected a play/pause button; got: {labels}"
        )

    def test_side_panel_renders_four_metrics(self):
        at = self._run()
        # Asserting on the stable markdown labels — the underlying chart
        # element's AppTest type name differs across Streamlit versions
        # (arrow_vega_lite_chart locally vs older alias on CI), so we
        # verify each panel's **<label>** heading was rendered instead.
        markdown_text = " ".join(m.value for m in at.markdown)
        for label in ("Brent Crude", "Baltic Dry", "Gold", "VIX"):
            assert label in markdown_text, (
                f"Expected side-panel label '{label}' in markdown output"
            )
