"""VaR & CVaR — Value at Risk and Conditional Value at Risk analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats as sp_stats
from data import fetch_stock_history

st.set_page_config(page_title="VaR & CVaR", page_icon="⚠️", layout="wide")
st.title("Value at Risk & Conditional VaR")

# ── Sidebar ──────────────────────────────────────────────────────────────────
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper().strip()
period = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
confidence = st.sidebar.slider("Confidence Level (%)", 90, 99, 95)

if not ticker:
    st.info("Enter a ticker symbol in the sidebar.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_returns(tkr: str, per: str) -> pd.Series:
    df = fetch_stock_history(tkr, per)
    return df["Close"].pct_change().dropna()


with st.spinner(f"Loading {ticker}..."):
    returns = load_returns(ticker, period)

if returns.empty:
    st.error(f"No data found for **{ticker}**.")
    st.stop()

# ── Compute VaR / CVaR ──────────────────────────────────────────────────────
alpha = 1 - confidence / 100
mean_r = returns.mean()
std_r = returns.std()
daily_vol = std_r

# Historical VaR: percentile of empirical returns
hist_var = np.percentile(returns, alpha * 100)

# Parametric VaR: assume normal
z_score = sp_stats.norm.ppf(alpha)
param_var = mean_r + z_score * std_r

# CVaR (Expected Shortfall): mean of returns below VaR
tail = returns[returns <= hist_var]
cvar = tail.mean() if len(tail) > 0 else hist_var

# ── Metrics ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Historical VaR", f"{hist_var:.4%}")
c2.metric("CVaR (Expected Shortfall)", f"{cvar:.4%}")
c3.metric("Daily Volatility", f"{daily_vol:.4%}")

st.markdown(f"""
| Measure | Value |
|---|---|
| Parametric VaR ({confidence}%) | {param_var:.4%} |
| Historical VaR ({confidence}%) | {hist_var:.4%} |
| CVaR ({confidence}%) | {cvar:.4%} |
| Mean Daily Return | {mean_r:.4%} |
| Observations | {len(returns)} |
""")

# ── Histogram ────────────────────────────────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Histogram(
    x=returns, nbinsx=80, name="Daily Returns",
    marker_color="steelblue", opacity=0.7,
))
fig.add_vline(x=hist_var, line_dash="dash", line_color="red",
              annotation_text=f"VaR {hist_var:.3%}", annotation_position="top left")
fig.add_vline(x=cvar, line_dash="dot", line_color="darkred",
              annotation_text=f"CVaR {cvar:.3%}", annotation_position="top left")
fig.update_layout(
    title=f"{ticker} Daily Returns Distribution ({confidence}% Confidence)",
    xaxis_title="Daily Return", yaxis_title="Frequency",
    height=500, margin=dict(t=60, b=40),
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "VaR estimates the maximum expected loss at a given confidence level. "
    "CVaR (Expected Shortfall) measures the average loss beyond the VaR threshold."
)
