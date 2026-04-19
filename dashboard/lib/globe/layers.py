"""pydeck Layer factories for the blue tech-globe aesthetic.

Each builder returns a ``pdk.Layer`` instance ready to be added to a
``pdk.Deck`` layer list.  The functions default to the blue aesthetic
constants in ``style.py`` but accept overrides for any parameter.
"""
from __future__ import annotations

import pydeck as pdk

from . import style


def bitmap_layer(
    image_url: str,
    *,
    id: str = "night-lights",
    opacity: float = 1.0,
) -> pdk.Layer:
    """Full-globe raster tile (e.g. NASA night-lights or an ocean texture)."""
    return pdk.Layer(
        "BitmapLayer",
        id=id,
        data=None,
        image=image_url,
        bounds=[-180, -90, 180, 90],
        opacity=opacity,
    )


def country_fill_layer(
    data: dict,
    *,
    id: str = "countries",
    fill_color: list[int] | str = style.CONTINENT_FILL,
    line_color: list[int] | str = style.CONTINENT_STROKE,
    line_width_min: float = style.CONTINENT_LINE_WIDTH,
    update_trigger: str = "",
    pickable: bool = False,
) -> pdk.Layer:
    """GeoJsonLayer for choropleth or styled country polygons.

    Pass ``fill_color="properties.ql_fill"`` to drive fills from feature
    properties (correlation, AQI, etc.).
    Pass a plain ``[R, G, B, A]`` list for a uniform static colour.
    """
    return pdk.Layer(
        "GeoJsonLayer",
        id=id,
        data=data,
        stroked=True,
        filled=True,
        get_fill_color=fill_color,
        get_line_color=line_color,
        line_width_min_pixels=line_width_min,
        pickable=pickable,
        update_triggers={"get_fill_color": update_trigger} if update_trigger else {},
    )


def arc_layer_stack(
    arcs: list[dict],
    *,
    colour_trigger: str = "",
) -> list[pdk.Layer]:
    """Triple-stack neon glow arcs: outer halo + soft glow + bright core.

    Each arc dict must have keys:
        source — [lon, lat]
        target — [lon, lat]
        color  — [R, G, B, A]
        width  — float (base width in pixels)

    The three-layer stack creates a bloom effect without WebGL post-processing.
    """
    triggers = {
        "getSourceColor": colour_trigger,
        "getTargetColor": colour_trigger,
        "getWidth": colour_trigger,
    }
    common = dict(
        data=arcs,
        get_source_position="source",
        get_target_position="target",
        get_source_color="color",
        get_target_color="color",
        great_circle=True,
        update_triggers=triggers,
    )
    return [
        pdk.Layer("ArcLayer", id="arc-outer", get_width="width * 8",
                  width_min_pixels=6, opacity=0.06, pickable=False, **common),
        pdk.Layer("ArcLayer", id="arc-glow",  get_width="width * 3",
                  width_min_pixels=3, opacity=0.18, pickable=False, **common),
        pdk.Layer("ArcLayer", id="arc-core",  get_width="width",
                  width_min_pixels=1, opacity=0.95, pickable=True,  **common),
    ]


def city_nodes_layer(
    nodes: list[dict],
    *,
    id: str = "city-nodes",
    color: list[int] = style.CITY_NODE_COLOR,
    radius: int = style.CITY_NODE_RADIUS,
) -> pdk.Layer:
    """ScatterplotLayer for destination city glowing dot markers.

    Each node dict must have key ``position`` ([lon, lat]).
    Optional ``label`` key for tooltip use.
    """
    return pdk.Layer(
        "ScatterplotLayer",
        id=id,
        data=nodes,
        get_position="position",
        get_fill_color=color,
        get_radius=radius,
        radius_units="meters",
        pickable=True,
    )
