"""Tests for the benchmark runner: structure, error capture, correctness."""

import pytest

from lib.benchmark.runner import run_benchmark, OpResult, EngineResult


def test_run_benchmark_returns_seven_results(tiny_ppd_path):
    results = run_benchmark(tiny_ppd_path, timed_runs=2, warmup_runs=1)
    assert isinstance(results, list)
    assert len(results) == 7
    for r in results:
        assert isinstance(r, OpResult)
        assert r.op_key in {"read", "count", "filter", "groupby", "sort", "regex", "write"}
        assert isinstance(r.pandas, EngineResult)
        assert isinstance(r.polars, EngineResult)
        assert r.pandas.error is None, f"{r.op_key} pandas error: {r.pandas.error}"
        assert r.polars.error is None, f"{r.op_key} polars error: {r.polars.error}"
        assert r.pandas.ms_median >= 0
        assert r.polars.ms_median >= 0
        assert len(r.pandas.ms_runs) == 2
        assert len(r.polars.ms_runs) == 2


def test_run_benchmark_correctness_flags_set(tiny_ppd_path):
    results = run_benchmark(tiny_ppd_path, timed_runs=2, warmup_runs=1)
    for r in results:
        assert r.correct, f"{r.op_key} correctness failed: {r.correctness_note}"


def test_run_benchmark_bad_column_captures_error(tiny_ppd_path):
    """An invalid column_config should land in EngineResult.error, not raise."""
    bad_cfg = {"numeric": "NONEXISTENT", "string": "ALSO_NONEXISTENT", "groupby": "NOPE"}
    results = run_benchmark(
        tiny_ppd_path,
        timed_runs=1,
        warmup_runs=0,
        column_config=bad_cfg,
    )
    # Read, count, write don't use column_config — they should still succeed
    read_result = next(r for r in results if r.op_key == "read")
    assert read_result.pandas.error is None
    assert read_result.polars.error is None
    # Filter, groupby, sort, regex use the config — they should report errors
    filter_result = next(r for r in results if r.op_key == "filter")
    assert filter_result.pandas.error is not None
    assert filter_result.polars.error is not None


def test_result_preview_shapes(tiny_ppd_path):
    import pandas as pd
    results = run_benchmark(tiny_ppd_path, timed_runs=1, warmup_runs=0)
    by_key = {r.op_key: r for r in results}
    for key in ("read", "filter", "groupby", "sort", "regex"):
        assert isinstance(by_key[key].result_preview, pd.DataFrame)
        assert len(by_key[key].result_preview) <= 10
    assert isinstance(by_key["count"].result_preview, int)
    assert by_key["count"].result_preview == 100
    assert isinstance(by_key["write"].result_preview, dict)
    assert "path" in by_key["write"].result_preview
    assert "bytes_written" in by_key["write"].result_preview
