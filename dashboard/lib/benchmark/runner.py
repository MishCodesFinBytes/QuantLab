"""Benchmark orchestrator: warmup, timing, memory, correctness."""

from __future__ import annotations

import gc
import hashlib
import statistics
import time
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import polars as pl

from . import engines as E


@dataclass
class EngineResult:
    ms_median: float = 0.0
    ms_runs: list = field(default_factory=list)
    peak_mb: float = 0.0
    rows_processed: int = 0
    rows_per_sec: float = 0.0
    error: str | None = None


@dataclass
class OpResult:
    op_key: str
    op_label: str
    pandas: EngineResult
    polars: EngineResult
    result_preview: Any
    correct: bool
    correctness_note: str


def _hash_result(value: Any) -> str:
    """Deterministic hash of an op's output, order-independent for DataFrames."""
    if isinstance(value, (int, float)):
        return f"scalar:{value}"
    if isinstance(value, dict):
        # Write op: bytes differ between engines due to compression defaults.
        # Correctness is "both engines wrote a valid parquet" which is already
        # implied by the absence of an exception — return a constant sentinel.
        return "write:ok"
    if isinstance(value, pl.DataFrame):
        value = value.to_pandas()
    if isinstance(value, pd.DataFrame):
        if value.empty:
            return "empty"
        sorted_df = value.sort_values(list(value.columns)).reset_index(drop=True)
        vals = pd.util.hash_pandas_object(sorted_df).values.tobytes()
        return hashlib.sha1(vals).hexdigest()
    return f"unknown:{type(value).__name__}"


def _time_once(fn: Callable, *args, **kwargs):
    """Run fn once with tracemalloc + wall clock. Returns (wall_ms, peak_mb, result)."""
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    t1 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    wall_ms = (t1 - t0) * 1000.0
    peak_mb = peak / (1024 * 1024)
    return wall_ms, peak_mb, result


def _measure_engine(fn: Callable, args_factory: Callable, warmup_runs: int, timed_runs: int):
    """Run warmup + timed runs. Returns (EngineResult, last_result)."""
    result_value: Any = None
    for _ in range(warmup_runs):
        try:
            _time_once(fn, *args_factory())
        except Exception:
            pass
    ms_runs = []
    peak_runs = []
    error: str | None = None
    for _ in range(timed_runs):
        try:
            wall_ms, peak_mb, result_value = _time_once(fn, *args_factory())
            ms_runs.append(wall_ms)
            peak_runs.append(peak_mb)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            break
    if error is not None:
        return EngineResult(error=error), None
    rows = _row_count(result_value)
    total_s = sum(ms_runs) / 1000.0 if ms_runs else 0.0
    rows_per_sec = (rows * len(ms_runs) / total_s) if total_s > 0 else 0.0
    return (
        EngineResult(
            ms_median=statistics.median(ms_runs),
            ms_runs=ms_runs,
            peak_mb=max(peak_runs),
            rows_processed=rows,
            rows_per_sec=rows_per_sec,
            error=None,
        ),
        result_value,
    )


def _row_count(value: Any) -> int:
    if isinstance(value, pd.DataFrame):
        return len(value)
    if isinstance(value, pl.DataFrame):
        return value.height
    if isinstance(value, int):
        return value
    return 0


def _build_preview(op_key: str, value: Any) -> Any:
    """Normalize an op's raw output into a small preview for UI rendering."""
    if op_key == "count":
        return int(value) if value is not None else 0
    if op_key == "write":
        return dict(value) if value is not None else {}
    if isinstance(value, pl.DataFrame):
        value = value.to_pandas()
    if isinstance(value, pd.DataFrame):
        return value.head(10).reset_index(drop=True)
    return value


