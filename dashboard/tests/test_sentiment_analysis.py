"""Frontend tests for Headline Sentiment Analysis page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestSentimentAnalysis:
    def _run(self):
        at = AppTest.from_file("pages/32_Sentiment_Analysis.py", default_timeout=15)
        at.run()
        return at

    def _skip_if_import_error(self, at):
        """Skip the test if the page crashed due to a missing dependency."""
        if at.exception:
            msgs = [str(e) for e in at.exception]
            if any("vaderSentiment" in m or "textblob" in m or "ModuleNotFoundError" in m for m in msgs):
                pytest.skip("vaderSentiment/textblob not installed")

    def test_loads_without_error(self):
        at = self._run()
        self._skip_if_import_error(at)
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        self._skip_if_import_error(at)
        assert any("Headline Sentiment Analysis" in t.value for t in at.title)

    def test_has_analyzer_radio(self):
        at = self._run()
        self._skip_if_import_error(at)
        radios = [r for r in at.radio if "VADER" in r.options]
        assert radios, "Expected a radio with VADER/TextBlob options"

    def test_has_headline_text_area(self):
        at = self._run()
        self._skip_if_import_error(at)
        assert len(at.text_area) >= 1, "Expected a text_area for headlines"

    def test_has_reset_button(self):
        at = self._run()
        self._skip_if_import_error(at)
        buttons = [b.label for b in at.button]
        assert any("Reset" in label for label in buttons), (
            "Expected a 'Reset to samples' button"
        )

    def test_textblob_mode(self):
        """Switch to TextBlob analyzer and verify no crash."""
        at = AppTest.from_file("pages/32_Sentiment_Analysis.py", default_timeout=15)
        at.run()
        self._skip_if_import_error(at)
        # Find the analyzer radio and switch to TextBlob
        for r in at.radio:
            if "VADER" in r.options:
                r.set_value("TextBlob")
                break
        at.run()
        self._skip_if_import_error(at)
        assert not at.exception, f"Page crashed in TextBlob mode: {at.exception}"
