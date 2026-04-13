"""Tests for the benchmark report builders."""

import plotly.graph_objects as go
import pandas as pd
import pytest

from lib.benchmark.runner import OpResult, EngineResult
from lib.benchmark.report import build_overview_chart, build_op_card


@pytest.fixture
def fake_results():
    def er(ms, peak=10.0, rows=100):
        return EngineResult(
            ms_median=ms,
            ms_runs=[ms, ms, ms],
            peak_mb=peak,
            rows_processed=rows,
            rows_per_sec=rows / (ms / 1000) if ms else 0,
            error=None,
        )
    return [
        OpResult("read",    "Read parquet",        er(82), er(14),
                 pd.DataFrame({"a": [1, 2]}), True, "hashes match"),
        OpResult("count",   "Count rows",          er(3),  er(1),
                 100, True, "hashes match"),
        OpResult("filter",  "Filter",              er(45), er(6),
                 pd.DataFrame({"price": [500_000]}), True, "hashes match"),
        OpResult("groupby", "Groupby + aggregate", er(210), er(28),
                 pd.DataFrame({"district": ["SW1"], "mean": [2.1e6]}), True, "hashes match"),
        OpResult("sort",    "Sort",                er(90),  er(15),
                 pd.DataFrame({"price": [9_000_000]}), True, "hashes match"),
        OpResult("regex",   "String extract",      er(60),  er(8),
                 pd.DataFrame({"postcode": ["SW1A"], "extracted": ["SW"]}), True, "hashes match"),
        OpResult("write",   "Write parquet",       er(120), er(22),
                 {"path": "/tmp/out.parquet", "bytes_written": 50_000}, True, "hashes match"),
    ]


def test_build_overview_chart_returns_figure(fake_results):
    fig = build_overview_chart(fake_results)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert any(trace.name.lower() == "pandas" for trace in fig.data)
    assert any(trace.name.lower() == "polars" for trace in fig.data)


def test_build_op_card_dataframe_result(fake_results):
    card = build_op_card(fake_results[0])
    assert "headline" in card
    assert "Read parquet" in card["headline"]
    assert "82" in card["headline"]
    assert "14" in card["headline"]
    assert "preview" in card
    assert isinstance(card["preview"], pd.DataFrame)
    assert card["preview_kind"] == "dataframe"


def test_build_op_card_scalar_result(fake_results):
    card = build_op_card(fake_results[1])
    assert card["preview_kind"] == "scalar"
    assert card["preview"] == 100


def test_build_op_card_write_result(fake_results):
    card = build_op_card(fake_results[6])
    assert card["preview_kind"] == "write"
    assert "bytes_written" in card["preview"]
