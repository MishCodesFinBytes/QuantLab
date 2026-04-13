# Benchmark Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Benchmark Lab" tab to the existing London House Prices Streamlit page that times 7 dataframe operations across pandas and polars, shows each op's real result alongside its timing, and embeds a PyGWalker explorer on the underlying dataset.

**Architecture:** A new `dashboard/lib/benchmark/` package holds pure engine functions (pandas + polars), a timing/memory runner, a preset dataset lookup, and a report builder. The existing [dashboard/pages/42_London_House_Prices.py](dashboard/pages/42_London_House_Prices.py) gains a 4th `st.tabs()` entry that wires those modules into the UI. Two bundled parquet files (existing 5 MB London file + new ~50 MB England-wide file built by a one-time script) act as preset datasets.

**Tech Stack:** Python 3.11, pandas, polars, PyGWalker (StreamlitRenderer), pytest, Streamlit, Plotly.

**Spec reference:** [docs/superpowers/specs/2026-04-13-benchmark-lab-design.md](../specs/2026-04-13-benchmark-lab-design.md)

---

## File Structure

**Created:**

| Path | Purpose |
|---|---|
| `dashboard/lib/benchmark/__init__.py` | Package marker, re-exports public API |
| `dashboard/lib/benchmark/engines.py` | Pure pandas + polars op functions |
| `dashboard/lib/benchmark/runner.py` | Timing + memory + correctness orchestration |
| `dashboard/lib/benchmark/datasets.py` | Preset parquet file lookup |
| `dashboard/lib/benchmark/report.py` | Plotly chart + op card builders |
| `dashboard/scripts/build_benchmark_parquet.py` | One-time script to create the large parquet from gov.uk source |
| `dashboard/tests/fixtures/tiny_ppd.parquet` | 100-row test fixture (binary, not editable) |
| `dashboard/tests/conftest.py` (extend) | Add `tiny_ppd_path` fixture |
| `dashboard/tests/test_benchmark_engines.py` | Parametrized parity tests per op |
| `dashboard/tests/test_benchmark_runner.py` | Runner structure + error capture tests |
| `dashboard/tests/test_benchmark_datasets.py` | Preset lookup test |
| `dashboard/tests/test_benchmark_report.py` | Chart builder test |

**Modified:**

| Path | Change |
|---|---|
| `dashboard/pages/42_London_House_Prices.py` | Add 4th tab "Benchmark Lab" with selector, run button, results UI, PyGWalker section |
| `dashboard/requirements.txt` | Add `polars>=1.0` and `pygwalker>=0.4` |

**Not created by this plan:**

- `dashboard/data/england_ppd_benchmark.parquet` — the user runs `build_benchmark_parquet.py` once locally to generate and commit it. Plan tasks work around its absence via `datasets.get_available_presets()` filtering.

---

## Task 1: Add dependencies

**Files:**
- Modify: `dashboard/requirements.txt`

- [ ] **Step 1: Read the current requirements.txt**

```bash
cat dashboard/requirements.txt
```

- [ ] **Step 2: Append the two new dependencies**

Append to the end of `dashboard/requirements.txt`:

```
polars>=1.0
pygwalker>=0.4
```

If the file already has either line, do not duplicate — verify both lines exist after the edit.

- [ ] **Step 3: Install locally**

```bash
cd dashboard && pip install polars pygwalker
```

Expected: both install successfully. Confirm with:

```bash
python -c "import polars; import pygwalker; print(polars.__version__, pygwalker.__version__)"
```

- [ ] **Step 4: Commit**

```bash
git add dashboard/requirements.txt
git commit -m "chore(benchmark): add polars and pygwalker dependencies"
```

---

## Task 2: Create the benchmark package skeleton

**Files:**
- Create: `dashboard/lib/benchmark/__init__.py`

- [ ] **Step 1: Create the package directory and init file**

Write `dashboard/lib/benchmark/__init__.py`:

```python
"""Benchmark Lab package — pandas vs polars timing suite.

Public API:
- run_benchmark(path, ...) -> list[OpResult]
- get_available_presets() -> dict[str, dict]
- build_overview_chart(results) -> plotly.graph_objects.Figure
- build_op_card(result) -> dict
- OpResult, EngineResult (dataclasses)
"""

from .runner import run_benchmark, OpResult, EngineResult
from .datasets import get_available_presets, PRESETS
from .report import build_overview_chart, build_op_card

__all__ = [
    "run_benchmark",
    "OpResult",
    "EngineResult",
    "get_available_presets",
    "PRESETS",
    "build_overview_chart",
    "build_op_card",
]
```

Note: this file imports from modules that don't exist yet. Python allows this — the error only fires at import time. We'll create those modules in later tasks. For this task, we only commit the `__init__.py` file.

- [ ] **Step 2: Commit**

```bash
git add dashboard/lib/benchmark/__init__.py
git commit -m "feat(benchmark): scaffold benchmark package"
```

---

## Task 3: Generate the tiny test fixture

**Files:**
- Create: `dashboard/tests/fixtures/tiny_ppd.parquet`
- Modify: `dashboard/tests/conftest.py`

- [ ] **Step 1: Generate the fixture**

Create `dashboard/tests/fixtures/` directory if it doesn't exist. Then run this Python snippet to generate the fixture from the existing small parquet:

