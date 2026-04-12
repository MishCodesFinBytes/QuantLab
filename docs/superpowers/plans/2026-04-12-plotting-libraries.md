# Plotting Libraries Compared — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit dashboard page comparing Plotly, Matplotlib, Altair, and Bokeh using the same editable financial dataset, plus a blog article for the Tech Stack tab covering the comparison and outlier handling.

**Architecture:** Single dashboard page with a frozen top section (ticker picker, editable OHLCV table, outlier detection) and a tabbed bottom section (one tab per library, each rendering line/candlestick/bar/histogram charts from the shared dataframe). Blog article is a standalone Jekyll post linking to the live demo.

**Tech Stack:** Streamlit, Plotly, Matplotlib, Altair, Bokeh, yfinance, pandas, NumPy

---

## File Structure

```
dashboard/
├── pages/
│   └── 41_Plotting_Libraries.py   # Main page — data section + 4 library tabs
├── lib/
│   └── plotting.py                # Chart builder functions for all 4 libraries
├── tests/
│   └── test_plotting_libraries.py # AppTest-based frontend tests
└── requirements.txt               # Add altair, bokeh

docs/_posts/
└── 2026-04-12-plotting-libraries-compared.html  # Blog article

docs/_tabs/
└── misc.md                        # Rename title Misc → Tech Stack, add entry

docs/_quant_lab/mini/
└── plotting-libraries.html        # Mini project page for quant-lab tab

docs/_tabs/
└── quant-lab.md                   # Add entry under Dashboards section
```

---

### Task 1: Add Dependencies

**Files:**
- Modify: `dashboard/requirements.txt`

- [ ] **Step 1: Add altair and bokeh to requirements.txt**

Add these three lines after the existing `boto3` entry:

```
altair>=5.2.0
bokeh>=3.3.0
matplotlib>=3.8.0
```

Matplotlib is a transitive dep of Streamlit but we pin it explicitly since we import it directly.

- [ ] **Step 2: Install locally**

