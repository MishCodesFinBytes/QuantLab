"""Global Contagion Command Center — replays geopolitical shocks on a 3D globe.

Phase 1: data + globe + timeline. Gesture control ships in Phase 2.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from contagion import constants, loader  # noqa: E402
from globe import style as _globe_style   # noqa: E402
from nav import render_sidebar  # noqa: E402
from page_header import render_page_header  # noqa: E402


st.set_page_config(
    page_title="Global Contagion — QuantLabs",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()

# ──────────────────────────────────────────────────────────────
# Page-level animations: staggered fade-in on mount, table pulse
# on re-render. All scoped to this page's containers.
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Page stays on the default light Streamlit theme — only the globe
       iframe is dark (via its own clearColor). Keeping the page light
       means the correlation table / ticker chips / expanders all use
       default text + chrome and feel like the rest of the dashboard;
       only the 3D visualisation is "in space". */

    @keyframes ql-contagion-fade-in {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes ql-contagion-pulse {
        0%   { box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.45); }
        100% { box-shadow: 0 0 0 12px rgba(217, 119, 6, 0); }
    }
    /* Stagger the top-level elements on first paint. nth-of-type is
       brittle against Streamlit layout changes but good enough here —
       the animation is cosmetic, a stale selector just means no fade. */
    [data-testid="stMain"] [data-testid="element-container"] {
        animation: ql-contagion-fade-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(1)  { animation-delay: 0.00s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(2)  { animation-delay: 0.06s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(3)  { animation-delay: 0.12s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(4)  { animation-delay: 0.18s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(5)  { animation-delay: 0.24s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(6)  { animation-delay: 0.30s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(7)  { animation-delay: 0.36s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(8)  { animation-delay: 0.42s; }
    [data-testid="stMain"] [data-testid="element-container"]:nth-of-type(n+9) { animation-delay: 0.48s; }

    /* Every time the correlation table re-renders (slider moves, period
       toggles), a brief amber pulse radiates from it — tells the eye
       "this just updated". */
    [data-testid="stMain"] [data-testid="stDataFrame"] {
        animation: ql-contagion-pulse 0.6s ease-out;
        border-radius: 4px;
    }

    /* Hand-rolled correlation table (replaces st.dataframe on this page
       so the RAG cell backgrounds always render). Each row gets a very
       brief brightness flash on every re-render — when the slider
       advances, the eye sees the five rows pulse, which sells the
       "values just updated" moment without being noisy. */
    @keyframes ql-corr-flash {
        0%   { filter: brightness(1.35); }
        100% { filter: brightness(1); }
    }
    .ql-corr-table .ql-corr-cell {
        animation: ql-corr-flash 0.45s ease-out;
        transition: background 0.3s ease;
    }

    /* Sparkline ticker values get the same flash so the value text
       visibly updates alongside the daily-price dot animating along
       the sparkline. */
    @keyframes ql-ticker-flash {
        0%   { filter: brightness(1.4); }
        100% { filter: brightness(1); }
    }
    .ql-ticker-row .ql-ticker-value {
        animation: ql-ticker-flash 0.4s ease-out;
    }

    /* Category chip beside each ticker label — "Energy" / "Safe haven"
       / "Fear". Soft light pill: labels the row without competing
       with the RAG-coloured value/arrow. */
    .ql-ticker-chip {
        display: inline-block;
        font-size: 0.68em;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 1px 7px;
        margin-left: 4px;
        border-radius: 8px;
        background: #f1f5f9;
        color: #64748b;
        vertical-align: 2px;
    }

    /* Sparklines are now inline SVG inside st.markdown (not altair) —
       the heartbeat pulse runs via an <animate> tag embedded in each
       SVG. No CSS targeting vega-embed elements needed. */

    /* Progress indicator under the timeline — thin greyscale bar so
       it clearly reads as "indicator", not a second slider. */
    .ql-contagion-progress-wrap {
        height: 2px;
        background: #ececec;
        border-radius: 1px;
        margin: 0.2rem 0 0.5rem;
        overflow: hidden;
    }
    .ql-contagion-progress-bar {
        height: 100%;
        background: #9ca3af;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Event-day markers — thin track below the progress bar with a dot
       per historical flashpoint. Dots have a hover-expand + tooltip. */
    .ql-contagion-events-track {
        position: relative;
        height: 18px;
        margin: 0 0 0.6rem;
        padding: 0 2px;
    }
    .ql-contagion-event-dot {
        position: absolute;
        top: 4px;
        width: 10px;
        height: 10px;
        margin-left: -5px;
        background: #991b1b;
        border: 2px solid #fff;
        border-radius: 50%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
        cursor: default;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ql-contagion-event-dot:hover {
        transform: scale(1.5);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        z-index: 10;
    }
    .ql-contagion-event-dot::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 140%;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
        background: #1a1a1a;
        color: #fff;
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.03em;
        padding: 3px 8px;
        border-radius: 3px;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease;
    }
    .ql-contagion-event-dot:hover::after {
        opacity: 1;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
render_page_header(
    "Global Contagion Command Center",
    "Visualising geopolitical-risk contagion on a 3D globe",
)


# ──────────────────────────────────────────────────────────────
# Project intro — what this is, what it tracks, how to read it
# ──────────────────────────────────────────────────────────────
with st.expander("ℹ️ About this project — what it shows & which tickers", expanded=False):
    st.markdown(
        """
        ### What this is

        A replay tool for two geopolitical episodes that rattled global markets:
        the **January 2020 US–Iran escalation** and the **2024–2026 Strait of
        Hormuz tensions**. For each episode we fetch daily prices for a curated
        set of tickers, compute a rolling correlation between a Middle-East
        "risk index" and major world markets, and draw those correlations as
        arcs on a 3D globe so you can *see* which markets caught contagion and
        which held up.

        Drag the slider (or press **▶ Play**) to watch the correlation field
        evolve day by day. Red arcs mean a market started moving *with* the
        Middle East (contagion); green arcs mean it moved *against* (classic
        flight-to-safety behaviour); gray means no relationship.

        ### Tickers considered

        | Role | Ticker(s) | Rationale |
        |---|---|---|
        | **Epicenter — Middle East risk** | `EIS`, `KSA`, `UAE` (iShares MSCI ETFs) | Bond-yield series for Israel / Saudi Arabia / UAE are not cleanly available via free data; sovereign-equity ETFs proxy the same risk premium. Their daily mean forms the **Middle East Risk Index**. |
        | **Contagion — energy-dependent economies** | `FRED:INDIRLTLT01STM` (India 10Y), `TUR` ETF (Turkey — FRED yield series discontinued), `FRED:IRLTLT01DEM156N` (Germany 10Y) | Large net importers whose sovereign risk tends to rise when oil supply is threatened. |
        | **Safe havens** | `^TNX` (US 10Y Treasury yield), `GC=F` (Gold futures) | Canonical crisis hedges — yields fall / gold rises when capital flees risk. |
        | **Energy link** | `BZ=F` (Brent Crude front month), `BDRY` ETF (Baltic Dry shipping proxy) | Direct transmission mechanism from Middle East supply shocks to global inflation / logistics. |
        | **Fear gauge** | `^VIX` | S&P 500 implied volatility — the market's thermometer for stress episodes. |

        Data fetched via `yfinance` and public FRED CSV endpoints, snapshotted
        into a committed parquet (`dashboard/data/contagion/events.parquet`)
        so the page has zero network dependencies at run time. Regenerate with
        `python scripts/fetch_contagion_data.py`.

        ### What's next

        **Phase 2** (designed, not yet shipped): hand-gesture control via
        `mediapipe` + `streamlit-webrtc` — pinch-zoom the globe, wave-rotate,
        two-finger-scrub the timeline. See
        `docs/superpowers/specs/2026-04-17-global-contagion-phase2-design.md`.
        """
    )


@st.cache_data(ttl=60 * 60 * 24)
def _load(period: str) -> pd.DataFrame:
    return loader.load_events(period=period)


# ──────────────────────────────────────────────────────────────
# Period toggle
# ──────────────────────────────────────────────────────────────
period_labels = {k: v["label"] for k, v in constants.PERIODS.items()}
period_key = st.radio(
    "Conflict period",
    options=list(period_labels.keys()),
    format_func=lambda k: period_labels[k],
    horizontal=True,
)

events = _load(period_key)

# ──────────────────────────────────────────────────────────────
# Key event flashpoints per period — used to draw markers on the
# timeline track so the slider isn't a mystery.
# ──────────────────────────────────────────────────────────────
_KEY_EVENTS: dict[str, list[tuple[date, str]]] = {
    "2020_us_iran": [
        (date(2020, 1,  3), "Soleimani strike"),
        (date(2020, 1,  8), "Iranian missile response"),
    ],
    "2024_hormuz": [
        (date(2024, 1, 11), "US/UK strike Houthis"),
        (date(2024, 4, 13), "Iran direct strike on Israel"),
        (date(2024, 7, 31), "Haniyeh assassination"),
        (date(2024, 9, 17), "Pager attacks"),
        (date(2024, 10, 1), "Iran ballistic missile attack"),
        (date(2025, 6, 13), "Israel strikes Iran nuclear sites"),
        (date(2025, 6, 22), "US strikes Iran nuclear sites"),
    ],
}


# ──────────────────────────────────────────────────────────────
# Timeline slider + play button + progress bar + event markers
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

# Session state for playback + current cursor.
if "contagion_date_idx" not in st.session_state:
    st.session_state.contagion_date_idx = len(dates) - 1
if "contagion_playing" not in st.session_state:
    st.session_state.contagion_playing = False
if "contagion_auto_rotate" not in st.session_state:
    st.session_state.contagion_auto_rotate = False
if "contagion_globe_bearing" not in st.session_state:
    st.session_state.contagion_globe_bearing = 0.0

# Clamp the cursor to the current period's range (period toggle may
# have shrunk `dates`).
if st.session_state.contagion_date_idx >= len(dates):
    st.session_state.contagion_date_idx = len(dates) - 1

col_slider, col_btn, col_rotate = st.columns([5, 1, 2])
with col_slider:
    idx = st.slider(
        "Date",
        min_value=0,
        max_value=len(dates) - 1,
        value=st.session_state.contagion_date_idx,
        format="%d",
        label_visibility="collapsed",
    )
    st.session_state.contagion_date_idx = idx
with col_btn:
    btn_label = "⏸ Pause" if st.session_state.contagion_playing else "▶ Play"
    if st.button(btn_label, use_container_width=True):
        st.session_state.contagion_playing = not st.session_state.contagion_playing
        st.rerun()
with col_rotate:
    st.session_state.contagion_auto_rotate = st.checkbox(
        "🌀 Auto-rotate",
        value=st.session_state.contagion_auto_rotate,
        help="Slowly spin the globe when Play is off.",
    )

# Progress bar showing how far through the period we are.
_progress_pct = (
    (st.session_state.contagion_date_idx / max(1, len(dates) - 1)) * 100
)
st.markdown(
    f'<div class="ql-contagion-progress-wrap">'
    f'<div class="ql-contagion-progress-bar" style="width:{_progress_pct:.1f}%"></div>'
    f'</div>',
    unsafe_allow_html=True,
)

# Event markers: draw each flashpoint as a dot at its proportional
# position along the timeline, with a hover tooltip.
_period_events = _KEY_EVENTS.get(period_key, [])
if _period_events and dates:
    _start, _end = dates[0], dates[-1]
    _span_days = max(1, (_end - _start).days)
    _dots_html = ""
    for ev_date, ev_label in _period_events:
        if not (_start <= ev_date <= _end):
            continue
        pct = ((ev_date - _start).days / _span_days) * 100
        _dots_html += (
            f'<div class="ql-contagion-event-dot" '
            f'style="left:{pct:.2f}%" '
            f'data-tooltip="{ev_date.isoformat()} · {ev_label}"></div>'
        )
    if _dots_html:
        st.markdown(
            f'<div class="ql-contagion-events-track">{_dots_html}</div>',
            unsafe_allow_html=True,
        )

selected_date = dates[st.session_state.contagion_date_idx]
st.caption(f"Showing snapshot at **{selected_date}**")

# Month-year badge moved from under the slider into the correlation
# column below — it sits next to the table so the numbers have a
# visible date anchor. See `with col_right:` block.
_month_year = selected_date.strftime("%B %Y") if hasattr(selected_date, "strftime") else str(selected_date)

# Auto-advance while playing — overrides auto-rotate.
# Cadence tuned for smooth perceived motion without outrunning
# Streamlit's rerun pipeline: advance 2 days per frame + 0.2s sleep.
# Earlier 1-day / 0.35s meant a slow page rebuild (pydeck + 4 altair
# charts) sometimes outlasted the sleep, producing jagged, half-
# repainted frames; 2-day steps mean fewer total reruns across the
# timeline, giving Streamlit time to fully repaint each frame.
# Playback state advance moved to the *bottom* of the script — see the
# "Playback tick" block at the end of the file. If st.rerun() fires
# here, the script halts immediately and nothing below this line
# renders, so during Play the globe / correlation table / sparklines
# never got a chance to redraw — which is why tickers appeared to
# update only 2-3 times across a full Play.

# ──────────────────────────────────────────────────────────────
# Globe — pydeck ArcLayer on GlobeView
# ──────────────────────────────────────────────────────────────
import pydeck as pdk  # noqa: E402

from contagion import correlations, globe  # noqa: E402


def _correlations_for_date(events: pd.DataFrame, target_date) -> dict:
    """For each destination country, compute rolling-corr(ME index, country_yield)
    and return the value at `target_date`.

    Two correlation regimes, chosen per-ticker:

    * **Daily tickers** (`TUR`, `^TNX`) use the standard 7-day rolling
      window on daily data.
    * **FRED monthly tickers** (India, Germany 10Y yields) use a 3-month
      rolling window on monthly data. Forward-filling them onto the daily
      calendar and applying the 7-day window produced zero-variance
      stretches and ±inf correlations — monthly-cadence is the honest
      match for monthly data. Values update once per month, not daily,
      but at least they're real numbers.
    """
    me_idx = correlations.middle_east_index(events)
    out: dict = {}
    for country, meta in constants.DESTINATION_CITIES.items():
        ticker = meta["ticker"]
        country_series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if country_series.empty:
            out[country] = 0.0
            continue
        # FRED monthly tickers get a 3-month window; daily tickers the
        # standard 7-day.
        window = 3 if ticker.startswith("FRED:") else constants.CORRELATION_WINDOW
        aligned = pd.concat([me_idx, country_series], axis=1, join="inner").dropna()
        if len(aligned) < window:
            out[country] = 0.0
            continue
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1], window=window
        )
        # Drop NaN + any ±inf that would come from constant-variance
        # windows (defensive — with the window-per-ticker split above,
        # we shouldn't hit inf in practice)
        corr = corr.replace([float("inf"), float("-inf")], float("nan")).dropna()
        td = pd.Timestamp(target_date).date()
        mask = corr.index <= td
        out[country] = float(corr[mask].iloc[-1]) if mask.any() else 0.0
    return out


corr_by_country = _correlations_for_date(events, selected_date)
arc_rows = globe.build_arc_rows(corr_by_country)

# pydeck GlobeView with map_provider=None renders only layers we explicitly
# add. Without a basemap we'd see arcs floating in empty 3D space, so put a
# country-outline GeoJsonLayer behind the arcs. The Natural Earth dataset
# is bundled locally (assets/geojson/world_countries.geojson) rather than
# fetched from a CDN — the deck.gl renderer cannot gracefully recover
# when the remote CDN returns HTML instead of GeoJSON, which was breaking
# the globe on Streamlit Cloud.
import json as _json

_COUNTRIES_GEOJSON_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets" / "geojson" / "world_countries.geojson"
)


@st.cache_data
def _load_countries_geojson() -> dict:
    with _COUNTRIES_GEOJSON_PATH.open(encoding="utf-8") as f:
        return _json.load(f)


# Group-specific ISO-A2 codes for colouring. Everything else stays neutral.
_EPICENTER_ISO = {"IL", "SA", "AE", "IR"}          # crisis red
_DESTINATION_ISO = {"IN", "TR", "DE", "US", "GB"}  # amber — the arc destinations


@st.cache_data
def _split_countries_by_role() -> tuple[dict, dict, dict]:
    """Split the world GeoJSON into three FeatureCollections so we can
    apply a different fill colour to each group."""
    src = _load_countries_geojson()
    epicenter: list = []
    destination: list = []
    rest: list = []
    for feat in src.get("features", []):
        iso = feat.get("properties", {}).get("ISO_A2")
        if iso in _EPICENTER_ISO:
            epicenter.append(feat)
        elif iso in _DESTINATION_ISO:
            destination.append(feat)
        else:
            rest.append(feat)
    return (
        {"type": "FeatureCollection", "features": epicenter},
        {"type": "FeatureCollection", "features": destination},
        {"type": "FeatureCollection", "features": rest},
    )


_epicenter_geo, _destination_geo, _rest_geo = _split_countries_by_role()

# Blue tech-globe basemap — all countries not in the epicenter or
# destination groups get a slightly lighter navy fill, no stroke.
# Stroke is intentionally omitted on the world basemap: applying cyan
# borders to ~200 country polygons in GlobeView floods the entire sphere
# with cyan (the border width is not constant in 3D projection). Cyan
# accents are reserved for the five destination countries where they
# read as highlights rather than noise.
rest_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_rest_geo,
    stroked=False,
    filled=True,
    get_fill_color=[30, 50, 90, 200],   # navy land mass against white background
    pickable=False,
)


# Destination countries now glow with their *current* correlation: red
# when the market is moving in lockstep with the Middle East index
# (contagion), green when it's decoupling (safe-haven / hedge), amber
# for moderate signal, slate when there's no relationship. The map
# itself becomes the story — strong correlations = bright saturated
# fill, weak ones fade toward slate so the eye focuses on where the
# effect is.
# Translucent glow fills — alpha is kept low so the night-lights
# texture still reads through the colour, giving a neon/emissive feel
# rather than a solid painted blob. The country stroke (configured on
# the layer, not here) stays bright so the shape is still crisply
# outlined.
def _corr_to_destination_fill(v: float) -> list[int]:
    if v >= 0.5:
        return [180, 70, 70, 80]       # muted rose, more transparent
    if v <= -0.5:
        return [50, 140, 80, 80]       # muted sage, more transparent
    if abs(v) >= 0.2:
        return [200, 140, 40, 60]      # muted amber
    return [71, 85, 105, 50]           # slate, barely-there


_dest_features_enriched: list[dict] = []
for _feat in _destination_geo.get("features", []):
    _iso = _feat.get("properties", {}).get("ISO_A2")
    _corr = corr_by_country.get(_iso, 0.0)
    _dest_features_enriched.append(
        {
            **_feat,
            "properties": {
                **_feat.get("properties", {}),
                "ql_fill": _corr_to_destination_fill(_corr),
            },
        }
    )

destination_layer = pdk.Layer(
    "GeoJsonLayer",
    data={"type": "FeatureCollection", "features": _dest_features_enriched},
    stroked=True,
    filled=True,
    # Accessor expression — each feature carries its own ql_fill rgba
    # baked in by the Python side. Pydeck serialises this with the
    # legitimate "@@=" accessor prefix, which deck.gl will evaluate
    # (unlike the buggy `image` case above).
    get_fill_color="properties.ql_fill",
    # Bright edge glow — the soft fill plus this crisp stroke gives the
    # "neon outline on a dark map" look. Stroke alpha kept high so the
    # polygon edges pop even when the fill itself is near-transparent.
    get_line_color=_globe_style.CONTINENT_STROKE,
    line_width_min_pixels=1.4,
    pickable=False,
)

# Epicenter: translucent red fill — retains the crisis-red signal
# against the blue basemap. Stroke warm-white so it pops against cyan.
epicenter_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_epicenter_geo,
    stroked=True,
    filled=True,
    get_fill_color=[180, 70, 70, 90],
    get_line_color=[255, 160, 160, 200],
    line_width_min_pixels=1.6,
    pickable=False,
)

# Triple-layer neon-glow arc stack. Outer halo is very wide + very
# low-opacity (bloom), middle glow fills the body with a soft haze,
# inner core is a thin bright line. Combined they read like a neon
# beam on the dark globe instead of three painted strokes. Width is
# driven by each arc's correlation magnitude (ql width field) so
# strong signals visibly thicken.
arc_outer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width="width * 8",
    width_min_pixels=6,
    opacity=0.06,
    great_circle=True,
    pickable=False,
)
arc_glow = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width="width * 3",
    width_min_pixels=3,
    opacity=0.18,
    great_circle=True,
    pickable=False,
)
arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width="width",
    width_min_pixels=1,
    opacity=0.95,
    great_circle=True,
    pickable=True,
)

# Glowing cyan dots at each destination city — echoes the digital-globe
# network aesthetic and gives the arc endpoints a visible anchor.
_city_nodes = [
    {"position": list(meta["lonlat"]), "label": meta["label"]}
    for meta in constants.DESTINATION_CITIES.values()
]
city_nodes_layer = pdk.Layer(
    "ScatterplotLayer",
    data=_city_nodes,
    get_position="position",
    get_fill_color=_globe_style.CITY_NODE_COLOR,
    get_radius=_globe_style.CITY_NODE_RADIUS,
    radius_units="meters",
    pickable=False,
)

# zoom=0 gives the classic "full earth as a sphere in space" look on
# pydeck's GlobeView. Higher values flatten the curvature because the
# viewport fills with land before the sphere edge is visible.
# bearing is driven by session_state so the auto-rotate checkbox can
# progressively rotate the globe between reruns.
# pitch=35 gives a "from orbit, looking down" tilt — the sphere reads
# as a 3D body in space rather than a head-on disc. latitude nudged
# up from the epicenter's 26° so Europe/Russia peek above the horizon
# on load and the arcs emerge from the upper-left of the sphere rather
# than straight out of the centre.
view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1] + 8,
    zoom=1.0,
    pitch=35,
    bearing=st.session_state.get("contagion_globe_bearing", 0.0),
)

deck = pdk.Deck(
    layers=[
        rest_layer,         # blue tech-globe basemap (all other countries)
        destination_layer,  # correlation-driven fills over basemap
        epicenter_layer,    # crisis-red over basemap
        arc_outer,
        arc_glow,
        arc_layer,
        city_nodes_layer,   # cyan destination city dots at arc endpoints
    ],
    initial_view_state=view_state,
    # pydeck's canonical class for the 3D globe is `_GlobeView` with a
    # leading underscore (deck.gl internal class name). Without the
    # underscore pydeck silently falls back to MapView (Mercator).
    views=[pdk.View(type="_GlobeView", controller=True)],
    parameters={"clearColor": [1.0, 1.0, 1.0, 1.0]},   # white outside sphere — must be [0,1] floats
    map_provider=None,
    tooltip={"text": "{dest_label}\nCorrelation: {correlation}"},
)

# ──────────────────────────────────────────────────────────────
# Main three-column layout: globe (60%) + correlation table (20%)
# + stacked sparklines (20%). Sparklines live alongside the globe
# so the "mood gauges" frame the viz instead of being buried below.
# ──────────────────────────────────────────────────────────────
# Two-column layout: globe on the left (bigger), right column stacks
# correlation table on top of ticker sparklines. Earlier three-column
# split (globe / table / sparks) ate into the globe's width for
# panels that don't need it.
col_globe, col_right = st.columns([5, 2])

with col_globe:
    # components.html reloads the iframe on every Play rerun. st.pydeck_chart
    # would avoid that but it doesn't honour _GlobeView — it falls back to
    # flat Mercator, losing the 3D sphere entirely. No BitmapLayer means the
    # pydeck 0.9.1 "@@=" image-prop bug no longer applies here.
    _deck_html = deck.to_html(as_string=True, notebook_display=False)
    components.html(_deck_html, height=980, scrolling=False)

with col_right:
    # Big month-year anchor above the correlation numbers — gives the
    # table a visible date header so the eye knows which moment of the
    # conflict it's reading.
    st.markdown(
        f'<div style="font-family:Georgia, serif;font-size:1.9rem;'
        f'font-weight:600;letter-spacing:-0.01em;margin:0 0 8px;'
        f'color:#1f2937">{_month_year}</div>',
        unsafe_allow_html=True,
    )
    st.caption("7-day corr vs ME index")

    # RAG colour rules — same semantics as the arc colour ramp on the globe
    # so the table and the globe agree at a glance:
    #   strong positive corr (≥ +0.5) = contagion           → red
    #   strong negative corr (≤ -0.5) = decoupling / hedge  → green
    #   weak / ambiguous (|corr| 0.2 – 0.5)                 → amber
    #   noise (|corr| < 0.2)                                → neutral grey
    #
    # Rendered as hand-rolled HTML because pandas Styler passed to
    # st.dataframe drops the cell background on some Streamlit Cloud
    # pandas/streamlit combos — the hand-rolled version is guaranteed
    # to render since it's just markdown HTML.
    # Light-theme RAG palette: tint-100 backgrounds with tint-800 text.
    # Clean on the default white page and still clearly signals the same
    # red/green/amber/slate categories as the arcs on the globe.
    def _rag_corr_style(v: float) -> str:
        if pd.isna(v):
            return "background:#f1f5f9;color:#475569;"
        if v >= 0.5:
            return "background:#fee2e2;color:#991b1b;"
        if v <= -0.5:
            return "background:#dcfce7;color:#166534;"
        if abs(v) >= 0.2:
            return "background:#fef3c7;color:#92400e;"
        return "background:#f1f5f9;color:#475569;"

    _rows_html = "".join(
        f"<tr class='ql-corr-row'>"
        f"<td style='padding:6px 8px'>{constants.DESTINATION_CITIES[c]['country']}</td>"
        f"<td class='ql-corr-cell' style='padding:6px 10px;text-align:right;"
        f"font-family:ui-monospace,monospace;font-weight:600;border-radius:4px;"
        f"{_rag_corr_style(v)}'>{v:+.3f}</td>"
        f"</tr>"
        for c, v in corr_by_country.items()
    )
    _table_html = (
        "<table class='ql-corr-table' style='width:100%;border-collapse:separate;"
        "border-spacing:0 4px;font-size:0.88rem'>"
        "<thead><tr>"
        "<th style='padding:4px 8px;text-align:left;font-weight:500;"
        "color:#6b7280;border-bottom:1px solid #e5e7eb'>Country</th>"
        "<th style='padding:4px 8px;text-align:right;font-weight:500;"
        "color:#6b7280;border-bottom:1px solid #e5e7eb'>Correlation</th>"
        "</tr></thead>"
        f"<tbody>{_rows_html}</tbody>"
        "</table>"
    )
    st.markdown(_table_html, unsafe_allow_html=True)

def _ticker_sparkline_svg(
    full_series: pd.Series,
    trail_series: pd.Series,
    colour: str,
    height: int = 66,
) -> str:
    """Inline SVG sparkline — faded full-period line + solid trail to
    the selected date + a heartbeat-pulsing cursor dot.

    Rendered as raw SVG inside st.markdown (not altair) because
    Streamlit throttles updates to vega-embed components during rapid
    st.rerun() loops, which meant the altair version visibly updated
    only 2-3 times over a full Play. Plain markdown HTML is part of
    the base render path and refreshes every frame. The <animate> tag
    drives the heartbeat directly inside the SVG — no CSS keyframe
    targeting vega-generated DOM needed.
    """
    if len(full_series) < 2 or len(trail_series) < 1:
        return ""
    values = full_series.values.astype(float)
    vmin, vmax = float(values.min()), float(values.max())
    span = (vmax - vmin) or 1.0
    W = 240
    pad = 5
    usable_h = height - 2 * pad
    xs = np.linspace(0, W, len(values))
    ys = pad + (1.0 - (values - vmin) / span) * usable_h
    pts_full = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))

    tv = trail_series.values.astype(float)
    tx = xs[: len(tv)]
    ty = pad + (1.0 - (tv - vmin) / span) * usable_h
    pts_trail = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(tx, ty))

    return (
        f'<svg viewBox="0 0 {W} {height}" preserveAspectRatio="none" '
        f'style="width:100%;height:{height}px;display:block;overflow:visible">'
        f'<polyline points="{pts_full}" fill="none" stroke="{colour}" '
        f'stroke-width="1" opacity="0.22" vector-effect="non-scaling-stroke"/>'
        f'<polyline points="{pts_trail}" fill="none" stroke="{colour}" '
        f'stroke-width="1.8" opacity="1" vector-effect="non-scaling-stroke"/>'
        f'<circle cx="{tx[-1]:.1f}" cy="{ty[-1]:.1f}" r="4.5" fill="{colour}" '
        f'stroke="#f8fafc" stroke-width="1.3" vector-effect="non-scaling-stroke">'
        f'<animate attributeName="opacity" '
        f'values="1;0.35;1;0.55;1" dur="1.4s" repeatCount="indefinite"/>'
        f'</circle>'
        f'</svg>'
    )


# Tickers live in the SAME right-hand column as the correlation table,
# stacked below it with a thin separator so the eye reads "correlations
# first, then the underlying stress signals."  `with col_right:` is
# reopened here — Streamlit concatenates content from repeat `with`
# calls on the same column.
with col_right:
    st.markdown(
        "<div style='height:1px;background:rgba(148,163,184,0.2);"
        "margin:12px 0 10px'></div>",
        unsafe_allow_html=True,
    )
    st.caption("Market stress signals")
    # polarity: "up_is_bad" means a rising value signals market stress
    # (energy spike, shipping stress, fear) → colour red on rise, green
    # on fall. Gold inverts: a rising gold price during crisis is the
    # safe-haven bid working → colour green on rise.
    # Category tag appears as a small chip beside each ticker label so
    # the "Energy · Safe haven · Fear" grouping is clear per-row
    # instead of being a single header that didn't line up with any
    # specific ticker.
    # Fifth field is the hover-tooltip text — shows the instrument's
    # full identifier. Futures (BZ=F, GC=F) and the VIX index don't
    # have an ISIN (ISINs only exist for equities/ETFs/bonds), so we
    # show the exchange + yfinance symbol instead. BDRY is an ETF so
    # it gets a real ISIN.
    _panel_tickers = [
        ("BZ=F", "Brent Crude",      "Energy",     "up_is_bad",  "ICE Brent front-month future · yfinance BZ=F"),
        ("BDRY", "Baltic Dry (ETF)", "Energy",     "up_is_bad",  "Breakwave Dry Bulk Shipping ETF · ISIN US10965F1012"),
        ("GC=F", "Gold",             "Safe haven", "up_is_good", "COMEX gold front-month future · yfinance GC=F"),
        ("^VIX", "VIX",              "Fear",       "up_is_bad",  "CBOE Volatility Index · ^VIX"),
    ]

    def _rag_ticker(pct: float, polarity: str) -> str:
        """RAG colour for a ticker's % change from period start.

        Amber band is ±2% — below that the move is noise, not a signal.
        Above, a 'bad' direction (given polarity) goes red; a 'good'
        direction goes green.

        Palette is the tint-700 cousin of the globe arc ramp
        (#b91c1c / #15803d / #b45309) rather than the saturated arc
        hexes. Arcs live on the dark globe iframe where the saturated
        hexes read as soft glow, but the ticker text + sparkline trail
        sit on the white page where the same hexes read as neon and
        hurt the eye. Same colour family, tone adjusted per context.
        """
        red, green, amber = "#b91c1c", "#15803d", "#b45309"
        if abs(pct) < 2:
            return amber
        rising = pct > 0
        if polarity == "up_is_bad":
            return red if rising else green
        return green if rising else red
    # Coerce selected_date to pd.Timestamp and make the index a
    # DatetimeIndex before slicing — this removes the Python-date vs
    # pandas-Timestamp mismatch that was producing empty filtered
    # series (visible in DevTools as "WARN Infinite extent for field
    # date" coming from the vega-lite sparkline embedder).
    _sel_ts = pd.Timestamp(selected_date)
    for ticker, label, category, polarity, tooltip in _panel_tickers:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if series.empty:
            st.markdown(f"**{label}** — *no data*")
            continue
        series.index = pd.to_datetime(series.index)
        # Drop NaN before passing to line_chart — a series that filters
        # down to all-NaN (or that has leading/trailing NaNs from a parquet
        # with ragged ticker calendars) makes vega-lite log
        # "WARN Infinite extent for field 'date'/'close'" because the
        # domain ends up [Infinity, -Infinity]. dropna keeps the domain
        # finite even when a ticker has sparse coverage.
        series_full = series.dropna()
        series = series[series.index <= _sel_ts].dropna()
        if series.empty:
            st.markdown(f"**{label}** — *no data before this date*")
            continue
        _start_val = float(series.iloc[0])
        _end_val = float(series.iloc[-1])
        _pct = ((_end_val - _start_val) / _start_val * 100) if _start_val else 0.0
        _colour = _rag_ticker(_pct, polarity)
        # Direction arrow mirrors the sign of the cumulative change:
        # ↑ on rising, ↓ on falling, · on flat. The arrow colour matches
        # the RAG polarity so rising Brent = red ↑, rising Gold = green ↑.
        _arrow = "↑" if _pct > 0.1 else ("↓" if _pct < -0.1 else "·")
        # Single <div> instead of mixing markdown bold with HTML spans —
        # Streamlit's markdown renderer was occasionally swallowing the
        # trailing pct span when the line started with **bold**. The
        # ql-ticker-value class gets a brief opacity pulse each re-render
        # so the values visibly flash when the slider advances.
        # title= on the row shows the instrument's identifier + data
        # source as a native browser tooltip on hover — ISIN for the
        # ETF, exchange + yfinance symbol for futures and indices.
        st.markdown(
            f"<div class='ql-ticker-row' title=\"{tooltip}\">"
            f"<strong>{label}</strong> "
            f"<span class='ql-ticker-chip'>{category}</span> &nbsp;"
            f"<span class='ql-ticker-value' "
            f"style='color:{_colour};font-family:ui-monospace,monospace;"
            f"font-weight:600'>{_end_val:.2f}</span>"
            f"&nbsp;&nbsp;"
            f"<span style='color:{_colour};font-size:0.82em;font-weight:600'>"
            f"{_arrow} {_pct:+.1f}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Inline SVG sparkline — faded full-period line + solid trail
        # + pulsing cursor dot. We ditched altair here because during
        # rapid st.rerun() loops Streamlit throttles updates to
        # vega-embed components, so the altair sparklines only visibly
        # updated 2-3 times across a full Play. Plain markdown HTML is
        # part of the base render path and refreshes every frame with
        # no component reconciliation step. The <animate> tag inside
        # the SVG drives the heartbeat directly — no CSS keyframe
        # targeting vega-generated nodes.
        st.markdown(
            _ticker_sparkline_svg(series_full, series, _colour),
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────
# Methodology + safe haven write-up (collapsible)
# ──────────────────────────────────────────────────────────────
def _safe_haven_summary(events: pd.DataFrame) -> str:
    """Compute a short narrative on how the safe havens moved during the
    selected period. Returns markdown text."""
    me_idx = correlations.middle_east_index(events)

    def _window_corr(ticker: str) -> float | None:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if series.empty:
            return None
        aligned = pd.concat([me_idx, series], axis=1, join="inner").dropna()
        if len(aligned) < constants.CORRELATION_WINDOW:
            return None
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1],
            window=constants.CORRELATION_WINDOW,
        )
        return float(corr.dropna().mean()) if not corr.dropna().empty else None

    def _range_change(ticker: str) -> tuple[float, float] | None:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if series.empty:
            return None
        return float(series.iloc[0]), float(series.iloc[-1])

    lines: list[str] = []
    for ticker, label in (("^TNX", "US 10Y Treasury yield"), ("GC=F", "Gold")):
        corr = _window_corr(ticker)
        rng = _range_change(ticker)
        if corr is None or rng is None:
            continue
        start, end = rng
        pct = ((end - start) / start * 100) if start else 0.0
        direction = "rose" if pct > 0 else "fell"
        interpret = (
            "tracked the Middle East index closely — limited safe-haven premium"
            if corr > 0.3
            else (
                "decoupled from the Middle East index — classic flight-to-safety signature"
                if corr < -0.3
                else "moved roughly independently of the Middle East index"
            )
        )
        lines.append(
            f"- **{label}** {direction} **{abs(pct):.1f}%** across the window "
            f"(avg 7-day corr to ME index: `{corr:+.2f}`) — {interpret}."
        )
    return "\n".join(lines) if lines else "_No safe-haven data for this period._"


with st.expander(
    "📘 How this works — correlation, safe havens, and how they responded",
    expanded=False,
):
    st.markdown(
        """
        #### How correlation is calculated

        Every ticker in the snapshot has a daily closing series for the selected
        period. The **Middle East Risk Index** is the simple mean of the three
        regional proxies (`EIS`, `KSA`, `UAE` ETF closes).

        For each destination country (Mumbai, Istanbul, Frankfurt, New York, London)
        we compute a **7-day rolling Pearson correlation** between the ME index
        and that country's 10-year yield (or ETF proxy where the yield series
        isn't publicly available). The timeline slider picks a date; the globe's
        arcs colour to the correlation value on that day.

        Reading the colours:
        - 🔴 **Red (+1)** — markets moved in lockstep with the Middle East: **strong contagion**.
        - ⚪ **Gray (0)** — no statistical relationship: markets decoupled or noise-dominated.
        - 🟢 **Green (−1)** — markets moved *against* the Middle East: **flight-to-safety or inverse hedging**.

        #### What counts as a "safe haven"

        Two assets are treated as reference safe havens:
        - **US 10-year Treasury yield (`^TNX`)** — when investors flee risk they buy
          US Treasuries, pushing yields down. A falling `^TNX` during a crisis
          episode is the classic flight-to-safety signature.
        - **Gold (`GC=F`)** — no counterparty risk, uncorrelated with equity cycles,
          tends to rally on geopolitical stress.

        The 🟢 arcs to **New York** and **London** on the globe capture the safe-haven
        hypothesis: when they go green during a Middle East risk spike, capital is
        flowing *away* from ME assets *toward* Treasuries and the GBP financial hub.

        #### Tickers and data sources

        Everything is snapshotted into the committed parquet at
        `dashboard/data/contagion/events.parquet` by the ETL script
        `scripts/fetch_contagion_data.py` — the page does zero network I/O at
        runtime, so these are the sources the snapshot is built from.

        | Role | Ticker | Instrument | Source |
        |---|---|---|---|
        | **Epicenter — ME risk index** | `EIS`  | iShares MSCI Israel ETF         | yfinance |
        | | `KSA`  | iShares MSCI Saudi Arabia ETF   | yfinance |
        | | `UAE`  | iShares MSCI UAE ETF            | yfinance |
        | **Contagion — destination markets** | `FRED:INDIRLTLT01STM` | India 10Y yield (monthly) | FRED CSV API |
        | | `TUR`  | iShares MSCI Turkey ETF (proxy — TR yield series discontinued) | yfinance |
        | | `FRED:IRLTLT01DEM156N` | Germany 10Y yield (monthly) | FRED CSV API |
        | | `^TNX` | CBOE US 10Y Treasury Yield Index   | yfinance |
        | **Safe haven** | `^TNX` | CBOE US 10Y Treasury Yield Index | yfinance |
        | | `GC=F` | COMEX gold front-month future  | yfinance |
        | **Energy link** | `BZ=F` | ICE Brent front-month future | yfinance |
        | | `BDRY` | Breakwave Dry Bulk Shipping ETF (ISIN US10965F1012) | yfinance |
        | **Fear gauge** | `^VIX` | CBOE Volatility Index          | yfinance |

        Correlation window: **7 trading days** for daily tickers, **3 months** for
        the FRED monthly series (mixing monthly data into a daily 7-day window
        produces zero-variance stretches → ±inf correlations, which we defensively
        drop but prefer to avoid at the source).

        #### Why "up" is red for some and green for others

        The RAG colour on each ticker (and the ↑ / ↓ arrow beside it) is
        polarity-aware — rising ≠ always bad. What we're really asking
        per ticker is *"is this move stress-on or stress-off for the
        global risk-on/off regime?"*:

        - 🔴 **Brent Crude (`BZ=F`) up = red.** Rising oil during a Middle East
          episode is the classic transmission channel — it feeds global
          inflation, squeezes energy-importing countries' current accounts,
          and signals a supply-side shock has priced in. Falling Brent back to
          pre-crisis levels = green (stress-off).
        - 🔴 **Baltic Dry (`BDRY`) up = red.** The Baltic Dry Index tracks
          dry-bulk shipping rates; it spikes when vessels are rerouted away
          from conflict chokepoints (Hormuz, Bab-el-Mandeb) or when freight
          insurance/fuel costs rise. A rising reading prices in a logistics
          shock that eventually shows up as CPI.
        - 🟢 **Gold (`GC=F`) up = green.** Gold has no counterparty risk and
          tends to rally when equity/credit investors seek a crisis hedge. A
          rising gold price during a Middle East flashpoint is the safe-haven
          bid working as expected — the hedge is paying. Falling gold during a
          crisis episode would mean the hedge failed, which is the troubling
          signal (hence red).
        - 🔴 **VIX (`^VIX`) up = red.** The S&P 500 implied-volatility index is
          the market's fear thermometer — a rising VIX always means risk
          premium is being repriced upward. Falling VIX = calm returning =
          green.

        Values inside a ±2% band from the period start are shown in **amber**
        regardless of direction — the move is small enough to be noise, not
        signal, so the polarity interpretation doesn't apply yet.

        #### A note on the globe animation

        The globe refreshes on every Play step because Streamlit recreates the
        entire WebGL iframe each rerun — a platform-level constraint of
        `components.html()`. You may see a brief flicker between frames; this
        is expected and not a data issue. The arc colours and correlation table
        are always in sync with the selected date.
        """
    )
    st.markdown("#### How did they respond in this window?")
    st.markdown(_safe_haven_summary(events))


# (Sparklines now live inside the 3-column main layout above — no
# separate bottom row.)


# ──────────────────────────────────────────────────────────────
# Playback tick — MUST be the last thing in the script.
#
# Placing `st.rerun()` here (after everything has rendered) lets each
# frame fully paint: slider, globe iframe, correlation table,
# sparklines, methodology expander. Earlier this block lived near the
# top of the file, which meant during Play the rerun fired before the
# rest of the page rendered — so the globe / table / tickers never
# redrew mid-playback and only "caught up" when Play stopped.
# ──────────────────────────────────────────────────────────────
if st.session_state.contagion_playing:
    import time as _time
    # Calendar-monthly stepping: advance to the first data point on or
    # after the 1st of the next month. Coarser than the previous 2-day
    # stepping, but the whole point is to shrink the number of iframe
    # reloads during Play — jumping month-to-month means the 0.6 s
    # fade-in has time to fully cover each reload, so the globe reads
    # as smooth progressive snapshots instead of a strobe. The large
    # month-year badge in the correlation column is now also the
    # natural unit of playback, so the visual cadence matches.
    _time.sleep(1.0)
    _cur_ts = pd.Timestamp(dates[st.session_state.contagion_date_idx])
    _next_month_start = (_cur_ts + pd.offsets.MonthBegin(1)).date()
    _next_idx = None
    for _i in range(
        st.session_state.contagion_date_idx + 1, len(dates)
    ):
        if pd.Timestamp(dates[_i]).date() >= _next_month_start:
            _next_idx = _i
            break
    if _next_idx is None:
        # No data beyond the current month → stop at the last point.
        st.session_state.contagion_date_idx = len(dates) - 1
        st.session_state.contagion_playing = False
    else:
        st.session_state.contagion_date_idx = _next_idx
    st.rerun()
elif st.session_state.contagion_auto_rotate:
    import time as _time
    _time.sleep(1.2)
    st.session_state.contagion_globe_bearing = (
        (st.session_state.contagion_globe_bearing + 5.0) % 360
    )
    st.rerun()
