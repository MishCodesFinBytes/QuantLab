"""Generic colour-ramp helpers for globe visualisations.

All functions return plain Python tuples / floats so they are pydeck-agnostic
and trivially testable without the pydeck import path.
"""
from __future__ import annotations


def _lerp(
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    return (
        int(a[0] + t * (b[0] - a[0])),
        int(a[1] + t * (b[1] - a[1])),
        int(a[2] + t * (b[2] - a[2])),
    )


def diverging_color(
    value: float,
    neg_anchor: tuple[int, int, int],
    zero_anchor: tuple[int, int, int],
    pos_anchor: tuple[int, int, int],
    alpha_range: tuple[int, int] = (70, 200),
) -> tuple[int, int, int, int]:
    """Diverging colour ramp: neg_anchor (−1) → zero_anchor (0) → pos_anchor (+1).

    Args:
        value:       Scalar in [−1, 1]; clamped outside that range.
        neg_anchor:  RGB for value = −1.
        zero_anchor: RGB for value =  0.
        pos_anchor:  RGB for value = +1.
        alpha_range: (alpha_min, alpha_max) — alpha scales linearly with |value|.

    Returns:
        RGBA tuple of ints in [0, 255].
    """
    v = max(-1.0, min(1.0, float(value)))
    if v >= 0:
        r, g, b = _lerp(zero_anchor, pos_anchor, v)
    else:
        r, g, b = _lerp(zero_anchor, neg_anchor, -v)
    strength = abs(v)
    alpha = int(alpha_range[0] + strength * (alpha_range[1] - alpha_range[0]))
    return (r, g, b, alpha)


def sequential_color(
    value: float,
    low_anchor: tuple[int, int, int],
    high_anchor: tuple[int, int, int],
    alpha_range: tuple[int, int] = (100, 220),
) -> tuple[int, int, int, int]:
    """Sequential colour ramp: low_anchor (0) → high_anchor (1).

    Useful for pollution / air-quality indexes where 0 = clean and 1 = worst.

    Args:
        value:       Scalar in [0, 1]; clamped outside that range.
        low_anchor:  RGB for value = 0.
        high_anchor: RGB for value = 1.
        alpha_range: (alpha_min, alpha_max) — alpha scales linearly with value.

    Returns:
        RGBA tuple of ints in [0, 255].
    """
    v = max(0.0, min(1.0, float(value)))
    r, g, b = _lerp(low_anchor, high_anchor, v)
    alpha = int(alpha_range[0] + v * (alpha_range[1] - alpha_range[0]))
    return (r, g, b, alpha)


def value_to_width(value: float, min_w: float = 0.8, max_w: float = 3.0) -> float:
    """Scale arc width linearly with |value|, clamped to [min_w, max_w]."""
    return min_w + min(1.0, abs(float(value))) * (max_w - min_w)
