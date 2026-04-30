"""Algo Trading -- backtest SMA Crossover and Momentum strategies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from page_init import setup_page
from stock_inputs import stock_input_panel
from cached_data import load_stock_data
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Algo Trading Backtest", "SMA crossover and momentum strategies with equity curves")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **SMA Crossover:** buys when the fast moving average crosses above the slow MA; sells on the cross below
        - **Momentum:** buys when the N-day return is positive; sells when it turns negative
        - **Signal shift:** signals are shifted by one day to avoid look-ahead bias (trade on next day's open)
        - **Backtest:** simulates historical execution, tracks cumulative strategy return vs buy-and-hold
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Strategy Return:** cumulative return from following the trading signals
        - **Buy & Hold Return:** what you would have earned simply holding the stock
        - **Sharpe Ratio:** annualized risk-adjusted return of the strategy
        - **Max Drawdown:** the largest peak-to-trough decline during the backtest
        - **Price chart:** shows buy (green triangle) and sell (red triangle) signal markers on the price line
        - **Equity Curve:** strategy cumulative return vs buy-and-hold over time
        """)

    # -- Inputs -------------------------------------------------------------------
    ticker, period = stock_input_panel(periods=["6mo", "1y", "2y", "5y"], default_period="2y")

    strategy = st.radio("Strategy", ["SMA Crossover", "Momentum"], horizontal=True)

    # Strategy-specific parameters
    param_col1, param_col2 = st.columns(2)

    if strategy == "SMA Crossover":
        with param_col1:
            fast_win = st.slider("Fast SMA Window", 5, 50, 10)
        with param_col2:
            slow_win = st.slider("Slow SMA Window", 20, 200, 50)
    else:
        with param_col1:
            lookback = st.slider("Momentum Lookback (days)", 5, 60, 20)

    if not ticker:
        st.info("Enter a ticker symbol above.")
        st.stop()

    st.divider()


    with st.spinner(f"Loading {ticker}..."):
        df = load_stock_data(ticker, period)

    if df.empty:
        st.error(f"No data found for **{ticker}**.")
        st.stop()

    df["Return"] = df["Close"].pct_change()

    # -- Generate signals ---------------------------------------------------------
    if strategy == "SMA Crossover":
        df["SMA_Fast"] = df["Close"].rolling(fast_win).mean()
        df["SMA_Slow"] = df["Close"].rolling(slow_win).mean()
        df["Signal"] = 0
        df.loc[df["SMA_Fast"] > df["SMA_Slow"], "Signal"] = 1
        df.loc[df["SMA_Fast"] <= df["SMA_Slow"], "Signal"] = -1
    else:
        df["Momentum"] = df["Close"].pct_change(lookback)
        df["Signal"] = 0
        df.loc[df["Momentum"] > 0, "Signal"] = 1
        df.loc[df["Momentum"] <= 0, "Signal"] = -1

    # Shift signal to avoid look-ahead bias
    df["Position"] = df["Signal"].shift(1)
    df.dropna(inplace=True)

    # -- Backtest -----------------------------------------------------------------
    df["Strategy_Return"] = df["Position"] * df["Return"]
    df["Cum_Strategy"] = (1 + df["Strategy_Return"]).cumprod()
    df["Cum_BuyHold"] = (1 + df["Return"]).cumprod()

    # Trade signals (position changes)
    df["Trade"] = df["Position"].diff().fillna(0)
    buys = df[df["Trade"] > 0]
    sells = df[df["Trade"] < 0]

    # -- Metrics ------------------------------------------------------------------
    total_ret = df["Cum_Strategy"].iloc[-1] - 1
    bh_ret = df["Cum_BuyHold"].iloc[-1] - 1
    sharpe = (df["Strategy_Return"].mean() / df["Strategy_Return"].std() * np.sqrt(252)
              if df["Strategy_Return"].std() > 0 else 0)
    rolling_max = df["Cum_Strategy"].cummax()
    drawdown = (df["Cum_Strategy"] - rolling_max) / rolling_max
    max_dd = drawdown.min()
    n_trades = len(buys) + len(sells)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Strategy Return", f"{total_ret:.2%}")
    m2.metric("Buy & Hold Return", f"{bh_ret:.2%}")
    m3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    m4.metric("Max Drawdown", f"{max_dd:.2%}")
    m5.metric("Trades", n_trades)

    # -- Charts -------------------------------------------------------------------
    tab1, tab2 = st.tabs(["Price and Signals", "Equity Curve"])

    with tab1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
                                  line=dict(color="steelblue")))
        if strategy == "SMA Crossover":
            fig1.add_trace(go.Scatter(x=df.index, y=df["SMA_Fast"], name=f"SMA {fast_win}",
                                      line=dict(dash="dash", color="orange")))
            fig1.add_trace(go.Scatter(x=df.index, y=df["SMA_Slow"], name=f"SMA {slow_win}",
                                      line=dict(dash="dash", color="purple")))
        if len(buys) > 0:
            fig1.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers",
                                      name="Buy", marker=dict(symbol="triangle-up", size=10, color="green")))
        if len(sells) > 0:
            fig1.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers",
                                      name="Sell", marker=dict(symbol="triangle-down", size=10, color="red")))
        fig1.update_layout(title=f"{ticker} -- {strategy} Signals", height=450,
                           margin=dict(t=50, b=40))
        st.plotly_chart(fig1, width='stretch')

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df["Cum_Strategy"], name="Strategy",
                                  line=dict(color="green")))
        fig2.add_trace(go.Scatter(x=df.index, y=df["Cum_BuyHold"], name="Buy & Hold",
                                  line=dict(color="gray", dash="dash")))
        fig2.update_layout(title="Equity Curve", yaxis_title="Cumulative Return",
                           height=400, margin=dict(t=50, b=40))
        st.plotly_chart(fig2, width='stretch')

with tab_tests:
    render_test_tab("test_algo_trading.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "pandas", "Plotly", "Streamlit"])