def run_benchmark(
    parquet_path,
    ops=None,
    column_config=None,
    warmup_runs: int = 1,
    timed_runs: int = 3,
):
    """Run the benchmark suite on one parquet file.

    Returns list[OpResult] in the order defined by E.OPS.
    """
    parquet_path = Path(parquet_path)
    op_keys = ops or [op["key"] for op in E.OPS]

    if column_config is None:
        peek = pd.read_parquet(parquet_path)
        column_config = E.default_column_config(peek)
        del peek
        gc.collect()

    results = []
    for op_spec in E.OPS:
        key = op_spec["key"]
        if key not in op_keys:
            continue
        pd_engine_result, pd_value = _run_op_engine(
            key, "pd", parquet_path, column_config, warmup_runs, timed_runs
        )
        pl_engine_result, pl_value = _run_op_engine(
            key, "pl", parquet_path, column_config, warmup_runs, timed_runs
        )

        if pd_engine_result.error is None and pl_engine_result.error is None:
            pd_hash = _hash_result(pd_value)
            pl_hash = _hash_result(pl_value)
            correct = pd_hash == pl_hash
            note = "hashes match" if correct else "hash mismatch"
        elif pd_engine_result.error is None:
            correct = False
            note = "only pandas ran"
        elif pl_engine_result.error is None:
            correct = False
            note = "only polars ran"
        else:
            correct = False
            note = "both engines failed"

        preview_source = pd_value if pd_value is not None else pl_value
        preview = _build_preview(key, preview_source)

        results.append(
            OpResult(
                op_key=key,
                op_label=op_spec["label"],
                pandas=pd_engine_result,
                polars=pl_engine_result,
                result_preview=preview,
                correct=correct,
                correctness_note=note,
            )
        )
    return results


def _run_op_engine(op_key, engine, parquet_path, column_config, warmup_runs, timed_runs):
    """Dispatch to the right engine function and measure it."""
    numeric = column_config["numeric"]
    string = column_config["string"]
    groupby = column_config["groupby"]

    def load_pd():
        return pd.read_parquet(parquet_path)

    def load_pl():
        return pl.read_parquet(parquet_path)

    if op_key == "read":
        fn = E.pd_read if engine == "pd" else E.pl_read
        args_factory = lambda: (parquet_path,)
    elif op_key == "count":
        fn = E.pd_count if engine == "pd" else E.pl_count
        args_factory = (lambda: (load_pd(),)) if engine == "pd" else (lambda: (load_pl(),))
    elif op_key == "filter":
        # Threshold is computed once from a separate pandas load so it's
        # identical for both engines.
        threshold = pd.read_parquet(parquet_path)[numeric].median() if numeric in pd.read_parquet(parquet_path).columns else 0
        fn = E.pd_filter if engine == "pd" else E.pl_filter
        args_factory = (
            (lambda: (load_pd(), numeric, threshold)) if engine == "pd"
            else (lambda: (load_pl(), numeric, threshold))
        )
    elif op_key == "groupby":
        fn = E.pd_groupby if engine == "pd" else E.pl_groupby
        args_factory = (
            (lambda: (load_pd(), groupby, numeric)) if engine == "pd"
            else (lambda: (load_pl(), groupby, numeric))
        )
    elif op_key == "sort":
        fn = E.pd_sort if engine == "pd" else E.pl_sort
        args_factory = (
            (lambda: (load_pd(), numeric)) if engine == "pd"
            else (lambda: (load_pl(), numeric))
        )
    elif op_key == "regex":
        pattern = r"^([A-Z]+)"
        fn = E.pd_regex if engine == "pd" else E.pl_regex
        args_factory = (
            (lambda: (load_pd(), string, pattern)) if engine == "pd"
            else (lambda: (load_pl(), string, pattern))
        )
    elif op_key == "write":
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp(prefix="bench_"))
        fn = E.pd_write if engine == "pd" else E.pl_write
        counter = {"i": 0}

        def wfactory():
            counter["i"] += 1
            return (
                load_pd() if engine == "pd" else load_pl(),
                tmp_dir / f"out_{engine}_{counter['i']}.parquet",
            )
        args_factory = wfactory
    else:
        raise ValueError(f"Unknown op_key: {op_key}")

    return _measure_engine(fn, args_factory, warmup_runs, timed_runs)