```bash
cd dashboard && python -c "
import pandas as pd
from pathlib import Path
src = Path('data/london_ppd.parquet')
dst = Path('tests/fixtures/tiny_ppd.parquet')
dst.parent.mkdir(parents=True, exist_ok=True)
df = pd.read_parquet(src)
# Take a deterministic 100-row sample seeded for reproducibility
sample = df.sample(n=100, random_state=42).reset_index(drop=True)
sample.to_parquet(dst, index=False)
print(f'Wrote {len(sample)} rows to {dst}, columns: {list(sample.columns)}')
"
```

Expected: `Wrote 100 rows to tests/fixtures/tiny_ppd.parquet, columns: [...]`

Verify the file exists and is small (~10 KB):

```bash
ls -l dashboard/tests/fixtures/tiny_ppd.parquet
```

- [ ] **Step 2: Add a pytest fixture for the path**

Read the existing `dashboard/tests/conftest.py`. Append to the end of the file:

```python
from pathlib import Path


@pytest.fixture
def tiny_ppd_path():
    """Path to the 100-row Price Paid parquet fixture."""
    return Path(__file__).parent / "fixtures" / "tiny_ppd.parquet"


@pytest.fixture
def tiny_ppd_df(tiny_ppd_path):
    """The 100-row Price Paid DataFrame, loaded fresh per test."""
    return pd.read_parquet(tiny_ppd_path)
```

If `from pathlib import Path` already exists at the top of conftest.py, do not add it again.

- [ ] **Step 3: Sanity-check the fixture loads**

```bash
cd dashboard && python -m pytest --collect-only tests/ 2>&1 | grep -i benchmark | head
```

Expected: no new collection errors from conftest changes. (No benchmark tests exist yet — this just confirms conftest.py parses.)

- [ ] **Step 4: Commit**

```bash
git add dashboard/tests/fixtures/tiny_ppd.parquet dashboard/tests/conftest.py
git commit -m "test(benchmark): add tiny 100-row ppd fixture"
```

---

## Task 4: Write failing tests for `engines.py`

**Files:**
- Create: `dashboard/tests/test_benchmark_engines.py`

- [ ] **Step 1: Write the test file**

Write `dashboard/tests/test_benchmark_engines.py`:

```python
"""Parity tests for pandas and polars engine implementations.

For each of the 7 operations, we run both engines on the tiny fixture
and confirm they produce equivalent results (after sorting and hashing).
"""

import hashlib

import pandas as pd
import polars as pl
import pytest

from lib.benchmark.engines import (
    OPS,
    pd_read,
    pl_read,
    pd_count,
    pl_count,
    pd_filter,
    pl_filter,
    pd_groupby,
    pl_groupby,
    pd_sort,
    pl_sort,
    pd_regex,
    pl_regex,
    pd_write,
    pl_write,
    default_column_config,
)


def _hash_df(df: pd.DataFrame) -> str:
    """Deterministic hash of a DataFrame ignoring row order."""
    if df.empty:
        return "empty"
    sorted_df = df.sort_values(list(df.columns)).reset_index(drop=True)
    vals = pd.util.hash_pandas_object(sorted_df).values.tobytes()
    return hashlib.sha1(vals).hexdigest()


def test_ops_constant_has_seven_entries():
    assert len(OPS) == 7
    assert [op["key"] for op in OPS] == [
        "read", "count", "filter", "groupby", "sort", "regex", "write",
    ]


def test_default_column_config_resolves(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    assert cfg["numeric"] in tiny_ppd_df.columns
    assert cfg["string"] in tiny_ppd_df.columns
    assert cfg["groupby"] in tiny_ppd_df.columns


def test_read_parity(tiny_ppd_path):
    pd_df = pd_read(tiny_ppd_path)
    pl_df = pl_read(tiny_ppd_path).to_pandas()
    assert _hash_df(pd_df) == _hash_df(pl_df)


def test_count_parity(tiny_ppd_df):
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    assert pd_count(pd_df) == pl_count(pl_df) == 100


def test_filter_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    threshold = pd_df[cfg["numeric"]].median()
    pd_out = pd_filter(pd_df, cfg["numeric"], threshold)
    pl_out = pl_filter(pl_df, cfg["numeric"], threshold).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_groupby_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_out = pd_groupby(pd_df, cfg["groupby"], cfg["numeric"])
    pl_out = pl_groupby(pl_df, cfg["groupby"], cfg["numeric"]).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_sort_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_out = pd_sort(pd_df, cfg["numeric"])
    pl_out = pl_sort(pl_df, cfg["numeric"]).to_pandas()
    # Sort results SHOULD have the same row set, order determined by sort key
    # Compare after re-sorting both deterministically
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_regex_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pattern = r"^([A-Z]+)"
    pd_out = pd_regex(pd_df, cfg["string"], pattern)
    pl_out = pl_regex(pl_df, cfg["string"], pattern).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_write_parity(tiny_ppd_df, tmp_path):
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_path = tmp_path / "pd_out.parquet"
    pl_path = tmp_path / "pl_out.parquet"
    pd_result = pd_write(pd_df, pd_path)
    pl_result = pl_write(pl_df, pl_path)
    # Write returns a dict {path, bytes_written}
    assert pd_result["path"] == pd_path
    assert pl_result["path"] == pl_path
    assert pd_path.exists()
    assert pl_path.exists()
    # Both parquets should round-trip to identical DataFrames
    pd_roundtrip = pd.read_parquet(pd_path)
    pl_roundtrip = pd.read_parquet(pl_path)
    assert _hash_df(pd_roundtrip) == _hash_df(pl_roundtrip)
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd dashboard && python -m pytest tests/test_benchmark_engines.py -v
```

