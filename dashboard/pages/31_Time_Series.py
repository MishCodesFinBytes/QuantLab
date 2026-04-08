"""Time Series Decomposition -- seasonal decompose and ACF analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf
from data import fetch_stock_history

st.set_page_config(page_title="Time Series", layout="wide")
st.title("Time Series Decomposition")

# -- Inputs -------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

with col2:
    period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=2)

if not ticker:
    st.info("Enter a ticker symbol above.")
    st.stop()

st.divider()


@st.cache_data(show_spinner=False)
def load_prices(tkr: str, per: str) -> pd.Series:
    df = fetch_stock_history(tkr, per)
    return df["Close"].dropna()


with st.spinner(f"Loading {ticker}..."):
    prices = load_prices(ticker, period)

if prices.empty or len(prices) < 260:
    st.error(f"Need at least 260 trading days. Got {len(prices)} for **{ticker}**.")
    st.stop()

# -- Decompose ----------------------------------------------------------------
decomp = seasonal_decompose(prices, model="multiplicative", period=252)

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
                      title=f"{ticker} Multiplicative Decomposition (period=252)")
    st.plotly_chart(fig, use_container_width=True)

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
    st.plotly_chart(acf_fig, use_container_width=True)

st.caption(
    "Multiplicative decomposition separates price into trend, seasonal, and residual "
    "components. ACF measures the correlation of returns with their lagged values."
)
