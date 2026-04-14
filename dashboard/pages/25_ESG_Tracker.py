"""ESG Tracker -- compare Environmental, Social, and Governance scores."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import random
import streamlit as st
from tech_footer import render_tech_footer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from nav import render_sidebar
from page_header import render_page_header
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="ESG Tracker", page_icon="assets/logo.png", layout="wide")
render_page_header("ESG Tracker", "ESG score comparison, radar chart, sector averages")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Data source:** attempts to fetch ESG scores from yfinance sustainability data
        - **Fallback:** if real ESG data is unavailable, generates deterministic sample scores for illustration
        - **Three pillars:** Environmental (E), Social (S), and Governance (G), each scored 0-100
        - **ESG Total:** simple average of the three pillar scores
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Radar chart:** overlays each company's E, S, and G scores for easy visual comparison
        - **Sector Averages chart:** grouped bars showing the average E/S/G scores per sector
        - **Score Comparison table:** raw scores for each company with ESG total
        - **Sample data warning:** if shown, scores are illustrative and not from a real ESG provider
        """)

    DEFAULT_TICKERS = "AAPL,MSFT,GOOG,AMZN,TSLA"

    SECTOR_MAP = {
        "Technology": "Tech", "Consumer Cyclical": "Auto",
        "Financial Services": "Finance", "Energy": "Energy",
        "Communication Services": "Tech", "Healthcare": "Healthcare",
        "Industrials": "Industrial", "Consumer Defensive": "Consumer",
        "Basic Materials": "Materials", "Real Estate": "Real Estate",
        "Utilities": "Utilities",
    }


    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_esg_data(tickers: list[str]) -> pd.DataFrame:
        """Fetch ESG scores from yfinance; fall back to random sample scores."""
        rows = []
        warnings = []
        for t in tickers:
            t = t.strip().upper()
            if not t:
                continue
            info = {}
            e_score = s_score = g_score = None
            sector_raw = "Unknown"
            company_name = t
            try:
                yticker = yf.Ticker(t)
                info = yticker.info or {}
                company_name = info.get("shortName", t)
                sector_raw = info.get("sector", "Unknown")
                sust = yticker.sustainability
                if sust is not None and not sust.empty:
                    vals = sust.to_dict()
                    # yfinance sustainability index varies; try common keys
                    if isinstance(vals, dict):
                        first_key = next(iter(vals))
                        inner = vals[first_key] if isinstance(vals[first_key], dict) else vals
                    else:
                        inner = {}
                    e_score = inner.get("environmentScore", inner.get("Environment Score"))
                    s_score = inner.get("socialScore", inner.get("Social Score"))
                    g_score = inner.get("governanceScore", inner.get("Governance Score"))
            except Exception:
                pass

            used_sample = False
            if e_score is None or s_score is None or g_score is None:
                random.seed(hash(t))
                e_score = random.randint(30, 90)
                s_score = random.randint(30, 90)
                g_score = random.randint(30, 90)
                used_sample = True
                warnings.append(t)

            sector = SECTOR_MAP.get(sector_raw, sector_raw)
            rows.append({
                "Company": company_name,
                "Ticker": t,
                "Sector": sector,
                "E_Score": float(e_score),
                "S_Score": float(s_score),
                "G_Score": float(g_score),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df["ESG_Total"] = (df["E_Score"] + df["S_Score"] + df["G_Score"]) / 3
        return df, warnings


    # -- Inputs (main area) -------------------------------------------------------
    ticker_input = st.text_input(
        "Tickers (comma-separated)", value=DEFAULT_TICKERS,
        help="Enter ticker symbols separated by commas.",
    )

    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    if not tickers:
        st.info("Enter at least one ticker above.")
        st.stop()

    with st.spinner("Fetching ESG data..."):
        esg, warn_tickers = fetch_esg_data(tickers)

    if warn_tickers:
        st.warning(
            f"Real ESG data unavailable for: {', '.join(warn_tickers)}. "
            "Showing randomly generated sample scores for those tickers."
        )

    if esg.empty:
        st.error("No data could be loaded.")
        st.stop()

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

    # -- Comparison Table ----------------------------------------------------------
    with st.expander("ESG Score Comparison"):
        display_cols = ["Company", "Ticker", "Sector", "E_Score", "S_Score", "G_Score", "ESG_Total"]
        st.dataframe(
            selected[display_cols].style.format({"ESG_Total": "{:.1f}"}),
            use_container_width=True,
        )

    # -- Charts --------------------------------------------------------------------
    categories = ["E_Score", "S_Score", "G_Score"]
    labels = ["Environmental", "Social", "Governance"]

    chart_tab1, chart_tab2 = st.tabs(["E / S / G Radar Comparison", "Sector Averages"])

    with chart_tab1:
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

    with chart_tab2:
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

with tab_tests:
    render_test_tab("test_esg_tracker.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "Plotly", "Streamlit"])