Expected: `ImportError: cannot import name 'OPS' from 'lib.benchmark.engines'` (or similar). All 10 tests fail at collection time because `engines.py` does not yet exist.

---

## Task 5: Implement `engines.py`

**Files:**
- Create: `dashboard/lib/benchmark/engines.py`

- [ ] **Step 1: Write the engines module**

Write `dashboard/lib/benchmark/engines.py`:

```python
"""Pure pandas + polars implementations of 7 dataframe operations.

Each function is side-effect-free except `pd_write` / `pl_write`, which
accept a target path. No timing, memory, or logging — the runner owns
those concerns.

Column roles:
- numeric: the column filtered, sorted, and aggregated
- string:  the column regex is applied to
- groupby: the column rows are grouped by
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import polars as pl


OPS = [
    {"key": "read",    "label": "Read parquet"},
    {"key": "count",   "label": "Count rows"},
    {"key": "filter",  "label": "Filter"},
    {"key": "groupby", "label": "Groupby + aggregate"},
    {"key": "sort",    "label": "Sort"},
    {"key": "regex",   "label": "String extract (regex)"},
    {"key": "write",   "label": "Write parquet"},
]


def default_column_config(df: pd.DataFrame) -> dict:
    """Pick sensible numeric/string/groupby columns from the schema.

    - numeric: first numeric dtype column
    - string:  first object/string dtype column
    - groupby: first string column that has fewer unique values than rows
    """
    numeric = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])), None)
    string = next((c for c in df.columns if pd.api.types.is_object_dtype(df[c])), None)
    groupby = next(
        (c for c in df.columns
         if pd.api.types.is_object_dtype(df[c]) and df[c].nunique() < len(df)),
        string,
    )
    if numeric is None or string is None or groupby is None:
        raise ValueError(
            f"Could not auto-detect columns from schema {list(df.columns)}. "
            "Pass an explicit column_config."
        )
    return {"numeric": numeric, "string": string, "groupby": groupby}


# --- Op 1: Read parquet ----------------------------------------------------

def pd_read(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def pl_read(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)


# --- Op 2: Count rows ------------------------------------------------------

def pd_count(df: pd.DataFrame) -> int:
    return len(df)


def pl_count(df: pl.DataFrame) -> int:
    return df.height


# --- Op 3: Filter ----------------------------------------------------------

def pd_filter(df: pd.DataFrame, col: str, threshold) -> pd.DataFrame:
    return df[df[col] > threshold]


def pl_filter(df: pl.DataFrame, col: str, threshold) -> pl.DataFrame:
    return df.filter(pl.col(col) > threshold)


# --- Op 4: Groupby + aggregate ---------------------------------------------

def pd_groupby(df: pd.DataFrame, group_col: str, numeric_col: str) -> pd.DataFrame:
    return (
        df.groupby(group_col)[numeric_col]
        .agg(["mean", "median", "count"])
        .reset_index()
    )


def pl_groupby(df: pl.DataFrame, group_col: str, numeric_col: str) -> pl.DataFrame:
    return df.group_by(group_col).agg([
        pl.col(numeric_col).mean().alias("mean"),
        pl.col(numeric_col).median().alias("median"),
        pl.col(numeric_col).count().alias("count"),
    ])


# --- Op 5: Sort ------------------------------------------------------------

def pd_sort(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.sort_values(col, ascending=False).reset_index(drop=True)


def pl_sort(df: pl.DataFrame, col: str) -> pl.DataFrame:
    return df.sort(col, descending=True)


# --- Op 6: String extract (regex) ------------------------------------------

def pd_regex(df: pd.DataFrame, col: str, pattern: str) -> pd.DataFrame:
    extracted = df[col].str.extract(pattern, expand=False)
    return pd.DataFrame({col: df[col], "extracted": extracted})


def pl_regex(df: pl.DataFrame, col: str, pattern: str) -> pl.DataFrame:
    return df.select([
        pl.col(col),
        pl.col(col).str.extract(pattern, 1).alias("extracted"),
    ])


# --- Op 7: Write parquet ---------------------------------------------------

def pd_write(df: pd.DataFrame, path: Path) -> dict:
    df.to_parquet(path, index=False)
    return {"path": path, "bytes_written": path.stat().st_size}


def pl_write(df: pl.DataFrame, path: Path) -> dict:
    df.write_parquet(path)
    return {"path": path, "bytes_written": path.stat().st_size}
```

- [ ] **Step 2: Run the tests again — all 10 should now pass**

```bash
cd dashboard && python -m pytest tests/test_benchmark_engines.py -v
```

