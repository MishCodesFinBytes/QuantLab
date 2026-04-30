"""Time Series Decomposition -- seasonal decompose and ACF analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf
from page_init import setup_page
from stock_inputs import stock_input_panel
from cached_data import load_stock_data
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Time Series", "Trend, seasonal, and residual decomposition with ACF")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Multiplicative decomposition:** splits price into `Trend * Seasonal * Residual` using statsmodels
        - **Trend:** the long-term direction of the price, smoothed over a 252-day (1-year) window
        - **Seasonal:** repeating patterns at a fixed period (e.g., intra-year cycles)
        - **ACF (Autocorrelation Function):** measures how today's return correlates with returns N days ago
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Observed panel:** the raw closing price series
        - **Trend panel:** the smoothed long-term trajectory -- rising trend = sustained growth
        - **Seasonal panel:** repeating cyclical patterns; values near 1.0 mean no seasonal effect
        - **Residual panel:** leftover noise after removing trend and seasonality -- large residuals indicate unusual moves
        - **ACF bar chart:** bars outside the gray confidence bands indicate statistically significant autocorrelation at that lag
        """)

    # -- Inputs -------------------------------------------------------------------
    ticker, period = stock_input_panel(periods=["6mo", "1y", "2y", "5y"], default_period="2y")

    _stop = False

    if not ticker:
        st.info("Enter a ticker symbol above.")
        _stop = True


    if not _stop:
        st.divider()

        with st.spinner(f"Loading {ticker}..."):
            prices = load_stock_data(ticker, period)["Close"].dropna()

        if prices.empty or len(prices) < 60:
            st.error(f"Need at least 60 trading days. Got {len(prices)} for **{ticker}**.")
            _stop = True

    if not _stop:
        # -- Decompose ----------------------------------------------------------------
        # Use period that fits the data: 252 if enough data, else half the observations
        decomp_period = 252 if len(prices) >= 504 else min(126, len(prices) // 2 - 1)
        try:
            decomp = seasonal_decompose(prices, model="multiplicative", period=decomp_period)
        except ValueError as e:
            st.error(f"Decomposition failed: {e}")
            _stop = True

    if not _stop:

        tab1, tab2 = st.tabs(["Decomposition", "Autocorrelation (ACF)"])

        with tab1:
            fig = make_subplots(
                rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                subplot_titles=["Observed", "Trend", "Seasonal", "Residual"],
                row_heights=[0.3, 0.3, 0.2, 0.2],
            )

            fig.add_trace(go.Scatter(x=prices.index, y=decomp.observed, name="Observed",
                                     line=dict(color="#1f77b4")), row=1, col=1)
            fig.add_trace(go.Scatter(x=prices.index, y=decomp.trend, name="Trend",
                                     line=dict(color="orange")), row=2, col=1)
            fig.add_trace(go.Scatter(x=prices.index, y=decomp.seasonal, name="Seasonal",
                                     line=dict(color="green")), row=3, col=1)
            fig.add_trace(go.Scatter(x=prices.index, y=decomp.resid, name="Residual",
                                     mode="markers", marker=dict(size=3, color="red")), row=4, col=1)

            fig.update_layout(height=700, margin=dict(t=60, b=30), showlegend=False,
                              title=f"{ticker} Multiplicative Decomposition (period={decomp_period})")
            st.plotly_chart(fig, width='stretch')

        with tab2:
            returns = prices.pct_change().dropna()
            nlags = min(60, len(returns) // 2 - 1)
            acf_vals, confint = acf(returns, nlags=nlags, alpha=0.05)
            lags = np.arange(nlags + 1)
            ci_lower = confint[:, 0] - acf_vals
            ci_upper = confint[:, 1] - acf_vals

            acf_fig = go.Figure()
            acf_fig.add_trace(go.Bar(x=lags, y=acf_vals, name="ACF",
                                     marker_color="steelblue", width=0.4))
            acf_fig.add_trace(go.Scatter(x=lags, y=ci_upper, mode="lines",
                                         line=dict(dash="dash", color="gray"), name="95% CI"))
            acf_fig.add_trace(go.Scatter(x=lags, y=ci_lower, mode="lines",
                                         line=dict(dash="dash", color="gray"), showlegend=False))
            acf_fig.update_layout(
                title=f"{ticker} ACF of Daily Returns",
                xaxis_title="Lag", yaxis_title="Autocorrelation",
                height=400, margin=dict(t=60, b=40),
            )
            st.plotly_chart(acf_fig, width='stretch')

        st.caption(
            "Multiplicative decomposition separates price into trend, seasonal, and residual "
            "components. ACF measures the correlation of returns with their lagged values."
        )

with tab_tests:
    render_test_tab("test_time_series.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "statsmodels", "Plotly", "Streamlit"])