"""Financial Reporting — summary statistics, returns analysis, and CSV export."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data import fetch_stock_history

st.set_page_config(page_title="Financial Reporting", page_icon="📄", layout="wide")
st.title("Financial Reporting")

# ── Sidebar ──────────────────────────────────────────────────────────────────
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper().strip()
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

if not ticker:
    st.info("Enter a ticker symbol in the sidebar.")
    st.stop()

# ── Fetch Data ───────────────────────────────────────────────────────────────
with st.spinner(f"Fetching {ticker} data..."):
    df = fetch_stock_history(ticker, period)

if df.empty:
    st.error(f"No data found for **{ticker}**.")
    st.stop()

# ── Compute Returns ──────────────────────────────────────────────────────────
df["Daily_Return"] = df["Close"].pct_change()
df["Cumulative_Return"] = (1 + df["Daily_Return"]).cumprod() - 1

# ── Summary Statistics ───────────────────────────────────────────────────────
st.subheader("Summary Statistics")
stats = df[["Open", "High", "Low", "Close", "Volume"]].describe().T
stats["range"] = stats["max"] - stats["min"]
st.dataframe(stats.style.format("{:.2f}"), use_container_width=True)

# ── Key Metrics ──────────────────────────────────────────────────────────────
st.subheader("Key Metrics")
c1, c2, c3, c4 = st.columns(4)
total_return = df["Cumulative_Return"].iloc[-1] * 100 if len(df) > 1 else 0
avg_daily = df["Daily_Return"].mean() * 100
volatility = df["Daily_Return"].std() * 100
sharpe = (df["Daily_Return"].mean() / df["Daily_Return"].std() * (252 ** 0.5)
          if df["Daily_Return"].std() > 0 else 0)

c1.metric("Total Return", f"{total_return:.2f}%")
c2.metric("Avg Daily Return", f"{avg_daily:.4f}%")
c3.metric("Daily Volatility", f"{volatility:.4f}%")
c4.metric("Sharpe Ratio (ann.)", f"{sharpe:.2f}")

# ── Charts: Price + Returns Histogram ────────────────────────────────────────
st.subheader("Price History")
fig_price = px.line(df, x=df.index, y="Close", title=f"{ticker} Closing Price")
fig_price.update_layout(xaxis_title="Date", yaxis_title="Price ($)")
st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Daily Returns Distribution")
returns_clean = df["Daily_Return"].dropna()
fig_hist = px.histogram(
    returns_clean, nbins=50,
    title="Daily Returns Histogram",
    labels={"value": "Daily Return", "count": "Frequency"},
)
fig_hist.update_layout(showlegend=False)
st.plotly_chart(fig_hist, use_container_width=True)

# ── Download Buttons ─────────────────────────────────────────────────────────
st.subheader("Export Data")
col_a, col_b = st.columns(2)

with col_a:
    csv_data = df.to_csv()
    st.download_button(
        label="Download Price Data (CSV)",
        data=csv_data,
        file_name=f"{ticker}_{period}_data.csv",
        mime="text/csv",
    )

with col_b:
    csv_stats = stats.to_csv()
    st.download_button(
        label="Download Summary Stats (CSV)",
        data=csv_stats,
        file_name=f"{ticker}_{period}_stats.csv",
        mime="text/csv",
    )
