"""Frontend tests for the Rent vs Buy London page."""
import pytest
from streamlit.testing.v1 import AppTest


def _run():
    at = AppTest.from_file("pages/16_Rent_vs_Buy.py", default_timeout=20)
    at.run()
    return at


def test_loads_without_error():
    at = _run()
    assert not at.exception, f"Page crashed: {at.exception}"


def test_has_bedroom_selectbox():
    at = _run()
    selectboxes = [s for s in at.selectbox if "Bedroom" in (s.label or "")]
    assert selectboxes, "Expected a selectbox with 'Bedroom' in its label"
    assert "Studio" in selectboxes[0].options
    assert "4+" in selectboxes[0].options
