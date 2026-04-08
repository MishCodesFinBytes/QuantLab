"""Algo Trading — backtest SMA Crossover and Momentum strategies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data import fetch_stock_history

st.set_page_config(page_title="Algo Trading", page_icon="🤖", layout="wide")
st.title("Algorithmic Trading Backtest")

# ── Sidebar ──────────────────────────────────────────────────────────────────
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper().strip()
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=2)
strategy = st.sidebar.radio("Strategy", ["SMA Crossover", "Momentum"])

if strategy == "SMA Crossover":
    fast_win = st.sidebar.slider("Fast SMA Window", 5, 50, 10)
    slow_win = st.sidebar.slider("Slow SMA Window", 20, 200, 50)
else:
    lookback = st.sidebar.slider("Momentum Lookback (days)", 5, 60, 20)

if not ticker:
    st.info("Enter a ticker symbol in the sidebar.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_data(tkr: str, per: str) -> pd.DataFrame:
    return fetch_stock_history(tkr, per)


with st.spinner(f"Loading {ticker}..."):
    df = load_data(ticker, period)

if df.empty:
    st.error(f"No data found for **{ticker}**.")
    st.stop()

df["Return"] = df["Close"].pct_change()

# ── Generate signals ─────────────────────────────────────────────────────────
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

# ── Backtest ─────────────────────────────────────────────────────────────────
df["Strategy_Return"] = df["Position"] * df["Return"]
df["Cum_Strategy"] = (1 + df["Strategy_Return"]).cumprod()
df["Cum_BuyHold"] = (1 + df["Return"]).cumprod()

# Trade signals (position changes)
df["Trade"] = df["Position"].diff().fillna(0)
buys = df[df["Trade"] > 0]
sells = df[df["Trade"] < 0]

# ── Metrics ──────────────────────────────────────────────────────────────────
total_ret = df["Cum_Strategy"].iloc[-1] - 1
bh_ret = df["Cum_BuyHold"].iloc[-1] - 1
sharpe = (df["Strategy_Return"].mean() / df["Strategy_Return"].std() * np.sqrt(252)
          if df["Strategy_Return"].std() > 0 else 0)
rolling_max = df["Cum_Strategy"].cummax()
drawdown = (df["Cum_Strategy"] - rolling_max) / rolling_max
max_dd = drawdown.min()
n_trades = len(buys) + len(sells)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Strategy Return", f"{total_ret:.2%}")
c2.metric("Sharpe Ratio", f"{sharpe:.2f}")
c3.metric("Max Drawdown", f"{max_dd:.2%}")
c4.metric("Trades", n_trades)

st.metric("Buy & Hold Return", f"{bh_ret:.2%}")

# ── Price chart with signals ─────────────────────────────────────────────────
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
fig1.update_layout(title=f"{ticker} — {strategy} Signals", height=450,
                   margin=dict(t=50, b=40))
st.plotly_chart(fig1, use_container_width=True)

# ── Equity curve ─────────────────────────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.index, y=df["Cum_Strategy"], name="Strategy",
                          line=dict(color="green")))
fig2.add_trace(go.Scatter(x=df.index, y=df["Cum_BuyHold"], name="Buy & Hold",
                          line=dict(color="gray", dash="dash")))
fig2.update_layout(title="Equity Curve", yaxis_title="Cumulative Return",
                   height=400, margin=dict(t=50, b=40))
st.plotly_chart(fig2, use_container_width=True)