Run: `cd C:/codebase/quant_lab/dashboard && pip install -r requirements.txt`

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/requirements.txt
git commit -m "deps: add altair, bokeh, matplotlib to dashboard requirements"
```

---

### Task 2: Chart Builder Library — Plotly Functions

**Files:**
- Create: `dashboard/lib/plotting.py`
- Test: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Write the failing test for Plotly line chart**

Create `dashboard/tests/test_plotting_libraries.py`:

```python
"""Frontend tests for Plotting Libraries page."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


@pytest.fixture
def sample_ohlcv():
    """Small OHLCV DataFrame for chart builder tests."""
    dates = pd.bdate_range("2026-01-02", periods=30)
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(30) * 2)
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.random.randint(1_000_000, 5_000_000, 30),
        },
        index=dates,
    )


class TestPlotlyCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_line_chart

        fig = plotly_line_chart(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestPlotlyCharts::test_line_chart_returns_figure -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write Plotly chart builders**

Create `dashboard/lib/plotting.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestPlotlyCharts::test_line_chart_returns_figure -v`
Expected: PASS

- [ ] **Step 5: Add remaining Plotly tests**

Append to `TestPlotlyCharts` in `tests/test_plotting_libraries.py`:

```python
    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_candlestick

        fig = plotly_candlestick(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_volume_bar

        fig = plotly_volume_bar(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import plotly_returns_histogram

        fig = plotly_returns_histogram(sample_ohlcv)
        assert fig is not None
        assert len(fig.data) >= 1
```

- [ ] **Step 6: Run all Plotly tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestPlotlyCharts -v`
Expected: 4 PASSED

- [ ] **Step 7: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/plotting.py dashboard/tests/test_plotting_libraries.py
git commit -m "feat: add Plotly chart builders with tests"
```

---

### Task 3: Chart Builder Library — Matplotlib Functions

**Files:**
- Modify: `dashboard/lib/plotting.py`
- Modify: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Write failing Matplotlib tests**

Add to `tests/test_plotting_libraries.py`:

```python
class TestMatplotlibCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_line_chart

        fig = matplotlib_line_chart(sample_ohlcv)
        assert fig is not None
        assert len(fig.get_axes()) >= 1

    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_candlestick

        fig = matplotlib_candlestick(sample_ohlcv)
        assert fig is not None
        assert len(fig.get_axes()) >= 1

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_volume_bar

        fig = matplotlib_volume_bar(sample_ohlcv)
        assert fig is not None

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import matplotlib_returns_histogram

        fig = matplotlib_returns_histogram(sample_ohlcv)
        assert fig is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestMatplotlibCharts -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write Matplotlib chart builders**

Append to `dashboard/lib/plotting.py`:

```python
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
```

- [ ] **Step 4: Run Matplotlib tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestMatplotlibCharts -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/plotting.py dashboard/tests/test_plotting_libraries.py
git commit -m "feat: add Matplotlib chart builders with tests"
```

---

### Task 4: Chart Builder Library — Altair Functions

**Files:**
- Modify: `dashboard/lib/plotting.py`
- Modify: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Write failing Altair tests**

Add to `tests/test_plotting_libraries.py`:

```python
class TestAltairCharts:
    def test_line_chart_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_line_chart
        import altair as alt

        chart = altair_line_chart(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_candlestick_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_candlestick
        import altair as alt

        chart = altair_candlestick(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_volume_bar_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_volume_bar
        import altair as alt

        chart = altair_volume_bar(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))

    def test_returns_histogram_returns_chart(self, sample_ohlcv):
        from lib.plotting import altair_returns_histogram
        import altair as alt

        chart = altair_returns_histogram(sample_ohlcv)
        assert isinstance(chart, (alt.Chart, alt.LayerChart))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestAltairCharts -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write Altair chart builders**

Append to `dashboard/lib/plotting.py`:

```python
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
    source["color"] = ["#2a7ae2" if c >= o else "#e24a4a"
                        for c, o in zip(source["Close"], source["Open"])]

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
```

- [ ] **Step 4: Run Altair tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestAltairCharts -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/plotting.py dashboard/tests/test_plotting_libraries.py
git commit -m "feat: add Altair chart builders with tests"
```

---

### Task 5: Chart Builder Library — Bokeh Functions

**Files:**
- Modify: `dashboard/lib/plotting.py`
- Modify: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Write failing Bokeh tests**

Add to `tests/test_plotting_libraries.py`:

```python
class TestBokehCharts:
    def test_line_chart_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_line_chart
        from bokeh.plotting import figure as bokeh_figure_type

        fig = bokeh_line_chart(sample_ohlcv)
        assert fig is not None

    def test_candlestick_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_candlestick

        fig = bokeh_candlestick(sample_ohlcv)
        assert fig is not None

    def test_volume_bar_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_volume_bar

        fig = bokeh_volume_bar(sample_ohlcv)
        assert fig is not None

    def test_returns_histogram_returns_figure(self, sample_ohlcv):
        from lib.plotting import bokeh_returns_histogram

        fig = bokeh_returns_histogram(sample_ohlcv)
        assert fig is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestBokehCharts -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write Bokeh chart builders**

Append to `dashboard/lib/plotting.py`:

```python
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

    colors = ["#2a7ae2" if c >= o else "#e24a4a"
              for c, o in zip(df["Close"], df["Open"])]
    w = 12 * 60 * 60 * 1000

    p.vbar(x=df.index, top=df["Volume"], width=w, color=colors)
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
```

- [ ] **Step 4: Run Bokeh tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestBokehCharts -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/plotting.py dashboard/tests/test_plotting_libraries.py
git commit -m "feat: add Bokeh chart builders with tests"
```

---

### Task 6: Outlier Detection Tests

**Files:**
- Modify: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Write outlier detection tests**

Add to `tests/test_plotting_libraries.py`:

```python
class TestOutlierDetection:
    def test_no_outliers_in_clean_data(self, sample_ohlcv):
        from lib.plotting import detect_outliers

        result = detect_outliers(sample_ohlcv)
        # Clean small dataset unlikely to have 3-sigma outliers
        assert result.sum().sum() == 0 or result.sum().sum() < 3

    def test_detects_injected_outlier(self, sample_ohlcv):
        from lib.plotting import detect_outliers

        df = sample_ohlcv.copy()
        # Spike one Close value to 10x the mean
        df.iloc[15, df.columns.get_loc("Close")] = df["Close"].mean() * 10
        result = detect_outliers(df)
        assert result["Close"].iloc[15] is True or result["Close"].iloc[15] == True

    def test_compute_daily_returns(self, sample_ohlcv):
        from lib.plotting import compute_daily_returns

        returns = compute_daily_returns(sample_ohlcv)
        assert len(returns) == len(sample_ohlcv) - 1
        assert returns.dtype == float
```

- [ ] **Step 2: Run tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestOutlierDetection -v`
Expected: 3 PASSED

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/tests/test_plotting_libraries.py
git commit -m "test: add outlier detection unit tests"
```

---

### Task 7: Dashboard Page

**Files:**
- Create: `dashboard/pages/41_Plotting_Libraries.py`

- [ ] **Step 1: Create the dashboard page**

Create `dashboard/pages/41_Plotting_Libraries.py`:

```python
"""Plotting Libraries Compared — same data rendered by Plotly, Matplotlib, Altair, and Bokeh."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import numpy as np
from data import fetch_stock_history
from nav import render_sidebar
from test_tab import render_test_tab
from plotting import (
    compute_daily_returns,
    detect_outliers,
    plotly_line_chart,
    plotly_candlestick,
    plotly_volume_bar,
    plotly_returns_histogram,
    matplotlib_line_chart,
    matplotlib_candlestick,
    matplotlib_volume_bar,
    matplotlib_returns_histogram,
    altair_line_chart,
    altair_candlestick,
    altair_volume_bar,
    altair_returns_histogram,
    bokeh_line_chart,
    bokeh_candlestick,
    bokeh_volume_bar,
    bokeh_returns_histogram,
)

