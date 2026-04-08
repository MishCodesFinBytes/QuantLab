"""Stock Tracker — candlestick chart with volume and key price metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import fetch_stock_history

st.set_page_config(page_title="Stock Tracker", page_icon="📈", layout="wide")
st.title("Stock Tracker")

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
    st.error(f"No data found for ticker **{ticker}**. Please check the symbol and try again.")
    st.stop()

# ── Key Metrics ──────────────────────────────────────────────────────────────
st.subheader(f"{ticker} — Key Metrics")
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"${latest['Close']:.2f}",
            f"{latest['Close'] - prev['Close']:.2f}")
col2.metric("52-Week High", f"${df['High'].max():.2f}")
col3.metric("52-Week Low", f"${df['Low'].min():.2f}")
col4.metric("Volume (latest)", f"{int(latest['Volume']):,}")

# ── Candlestick + Volume Chart ───────────────────────────────────────────────
st.subheader("Price & Volume")
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25],
    subplot_titles=("Price", "Volume"),
)

fig.add_trace(
    go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="OHLC",
    ),
    row=1, col=1,
)

colors = ["green" if c >= o else "red" for c, o in zip(df["Close"], df["Open"])]
fig.add_trace(
    go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="Volume",
           showlegend=False),
    row=2, col=1,
)

fig.update_layout(
    xaxis_rangeslider_visible=False,
    height=600,
    title_text=f"{ticker} — {period}",
    margin=dict(t=60, b=30),
)
fig.update_yaxes(title_text="Price ($)", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)
