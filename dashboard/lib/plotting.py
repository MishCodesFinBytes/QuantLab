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


def ohlc_colors(df: pd.DataFrame, up: str = "#2a7ae2", down: str = "#e24a4a") -> list[str]:
    return [up if c >= o else down for c, o in zip(df["Close"], df["Open"])]


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

    fig = go.Figure(data=[go.Bar(
        x=df.index, y=df["Volume"], marker_color=ohlc_colors(df), name="Volume",
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
    ax.bar(df.index, df["Volume"], color=ohlc_colors(df), width=0.8)
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


# ── Altair ──────────────────────────────────────────────────────────

def _altair_df(df: pd.DataFrame) -> pd.DataFrame:
    """Reset index so Altair can use the Date column."""
    out = df.reset_index()
    out.columns = [c if c != df.index.name and c != "Date" else "Date" for c in out.columns]
    if "Date" not in out.columns:
        out = out.rename(columns={out.columns[0]: "Date"})
    return out


def altair_line_chart(df: pd.DataFrame):
    """Close price line chart using Altair."""
    import altair as alt

    source = _altair_df(df)
    outliers_mask = detect_outliers(df)["Close"]
    source["is_outlier"] = outliers_mask.values

    line = alt.Chart(source).mark_line(color="#2a7ae2").encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Close:Q", title="Price"),
    )
    points = alt.Chart(source[source["is_outlier"]]).mark_point(
        color="red", size=100, shape="cross",
    ).encode(x="Date:T", y="Close:Q")

    return (line + points).properties(title="Close Price (Altair)", width="container")


def altair_candlestick(df: pd.DataFrame):
    """OHLC candlestick chart using Altair (rule + bar layers)."""
    import altair as alt

    source = _altair_df(df)
    source["color"] = ["green" if c >= o else "red"
                        for c, o in zip(source["Close"], source["Open"])]

    rule = alt.Chart(source).mark_rule().encode(
        x="Date:T",
        y="Low:Q",
        y2="High:Q",
        color=alt.Color("color:N", scale=None),
    )
    bar = alt.Chart(source).mark_bar(size=6).encode(
        x="Date:T",
        y="Open:Q",
        y2="Close:Q",
        color=alt.Color("color:N", scale=None),
    )
    return (rule + bar).properties(title="Candlestick (Altair)", width="container")


def altair_volume_bar(df: pd.DataFrame):
    """Volume bar chart using Altair."""
    import altair as alt

    source = _altair_df(df)
    source["color"] = ohlc_colors(df)

    return alt.Chart(source).mark_bar().encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Volume:Q", title="Volume"),
        color=alt.Color("color:N", scale=None),
    ).properties(title="Volume (Altair)", width="container")


def altair_returns_histogram(df: pd.DataFrame):
    """Daily returns histogram using Altair."""
    import altair as alt

    returns = compute_daily_returns(df)
    source = pd.DataFrame({"Return": returns.values})

    return alt.Chart(source).mark_bar(color="#2a7ae2", opacity=0.75).encode(
        x=alt.X("Return:Q", bin=alt.Bin(maxbins=40), title="Return"),
        y=alt.Y("count()", title="Frequency"),
    ).properties(title="Daily Returns Distribution (Altair)", width="container")


# ── Bokeh ───────────────────────────────────────────────────────────

def bokeh_line_chart(df: pd.DataFrame):
    """Close price line chart using Bokeh."""
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource

    source = ColumnDataSource(data=dict(
        date=df.index, close=df["Close"],
    ))
    p = figure(title="Close Price (Bokeh)", x_axis_type="datetime",
               x_axis_label="Date", y_axis_label="Price",
               width=800, height=350)
    p.line("date", "close", source=source, color="#2a7ae2", line_width=2)

    # Mark outliers
    outliers_mask = detect_outliers(df)["Close"]
    if outliers_mask.any():
        outlier_src = ColumnDataSource(data=dict(
            date=df.index[outliers_mask],
            close=df["Close"][outliers_mask],
        ))
        p.cross("date", "close", source=outlier_src, color="red",
                size=12, line_width=2, legend_label="Outlier")

    return p


def bokeh_candlestick(df: pd.DataFrame):
    """OHLC candlestick chart using Bokeh (segment + vbar)."""
    from bokeh.plotting import figure

    p = figure(title="Candlestick (Bokeh)", x_axis_type="datetime",
               x_axis_label="Date", y_axis_label="Price",
               width=800, height=350)

    up = df[df["Close"] >= df["Open"]]
    down = df[df["Close"] < df["Open"]]
    w = 12 * 60 * 60 * 1000  # half-day in ms

    # Wicks
    p.segment(df.index, df["High"], df.index, df["Low"], color="black")

    # Up candles
    p.vbar(up.index, w, up["Open"], up["Close"], fill_color="#2ea043",
           line_color="#2ea043")
    # Down candles
    p.vbar(down.index, w, down["Open"], down["Close"], fill_color="#e24a4a",
           line_color="#e24a4a")

    return p


def bokeh_volume_bar(df: pd.DataFrame):
    """Volume bar chart using Bokeh."""
    from bokeh.plotting import figure

    p = figure(title="Volume (Bokeh)", x_axis_type="datetime",
               x_axis_label="Date", y_axis_label="Volume",
               width=800, height=250)

    w = 12 * 60 * 60 * 1000
    p.vbar(x=df.index, top=df["Volume"], width=w, color=ohlc_colors(df))
    return p


def bokeh_returns_histogram(df: pd.DataFrame):
    """Daily returns histogram using Bokeh."""
    from bokeh.plotting import figure

    returns = compute_daily_returns(df)
    hist, edges = np.histogram(returns, bins=40)

    p = figure(title="Daily Returns Distribution (Bokeh)",
               x_axis_label="Return", y_axis_label="Frequency",
               width=800, height=350)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color="#2a7ae2", fill_alpha=0.75, line_color="white")

    return p
