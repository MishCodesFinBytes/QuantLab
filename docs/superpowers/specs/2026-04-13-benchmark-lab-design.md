# Benchmark Lab — Pandas vs Polars + PyGWalker Explorer

**Date:** 2026-04-13 (originally drafted), resumed same day
**Status:** Final — ready for implementation plan

## Goal

Add a "Benchmark Lab" tab to the existing London House Prices page in the QuantLab Streamlit dashboard that:

1. Runs a fixed suite of 7 dataframe operations in both pandas and polars on UK Land Registry Price Paid Data
2. Shows per-op timing comparison (wall ms, peak memory, speedup ratio) alongside each op's actual result as a small preview
3. Embeds a PyGWalker interactive explorer on the same dataset at the bottom of the tab for ad-hoc drill-down

The user has published a [pandas-vs-polars blog post](https://mish-codes.github.io/FinBytes/posts/pandas-vs-polars/) but has not shipped polars in code anywhere. This project closes that loop with a working empirical demonstration.

## Non-goals

- No URL file fetch, no `st.file_uploader`, no cloud storage — benchmark runs against bundled parquet files only
- No preset "analysis questions" feature (PyGWalker replaces that)
- No custom dataset upload — user picks between two bundled presets
- No automatic CI benchmark runs — this is a manual interactive tool, not a regression suite
- No JavaScript-level PyGWalker testing — UI library, manual verification only

## Architecture

### Files

| Path | Status | Purpose |
|---|---|---|
| `dashboard/lib/benchmark/__init__.py` | New | Package marker |
| `dashboard/lib/benchmark/engines.py` | New | Pure pandas + polars implementations of the 7 ops, no timing |
| `dashboard/lib/benchmark/runner.py` | New | Orchestration: warmup, median-of-3 timing, memory sampling, correctness hashing, error capture |
| `dashboard/lib/benchmark/datasets.py` | New | Lookup table of the 2 preset parquet files |
| `dashboard/lib/benchmark/report.py` | New | Results → Plotly overview chart + per-op card contents + markdown export |
| `dashboard/pages/42_London_House_Prices.py` | Modified | New "Benchmark Lab" tab added between "Brand" and "Tests" |
| `dashboard/data/england_ppd_benchmark.parquet` | New (~50 MB) | Large benchmark dataset — England-wide PPD, 2-year window, pre-processed |
| `dashboard/data/london_ppd.parquet` | Existing (5.4 MB) | Reused as the "Small" option |
| `dashboard/tests/fixtures/tiny_ppd.parquet` | New (~10 KB) | 100-row test fixture with same schema |
| `dashboard/tests/test_benchmark_engines.py` | New | Parity tests for each op × engine |
| `dashboard/tests/test_benchmark_runner.py` | New | Runner structure + error capture tests |
| `dashboard/requirements.txt` | Modified | Add `pygwalker`, `polars` |

### Why this split

- `engines.py` is pure functions, pytest-able without Streamlit's harness.
- `runner.py` owns all timing/memory code so engine functions stay side-effect-free.
- `datasets.py` is a tiny lookup — no download logic, no caching, just a dict of `(size_key, path, label, description)`.
- The page stays UI-glue only; everything meaningful is importable.
- PyGWalker is not wrapped in a module — the page imports `StreamlitRenderer` directly at the point of use, with a try/except fallback.

## The 7 benchmark operations

Carried over from the original draft; unchanged.

| # | Op | Pandas expression | Polars expression |
|---|---|---|---|
| 1 | Read parquet | `pd.read_parquet(path)` | `pl.read_parquet(path)` |
| 2 | Count rows | `len(df)` | `df.height` |
| 3 | Filter | `df[df["price"] > threshold]` | `df.filter(pl.col("price") > threshold)` |
| 4 | Groupby + aggregate | `df.groupby("postcode_district")["price"].agg(["mean","median","count"])` | `df.group_by("postcode_district").agg([pl.col("price").mean(), pl.col("price").median(), pl.col("price").count()])` |
| 5 | Sort | `df.sort_values("price", ascending=False)` | `df.sort("price", descending=True)` |
| 6 | String extract (regex) | `df["postcode"].str.extract(r"^([A-Z]+)", expand=False)` | `df["postcode"].str.extract(r"^([A-Z]+)")` |
| 7 | Write parquet | `df.to_parquet(tmp_path)` | `df.write_parquet(tmp_path)` |

**Column auto-detect:** `runner.run_benchmark` takes a `column_config` dict. If not provided, it picks sensible defaults from the schema — first string, first numeric, first timestamp. For the Land Registry schema the defaults resolve cleanly: `price` (numeric), `postcode` (string, regex source), `postcode_district` (string, groupby key).

## Data model

### Benchmark results

```python
@dataclass
class EngineResult:
    ms_median: float
    ms_runs: list[float]          # all N timed runs
    peak_mb: float
    rows_processed: int
    rows_per_sec: float
    error: str | None             # exception message, or None

@dataclass
class OpResult:
    op_key: str                   # "read", "count", "filter", etc.
    op_label: str                 # "Read parquet"
    pandas: EngineResult
    polars: EngineResult
    result_preview: Any           # shape depends on op — see Result preview shapes
    correct: bool                 # True if both engines agreed on result hash
    correctness_note: str         # "hashed n rows" / "mismatch detected" / "only pandas ran"
```

### Result preview shapes

Not every op returns a DataFrame — the runner normalizes each op's output into a small Python value that `report.build_op_card` knows how to render.

| Op | `result_preview` value |
|---|---|
| Read parquet | `DataFrame.head(10)` of the loaded table |
| Count rows | `int` (the row count) |
| Filter | `DataFrame.head(10)` of the filtered subset + total row count |
| Groupby + aggregate | `DataFrame.head(10)` sorted by the first aggregate column |
| Sort | `DataFrame.head(10)` of the sorted output |
| String extract | `DataFrame.head(10)` with the original + extracted columns |
| Write parquet | `dict` with `{path, bytes_written}` |

`report.build_op_card` dispatches on the op_key to choose the right Streamlit widget: `st.dataframe` for tabular, `st.metric` for scalars (Count), `st.caption` for the Write result.

```python
# (continuation of the data model block above)

def run_benchmark(parquet_path: Path, ops: list[str] | None = None,
                  column_config: dict | None = None,
                  warmup_runs: int = 1, timed_runs: int = 3) -> list[OpResult]:
    ...
```

### Dataset presets

```python
PRESETS = {
    "small": {
        "label": "Small (5 MB · London only)",
        "path": DATA_DIR / "london_ppd.parquet",
        "description": "London postcode districts, pre-processed. Good for a quick smoke test.",
    },
    "large": {
        "label": "Large (~50 MB · England-wide, 2 years)",
        "path": DATA_DIR / "england_ppd_benchmark.parquet",
        "description": "England-wide PPD for the most recent 2 years. Shows polars' speedup dramatically.",
    },
}
```

`datasets.get_available_presets()` filters out entries whose file doesn't exist — so if the Large parquet isn't yet bundled, the dropdown only offers Small.

## Tab layout

Modify [dashboard/pages/42_London_House_Prices.py](dashboard/pages/42_London_House_Prices.py) to add a 4th tab between Brand and Tests:

```python
tab_growth, tab_compare, tab_brand, tab_bench, tab_tests = st.tabs(
    ["Growth", "Compare", "Brand", "Benchmark Lab", "Tests"]
)
```

Inside `tab_bench`:

```
┌─────────────────────────────────────────────────────────────┐
│ Dataset:  [Small (5 MB · London only) ▼]  [▶ Run Benchmark] │
├─────────────────────────────────────────────────────────────┤
│ Overall comparison                                          │
│ ┌─ Plotly grouped bar chart ───────────────────────────────┐│
│ │ ops on x-axis, ms on y-axis, pandas vs polars grouped   ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ Per-op detail  (7 expanders)                                │
│ ▸ 1. Read parquet        pandas 82ms · polars 14ms · 5.9x  │
│ ▸ 2. Count rows          pandas  3ms · polars  1ms · 3.0x  │
│ ▼ 4. Groupby + aggregate pandas 210ms · polars 28ms · 7.5x │
│     ┌─ Result preview (top 10 districts by avg price) ──┐  │
│     │ SW1  £2.1M   W1  £1.8M  ...                        │  │
│     └────────────────────────────────────────────────────┘  │
│ ...                                                         │
├─────────────────────────────────────────────────────────────┤
│ Explore the dataset yourself                                │
│ ┌─ pygwalker.StreamlitRenderer(df, kernel_computation=True)┐│
│ │ (full Tableau-style drag & drop GUI)                     ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

- Each per-op card is `st.expander`. Collapsed shows only the timing summary line; expanded shows the result preview (`st.dataframe` for tabular, `st.plotly_chart` where applicable).
- The overview chart at the top is always visible after a run.
- The PyGWalker section is always visible after a run (lazy-created on first render via session state).
- Before any run, the tab shows only the dataset selector + run button + a short explainer paragraph.

## Data flow

```
[Run Benchmark clicked]
        │
        ▼
runner.run_benchmark(parquet_path, ops=ALL_7)
        │
        ├── For each op:
        │     ├── 1 warmup run (pandas + polars), discard timings
        │     ├── 3 timed runs × pandas  → ms list, peak_mb
        │     ├── gc.collect()  (prevent inter-engine memory stacking)
        │     ├── 3 timed runs × polars  → ms list, peak_mb
        │     ├── Hash both final results after sorting → correctness flag
        │     └── try/except captures per-engine errors without killing the run
        │
        ├── Returns: list[OpResult]
        │
        ▼
report.build_overview_chart(results) → Plotly Figure
report.build_op_card(result)         → dict of {headline, preview}
        │
        ▼
Streamlit renders: overview chart → 7 expanders
        │
        ▼
Lazy PyGWalker: on first entry to the tab after a run, create
StreamlitRenderer on the loaded DataFrame and cache it in
st.session_state keyed by dataset_path.
```

### Caching strategy

- Results cached in `st.session_state["benchmark_results"]` keyed by `(dataset_path, ops_tuple)`.
- Changing the dataset selector does NOT auto-rerun — the old results remain visible with a note "results from [old dataset]" until the user clicks Run again.
- PyGWalker renderer cached in `st.session_state["pygwalker_renderer"]` keyed by `dataset_path` so tab switches don't rebuild it.

### Memory measurement

- `tracemalloc.start()` before each timed run, `tracemalloc.get_traced_memory()[1]` captures peak, `tracemalloc.stop()` afterwards.
- `gc.collect()` explicitly called between pandas and polars halves of each op's measurement so pandas allocations don't inflate polars' peak.

### Correctness hashing

- For pandas results: `hashlib.sha1(pd.util.hash_pandas_object(result.sort_index().reset_index(drop=True)).values.tobytes()).hexdigest()`
- For polars results: convert to pandas via `.to_pandas()` then apply the same hash. Slow for large results, but correctness is a sanity check not a hot path.
- Results are sorted before hashing to absorb legitimate row-order differences.
- If hashes differ, `correct=False` and the card shows a warning icon. The run does NOT fail — timings are still reported.

## Error handling

| Failure mode | Behavior |
|---|---|
| Large parquet missing from disk | `datasets.get_available_presets()` filters it out. Dropdown shows only Small. |
| One op throws for one engine | Card shows the successful engine normally, failed engine shows `❌ <exception message>`. Overall chart omits that engine's bar for that op. |
| Both engines fail on an op | Card shows `❌ skipped` with both error messages. Op omitted from overall chart. |
| Correctness mismatch | Card shows timings normally plus a yellow `⚠` icon and tooltip "Engines returned different results — inspect the previews." Run does NOT fail. |
| OOM caught by Python | Captured as normal exception in `runner.py` per-op try/except. |
| OOM causing process kill | Uncatchable in-Python. Streamlit will show its generic crash screen. Mitigated by bundled file sizes being well under cloud limits. |
| `pygwalker` import fails | Try/except ImportError around the PyGWalker section, shows `st.info("PyGWalker not installed")` and falls back to `st.dataframe(df.head(100))`. |
| PyGWalker render error | Try/except around `StreamlitRenderer(...)`, shows `st.warning(...)` and falls back to `st.dataframe(df.head(1000))`. |

## Testing

### Automated

**`test_benchmark_engines.py`** — one parametrized test per op that feeds the tiny fixture parquet to both `pd_<op>` and `pl_<op>`, then compares outputs by sorting and hashing. 7 ops × 2 engines = 14 test cases via `pytest.mark.parametrize`.

**`test_benchmark_runner.py`** — 2 tests:
1. `run_benchmark` on fixture returns a `list[OpResult]` with the correct structure: len == 7, each has both engine results, correctness flag set.
2. A deliberately-broken op (inject a bad column name via `column_config`) is captured in `EngineResult.error` without propagating.

**`test_benchmark_datasets.py`** — 1 test: preset lookup table entries resolve to real files. The Large entry's test is skipped if the file isn't yet committed (`pytest.mark.skipif`).

**`test_benchmark_report.py`** — 1 test: `build_overview_chart` given a fake `OpResult` list returns a Plotly `Figure` with non-empty traces.

**Total: ~18 test cases.** All use the tiny 100-row fixture. No dependency on the real bundled parquet files.

**Running:**
```bash
cd dashboard && python -m pytest tests/test_benchmark*.py
```

### Manual verification

- Run the Streamlit app, click Benchmark Lab tab, pick Small, click Run. Confirm all 7 ops complete, chart renders, expanders show result previews, PyGWalker loads.
- Repeat with Large once the bundled file exists.
- Hover timing summaries for tooltips.
- Resize window, confirm layout holds.

## Bundled large parquet (one-time prep)

The ~50 MB `england_ppd_benchmark.parquet` is not generated on-demand. It's a one-time build:

1. Download England-wide PPD from [gov.uk](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads) for the two most recent calendar years (typically ~400–600 MB CSV).
2. Pre-process to match the existing schema (`postcode`, `postcode_district`, `price`, `date`, etc.).
3. Write as parquet with snappy compression — should land around 40–60 MB.
4. Commit to `dashboard/data/england_ppd_benchmark.parquet`.

GitHub's soft limit is 100 MB per file — we're comfortably under. No git LFS required.

A small helper script at `dashboard/scripts/build_benchmark_parquet.py` documents and automates the prep so it can be regenerated if the data grows stale. Not imported by any production code.

## Dependencies

Add to `dashboard/requirements.txt`:

```
polars>=1.0
pygwalker>=0.4
```

Both are pure-Python wheels — no system deps. Confirmed compatible with Python 3.11 on Streamlit Cloud.

## Resource budget

- Small (5 MB) run: <1 s wall, <100 MB peak memory.
- Large (50 MB) run: ~2–5 s wall, ~300–500 MB peak memory combined across both engines.
- PyGWalker renderer on 50 MB file: ~200–400 MB additional at steady state (stores data server-side for `kernel_computation=True` mode).
- Total worst case: ~1 GB. Streamlit Cloud free tier is exactly 1 GB — tight but workable. The dataset selector and the "Run Benchmark" explicit button let users choose not to run the Large option on cloud.

If cloud memory becomes a problem, future mitigation: detect cloud environment and auto-disable the Large option, or page the PyGWalker view with a `head(N)` cap.

## Open questions

None remaining. All design decisions locked.

## Next step

Invoke the `superpowers:writing-plans` skill to break this spec into an implementation plan with per-task test + commit checkpoints.
