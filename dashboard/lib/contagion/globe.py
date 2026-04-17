"""pydeck globe arc-layer builders.

Returns plain-dict arc rows so the Streamlit page can pass them straight
into `pdk.Layer("ArcLayer", data=arcs, ...)`. Keeping this dict-shaped
(not a pydeck object) makes tests trivial and avoids pulling pydeck
into the unit-test import path.
"""
from __future__ import annotations


from .constants import DESTINATION_CITIES, EPICENTER_LONLAT


def correlation_to_color(corr: float) -> tuple[int, int, int, int]:
    """Diverging color ramp: green (-1) → gray (0) → red (+1)."""
    c = max(-1.0, min(1.0, float(corr)))
    # Anchors
    green = (20, 160, 40)
    gray = (128, 128, 128)
    red = (200, 30, 30)
    if c >= 0:
        t = c
        r = int(gray[0] + t * (red[0] - gray[0]))
        g = int(gray[1] + t * (red[1] - gray[1]))
        b = int(gray[2] + t * (red[2] - gray[2]))
    else:
        t = -c
        r = int(gray[0] + t * (green[0] - gray[0]))
        g = int(gray[1] + t * (green[1] - gray[1]))
        b = int(gray[2] + t * (green[2] - gray[2]))
    return (r, g, b, 220)


def build_arc_rows(
    correlations_by_country: dict[str, float]
) -> list[dict]:
    """Build arc dicts for pydeck ArcLayer.

    Args:
        correlations_by_country: e.g. {"IN": 0.8, "TR": -0.3, ...}

    Returns:
        List of dicts with keys: source, target, color, dest_country,
        dest_label, correlation. Ready to be passed as the ArcLayer `data`.
    """
    rows: list[dict] = []
    for country_code, meta in DESTINATION_CITIES.items():
        corr = correlations_by_country.get(country_code, 0.0)
        rows.append({
            "source": list(EPICENTER_LONLAT),
            "target": list(meta["lonlat"]),
            "color": list(correlation_to_color(corr)),
            "dest_country": country_code,
            "dest_label": meta["label"],
            "correlation": float(corr),
        })
    return rows
