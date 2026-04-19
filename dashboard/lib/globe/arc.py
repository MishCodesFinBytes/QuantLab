"""Generic arc-row builder for pydeck ArcLayer.

Returns plain-dict arc rows so they can be passed straight into
`pdk.Layer("ArcLayer", data=arcs, ...)`. Keeping this dict-shaped
(not a pydeck object) makes tests trivial and avoids pulling pydeck
into the unit-test import path.
"""
from __future__ import annotations

from typing import Callable


def build_arc_rows(
    source: tuple[float, float],
    destinations: dict[str, dict],
    values: dict[str, float],
    color_fn: Callable[[float], tuple[int, int, int, int]],
    width_fn: Callable[[float], float] | None = None,
    default_value: float = 0.0,
) -> list[dict]:
    """Build arc dicts for pydeck ArcLayer.

    Args:
        source:        (longitude, latitude) of the arc source / epicenter.
        destinations:  {key: {"lonlat": (lon, lat), "label": str, ...}}
                       Any extra keys in the dict are forwarded to each row.
        values:        {key: float} — one scalar per destination key.
        color_fn:      Maps a scalar to an RGBA tuple.
        width_fn:      Maps a scalar to a width in pixels.
                       Defaults to a linear 0.8–3.0 px ramp.
        default_value: Value used for destinations absent from *values*.

    Returns:
        List of dicts with keys: source, target, color, width, key, label,
        value — plus any extra fields forwarded from *destinations[key]*.
    """
    if width_fn is None:
        def width_fn(v: float) -> float:
            return 0.8 + min(1.0, abs(float(v))) * 2.2

    rows: list[dict] = []
    for key, meta in destinations.items():
        v = float(values.get(key, default_value))
        row: dict = {
            "source": list(source),
            "target": list(meta["lonlat"]),
            "color": list(color_fn(v)),
            "width": width_fn(v),
            "key": key,
            "label": meta.get("label", key),
            "value": v,
        }
        for mk, mv in meta.items():
            if mk not in ("lonlat", "label"):
                row.setdefault(mk, mv)
        rows.append(row)
    return rows
