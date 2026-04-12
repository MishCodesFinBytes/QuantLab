"""Chart builder functions for all four plotting libraries.

Each library has four functions: line, candlestick, bar (volume), histogram (returns).
All accept the same OHLCV DataFrame and return a renderable figure object.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ── Helpers ─────────────────────────────────────────────────────────

def compute_daily_returns(df: pd.DataFrame) -> pd.Series:
    """Compute daily percentage returns from Close prices."""
    return df["Close"].pct_change().dropna()


def detect_outliers(df: pd.DataFrame, n_std: float = 3.0) -> pd.DataFrame:
    """Flag rows where any numeric column exceeds n_std from its mean.

    Returns a boolean DataFrame (same shape as numeric columns).
    """
    numeric = df.select_dtypes(include=[np.number])
    z_scores = (numeric - numeric.mean()).abs() / numeric.std()
    return z_scores > n_std


# ── Plotly ──────────────────────────────────────────────────────────

def plotly_line_chart(df: pd.DataFrame):
    """Close price line chart using Plotly."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], mode="lines", name="Close",
        line=dict(color="#2a7ae2"),
    ))
    # Mark outlier points
    outliers = detect_outliers(df)
    if outliers["Close"].any():
        mask = outliers["Close"]
        fig.add_trace(go.Scatter(
            x=df.index[mask], y=df["Close"][mask],
            mode="markers", name="Outlier",
            marker=dict(color="red", size=10, symbol="x"),
        ))
    fig.update_layout(title="Close Price (Plotly)", xaxis_title="Date", yaxis_title="Price")
    return fig


def plotly_candlestick(df: pd.DataFrame):
    """OHLC candlestick chart using Plotly."""
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="OHLC",
    )])
    fig.update_layout(title="Candlestick (Plotly)", xaxis_title="Date", yaxis_title="Price")
    return fig


def plotly_volume_bar(df: pd.DataFrame):
    """Volume bar chart using Plotly."""
    import plotly.graph_objects as go

    colors = ["#2a7ae2" if c >= o else "#e24a4a"
              for c, o in zip(df["Close"], df["Open"])]
    fig = go.Figure(data=[go.Bar(
        x=df.index, y=df["Volume"], marker_color=colors, name="Volume",
    )])
    fig.update_layout(title="Volume (Plotly)", xaxis_title="Date", yaxis_title="Volume")
    return fig


def plotly_returns_histogram(df: pd.DataFrame):
    """Daily returns histogram using Plotly."""
    import plotly.graph_objects as go

    returns = compute_daily_returns(df)
    fig = go.Figure(data=[go.Histogram(
        x=returns, nbinsx=40, name="Daily Returns",
        marker_color="#2a7ae2", opacity=0.75,
    )])
    fig.update_layout(title="Daily Returns Distribution (Plotly)",
                      xaxis_title="Return", yaxis_title="Frequency")
    return fig


# ── Matplotlib ──────────────────────────────────────────────────────

def matplotlib_line_chart(df: pd.DataFrame):
    """Close price line chart using Matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Close"], color="#2a7ae2", label="Close")
    # Mark outliers
    outliers = detect_outliers(df)
    if outliers["Close"].any():
        mask = outliers["Close"]
        ax.scatter(df.index[mask], df["Close"][mask], color="red", marker="x",
                   s=100, zorder=5, label="Outlier")
        for idx in df.index[mask]:
            ax.annotate("outlier", xy=(idx, df.loc[idx, "Close"]),
                        xytext=(0, 15), textcoords="offset points",
                        fontsize=8, color="red", ha="center",
                        arrowprops=dict(arrowstyle="->", color="red"))
    ax.set_title("Close Price (Matplotlib)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def matplotlib_candlestick(df: pd.DataFrame):
    """OHLC candlestick chart using Matplotlib (manual bars + wicks)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    fig, ax = plt.subplots(figsize=(10, 4))
    dates = mdates.date2num(df.index.to_pydatetime())
    width = 0.6

    up = df["Close"] >= df["Open"]
    down = ~up

    # Up candles (green)
    ax.bar(dates[up], (df["Close"] - df["Open"])[up], width,
           bottom=df["Open"][up], color="#2ea043", edgecolor="#2ea043")
    ax.vlines(dates[up], df["Low"][up], df["High"][up], color="#2ea043", linewidth=0.8)

    # Down candles (red)
    ax.bar(dates[down], (df["Open"] - df["Close"])[down], width,
           bottom=df["Close"][down], color="#e24a4a", edgecolor="#e24a4a")
    ax.vlines(dates[down], df["Low"][down], df["High"][down], color="#e24a4a", linewidth=0.8)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.set_title("Candlestick (Matplotlib)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def matplotlib_volume_bar(df: pd.DataFrame):
    """Volume bar chart using Matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 3))
    colors = ["#2a7ae2" if c >= o else "#e24a4a"
              for c, o in zip(df["Close"], df["Open"])]
    ax.bar(df.index, df["Volume"], color=colors, width=0.8)
    ax.set_title("Volume (Matplotlib)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def matplotlib_returns_histogram(df: pd.DataFrame):
    """Daily returns histogram using Matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    returns = compute_daily_returns(df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(returns, bins=40, color="#2a7ae2", alpha=0.75, edgecolor="white")
    ax.set_title("Daily Returns Distribution (Matplotlib)")
    ax.set_xlabel("Return")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    return fig
