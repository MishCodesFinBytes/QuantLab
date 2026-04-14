"""Stock Tracker — candlestick chart with volume and key price metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import fetch_stock_history
from nav import render_sidebar
from page_header import render_page_header
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="Stock Tracker", page_icon="assets/logo.png", layout="wide")
render_page_header("Stock Tracker", "Candlestick charts, volume bars, 52-week range")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Data source:** fetches OHLCV (Open, High, Low, Close, Volume) data from yfinance
        - **Candlestick chart:** each candle shows the open, high, low, and close for one trading day
        - **Green candle:** close > open (price went up); **Red candle:** close < open (price went down)
        - **Volume bars:** show how many shares traded each day, colored by price direction
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Current Price:** the most recent closing price and daily change
        - **52-Week High / Low:** the highest and lowest prices in the selected period
        - **Volume:** number of shares traded on the most recent day
        - **Candlestick chart:** visual price action -- long candles mean large price moves, wicks show intraday range
        """)

    # -- Inputs (main area) ------------------------------------------------------
    col_in1, col_in2 = st.columns(2)

    with col_in1:
        ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

    with col_in2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    st.divider()

    if not ticker:
        st.info("Enter a ticker symbol above.")
        st.stop()

    # -- Fetch Data ---------------------------------------------------------------
    with st.spinner(f"Fetching {ticker} data..."):
        df = fetch_stock_history(ticker, period)

    if df.empty:
        st.error(f"No data found for ticker **{ticker}**. Please check the symbol and try again.")
        st.stop()

    # -- Key Metrics --------------------------------------------------------------
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"${latest['Close']:.2f}",
                f"{latest['Close'] - prev['Close']:.2f}")
    col2.metric("52-Week High", f"${df['High'].max():.2f}")
    col3.metric("52-Week Low", f"${df['Low'].min():.2f}")
    col4.metric("Volume (latest)", f"{int(latest['Volume']):,}")

    # -- Candlestick + Volume Chart -----------------------------------------------
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
        title_text=f"{ticker} -- {period}",
        margin=dict(t=60, b=30),
    )
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

with tab_tests:
    render_test_tab("test_stock_tracker.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "Plotly", "Streamlit"])