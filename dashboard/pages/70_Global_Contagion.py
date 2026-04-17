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
# Timeline slider
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

selected_date = st.slider(
    "Date",
    min_value=dates[0],
    max_value=dates[-1],
    value=dates[-1],
    format="YYYY-MM-DD",
)

st.caption(f"Showing snapshot at **{selected_date}**")
