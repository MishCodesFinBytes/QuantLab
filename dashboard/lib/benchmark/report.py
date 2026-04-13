"""Report builders: Plotly overview chart + per-op card contents."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from .runner import OpResult


def build_overview_chart(results) -> go.Figure:
    """Grouped bar chart: ops on x-axis, wall ms on y-axis, pandas vs polars."""
    labels = [r.op_label for r in results]
    pandas_ms = [r.pandas.ms_median if r.pandas.error is None else None for r in results]
    polars_ms = [r.polars.ms_median if r.polars.error is None else None for r in results]

    fig = go.Figure()
    fig.add_bar(name="pandas", x=labels, y=pandas_ms, marker_color="#2a7ae2")
    fig.add_bar(name="polars", x=labels, y=polars_ms, marker_color="#e8893c")
    fig.update_layout(
        barmode="group",
        title="Wall time per operation (lower is faster)",
        xaxis_title="Operation",
        yaxis_title="Milliseconds (median of 3 runs)",
        legend_title="Engine",
        height=400,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    return fig


def _fmt_ms(er) -> str:
    if er.error is not None:
        return "❌"
    return f"{er.ms_median:.0f}ms"


def _speedup(pd_er, pl_er) -> str:
    if pd_er.error is not None or pl_er.error is not None:
        return ""
    if pl_er.ms_median == 0:
        return ""
    ratio = pd_er.ms_median / pl_er.ms_median
    return f"{ratio:.1f}x"


def build_op_card(result: OpResult) -> dict:
    """Build a dict the Streamlit UI renders inside an expander.

    Returns:
        {
            "headline": str,
            "preview": Any,
            "preview_kind": str,    # "dataframe" | "scalar" | "write" | "unknown"
            "warning": str | None,
        }
    """
    pd_ms = _fmt_ms(result.pandas)
    pl_ms = _fmt_ms(result.polars)
    speedup = _speedup(result.pandas, result.polars)
    speedup_frag = f" · {speedup}" if speedup else ""
    headline = f"{result.op_label}  ·  pandas {pd_ms}  ·  polars {pl_ms}{speedup_frag}"

    preview = result.result_preview
    if isinstance(preview, pd.DataFrame):
        kind = "dataframe"
    elif isinstance(preview, (int, float)):
        kind = "scalar"
    elif isinstance(preview, dict):
        kind = "write"
    else:
        kind = "unknown"

    warning = None
    if not result.correct:
        warning = f"⚠ {result.correctness_note}"

    return {
        "headline": headline,
        "preview": preview,
        "preview_kind": kind,
        "warning": warning,
    }