Expected: `10 passed`. If any fail, read the failure carefully — the usual suspect is row order from groupby (polars doesn't guarantee group order). The `_hash_df` helper in the test sorts before hashing, so true data differences should surface cleanly.

- [ ] **Step 3: Commit**

```bash
git add dashboard/lib/benchmark/engines.py dashboard/tests/test_benchmark_engines.py
git commit -m "feat(benchmark): add pandas and polars engine implementations with parity tests"
```

---

## Task 6: Write failing tests for `runner.py`

**Files:**
- Create: `dashboard/tests/test_benchmark_runner.py`

- [ ] **Step 1: Write the test file**

Write `dashboard/tests/test_benchmark_runner.py`:

```python
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
        # Tiny fixture is valid so no errors expected
        assert r.pandas.error is None, f"{r.op_key} pandas error: {r.pandas.error}"
        assert r.polars.error is None, f"{r.op_key} polars error: {r.polars.error}"
        assert r.pandas.ms_median > 0
        assert r.polars.ms_median > 0
        assert len(r.pandas.ms_runs) == 2
        assert len(r.polars.ms_runs) == 2


def test_run_benchmark_correctness_flags_set(tiny_ppd_path):
    results = run_benchmark(tiny_ppd_path, timed_runs=2, warmup_runs=1)
    for r in results:
        # Every op on valid data should agree
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
    # Read, filter, groupby, sort, regex → DataFrame preview
    for key in ("read", "filter", "groupby", "sort", "regex"):
        assert isinstance(by_key[key].result_preview, pd.DataFrame)
        assert len(by_key[key].result_preview) <= 10
    # Count → int
    assert isinstance(by_key["count"].result_preview, int)
    assert by_key["count"].result_preview == 100
    # Write → dict with path and bytes_written
    assert isinstance(by_key["write"].result_preview, dict)
    assert "path" in by_key["write"].result_preview
    assert "bytes_written" in by_key["write"].result_preview
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd dashboard && python -m pytest tests/test_benchmark_runner.py -v
```

Expected: ImportError for `runner` module. All 4 tests fail at collection.

---

## Task 7: Implement `runner.py`

**Files:**
- Create: `dashboard/lib/benchmark/runner.py`

- [ ] **Step 1: Write the runner module**

Write `dashboard/lib/benchmark/runner.py`:

```python
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
    ms_runs: list[float] = field(default_factory=list)
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
        # Write op returns {"path", "bytes_written"} — hash the bytes count only
        return f"write:{value.get('bytes_written', 0)}"
    if isinstance(value, pl.DataFrame):
        value = value.to_pandas()
    if isinstance(value, pd.DataFrame):
        if value.empty:
            return "empty"
        sorted_df = value.sort_values(list(value.columns)).reset_index(drop=True)
        vals = pd.util.hash_pandas_object(sorted_df).values.tobytes()
        return hashlib.sha1(vals).hexdigest()
    return f"unknown:{type(value).__name__}"


def _time_once(fn: Callable, *args, **kwargs) -> tuple[float, float, Any]:
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


def _measure_engine(
    fn: Callable, args_factory: Callable, warmup_runs: int, timed_runs: int
) -> tuple[EngineResult, Any]:
    """Run warmup + timed runs. Returns (EngineResult, last_result)."""
    result_value: Any = None
    # Warmup
    for _ in range(warmup_runs):
        try:
            _time_once(fn, *args_factory())
        except Exception:
            pass  # warmup errors are OK, real runs will fail loudly
    # Timed runs
    ms_runs: list[float] = []
    peak_runs: list[float] = []
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
    if isinstance(value, dict):
        return 0
    return 0


def _build_preview(op_key: str, value: Any) -> Any:
    """Normalize an op's raw output into a small preview for UI rendering."""
    if op_key == "count":
        return int(value)
    if op_key == "write":
        return dict(value)  # {"path", "bytes_written"}
    # All other ops return a DataFrame — take head(10), coerce polars→pandas
    if isinstance(value, pl.DataFrame):
        value = value.to_pandas()
    if isinstance(value, pd.DataFrame):
        return value.head(10).reset_index(drop=True)
    return value


def run_benchmark(
    parquet_path: Path,
    ops: list[str] | None = None,
    column_config: dict | None = None,
    warmup_runs: int = 1,
    timed_runs: int = 3,
) -> list[OpResult]:
    """Run the benchmark suite on one parquet file.

    Args:
        parquet_path: path to the input parquet
        ops: list of op keys to run (default: all 7)
        column_config: {"numeric", "string", "groupby"} column names.
                       If None, auto-detects from the pandas-loaded DataFrame.
        warmup_runs: warmup runs per engine per op (not timed)
        timed_runs: timed runs per engine per op (median reported)

    Returns:
        list of OpResult in the order defined by E.OPS.
    """
    parquet_path = Path(parquet_path)
    op_keys = ops or [op["key"] for op in E.OPS]

    # Auto-detect columns from a single pandas load if no config provided
    if column_config is None:
        peek = pd.read_parquet(parquet_path)
        column_config = E.default_column_config(peek)
        del peek
        gc.collect()

    results: list[OpResult] = []
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
        # Correctness: hash the most recent successful value from each engine
        if pd_engine_result.error is None and pl_engine_result.error is None:
            pd_hash = _hash_result(pd_value)
            pl_hash = _hash_result(pl_value)
            correct = pd_hash == pl_hash
            note = "hashes match" if correct else "hash mismatch"
        elif pd_engine_result.error is None:
            correct = False
            note = "only pandas ran"
            pl_value = None
        elif pl_engine_result.error is None:
            correct = False
            note = "only polars ran"
            pd_value = None
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


def _run_op_engine(
    op_key: str,
    engine: str,
    parquet_path: Path,
    column_config: dict,
    warmup_runs: int,
    timed_runs: int,
) -> tuple[EngineResult, Any]:
    """Dispatch to the right engine function and measure it."""
    numeric = column_config["numeric"]
    string = column_config["string"]
    groupby = column_config["groupby"]

    # For ops that need a loaded DataFrame, we load once per measurement
    # via the args_factory closure (so each run gets a fresh copy).
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
        threshold_pd = pd.read_parquet(parquet_path)[numeric].median()
        fn = E.pd_filter if engine == "pd" else E.pl_filter
        args_factory = (
            (lambda: (load_pd(), numeric, threshold_pd)) if engine == "pd"
            else (lambda: (load_pl(), numeric, threshold_pd))
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
        # Each run writes to a different filename to avoid overwrite skew
        counter = {"i": 0}
        def wfactory():
            counter["i"] += 1
            return (load_pd() if engine == "pd" else load_pl(),
                    tmp_dir / f"out_{engine}_{counter['i']}.parquet")
        args_factory = wfactory
    else:
        raise ValueError(f"Unknown op_key: {op_key}")

    return _measure_engine(fn, args_factory, warmup_runs, timed_runs)
```

- [ ] **Step 2: Run the runner tests — should now pass**

```bash
cd dashboard && python -m pytest tests/test_benchmark_runner.py -v
```

Expected: `4 passed`.

- [ ] **Step 3: Run the full benchmark test suite**

```bash
cd dashboard && python -m pytest tests/test_benchmark_engines.py tests/test_benchmark_runner.py -v
```

Expected: `14 passed` (10 engine tests + 4 runner tests).

- [ ] **Step 4: Commit**

```bash
git add dashboard/lib/benchmark/runner.py dashboard/tests/test_benchmark_runner.py
git commit -m "feat(benchmark): add runner with timing, memory, and correctness hashing"
```

---

## Task 8: Implement `datasets.py` with tests

**Files:**
- Create: `dashboard/lib/benchmark/datasets.py`
- Create: `dashboard/tests/test_benchmark_datasets.py`

- [ ] **Step 1: Write the datasets test first**

Write `dashboard/tests/test_benchmark_datasets.py`:

```python
"""Tests for the benchmark dataset preset lookup."""

from pathlib import Path

import pytest

from lib.benchmark.datasets import PRESETS, get_available_presets


def test_presets_has_small_and_large_keys():
    assert set(PRESETS.keys()) == {"small", "large"}


def test_preset_entries_have_required_fields():
    for key, entry in PRESETS.items():
        assert "label" in entry
        assert "path" in entry
        assert "description" in entry
        assert isinstance(entry["path"], Path)


def test_get_available_presets_filters_missing_files():
    """Only presets whose file exists on disk should be returned."""
    available = get_available_presets()
    for key, entry in available.items():
        assert entry["path"].exists(), f"{key} preset path does not exist"
    # Small should always be available in CI since london_ppd.parquet is committed
    assert "small" in available
```

- [ ] **Step 2: Run the test — should fail (module missing)**

```bash
cd dashboard && python -m pytest tests/test_benchmark_datasets.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write the datasets module**

Write `dashboard/lib/benchmark/datasets.py`:

```python
"""Preset parquet file lookup for the benchmark lab.

Two presets are bundled with the repo:
- small: the existing 5 MB London-only parquet
- large: a ~50 MB England-wide parquet generated by
         dashboard/scripts/build_benchmark_parquet.py

Missing files are filtered out by get_available_presets() so the
UI only offers presets whose data is actually on disk.
"""

from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

PRESETS: dict[str, dict] = {
    "small": {
        "label": "Small (5 MB · London only)",
        "path": DATA_DIR / "london_ppd.parquet",
        "description": (
            "London postcode districts, pre-processed. "
            "Quick smoke test — both engines finish in under a second."
        ),
    },
    "large": {
        "label": "Large (~50 MB · England-wide, 2 years)",
        "path": DATA_DIR / "england_ppd_benchmark.parquet",
        "description": (
            "England-wide PPD for the most recent 2 years. "
            "Shows polars' speedup dramatically on groupby and sort."
        ),
    },
}


def get_available_presets() -> dict[str, dict]:
    """Return only presets whose parquet file exists on disk."""
    return {key: entry for key, entry in PRESETS.items() if entry["path"].exists()}
```

- [ ] **Step 4: Run the test — should pass**

```bash
cd dashboard && python -m pytest tests/test_benchmark_datasets.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/benchmark/datasets.py dashboard/tests/test_benchmark_datasets.py
git commit -m "feat(benchmark): add preset dataset lookup with existence filter"
```

---

## Task 9: Implement `report.py` with tests

**Files:**
- Create: `dashboard/lib/benchmark/report.py`
- Create: `dashboard/tests/test_benchmark_report.py`

- [ ] **Step 1: Write the report test first**

Write `dashboard/tests/test_benchmark_report.py`:

```python
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
        OpResult("read",    "Read parquet",        er(82), er(14), pd.DataFrame({"a": [1, 2]}), True,  "hashes match"),
        OpResult("count",   "Count rows",          er(3),  er(1),  100, True, "hashes match"),
        OpResult("filter",  "Filter",              er(45), er(6),  pd.DataFrame({"price": [500_000]}), True, "hashes match"),
        OpResult("groupby", "Groupby + aggregate", er(210), er(28), pd.DataFrame({"district": ["SW1"], "mean": [2.1e6]}), True, "hashes match"),
        OpResult("sort",    "Sort",                er(90),  er(15), pd.DataFrame({"price": [9_000_000]}), True, "hashes match"),
        OpResult("regex",   "String extract",      er(60),  er(8),  pd.DataFrame({"postcode": ["SW1A"], "extracted": ["SW"]}), True, "hashes match"),
        OpResult("write",   "Write parquet",       er(120), er(22), {"path": "/tmp/out.parquet", "bytes_written": 50_000}, True, "hashes match"),
    ]


