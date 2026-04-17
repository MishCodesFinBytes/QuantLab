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
        # st.line_chart renders as arrow_vega_lite_chart in AppTest.
        # Count those elements across the main block.
        charts = [el for el in at.main if getattr(el, "type", "") == "arrow_vega_lite_chart"]
        assert len(charts) >= 4, (
            f"Expected ≥4 sparklines; got {len(charts)}"
        )
