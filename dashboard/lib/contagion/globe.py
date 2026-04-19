"""pydeck globe arc-layer builders.

Returns plain-dict arc rows so the Streamlit page can pass them straight
into `pdk.Layer("ArcLayer", data=arcs, ...)`. Keeping this dict-shaped
(not a pydeck object) makes tests trivial and avoids pulling pydeck
into the unit-test import path.
"""
from __future__ import annotations


from .constants import DESTINATION_CITIES, EPICENTER_LONLAT


def correlation_to_color(corr: float) -> tuple[int, int, int, int]:
    """Diverging color ramp: green (-1) → slate (0) → red (+1).

    Anchors deliberately match the page palette so arcs, destination
    country fills, correlation cells, and ticker chips all speak the
    same colour language:
        red   = #c81e1e  (strong contagion)
        green = #14a028  (strong decoupling / safe-haven bid)
        slate = #475569  (no signal) — swapped from neutral gray so the
                                       arc midpoints read against the
                                       dark night-lights globe.
    """
    c = max(-1.0, min(1.0, float(corr)))
    green = (20, 160, 40)    # #14a028
    slate = (71, 85, 105)    # #475569
    red = (200, 30, 30)      # #c81e1e
    if c >= 0:
        t = c
        r = int(slate[0] + t * (red[0] - slate[0]))
        g = int(slate[1] + t * (red[1] - slate[1]))
        b = int(slate[2] + t * (red[2] - slate[2]))
    else:
        t = -c
        r = int(slate[0] + t * (green[0] - slate[0]))
        g = int(slate[1] + t * (green[1] - slate[1]))
        b = int(slate[2] + t * (green[2] - slate[2]))
    # Alpha scales with |correlation| so strong signals read as bright
    # glow and weak ones fade toward slate — helps the eye pick out
    # which markets are actually "lit up" without having to read the
    # correlation table. Range 110 (weak) → 240 (strong).
    strength = abs(c)
    alpha = int(110 + strength * 130)
    return (r, g, b, alpha)


_MIN_ARC_WIDTH: float = 0.8
_MAX_ARC_WIDTH: float = 3.0


def correlation_to_width(corr: float) -> float:
    """Arc width in pixels — scales with |correlation| so strong contagion
    reads as a thick bold arc and weak signal reads as a hairline.
    Range is deliberately thin (0.8–3 px) so the arc stack (outer halo
    + inner core) reads as a neon beam rather than a painted line."""
    strength = min(1.0, abs(float(corr)))
    return _MIN_ARC_WIDTH + strength * (_MAX_ARC_WIDTH - _MIN_ARC_WIDTH)


def build_arc_rows(
    correlations_by_country: dict[str, float]
) -> list[dict]:
    """Build arc dicts for pydeck ArcLayer.

    Args:
        correlations_by_country: e.g. {"IN": 0.8, "TR": -0.3, ...}

    Returns:
        List of dicts with keys: source, target, color, width, dest_country,
        dest_label, correlation. Ready to be passed as the ArcLayer `data`.
    """
    rows: list[dict] = []
    for country_code, meta in DESTINATION_CITIES.items():
        corr = correlations_by_country.get(country_code, 0.0)
        rows.append({
            "source": list(EPICENTER_LONLAT),
            "target": list(meta["lonlat"]),
            "color": list(correlation_to_color(corr)),
            "width": correlation_to_width(corr),
            # pre-computed rounded correlation for the ArcLayer tooltip;
            # deck.gl doesn't do numeric formatting so we format here.
            "dest_country": country_code,
            "dest_label": meta["label"],
            "correlation": float(corr),
        })
    return rows