def test_build_overview_chart_returns_figure(fake_results):
    fig = build_overview_chart(fake_results)
    assert isinstance(fig, go.Figure)
    # Two traces: one for pandas, one for polars
    assert len(fig.data) == 2
    assert any(trace.name.lower() == "pandas" for trace in fig.data)
    assert any(trace.name.lower() == "polars" for trace in fig.data)


def test_build_op_card_dataframe_result(fake_results):
    card = build_op_card(fake_results[0])  # read op
    assert "headline" in card
    assert "Read parquet" in card["headline"]
    assert "82" in card["headline"]
    assert "14" in card["headline"]
    assert "preview" in card
    assert isinstance(card["preview"], pd.DataFrame)
    assert card["preview_kind"] == "dataframe"


def test_build_op_card_scalar_result(fake_results):
    card = build_op_card(fake_results[1])  # count op
    assert card["preview_kind"] == "scalar"
    assert card["preview"] == 100


def test_build_op_card_write_result(fake_results):
    card = build_op_card(fake_results[6])  # write op
    assert card["preview_kind"] == "write"
    assert "bytes_written" in card["preview"]
```

- [ ] **Step 2: Run the test — should fail (module missing)**

```bash
cd dashboard && python -m pytest tests/test_benchmark_report.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write the report module**

