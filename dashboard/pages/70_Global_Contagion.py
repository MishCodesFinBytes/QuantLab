"""Global Contagion Command Center — replays geopolitical shocks on a 3D globe.

Phase 1: data + globe + timeline. Gesture control ships in Phase 2.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from contagion import constants, loader  # noqa: E402
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

    /* Soften the per-frame iframe reload of the globe — each rerun
       creates a fresh components.html iframe, which used to snap in
       abruptly. Fade-in over 250ms covers the reload. */
    @keyframes ql-globe-fade-in {
        from { opacity: 0.35; }
        to   { opacity: 1; }
    }
    [data-testid="stMain"] iframe[title="streamlit_app"],
    [data-testid="stMain"] .stIFrame iframe {
        animation: ql-globe-fade-in 0.25s ease-out;
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

# Auto-advance while playing — overrides auto-rotate.
if st.session_state.contagion_playing:
    import time as _time
    _time.sleep(0.35)   # slower default — gives the eye time to register each frame
    if st.session_state.contagion_date_idx < len(dates) - 1:
        st.session_state.contagion_date_idx += 1
    else:
        st.session_state.contagion_playing = False   # stop at the end
    st.rerun()
# Else: auto-rotate globe if the user opted in.
elif st.session_state.contagion_auto_rotate:
    import time as _time
    _time.sleep(1.2)   # slow cadence — 0.83 Hz rerun, battery-friendly
    st.session_state.contagion_globe_bearing = (
        (st.session_state.contagion_globe_bearing + 5.0) % 360
    )
    st.rerun()

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

# Earth surface: 3 country polygon layers.
#
# We tried a BitmapLayer with NASA Black Marble night-lights for a prettier
# "dark earth with glowing cities" look, but pydeck 0.9.1 incorrectly
# prepends "@@=" to the `image` string prop (treating it as an accessor
# expression), which makes deck.gl's JSON converter try to parse the data:
# URL and fail at the first colon ("Unexpected ':' at character 4"). Until
# pydeck's serialiser fixes that or we work around it with HTML surgery,
# we stay on polygon layers. Bonus: the 3-role visual split stays
# (red epicenter / amber destinations / slate rest).
rest_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_rest_geo,
    stroked=False,
    filled=True,
    get_fill_color=[40, 50, 70, 220],
    pickable=False,
)
destination_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_destination_geo,
    stroked=True,
    filled=True,
    get_fill_color=[217, 119, 6, 200],
    get_line_color=[255, 255, 255, 180],
    line_width_min_pixels=1,
    pickable=False,
)
epicenter_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_epicenter_geo,
    stroked=True,
    filled=True,
    get_fill_color=[153, 27, 27, 220],
    get_line_color=[255, 255, 255, 200],
    line_width_min_pixels=1,
    pickable=False,
)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    # Earlier we had `get_width="width"` to drive thickness from
    # correlation magnitude, but something in the Streamlit Cloud
    # iframe silently broke that accessor — arcs disappeared entirely.
    # Reverting to a constant width until we diagnose the accessor
    # issue properly. Arc colour still changes with correlation,
    # so the contagion signal is still visible.
    get_width=5,
    width_min_pixels=2,
    great_circle=True,
    pickable=True,
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
    zoom=0.6,
    pitch=35,
    bearing=st.session_state.get("contagion_globe_bearing", 0.0),
)

deck = pdk.Deck(
    layers=[rest_layer, destination_layer, epicenter_layer, arc_layer],
    initial_view_state=view_state,
    # pydeck's canonical class for the 3D globe is `_GlobeView` with a
    # leading underscore (deck.gl internal class name). Without the
    # underscore pydeck silently falls back to MapView (Mercator),
    # which is why earlier versions rendered as a flat world map.
    views=[pdk.View(type="_GlobeView", controller=True)],
    # Suspect the blanket cull=True was silently removing ArcLayer
    # geometry (and possibly BitmapLayer back faces) — user reports no
    # arcs visible even after reverting get_width to a constant. Dropping
    # cull for now; if back-side bleed-through becomes an issue with the
    # bitmap earth we can solve it per-layer. clearColor black matches
    # the dark night-lights aesthetic.
    parameters={"clearColor": [0, 0, 0, 1]},
    map_provider=None,
    tooltip={"text": "{dest_label}\nCorrelation: {correlation}"},
)

# ──────────────────────────────────────────────────────────────
# Main three-column layout: globe (60%) + correlation table (20%)
# + stacked sparklines (20%). Sparklines live alongside the globe
# so the "mood gauges" frame the viz instead of being buried below.
# ──────────────────────────────────────────────────────────────
col_globe, col_table, col_sparks = st.columns([3, 1, 1])

with col_globe:
    # st.pydeck_chart does NOT forward the views= config to its internal
    # deck.gl renderer — it always uses MapView, silently ignoring
    # _GlobeView. Rendering via deck.to_html() + components.html gives
    # us deck.gl's native JS renderer which honours GlobeView correctly.
    _deck_html = deck.to_html(as_string=True, notebook_display=False)
    components.html(_deck_html, height=720, scrolling=False)

with col_table:
    st.caption("7-day corr vs ME index")
    st.dataframe(
        pd.DataFrame(
            [
                {"Country": constants.DESTINATION_CITIES[c]["label"], "Correlation": round(v, 3)}
                for c, v in corr_by_country.items()
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

with col_sparks:
    st.caption("Energy · Safe haven · Fear")
    _panel_tickers = [
        ("BZ=F", "Brent Crude"),
        ("BDRY", "Baltic Dry (ETF)"),
        ("GC=F", "Gold"),
        ("^VIX", "VIX"),
    ]
    # Coerce selected_date to pd.Timestamp and make the index a
    # DatetimeIndex before slicing — this removes the Python-date vs
    # pandas-Timestamp mismatch that was producing empty filtered
    # series (visible in DevTools as "WARN Infinite extent for field
    # date" coming from the vega-lite sparkline embedder).
    _sel_ts = pd.Timestamp(selected_date)
    for ticker, label in _panel_tickers:
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
        series = series[series.index <= _sel_ts].dropna()
        if series.empty:
            st.markdown(f"**{label}** — *no data before this date*")
            continue
        st.markdown(f"**{label}** &nbsp; `{series.iloc[-1]:.2f}`", unsafe_allow_html=True)
        st.line_chart(series, height=60)


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
        """
    )
    st.markdown("#### How did they respond in this window?")
    st.markdown(_safe_haven_summary(events))


# (Sparklines now live inside the 3-column main layout above — no
# separate bottom row.)
