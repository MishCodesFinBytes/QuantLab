"""Global Contagion Command Center — replays geopolitical shocks on a 3D globe.

Phase 1: data + globe + timeline. Gesture control ships in Phase 2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

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
render_page_header(
    "Global Contagion Command Center",
    "Replay geopolitical shocks across a 3D globe",
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
# Timeline slider + play button
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

# Clamp the cursor to the current period's range (period toggle may
# have shrunk `dates`).
if st.session_state.contagion_date_idx >= len(dates):
    st.session_state.contagion_date_idx = len(dates) - 1

col_slider, col_btn = st.columns([6, 1])
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

selected_date = dates[st.session_state.contagion_date_idx]
st.caption(f"Showing snapshot at **{selected_date}**")

# Auto-advance while playing
if st.session_state.contagion_playing:
    import time as _time
    _time.sleep(0.15)
    if st.session_state.contagion_date_idx < len(dates) - 1:
        st.session_state.contagion_date_idx += 1
    else:
        st.session_state.contagion_playing = False   # stop at the end
    st.rerun()

# ──────────────────────────────────────────────────────────────
# Globe — pydeck ArcLayer on GlobeView
# ──────────────────────────────────────────────────────────────
import pydeck as pdk  # noqa: E402

from contagion import correlations, globe  # noqa: E402


def _correlations_for_date(events: pd.DataFrame, target_date) -> dict:
    """For each destination country, compute rolling-corr(ME index, country_yield)
    and return the value at `target_date`."""
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
        # Align on common dates
        aligned = pd.concat([me_idx, country_series], axis=1, join="inner").dropna()
        if len(aligned) < constants.CORRELATION_WINDOW:
            out[country] = 0.0
            continue
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1],
            window=constants.CORRELATION_WINDOW,
        )
        # Pick the correlation at target_date (or most recent ≤ target_date)
        corr = corr.dropna()
        td = pd.Timestamp(target_date).date()
        mask = corr.index <= td
        out[country] = float(corr[mask].iloc[-1]) if mask.any() else 0.0
    return out


corr_by_country = _correlations_for_date(events, selected_date)
arc_rows = globe.build_arc_rows(corr_by_country)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width=3,
    great_circle=True,
    pickable=True,
)

view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=1.5,
    pitch=0,
    bearing=0,
)

deck = pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    views=[pdk.View(type="GlobeView", controller=True)],
    map_provider=None,   # GlobeView does not use map tiles
    tooltip={"text": "{dest_label}\nCorrelation: {correlation}"},
)

st.pydeck_chart(deck, use_container_width=True)

# Correlation read-out table under the globe
st.caption("Rolling 7-day correlation vs Middle East Risk Index")
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

# ──────────────────────────────────────────────────────────────
# Side panel: Brent / Baltic / Gold / VIX sparklines
# ──────────────────────────────────────────────────────────────
st.markdown("### Energy, Safe Haven & Fear")

panel_tickers = [
    ("BZ=F", "Brent Crude"),
    ("BDRY", "Baltic Dry (ETF)"),
    ("GC=F", "Gold"),
    ("^VIX", "VIX"),
]
cols = st.columns(4)
for (ticker, label), col in zip(panel_tickers, cols):
    with col:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        st.markdown(f"**{label}**")
        if series.empty:
            st.caption("no data")
            continue
        # Truncate to dates ≤ selected_date so the sparkline "plays along"
        series = series[series.index <= selected_date]
        st.line_chart(series, height=80)
        st.caption(f"Latest: {series.iloc[-1]:.2f}")