Write `dashboard/lib/benchmark/report.py`:

```python
"""Report builders: Plotly overview chart + per-op card contents."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from .runner import OpResult


def build_overview_chart(results: list[OpResult]) -> go.Figure:
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
            "headline": str,        # one-line summary with timings
            "preview": Any,         # shape depends on preview_kind
            "preview_kind": str,    # "dataframe" | "scalar" | "write"
            "warning": str | None,  # yellow warning text if correctness mismatched
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
```

- [ ] **Step 4: Run the report tests — should pass**

```bash
cd dashboard && python -m pytest tests/test_benchmark_report.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Run the full benchmark suite**

```bash
cd dashboard && python -m pytest tests/test_benchmark_engines.py tests/test_benchmark_runner.py tests/test_benchmark_datasets.py tests/test_benchmark_report.py -v
```

Expected: `21 passed` (10 + 4 + 3 + 4).

- [ ] **Step 6: Commit**

```bash
git add dashboard/lib/benchmark/report.py dashboard/tests/test_benchmark_report.py
git commit -m "feat(benchmark): add report builders for chart and op cards"
```

---

## Task 10: Write the build-benchmark-parquet helper script

This script is a one-time tool for generating `england_ppd_benchmark.parquet`. It's not imported by production code and has no tests. It just documents how the file is created.

**Files:**
- Create: `dashboard/scripts/build_benchmark_parquet.py`

- [ ] **Step 1: Create the scripts directory and write the helper**

Write `dashboard/scripts/build_benchmark_parquet.py`:

```python
"""Build the ~50 MB england_ppd_benchmark.parquet file.

One-time tool. Downloads the current UK Land Registry Price Paid Data
incremental monthly release, keeps the most recent 2 years of transactions,
and writes a compressed parquet at dashboard/data/england_ppd_benchmark.parquet.

Run:
    cd dashboard && python scripts/build_benchmark_parquet.py

Source:
    https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads

The data is published under the Open Government Licence v3.0.
"""

from __future__ import annotations

import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd

# The monthly CSV is large (~5 GB for the full archive, ~30-60 MB per month
# via the incremental feed). We use the two-year download endpoint which is
# hosted as a single CSV per recent year.
YEAR_CSV_URL = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-{year}.csv"

# Schema for the raw gov.uk CSV (headerless, 16 cols)
RAW_COLUMNS = [
    "transaction_id", "price", "date", "postcode", "property_type",
    "new_build", "duration", "paon", "saon", "street", "locality",
    "town_city", "district", "county", "ppd_category", "record_status",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_PATH = DATA_DIR / "england_ppd_benchmark.parquet"


def download_year(year: int) -> pd.DataFrame:
    url = YEAR_CSV_URL.format(year=year)
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url) as resp:
        raw = resp.read()
    print(f"  got {len(raw) / (1024*1024):.1f} MB")
    df = pd.read_csv(
        io.BytesIO(raw),
        names=RAW_COLUMNS,
        header=None,
        parse_dates=["date"],
        low_memory=False,
    )
    return df