render_sidebar()
st.set_page_config(page_title="Plotting Libraries", page_icon="assets/logo.png", layout="wide")
st.title("Plotting Libraries Compared")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Same dataset, four libraries:** fetch OHLCV data for any ticker, then render
          identical chart types with Plotly, Matplotlib, Altair, and Bokeh
        - **Editable data:** modify values in the table to see how each library handles
          outliers and extreme values
        - **Outlier detection:** rows with any value > 3 standard deviations from the
          column mean are flagged automatically
        - For the full comparison and outlier-handling guide, see the
          [Plotting Libraries blog post](https://mish-codes.github.io/FinBytes/tech-stack/plotting-libraries/)
        """)

    # ── Sidebar inputs ──────────────────────────────────────────────
    with st.sidebar:
        st.subheader("Data Settings")
        ticker = st.text_input("Ticker", value="AAPL").upper().strip()
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)

    if not ticker:
        st.info("Enter a ticker symbol in the sidebar.")
        st.stop()

    # ── Fetch data ──────────────────────────────────────────────────

    @st.cache_data(show_spinner="Fetching market data...")
    def load_data(tkr: str, per: str) -> pd.DataFrame:
        return fetch_stock_history(tkr, per)

    raw_df = load_data(ticker, period)
    if raw_df.empty:
        st.error(f"No data found for {ticker}.")
        st.stop()

    # ── TOP SECTION: Editable data table ────────────────────────────
    st.subheader(f"{ticker} — OHLCV Data")
    st.caption("Edit any cell to see how each library handles the change. Try spiking a Close price to simulate an outlier.")

    edited_df = st.data_editor(
        raw_df.round(2),
        use_container_width=True,
        num_rows="fixed",
        key="ohlcv_editor",
    )

    # ── Outlier detection ───────────────────────────────────────────
    outlier_flags = detect_outliers(edited_df)
    outlier_rows = outlier_flags.any(axis=1)
    if outlier_rows.any():
        dates = [d.strftime("%Y-%m-%d") for d in edited_df.index[outlier_rows]]
        st.warning(f"Outliers detected (>3σ) on: {', '.join(dates)}")
    else:
        st.success("No outliers detected in the current data.")

    st.divider()

    # ── BOTTOM SECTION: Library tabs ────────────────────────────────
    tab_plotly, tab_mpl, tab_altair, tab_bokeh = st.tabs(
        ["Plotly", "Matplotlib", "Altair", "Bokeh"]
    )

    with tab_plotly:
        st.plotly_chart(plotly_line_chart(edited_df), use_container_width=True)
        st.plotly_chart(plotly_candlestick(edited_df), use_container_width=True)
        st.plotly_chart(plotly_volume_bar(edited_df), use_container_width=True)
        st.plotly_chart(plotly_returns_histogram(edited_df), use_container_width=True)

    with tab_mpl:
        st.pyplot(matplotlib_line_chart(edited_df))
        st.pyplot(matplotlib_candlestick(edited_df))
        st.pyplot(matplotlib_volume_bar(edited_df))
        st.pyplot(matplotlib_returns_histogram(edited_df))

    with tab_altair:
        st.altair_chart(altair_line_chart(edited_df), use_container_width=True)
        st.altair_chart(altair_candlestick(edited_df), use_container_width=True)
        st.altair_chart(altair_volume_bar(edited_df), use_container_width=True)
        st.altair_chart(altair_returns_histogram(edited_df), use_container_width=True)

    with tab_bokeh:
        st.bokeh_chart(bokeh_line_chart(edited_df), use_container_width=True)
        st.bokeh_chart(bokeh_candlestick(edited_df), use_container_width=True)
        st.bokeh_chart(bokeh_volume_bar(edited_df), use_container_width=True)
        st.bokeh_chart(bokeh_returns_histogram(edited_df), use_container_width=True)

with tab_tests:
    render_test_tab("test_plotting_libraries.py")
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/pages/41_Plotting_Libraries.py
git commit -m "feat: add Plotting Libraries dashboard page"
```

---

### Task 8: AppTest Smoke Tests

**Files:**
- Modify: `dashboard/tests/test_plotting_libraries.py`

- [ ] **Step 1: Add AppTest smoke tests**

Add to the top of `tests/test_plotting_libraries.py` (after imports, before the chart builder tests):

```python
from streamlit.testing.v1 import AppTest


class TestPlottingLibrariesPage:
    def _run(self):
        at = AppTest.from_file("pages/41_Plotting_Libraries.py", default_timeout=30)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Plotting Libraries" in t.value for t in at.title)

    def test_has_ticker_input(self):
        at = self._run()
        ti = [w for w in at.text_input if w.value == "AAPL"]
        assert ti, "Expected a ticker text_input defaulting to AAPL"

    def test_has_period_selectbox(self):
        at = self._run()
        assert len(at.selectbox) >= 1, "Expected at least one selectbox (period)"
```

- [ ] **Step 2: Run smoke tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py::TestPlottingLibrariesPage -v`
Expected: 4 PASSED

- [ ] **Step 3: Run full test file**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_plotting_libraries.py -v`
Expected: All PASSED (smoke tests + chart builder tests + outlier tests)

- [ ] **Step 4: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/tests/test_plotting_libraries.py
git commit -m "test: add AppTest smoke tests for Plotting Libraries page"
```

---

### Task 9: Rename Misc Tab → Tech Stack + Add Entry

**Files:**
- Modify: `c:/codebase/finbytes_git/docs/_tabs/misc.md`

- [ ] **Step 1: Update title and lede in misc.md**

In `docs/_tabs/misc.md`, change:

```yaml
title: Misc
```
to:
```yaml
title: Tech Stack
```

And change the lede paragraph:

```html
<p class="misc-lede">Infrastructure, tooling, and systems. Practical references with code examples you can copy-paste.</p>
```
to:
```html
<p class="misc-lede">Technology stack references &mdash; libraries, infrastructure, and tooling. Practical guides with code examples you can copy-paste.</p>
```

- [ ] **Step 2: Add plotting libraries entry to the Technology references section**

In the `<ul class="misc-list">` under the "Technology references" `<div>`, add after the Streamlit entry:

```html
    <li>
      <a href="{{ "/tech-stack/plotting-libraries/" | relative_url }}">Plotting Libraries Compared</a>
      <span class="misc-desc">Plotly, Matplotlib, Altair, Bokeh &mdash; same data, four views, outlier handling</span>
    </li>
```

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/finbytes_git
git add docs/_tabs/misc.md
git commit -m "feat: rename Misc tab to Tech Stack, add plotting libraries entry"
```

---

### Task 10: Blog Article

**Files:**
- Create: `c:/codebase/finbytes_git/docs/_posts/2026-04-12-plotting-libraries-compared.html`

- [ ] **Step 1: Create the blog article**

Create `docs/_posts/2026-04-12-plotting-libraries-compared.html`:

```html
---
layout: post
title: "Plotting Libraries Compared — Plotly, Matplotlib, Altair, Bokeh"
date: 2026-04-12
tags: [python, visualization, plotly, matplotlib, altair, bokeh, tech-stack]
section: infrastructure
permalink: "/tech-stack/plotting-libraries/"
---

<h2>Why Know More Than One Charting Library</h2>

<p>If you build finance dashboards in Python, you will reach for Plotly by default &mdash; it is interactive, declarative, and works natively in Streamlit. But every library makes different trade-offs. Matplotlib gives pixel-level control for publication figures. Altair compresses complex charts into a few lines of grammar-of-graphics. Bokeh offers server-side interactivity without JavaScript. Knowing when to use each one is a practical skill.</p>

<p>This post compares all four using the same OHLCV dataset, then digs into how each handles <strong>outlier values</strong> &mdash; the most common visual problem in financial data.</p>

<h2>The Four Libraries</h2>

<table>
  <thead>
    <tr><th>Library</th><th>API Style</th><th>Interactivity</th><th>Streamlit Support</th><th>Best For</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Plotly</strong></td><td>Declarative (graph_objects) or Express</td><td>Built-in zoom, hover, pan</td><td><code>st.plotly_chart</code></td><td>Dashboards, finance charts, candlesticks</td></tr>
    <tr><td><strong>Matplotlib</strong></td><td>Imperative (axes-based)</td><td>Static by default</td><td><code>st.pyplot</code></td><td>Publication figures, full pixel control</td></tr>
    <tr><td><strong>Altair</strong></td><td>Grammar of Graphics (Vega-Lite)</td><td>Selections, tooltips</td><td><code>st.altair_chart</code></td><td>Exploratory analysis, concise code</td></tr>
    <tr><td><strong>Bokeh</strong></td><td>Glyph-based, server widgets</td><td>Built-in tools, server callbacks</td><td><code>st.bokeh_chart</code></td><td>Server-side apps, custom interactions</td></tr>
  </tbody>
</table>

<h3>Plotly</h3>

<p>Plotly is the default choice for Streamlit finance dashboards. It has native <code>Candlestick</code> and <code>OHLC</code> chart types, interactive zoom/hover out of the box, and a high-level Express API for quick plots. The trade-off: figure objects are heavy (JSON-serialised) and customisation beyond the built-in options requires verbose <code>update_layout</code> calls.</p>

<pre><code class="language-python">import plotly.graph_objects as go

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df["Open"], high=df["High"],
    low=df["Low"], close=df["Close"],
)])
st.plotly_chart(fig, use_container_width=True)
</code></pre>

<h3>Matplotlib</h3>

<p>The foundation of Python visualisation. Every other library either wraps it (Seaborn) or was built as a reaction to it (Altair, Plotly). Matplotlib gives you axes, artists, and transforms &mdash; full control over every pixel. Candlesticks require manual <code>bar</code> + <code>vlines</code> construction since there is no built-in financial chart type (without the mplfinance extension).</p>

<pre><code class="language-python">import matplotlib.pyplot as plt
import matplotlib.dates as mdates

fig, ax = plt.subplots()
up = df[df["Close"] >= df["Open"]]
ax.bar(mdates.date2num(up.index), (up["Close"] - up["Open"]),
       bottom=up["Open"], color="#2ea043", width=0.6)
ax.vlines(mdates.date2num(up.index), up["Low"], up["High"], color="#2ea043")
st.pyplot(fig)
</code></pre>

<h3>Altair</h3>

<p>Altair implements the grammar of graphics via Vega-Lite. You describe <em>what</em> to plot (encodings, marks, transforms) rather than <em>how</em> to draw it. A candlestick is a layered <code>mark_rule</code> (wicks) + <code>mark_bar</code> (bodies) with a colour encoding on the sign of close minus open. The learning curve is the grammar itself, but once internalised, charts are remarkably concise.</p>

<pre><code class="language-python">import altair as alt

rule = alt.Chart(df).mark_rule().encode(
    x="Date:T", y="Low:Q", y2="High:Q",
    color=alt.Color("color:N", scale=None),
)
bar = alt.Chart(df).mark_bar(size=6).encode(
    x="Date:T", y="Open:Q", y2="Close:Q",
    color=alt.Color("color:N", scale=None),
)
st.altair_chart(rule + bar, use_container_width=True)
</code></pre>

<h3>Bokeh</h3>

<p>Bokeh renders to HTML Canvas and provides its own toolbar (pan, zoom, reset, save). Unlike Plotly, Bokeh supports server-side callbacks and custom widgets without JavaScript. In Streamlit, <code>st.bokeh_chart</code> renders static Bokeh figures; for full server interactivity you would run Bokeh serve separately. Candlesticks use <code>segment</code> (wicks) + <code>vbar</code> (bodies).</p>

<pre><code class="language-python">from bokeh.plotting import figure

p = figure(x_axis_type="datetime", width=800, height=350)
p.segment(df.index, df["High"], df.index, df["Low"], color="black")
p.vbar(up.index, w, up["Open"], up["Close"], fill_color="#2ea043")
st.bokeh_chart(p, use_container_width=True)
</code></pre>

<h2>Handling Outliers in Financial Charts</h2>

<p>Financial data regularly contains extreme values &mdash; a flash crash, a stock split that was not adjusted, a fat-finger trade. A single outlier can compress the y-axis so severely that 99% of the data becomes an unreadable flat line. Every charting library has tools to handle this, but the approaches differ.</p>

<h3>The Problem</h3>

<p>Imagine a 6-month AAPL price history where one closing price was accidentally entered as 10x the real value. The chart auto-scales to fit the spike, and every other data point is crushed to the bottom. The distribution histogram grows a long tail with one bar far from the rest. This is not a rare edge case &mdash; it is what happens when you display raw market data without validation.</p>

<h3>Detection: 3-Sigma Flagging</h3>

<p>A simple first pass: for each numeric column, compute the z-score. Any value more than 3 standard deviations from the column mean is flagged. This catches extreme values without being sensitive to minor fluctuations.</p>

<pre><code class="language-python">z_scores = (df - df.mean()).abs() / df.std()
outliers = z_scores > 3.0
</code></pre>

<h3>Display Approaches by Library</h3>

<h4>Plotly &mdash; Annotations</h4>

<p>Plotly&rsquo;s <code>add_annotation</code> places a text label with an arrow pointing at the outlier. Combined with a separate scatter trace using red <code>x</code> markers, outliers are visually distinct without distorting the chart. For the histogram, adjusting <code>nbinsx</code> or switching to a log y-axis prevents the spike bin from dominating.</p>

<pre><code class="language-python">fig.add_trace(go.Scatter(
    x=outlier_dates, y=outlier_values,
    mode="markers", marker=dict(color="red", size=10, symbol="x"),
))
</code></pre>

<h4>Matplotlib &mdash; Annotate with Arrows</h4>

<p><code>ax.annotate</code> with <code>arrowprops</code> draws a labelled arrow to the outlier point. For axis management, <code>ax.set_ylim</code> can clip the y-axis to a sane range, pushing the outlier off-screen but keeping the rest readable. Alternatively, <code>ax.set_yscale("log")</code> compresses the dynamic range.</p>

<pre><code class="language-python">ax.annotate("outlier", xy=(date, value),
            xytext=(0, 15), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="red"))
</code></pre>

<h4>Altair &mdash; Conditional Colour Encoding</h4>

<p>Altair&rsquo;s declarative model handles this elegantly: add a boolean <code>is_outlier</code> column and use <code>alt.condition</code> to colour outlier points differently. No manual loop required. For histograms, the <code>bin</code> transform with <code>maxbins</code> can be tuned, and Altair supports log-scale axes via <code>alt.Scale(type="log")</code>.</p>

<pre><code class="language-python">points = alt.Chart(df[df["is_outlier"]]).mark_point(
    color="red", size=100, shape="cross",
).encode(x="Date:T", y="Close:Q")
</code></pre>

<h4>Bokeh &mdash; Glyph Overlay</h4>

<p>Bokeh lets you overlay a separate glyph renderer. Add <code>p.cross</code> or <code>p.circle</code> for outlier points with a distinct colour. For axis control, set <code>p.y_range = Range1d(start, end)</code> to clip, or use <code>p.y_range.bounds = (min, max)</code> to constrain interactive zooming.</p>

<pre><code class="language-python">p.cross(outlier_dates, outlier_values,
        color="red", size=12, line_width=2)
</code></pre>

<h2>When to Use What</h2>

<p><strong>Plotly</strong> &mdash; your default for Streamlit dashboards and anything interactive. Native finance chart types, minimal code, good hover tooltips. Use it unless you have a reason not to.</p>

<p><strong>Matplotlib</strong> &mdash; when you need pixel-perfect control, publication-quality static figures, or when you are working in Jupyter notebooks and want inline plots. Also the only option when mplfinance-style charts are required.</p>

<p><strong>Altair</strong> &mdash; when you want concise, declarative charts and your data fits the grammar-of-graphics mental model. Excellent for exploratory data analysis where you are layering encodings and transforms.</p>

<p><strong>Bokeh</strong> &mdash; when you need server-side interactivity, custom widget callbacks, or are building a standalone web app outside Streamlit. Overkill for simple dashboard charts but powerful for bespoke tools.</p>

<p><strong>Honourable mentions:</strong> <em>Seaborn</em> wraps Matplotlib with better defaults and statistical plotting (violin, swarm, pair plots) &mdash; great for EDA but not distinct enough to warrant its own tab here. <em>mplfinance</em> provides one-liner candlestick charts on top of Matplotlib &mdash; useful if you only need financial charts and do not want to build them manually.</p>

<h2>Try It Yourself</h2>

<p>The <a href="https://finbytes.streamlit.app/Plotting_Libraries">Plotting Libraries</a> mini project on FinBytes QuantLabs lets you load any ticker, edit the data table to inject outliers, and see all four libraries render the same charts side by side.</p>
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/finbytes_git
git add docs/_posts/2026-04-12-plotting-libraries-compared.html
git commit -m "feat: add plotting libraries comparison blog article"
```

---

### Task 11: Mini Project Page for Quant Lab Tab

**Files:**
- Create: `c:/codebase/finbytes_git/docs/_quant_lab/mini/plotting-libraries.html`
- Modify: `c:/codebase/finbytes_git/docs/_tabs/quant-lab.md`

- [ ] **Step 1: Create mini project page**

Create `docs/_quant_lab/mini/plotting-libraries.html`:

```html
---
layout: quant-lab-mini
title: "Plotting Libraries Compared"
description: "Same financial data rendered by Plotly, Matplotlib, Altair, and Bokeh — with editable data and outlier detection."
date: 2026-08-20
permalink: /quant-lab/plotting-libraries/
tech: [Python, Plotly, Matplotlib, Altair, Bokeh]
demo_url: "https://finbytes.streamlit.app/Plotting_Libraries"
category: dashboard
tech_stack:
  - name: Python
    role: Core language
  - name: yfinance
    role: Market data — OHLCV history
  - name: Plotly
    role: Interactive charts — native candlestick, hover, zoom
  - name: Matplotlib
    role: Static charts — manual candlestick, pixel control
  - name: Altair
    role: Grammar of graphics — declarative, concise
  - name: Bokeh
    role: Server-side interactive — glyph-based rendering
  - name: Streamlit
    role: Web dashboard framework with st.data_editor
---

<div id="tab-concept" class="ql-tab-content active">
  <h3>What it does</h3>
  <p>Fetches OHLCV data for any ticker and renders four chart types (line, candlestick, volume bar, returns histogram) using four different Python plotting libraries. The data table is editable — spike a value to see how each library handles outliers.</p>

  <h3>Why four libraries</h3>
  <p>Each library represents a different philosophy: <strong>Plotly</strong> is interactive and declarative, <strong>Matplotlib</strong> is imperative with pixel control, <strong>Altair</strong> uses grammar-of-graphics for concise specs, and <strong>Bokeh</strong> offers server-side rendering with glyph composition. Comparing them side-by-side reveals which tool fits which job.</p>

  <h3>Outlier handling</h3>
  <p>Financial data regularly contains extreme values. This project flags values beyond 3 standard deviations and demonstrates each library's approach to marking outliers: annotations (Plotly), arrow labels (Matplotlib), conditional encoding (Altair), and glyph overlays (Bokeh).</p>
</div>

<div id="tab-code" class="ql-tab-content" style="display:none">
  <h3>Chart builder pattern</h3>
  <pre><code class="language-python"># Each library has four functions with the same signature:
# library_chart_type(df: pd.DataFrame) -> figure_object

from lib.plotting import (
    plotly_line_chart,      matplotlib_line_chart,
    altair_line_chart,      bokeh_line_chart,
    plotly_candlestick,     matplotlib_candlestick,
    altair_candlestick,     bokeh_candlestick,
)

# Same data, different renderers
st.plotly_chart(plotly_line_chart(df))
st.pyplot(matplotlib_line_chart(df))
st.altair_chart(altair_line_chart(df))
st.bokeh_chart(bokeh_line_chart(df))
</code></pre>

  <h3>Outlier detection</h3>
  <pre><code class="language-python">def detect_outliers(df, n_std=3.0):
    numeric = df.select_dtypes(include=[np.number])
    z_scores = (numeric - numeric.mean()).abs() / numeric.std()
    return z_scores > n_std
</code></pre>
</div>
```

- [ ] **Step 2: Add entry to quant-lab.md Dashboards section**

In `docs/_tabs/quant-lab.md`, inside the `Mini Projects — Dashboards` `<ul class="ql-list">` block, add after the Financial Reporting entry:

```html
  <li>
    <a href="{{ "/quant-lab/plotting-libraries/" | relative_url }}">Plotting Libraries Compared</a>
    <span class="ql-badges"><span class="ql-badge ql-badge-mini">Mini Project</span><span class="ql-badge ql-badge-dash">Dashboard</span></span>
    <span class="ql-desc">Same data rendered by Plotly, Matplotlib, Altair, Bokeh &mdash; editable data, outlier detection</span>
    <span class="ql-tech">Python &middot; yfinance &middot; Plotly &middot; Matplotlib &middot; Altair &middot; Bokeh &middot; Streamlit</span>
  </li>
```

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/finbytes_git
git add docs/_quant_lab/mini/plotting-libraries.html docs/_tabs/quant-lab.md
git commit -m "feat: add plotting libraries mini project page and quant-lab tab entry"
```

---

### Task 12: Final Verification

**Files:** None (verification only)

- [ ] **Step 1: Run full dashboard test suite**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/ -v --tb=short`
Expected: All tests PASS including the new `test_plotting_libraries.py`

- [ ] **Step 2: Run the dashboard page locally**

Run: `cd C:/codebase/quant_lab/dashboard && streamlit run app.py`

Manually verify:
- Page 41 "Plotting Libraries" appears in the sidebar
- Default AAPL data loads in the table
- All four library tabs render charts
- Editing a Close value to 10x triggers the outlier warning
- Charts re-render with the edited data

- [ ] **Step 3: Build Jekyll site locally (if possible)**

Run: `cd C:/codebase/finbytes_git/docs && bundle exec jekyll serve`

Verify:
- Tech Stack tab shows (renamed from Misc)
- Plotting Libraries post is accessible at `/tech-stack/plotting-libraries/`
- Mini project page at `/quant-lab/plotting-libraries/` renders correctly
- Entry appears in the Quant Lab Dashboards section
