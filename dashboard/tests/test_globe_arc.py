"""Unit tests for lib/globe/arc.py."""
from lib.globe.arc import build_arc_rows
from lib.globe.color import diverging_color

_SOURCE = (56.0, 26.0)
_DESTS = {
    "IN": {"lonlat": (72.88, 19.08), "label": "Mumbai", "country": "India"},
    "DE": {"lonlat": (8.68, 50.11),  "label": "Frankfurt"},
    "US": {"lonlat": (-74.01, 40.71), "label": "New York"},
}
_COLOR_FN = lambda v: diverging_color(v, (50, 140, 80), (71, 85, 105), (180, 70, 70))


def test_returns_one_row_per_destination():
    rows = build_arc_rows(_SOURCE, _DESTS, {"IN": 0.8}, color_fn=_COLOR_FN)
    assert len(rows) == 3


def test_row_keys_present():
    rows = build_arc_rows(_SOURCE, _DESTS, {"IN": 0.8}, color_fn=_COLOR_FN)
    for row in rows:
        assert len(row["source"]) == 2
        assert len(row["target"]) == 2
        assert len(row["color"]) == 4
        assert isinstance(row["width"], float)
        assert "key" in row and "label" in row and "value" in row


def test_missing_destination_uses_default():
    rows = build_arc_rows(_SOURCE, _DESTS, {}, color_fn=_COLOR_FN, default_value=0.0)
    for row in rows:
        assert row["value"] == 0.0


def test_extra_meta_forwarded():
    rows = build_arc_rows(_SOURCE, _DESTS, {"IN": 0.5}, color_fn=_COLOR_FN)
    india = next(r for r in rows if r["key"] == "IN")
    assert india["country"] == "India"


def test_source_matches_input():
    rows = build_arc_rows(_SOURCE, _DESTS, {}, color_fn=_COLOR_FN)
    assert all(row["source"] == list(_SOURCE) for row in rows)
