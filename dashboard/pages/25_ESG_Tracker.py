"""ESG Tracker — compare Environmental, Social, and Governance scores."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data import SAMPLE_ESG_DATA

st.set_page_config(page_title="ESG Tracker", layout="wide")
st.title("ESG Score Tracker")

esg = SAMPLE_ESG_DATA.copy()

# -- Inputs (main area) ------------------------------------------------------
col_in1, col_in2 = st.columns(2)

with col_in1:
    sectors = st.multiselect(
        "Filter by Sector", esg["Sector"].unique().tolist(),
        default=esg["Sector"].unique().tolist(),
    )

filtered = esg[esg["Sector"].isin(sectors)]

with col_in2:
    companies = st.multiselect(
        "Select Companies", filtered["Company"].tolist(),
        default=filtered["Company"].tolist()[:5],
    )

selected = filtered[filtered["Company"].isin(companies)]

st.divider()

if selected.empty:
    st.info("Select at least one company above.")
    st.stop()

# -- Comparison Table ---------------------------------------------------------
with st.expander("ESG Score Comparison"):
    display_cols = ["Company", "Ticker", "Sector", "E_Score", "S_Score", "G_Score", "ESG_Total"]
    st.dataframe(
        selected[display_cols].style.format({"ESG_Total": "{:.1f}"}),
        use_container_width=True,
    )

# -- Charts -------------------------------------------------------------------
categories = ["E_Score", "S_Score", "G_Score"]
labels = ["Environmental", "Social", "Governance"]

tab1, tab2 = st.tabs(["E / S / G Radar Comparison", "Sector Averages"])

with tab1:
    fig_radar = go.Figure()
    for _, row in selected.iterrows():
        values = [row[c] for c in categories] + [row[categories[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=labels + [labels[0]],
            fill="toself",
            name=row["Company"],
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="ESG Radar",
        height=500,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    sector_avg = (
        filtered.groupby("Sector")[categories]
        .mean()
        .reset_index()
        .melt(id_vars="Sector", var_name="Pillar", value_name="Score")
    )
    sector_avg["Pillar"] = sector_avg["Pillar"].map(
        {"E_Score": "Environmental", "S_Score": "Social", "G_Score": "Governance"}
    )

    fig_bar = px.bar(
        sector_avg, x="Sector", y="Score", color="Pillar",
        barmode="group", title="Average E/S/G by Sector",
        color_discrete_sequence=["#2ecc71", "#3498db", "#9b59b6"],
    )
    fig_bar.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_bar, use_container_width=True)