def main() -> int:
    this_year = dt.date.today().year
    years = [this_year - 1, this_year - 2]
    frames = [download_year(y) for y in years]
    df = pd.concat(frames, ignore_index=True)
    print(f"Combined rows: {len(df):,}")

    # Match the schema of london_ppd.parquet for compatibility with the
    # rest of the page. The existing file has at minimum: postcode,
    # postcode_district, price, date. Derive postcode_district from postcode.
    df = df.dropna(subset=["postcode", "price", "date"])
    df["postcode_district"] = df["postcode"].str.split(" ").str[0]
    df = df[["transaction_id", "price", "date", "postcode",
             "postcode_district", "property_type", "town_city", "district"]]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, compression="snappy", index=False)
    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT_PATH} ({size_mb:.1f} MB, {len(df):,} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Commit**

```bash
git add dashboard/scripts/build_benchmark_parquet.py
git commit -m "feat(benchmark): add one-time script to build large benchmark parquet"
```

Note: the user runs this script once locally to generate `england_ppd_benchmark.parquet` and commits the result. This plan does NOT include that commit — the Large preset option simply stays hidden from the UI until the file exists.

---

## Task 11: Wire the new tab into the London House Prices page

**Files:**
- Modify: `dashboard/pages/42_London_House_Prices.py`

- [ ] **Step 1: Read the current page to locate the tab declaration**

```bash
grep -n "st.tabs\|tab_growth\|tab_tests" dashboard/pages/42_London_House_Prices.py
```

Expected output shows the existing `st.tabs([...])` call around line 37 and the `with tab_*:` blocks.

- [ ] **Step 2: Add the benchmark imports at the top of the page**

Find the block of imports near the top of `dashboard/pages/42_London_House_Prices.py` (after the existing `from house_prices import ...` line). Add:

```python
from benchmark import (
    run_benchmark,
    get_available_presets,
    build_overview_chart,
    build_op_card,
)
```

If a `from benchmark ...` import already exists, update it to include all four names.

- [ ] **Step 3: Add the new tab to the `st.tabs` tuple**

Find the existing line:

```python
tab_growth, tab_compare, tab_brand, tab_tests = st.tabs(
    ["Growth", "Compare", "Brand", "Tests"]
)
```

Replace with:

```python
tab_growth, tab_compare, tab_brand, tab_bench, tab_tests = st.tabs(
    ["Growth", "Compare", "Brand", "Benchmark Lab", "Tests"]
)
```

- [ ] **Step 4: Add the `with tab_bench:` block**

After the `with tab_brand:` block ends and BEFORE the `with tab_tests:` block, insert:

```python
with tab_bench:
    st.markdown("### Benchmark Lab — pandas vs polars")
    st.caption(
        "Runs 7 dataframe operations in both engines, shows each op's real "
        "result alongside its wall-time, then lets you explore the dataset "
        "in PyGWalker."
    )

    presets = get_available_presets()
    if not presets:
        st.error(
            "No benchmark dataset bundled. Run "
            "`python scripts/build_benchmark_parquet.py` to generate the "
            "large file, or ensure `data/london_ppd.parquet` exists."
        )
    else:
        preset_labels = {key: entry["label"] for key, entry in presets.items()}
        preset_keys = list(presets.keys())
        col1, col2 = st.columns([3, 1])
        with col1:
            chosen_key = st.selectbox(
                "Dataset",
                options=preset_keys,
                format_func=lambda k: preset_labels[k],
                key="bench_preset_key",
            )
        with col2:
            st.write("")  # align with selectbox
            run_clicked = st.button("▶ Run Benchmark", key="bench_run_btn",
                                    use_container_width=True)

        st.caption(presets[chosen_key]["description"])

        # Run or load cached results
        cache_key = f"bench_results_{chosen_key}"
        if run_clicked:
            with st.spinner(f"Running 7 ops × 2 engines × 4 runs on {preset_labels[chosen_key]}..."):
                st.session_state[cache_key] = run_benchmark(
                    presets[chosen_key]["path"]
                )

        results = st.session_state.get(cache_key)
        if results is None:
            st.info("Click **Run Benchmark** to start.")
        else:
            # Overview chart
            st.plotly_chart(
                build_overview_chart(results), use_container_width=True
            )

            # Per-op detail expanders
            st.markdown("#### Per-op detail")
            for result in results:
                card = build_op_card(result)
                with st.expander(card["headline"]):
                    if card["warning"]:
                        st.warning(card["warning"])
                    kind = card["preview_kind"]
                    preview = card["preview"]
                    if kind == "dataframe":
                        st.dataframe(preview, use_container_width=True)
                    elif kind == "scalar":
                        st.metric("Row count", f"{preview:,}")
                    elif kind == "write":
                        st.caption(
                            f"Wrote {preview.get('bytes_written', 0):,} bytes "
                            f"to `{preview.get('path')}`"
                        )
                    else:
                        st.write(preview)

            # PyGWalker explorer
            st.markdown("---")
            st.markdown("#### Explore the dataset yourself")
            try:
                from pygwalker.api.streamlit import StreamlitRenderer
                import pandas as pd

                pyg_cache_key = f"pyg_renderer_{chosen_key}"
                if pyg_cache_key not in st.session_state:
                    df_for_pyg = pd.read_parquet(presets[chosen_key]["path"])
                    st.session_state[pyg_cache_key] = StreamlitRenderer(
                        df_for_pyg, kernel_computation=True
                    )
                st.session_state[pyg_cache_key].explorer()
            except ImportError:
                st.info(
                    "PyGWalker not installed — run "
                    "`pip install pygwalker` to enable the interactive explorer."
                )
                import pandas as pd
                st.dataframe(
                    pd.read_parquet(presets[chosen_key]["path"]).head(100),
                    use_container_width=True,
                )
            except Exception as exc:
                st.warning(f"PyGWalker render error: {exc}")
                import pandas as pd
                st.dataframe(
                    pd.read_parquet(presets[chosen_key]["path"]).head(1000),
                    use_container_width=True,
                )
```

- [ ] **Step 5: Launch the app locally and manually verify**

```bash
cd dashboard && streamlit run app.py
```

Open http://localhost:8501, navigate to **London House Prices** page, click the **Benchmark Lab** tab. Verify:

1. The page loads without Python errors.
2. The dataset dropdown shows "Small (5 MB · London only)" (Large is hidden since the file doesn't exist yet).
3. Click **Run Benchmark**. A spinner appears.
4. After ~1–2 seconds, the overview bar chart renders.
5. The 7 per-op expanders appear with timing headlines.
6. Expanding each one shows the appropriate preview: DataFrame for most, row count metric for Count, bytes written caption for Write.
7. The PyGWalker explorer renders below and is interactive (drag columns to axes, try a bar chart).
8. Switch to another tab (e.g., Growth) and back — benchmark results are still shown (cached in session state).

Stop the server (Ctrl+C) when verified.

- [ ] **Step 6: Commit**

```bash
git add dashboard/pages/42_London_House_Prices.py
git commit -m "feat(benchmark): wire Benchmark Lab tab into London House Prices page"
```

---

## Task 12: Final test run + manual verification

**Files:** none (verification only)

- [ ] **Step 1: Run the full test suite**

```bash
cd dashboard && python -m pytest tests/ -v 2>&1 | tail -40
```

Expected: all existing tests still pass plus the new 21 benchmark tests. Zero failures, zero errors.

- [ ] **Step 2: Run the focused benchmark suite**

```bash
cd dashboard && python -m pytest tests/test_benchmark*.py -v
```

Expected: `21 passed` (10 engines + 4 runner + 3 datasets + 4 report).

- [ ] **Step 3: Manual verification checklist**

Start the app:

```bash
cd dashboard && streamlit run app.py
```

- [ ] London House Prices page loads without errors
- [ ] Benchmark Lab tab is present between Brand and Tests
- [ ] Dataset dropdown shows Small only (Large hidden until file bundled)
- [ ] Run Benchmark button triggers a spinner, completes in under 5 seconds
- [ ] Overview Plotly chart shows 7 ops × 2 engine bars each
- [ ] All 7 expanders appear with headline format: `<Op>  ·  pandas Xms  ·  polars Yms  ·  Nx`
- [ ] Read/Filter/Groupby/Sort/Regex expanders show a DataFrame preview (≤10 rows)
- [ ] Count expander shows a metric widget with row count
- [ ] Write expander shows the bytes-written caption
- [ ] PyGWalker explorer renders below with the full dataset
- [ ] Dragging a column in PyGWalker produces a chart
- [ ] Tab switch and return: results are still displayed (session cache)
- [ ] No uncaught exceptions in the terminal streamlit log

- [ ] **Step 4: Full commit+push workflow**

Per project convention for QuantLab, commits go via PR to master:

```bash
git push origin working
```

Then open a PR from `working` to `master` via GitHub or `gh pr create` for the user to review and merge.

---

## Self-Review Notes

**Spec coverage check:**

- ✅ 7 benchmark ops (Task 5 — engines.py)
- ✅ Median of 3 runs + 1 warmup (Task 7 — runner.py, `timed_runs=3, warmup_runs=1`)
- ✅ Peak memory via tracemalloc (Task 7 — `_time_once`)
- ✅ `gc.collect()` between engines (Task 7 — inside `_time_once`)
- ✅ Correctness hash with sort (Task 7 — `_hash_result`)
- ✅ Per-engine error capture (Task 7 — try/except in `_measure_engine`)
- ✅ Result preview shapes (Task 7 — `_build_preview`, Task 9 — `build_op_card`)
- ✅ Plotly overview chart (Task 9 — `build_overview_chart`)
- ✅ Per-op expanders (Task 11 — page integration)
- ✅ Dataset size selector (Task 11)
- ✅ PyGWalker lazy rendering with fallback (Task 11 — try/except ImportError + Exception)
- ✅ Tab order Growth → Compare → Brand → Benchmark Lab → Tests (Task 11)
- ✅ Session state caching (Task 11 — `st.session_state[cache_key]`)
- ✅ Missing Large file handled (Task 8 — `get_available_presets()`, Task 11 — only shows available)
- ✅ Tests for engines, runner, datasets, report (Tasks 4, 6, 8, 9)
- ✅ Tiny fixture for tests (Task 3)
- ✅ Dependencies (Task 1)
- ✅ Build script for large parquet (Task 10)

**Placeholder scan:** no TBD/TODO strings in tasks. All code blocks are complete.

**Type consistency:**
- `OpResult.pandas` and `OpResult.polars` are both `EngineResult` throughout
- `result_preview` is typed `Any` in dataclass, normalized in `_build_preview`, and dispatched on in `build_op_card` — kinds are `"dataframe" | "scalar" | "write"` consistently
- `get_available_presets()` returns the same shape as `PRESETS` (dict of dicts with keys `label`, `path`, `description`) — consistent in Task 8 test and Task 11 consumer
- `run_benchmark(parquet_path, ops, column_config, warmup_runs, timed_runs)` signature matches in definition (Task 7) and test call (Task 6)

**Scope check:** single feature, single plan. ~21 tests, ~1000 lines of production code. Appropriate for one implementation session.

No gaps found.
