"""Stock Analysis — technical indicators with interactive overlays."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import fetch_stock_history, compute_technical_indicators

st.set_page_config(page_title="Stock Analysis", layout="wide")
st.title("Technical Analysis")

# -- Inputs (main area) ------------------------------------------------------
col_in1, col_in2 = st.columns(2)

with col_in1:
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

with col_in2:
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

col_ind1, col_ind2, col_ind3, col_ind4, col_ind5 = st.columns(5)
with col_ind1:
    show_sma = st.checkbox("SMA (20 & 50)", value=True)
with col_ind2:
    show_ema = st.checkbox("EMA (20)")
with col_ind3:
    show_bb = st.checkbox("Bollinger Bands")
with col_ind4:
    show_rsi = st.checkbox("RSI", value=True)
with col_ind5:
    show_macd = st.checkbox("MACD", value=True)

st.divider()

if not ticker:
    st.info("Enter a ticker symbol above.")
    st.stop()

# -- Fetch & Compute ---------------------------------------------------------
with st.spinner(f"Loading {ticker}..."):
    df = fetch_stock_history(ticker, period)

if df.empty:
    st.error(f"No data found for **{ticker}**.")
    st.stop()

df = compute_technical_indicators(df)

# -- Build Subplots -----------------------------------------------------------
n_rows = 1 + int(show_rsi) + int(show_macd)
heights = [0.6]
titles = [f"{ticker} Price"]
if show_rsi:
    heights.append(0.2)
    titles.append("RSI")
if show_macd:
    heights.append(0.2)
    titles.append("MACD")

fig = make_subplots(
    rows=n_rows, cols=1, shared_xaxes=True,
    vertical_spacing=0.04, row_heights=heights,
    subplot_titles=titles,
)

# Price line
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close",
                         line=dict(color="#1f77b4")), row=1, col=1)

# Overlays on price
if show_sma:
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20",
                             line=dict(dash="dash")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50",
                             line=dict(dash="dash")), row=1, col=1)
if show_ema:
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], name="EMA 20",
                             line=dict(dash="dot", color="orange")), row=1, col=1)
if show_bb:
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], name="BB Upper",
                             line=dict(width=1, color="gray")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], name="BB Lower",
                             fill="tonexty", line=dict(width=1, color="gray")), row=1, col=1)

# RSI subplot
current_row = 2
if show_rsi:
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="purple")), row=current_row, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
    fig.update_yaxes(range=[0, 100], row=current_row, col=1)
    current_row += 1

# MACD subplot
if show_macd:
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                             line=dict(color="blue")), row=current_row, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signal",
                             line=dict(color="red")), row=current_row, col=1)
    colors = ["green" if v >= 0 else "red" for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="Histogram",
                         marker_color=colors), row=current_row, col=1)

fig.update_layout(height=200 + n_rows * 250, margin=dict(t=60, b=30),
                  xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
