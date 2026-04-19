"""Reusable deck.gl globe helpers — colour ramps, arc builders, layer factories.

Designed for global-scale visualisations (air quality, water quality,
geopolitical risk, etc.).  All functions return plain Python dicts/tuples
so they are pydeck-agnostic and trivially testable.

Public API
----------
    from globe.color import diverging_color, sequential_color, value_to_width
    from globe.arc import build_arc_rows
    from globe.layers import bitmap_layer, country_fill_layer, arc_layer_stack, city_nodes_layer
    from globe import style
"""
from .color import diverging_color, sequential_color, value_to_width
from .arc import build_arc_rows
from . import style
