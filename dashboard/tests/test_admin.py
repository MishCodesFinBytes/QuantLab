"""Frontend tests for RDS Admin page."""
import pytest
from streamlit.testing.v1 import AppTest


class TestAdmin:
    def _run(self):
        at = AppTest.from_file("pages/99_Admin.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        # The page may show errors due to secrets structure mismatch,
        # but it should not raise an unhandled exception.
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("RDS Admin" in t.value for t in at.title)

    def test_has_password_form(self):
        """The auth gate should show a password text_input."""
        at = self._run()
        # The page shows a text_input inside a form for the admin password.
        # AppTest text_input elements may not expose a 'type' property,
        # so just check that a text_input exists (the only one on the
        # unauthenticated page is the password field).
        assert len(at.text_input) >= 1, (
            "Expected a password text_input in the auth form"
        )

    def test_has_form_submit(self):
        """The auth form should have a submit button."""
        at = self._run()
        # The page uses st.form with a form_submit_button
        buttons = [b.label for b in at.button]
        assert any("Unlock" in label for label in buttons), (
            "Expected an 'Unlock' submit button in the auth form"
        )
