"""Benchmark Rates Dashboard — SONIA, €STR, SOFR comparison and position calculator."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from data import fetch_sonia, fetch_estr, fetch_sofr
from page_init import setup_page
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Benchmark Rates", "SOFR, SONIA, and ESTR — fixed vs floating rate swap value")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **SONIA** (Sterling Overnight Index Average) — Bank of England's unsecured overnight rate for GBP
        - **€STR** (Euro Short-Term Rate) — ECB's replacement for EONIA, unsecured overnight rate for EUR
        - **SOFR** (Secured Overnight Financing Rate) — NY Fed's repo-based overnight rate for USD
        - **Position calculator** computes daily accrued interest by compounding the overnight rate in arrears
        - For the full theory and LIBOR transition story, see the
          [Benchmark Rates post](https://mish-codes.github.io/FinBytes/math-finance/benchmark-rates-libor-transition/)
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Latest Rate:** the most recently published overnight rate
        - **Period Average:** mean rate over the selected date range
        - **High / Low:** highest and lowest rates in the period
        - **Volatility:** standard deviation of daily rate changes
        - **Daily Accrual:** interest earned each day = Notional × rate / 360 (or /365 for SONIA)
        - **Cumulative PnL:** running total of daily accruals, compounded
        """)

    st.divider()

    # ── Position Calculator ──────────────────────────────────────────────
    st.subheader("Position Calculator")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        currency = st.selectbox("Currency", ["GBP (SONIA)", "EUR (€STR)", "USD (SOFR)"])
        notional = st.number_input("Notional", min_value=1_000.0, value=10_000_000.0, step=1_000_000.0)
    with col_b:
        position_type = st.radio("Position", ["Receive floating", "Pay floating"], horizontal=True)
        fixed_rate = st.number_input("Fixed Rate (%)", min_value=0.0, max_value=20.0, value=4.50, step=0.25)
    with col_c:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=90))
        end_date = st.date_input("End Date", value=date.today())

    # Map currency to fetch function and day count
    RATE_MAP = {
        "GBP (SONIA)": ("SONIA", fetch_sonia, 365),
        "EUR (€STR)": ("€STR", fetch_estr, 360),
        "USD (SOFR)": ("SOFR", fetch_sofr, 360),
    }
    rate_name, fetch_fn, day_count = RATE_MAP[currency]

    @st.cache_data(show_spinner=False, ttl=3600)
    def load_rate(name: str, start: str, end: str) -> pd.DataFrame:
        fn = {"SONIA": fetch_sonia, "€STR": fetch_estr, "SOFR": fetch_sofr}[name]
        return fn(start, end)

    with st.spinner(f"Fetching {rate_name} rates..."):
        rate_df = load_rate(rate_name, str(start_date), str(end_date))

    if rate_df.empty:
        st.error(f"No {rate_name} data available for the selected period.")
    else:
        # Build accrual schedule
        df = rate_df.copy()
        df["daily_accrual"] = notional * (df["rate"] / 100) / day_count
        df["fixed_accrual"] = notional * (fixed_rate / 100) / day_count
        if "Receive" in position_type:
            df["net_daily"] = df["daily_accrual"] - df["fixed_accrual"]
        else:
            df["net_daily"] = df["fixed_accrual"] - df["daily_accrual"]
        df["cumulative_pnl"] = df["net_daily"].cumsum()

        sign = "+" if df["cumulative_pnl"].iloc[-1] >= 0 else ""
        ccy_symbol = {"GBP (SONIA)": "£", "EUR (€STR)": "€", "USD (SOFR)": "$"}[currency]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Floating Interest",
                  f"{ccy_symbol}{df['daily_accrual'].sum():,.2f}")
        m2.metric("Total Fixed Interest",
                  f"{ccy_symbol}{df['fixed_accrual'].sum():,.2f}")
        m3.metric("Net PnL",
                  f"{sign}{ccy_symbol}{df['cumulative_pnl'].iloc[-1]:,.2f}")
        m4.metric("Trading Days", len(df))

        fig_pnl = go.Figure()
        fig_pnl.add_trace(go.Scatter(
            x=df["date"], y=df["cumulative_pnl"], mode="lines",
            name="Cumulative PnL", line=dict(color="#636EFA", width=2),
        ))
        fig_pnl.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_pnl.update_layout(
            title=f"Position PnL — {position_type} {rate_name} vs {fixed_rate:.2f}% fixed",
            xaxis_title="Date", yaxis_title=f"PnL ({ccy_symbol})",
            hovermode="x unified", height=350,
        )
        st.plotly_chart(fig_pnl, width='stretch')

        with st.expander("Daily Accrual Schedule"):
            display_df = df[["date", "rate", "daily_accrual", "fixed_accrual", "net_daily", "cumulative_pnl"]].copy()
            display_df.columns = ["Date", f"{rate_name} (%)", "Float Accrual", "Fixed Accrual", "Net Daily", "Cumulative PnL"]
            for col in ["Float Accrual", "Fixed Accrual", "Net Daily", "Cumulative PnL"]:
                display_df[col] = display_df[col].map(lambda x: f"{ccy_symbol}{x:,.2f}")
            st.dataframe(display_df, width='stretch', hide_index=True)

    # ── Rate Comparison ──────────────────────────────────────────────────
    st.divider()
    st.subheader("Rate Comparison")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        rate_choice = st.selectbox("Rate", ["All three", "SONIA", "€STR", "SOFR"])
    with col_r2:
        period = st.selectbox("Period", ["1m", "3m", "6m", "1y", "2y"], index=2)

    period_days = {"1m": 30, "3m": 90, "6m": 180, "1y": 365, "2y": 730}[period]
    comp_start = (date.today() - timedelta(days=period_days)).isoformat()
    comp_end = date.today().isoformat()

    @st.cache_data(show_spinner=False, ttl=3600)
    def load_comparison(choice: str, start: str, end: str) -> dict:
        result = {}
        if choice in ("All three", "SONIA"):
            result["SONIA"] = fetch_sonia(start, end)
        if choice in ("All three", "€STR"):
            result["€STR"] = fetch_estr(start, end)
        if choice in ("All three", "SOFR"):
            result["SOFR"] = fetch_sofr(start, end)
        return result

    with st.spinner("Fetching rates..."):
        rates = load_comparison(rate_choice, comp_start, comp_end)

    if not any(not v.empty for v in rates.values()):
        st.error("No rate data available for the selected period.")
    else:
        # Metrics for each rate
        for name, rdf in rates.items():
            if rdf.empty:
                continue
            cols = st.columns(5)
            cols[0].metric(f"{name} Latest", f"{rdf['rate'].iloc[-1]:.3f}%")
            cols[1].metric("Average", f"{rdf['rate'].mean():.3f}%")
            cols[2].metric("High", f"{rdf['rate'].max():.3f}%")
            cols[3].metric("Low", f"{rdf['rate'].min():.3f}%")
            cols[4].metric("Volatility", f"{rdf['rate'].diff().std():.4f}%")

        # Time series chart
        fig_ts = go.Figure()
        colors = {"SONIA": "#636EFA", "€STR": "#EF553B", "SOFR": "#00CC96"}
        for name, rdf in rates.items():
            if rdf.empty:
                continue
            fig_ts.add_trace(go.Scatter(
                x=rdf["date"], y=rdf["rate"], mode="lines",
                name=name, line=dict(color=colors.get(name, "#636EFA"), width=2),
            ))
        fig_ts.update_layout(
            title="Overnight Benchmark Rates",
            xaxis_title="Date", yaxis_title="Rate (%)",
            hovermode="x unified", height=400,
        )
        st.plotly_chart(fig_ts, width='stretch')

        # Distribution chart
        fig_dist = go.Figure()
        for name, rdf in rates.items():
            if rdf.empty:
                continue
            changes = rdf["rate"].diff().dropna()
            fig_dist.add_trace(go.Histogram(
                x=changes, name=name, opacity=0.7,
                marker_color=colors.get(name, "#636EFA"),
            ))
        fig_dist.update_layout(
            title="Daily Rate Change Distribution",
            xaxis_title="Daily Change (%)", yaxis_title="Count",
            barmode="overlay", height=350,
        )
        st.plotly_chart(fig_dist, width='stretch')

        # Spread chart (only when multiple rates available)
        if len([r for r in rates.values() if not r.empty]) >= 2:
            # Align all rates on a common date index
            aligned = {}
            for name, rdf in rates.items():
                if not rdf.empty:
                    s = rdf.set_index("date")["rate"]
                    s.name = name
                    aligned[name] = s
            merged = pd.DataFrame(aligned).dropna()

            if len(merged) > 0 and len(merged.columns) >= 2:
                fig_spread = go.Figure()
                spread_colors = ["#AB63FA", "#FFA15A", "#19D3F3"]
                names = list(merged.columns)
                ci = 0
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        spread = merged[names[i]] - merged[names[j]]
                        label = f"{names[i]} − {names[j]}"
                        fig_spread.add_trace(go.Scatter(
                            x=merged.index, y=spread, mode="lines",
                            name=label, line=dict(color=spread_colors[ci % len(spread_colors)], width=2),
                        ))
                        ci += 1
                fig_spread.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_spread.update_layout(
                    title="Rate Spreads — Monetary Policy Divergence",
                    xaxis_title="Date", yaxis_title="Spread (%)",
                    hovermode="x unified", height=400,
                )
                st.plotly_chart(fig_spread, width='stretch')

with tab_tests:
    render_test_tab("test_benchmark_rates.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "requests", "Plotly", "Streamlit", "BoE / ECB / NY Fed APIs"])