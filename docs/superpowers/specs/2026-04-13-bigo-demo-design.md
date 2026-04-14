# Big O Demo — Same Problem, Different Complexities

**Date:** 2026-04-13
**Status:** Final — ready for implementation plan

## Goal

Add a new "Big O Notation" page to the QuantLab Streamlit dashboard under a new "Tech Understanding" sidebar section. The page lets a user pick a problem (Fibonacci or Pair-sum), runs every algorithm variant for that problem at increasing input sizes, and plots wall-time vs n on a log-log chart. The intent is pedagogical: see the gap between O(n²), O(n log n), O(n), O(log n), and O(2ⁿ) on real numbers from real Python code.

Two starter problems:

1. **Fibonacci(n)** — naive recursive (O(2ⁿ)), iterative (O(n)), memoized (O(n)), matrix exponentiation (O(log n))
2. **Pair-sum** — brute force nested loops (O(n²)), sort + two-pointer (O(n log n)), hash set single pass (O(n))

The architecture supports adding more problems later by appending an entry to a registry; no UI changes required.

## Non-goals

- No multi-problem comparison (one problem at a time)
- No user-defined algorithms
- No CPU profiling or memory tracking — wall time only
- No async / streaming — synchronous benchmark wrapped in `st.spinner`
- No JavaScript or canvas-level animation — Plotly only
- No tests for the Streamlit page itself (consistent with QuantLab convention)
- No use of pyarrow / numpy / pandas vectorization in the algorithms — would defeat the point of demonstrating *Python algorithmic* complexity

## Architecture

### Files

| Path | Status | Purpose |
|---|---|---|
| `dashboard/lib/bigo/__init__.py` | New | Package marker, re-exports public API |
| `dashboard/lib/bigo/algorithms.py` | New | Pure algorithm implementations for all variants |
| `dashboard/lib/bigo/problems.py` | New | Problem registry (dataclasses + `PROBLEMS` dict) |
| `dashboard/lib/bigo/runner.py` | New | Times each variant at each n, time-budget skip, correctness check |
| `dashboard/lib/bigo/report.py` | New | Plotly log-log chart + per-algorithm card builders |
| `dashboard/pages/60_Big_O.py` | New | Streamlit page (UI glue only) |
| `dashboard/lib/nav.py` | Modified | Add "Tech Understanding" section + Big O entry |
| `dashboard/tests/test_bigo_algorithms.py` | New | Correctness tests per variant |
| `dashboard/tests/test_bigo_runner.py` | New | Runner structure + budget skip + error capture |
| `dashboard/tests/test_bigo_problems.py` | New | Registry shape tests |
| `dashboard/tests/test_bigo_report.py` | New | Plotly chart structure test |

### Why this split

- `algorithms.py` is plain Python functions, pytest-able without Streamlit.
- `runner.py` owns timing, the skip-on-too-slow logic, and correctness checking — all separated from the algorithms themselves so the algorithms stay readable.
- `problems.py` is the registry pattern that makes adding a 3rd, 4th, Nth problem trivial — drop a `Problem(...)` entry into `PROBLEMS` and the page picks it up automatically.
- The page is UI glue only; no logic.

### No new dependencies

Reuses Plotly, pandas (only for trivial DataFrame conversion in tests), and Python stdlib. No pyarrow, no numpy, no extra installs.

## Data model

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class AlgorithmVariant:
    key: str           # "fib_naive"
    label: str         # "Naive recursive"
    big_o: str         # "O(2^n)"
    fn: Callable       # the implementation, takes (*args) returns result

@dataclass
class Problem:
    key: str                       # "fibonacci"
    label: str                     # "Fibonacci(n)"
    description: str               # one-liner under the dropdown
    explainer: str                 # markdown blob for the "About" expander
    n_values: list[int]            # x-axis points to benchmark at
    input_factory: Callable        # n -> tuple of args for the variant fn
    variants: list[AlgorithmVariant]

@dataclass
class NPoint:
    n: int
    wall_ms: float
    result_hash: str               # for cross-variant correctness check
    error: str | None              # exception class+message, or None
    skipped: bool                  # True if past the time budget for this variant

@dataclass
class VariantResult:
    variant: AlgorithmVariant
    points: list[NPoint]           # one per n in problem.n_values

@dataclass
class ProblemResult:
    problem: Problem
    variant_results: list[VariantResult]
    correctness: dict              # {(variant_key, n): bool}
```

## The 7 algorithms (v1)

### Fibonacci

| Variant | Big O | Notes |
|---|---|---|
| `fib_naive` | O(2ⁿ) | Textbook recursive `fib(n) = fib(n-1) + fib(n-2)`. Becomes unusable around n=35. |
| `fib_iterative` | O(n) | Single loop tracking `(a, b)`. Constant memory. |
| `fib_memoized` | O(n) | Recursive with `@functools.lru_cache(maxsize=None)`. O(n) time and space. |
| `fib_matrix` | O(log n) | Powers of `[[1,1],[1,0]]` via fast exponentiation. |

`n_values = [5, 10, 15, 20, 25, 28, 30, 32, 34, 36]` — chosen so the naive variant gets to show its exponential blow-up but doesn't lock the page.

### Pair-sum

| Variant | Big O | Notes |
|---|---|---|
| `pair_brute` | O(n²) | Nested loops checking every pair. |
| `pair_sorted` | O(n log n) | Sort then two-pointer scan. |
| `pair_hash` | O(n) | Single pass with a `set()` of seen values. |

`n_values = [100, 500, 1000, 2500, 5000, 7500, 10000]` — at 10K the brute-force variant runs ~100M comparisons in ~3 seconds, just under the budget.

`input_factory` for pair-sum generates a deterministic seeded random list of `n` integers and a target value chosen so the answer is True for every n (so all variants compute meaningful work).

## Page layout (`60_Big_O.py`)

```
┌─────────────────────────────────────────────────────────────┐
│ # Big O Notation                                            │
│ Same problem, different complexities — see the gap.         │
├─────────────────────────────────────────────────────────────┤
│ Problem: [Fibonacci(n) ▼]              [▶ Run benchmark]    │
│   Computing the nth Fibonacci number — 4 algorithms.        │
├─────────────────────────────────────────────────────────────┤
│ ▸ About this problem                                        │
│   (markdown explainer collapsed by default)                 │
├─────────────────────────────────────────────────────────────┤
│ Wall time vs n  (log-log axis)                              │
│ ┌─ Plotly chart ───────────────────────────────────────────┐│
│ │   ●─ naive recursive  O(2^n)                              ││
│ │   ●─ iterative        O(n)                                ││
│ │   ●─ memoized         O(n)                                ││
│ │   ●─ matrix expon.    O(log n)                            ││
│ │   ─── theoretical curves overlaid as faint dashed lines   ││
│ └───────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ Per-algorithm detail (expanders)                            │
│ ▸ Naive recursive  O(2^n)   skipped past n=32 (>2s)         │
│ ▸ Iterative        O(n)     n=10000 in 0.4ms                │
│ ▸ Memoized         O(n)     n=10000 in 0.5ms                │
│ ▸ Matrix exponent. O(log n) n=10000 in 0.02ms               │
└─────────────────────────────────────────────────────────────┘
```

### Detailed UI behaviors

- **Dropdown** lists every problem in `PROBLEMS` ordered by registry insertion. Default = first entry (Fibonacci).
- **Run button** explicit — does NOT auto-run on dropdown change. Avoids accidental long runs and lets users read the explainer first.
- **About expander** is collapsed by default. Contents = `problem.explainer` rendered with `st.markdown`.
- **Chart** uses Plotly with `xaxis_type="log"` and `yaxis_type="log"`. One scatter+line trace per variant. Theoretical curves overlaid as dashed lines computed from the smallest measured (n, ms) point and scaled to the variant's Big O.
- **Per-algo expanders** show:
  - Headline: `<label>  ·  <big_o>  ·  <largest n successfully timed> in <ms>` or `skipped past n=<x> (>2s)`
  - Inside: a small `st.dataframe` with columns `n | wall_ms | status` where status is `ok`, `skipped`, or `error: <msg>`.
- **Result caching:** results stored in `st.session_state[f"bigo_results_{problem_key}"]`. Switching problems via the dropdown does NOT auto-rerun — stale results from the previous problem clear, the user clicks Run again. Same-problem reruns overwrite the cache.

### Markdown explainers

Stored as a multi-line string on the `Problem` dataclass. Full text for the two starter problems is in the **Explainer content** section below.

## Theoretical-curve overlay

For each variant, after collecting empirical `(n, ms)` points, compute a theoretical reference curve:

| Big O | Reference |
|---|---|
| `O(1)` | constant (median of measured ms) |
| `O(log n)` | `c * log2(n)` |
| `O(n)` | `c * n` |
| `O(n log n)` | `c * n * log2(n)` |
| `O(n²)` | `c * n²` |
| `O(2^n)` | `c * 2ⁿ` |

`c` is calibrated by anchoring to the smallest successful empirical point so the theoretical line passes through (or near) the data. The overlay is rendered as a faint dashed Plotly line with `opacity=0.4`. Purpose: visual gut-check that the empirical timings track theoretical complexity.

The Big O label lookup is done by string match against a small dispatch table in `report.py`. Unknown labels skip the overlay (no crash).

## Runner behavior

```python
def run_problem(problem: Problem,
                budget_ms: float = 2000.0) -> ProblemResult:
    """Time every variant at every n in problem.n_values.

    For each variant:
      - walk n_values in ascending order
      - time one call with time.perf_counter()
      - if the call raises, capture exception, mark error, continue to next n
      - if wall_ms > budget_ms, mark this and all larger n as skipped, break
      - record result_hash for correctness checking

    After all variants run, populate ProblemResult.correctness:
      For each n, all variants that successfully ran at that n must produce
      the same result_hash. A mismatch sets correctness[(variant_key, n)] = False
      and the per-algo card surfaces a warning.
    """
```

### Result hashing

Each variant's return value is hashed:
- `int`/`float`/`bool` → `str(value)`
- `list`/`tuple` → `str(sorted(value))` for order-independent comparison (pair-sum returns bool, so this is mostly defensive)
- everything else → `repr(value)`

The first successful variant at each n establishes the "truth"; subsequent variants are compared against it.

### Time budget rationale

A single per-call hard timeout (e.g., via `signal.alarm`) is platform-specific and adds complexity. The simpler post-hoc check works because:
- Each `n_values` list is hand-tuned so even the slowest variant takes <5 seconds at the largest `n` it'll attempt.
- The 2-second budget triggers between calls, not during. Worst case for one variant: it finishes one ~3-second call, then is skipped for all subsequent n.
- Total worst case across all variants of one problem: ~10 seconds. Acceptable for a synchronous Streamlit run with a spinner.

## Error handling

| Failure | Behavior |
|---|---|
| Algorithm raises (e.g., `RecursionError` on naive Fib) | `NPoint.error` set, that point omitted from chart, expander shows `error: RecursionError` |
| Result correctness mismatch | `correctness[(variant_key, n)] = False`, expander shows yellow ⚠ with a tooltip; run does NOT fail |
| All variants fail at all n | Chart shows empty axes with a message "All algorithms failed — check the logs" |
| Unknown problem key in URL params | Falls back to first problem in registry |
| Empty `n_values` (impossible in v1 but guarded) | Skip the run, show `st.error("Problem has no n_values configured")` |
| Spinner mid-run | Synchronous block; user must wait. No cancel button. |

## Testing

### `test_bigo_algorithms.py`

**Fibonacci correctness — parametrized over a known-truth table:**

```python
KNOWN_FIB = {0: 0, 1: 1, 2: 1, 5: 5, 10: 55, 20: 6765, 25: 75025}
FIB_VARIANTS = [fib_naive, fib_iterative, fib_memoized, fib_matrix]

@pytest.mark.parametrize("n,expected", KNOWN_FIB.items())
@pytest.mark.parametrize("variant", FIB_VARIANTS)
def test_fib_variant_correct(variant, n, expected):
    assert variant(n) == expected
```

= 4 × 7 = 28 cases.

**Pair-sum correctness — parametrized over hand-picked cases:**

```python
PAIR_CASES = [
    ([1, 2, 3, 4], 5, True),
    ([1, 2, 3, 4], 8, False),
    ([], 5, False),
    ([5], 5, False),
    ([3, 3], 6, True),
]
PAIR_VARIANTS = [pair_brute, pair_sorted, pair_hash]

@pytest.mark.parametrize("arr,target,expected", PAIR_CASES)
@pytest.mark.parametrize("variant", PAIR_VARIANTS)
def test_pair_variant_correct(variant, arr, target, expected):
    assert variant(arr, target) is expected
```

= 3 × 5 = 15 cases.

### `test_bigo_runner.py`

1. **`test_run_problem_returns_expected_structure`** — `run_problem(PROBLEMS["fibonacci"])` returns a `ProblemResult` with one `VariantResult` per variant, each with `len(points) == len(problem.n_values)`.
2. **`test_run_problem_skips_past_budget`** — inject a fake variant whose `fn = lambda n: time.sleep(3) or 0`. Confirm subsequent points have `skipped=True`.
3. **`test_run_problem_correctness_check`** — Fibonacci variants all agree at n=10 (every `correctness[(variant_key, 10)]` is True).
4. **`test_run_problem_captures_exception`** — fake variant that raises ValueError. Confirm `point.error` contains the exception message and other variants still run.

### `test_bigo_problems.py`

1. **`test_registry_has_seed_problems`** — `PROBLEMS` contains `"fibonacci"` and `"pair_sum"`, each with `len(variants) >= 3` and a non-empty `explainer`.
2. **`test_input_factory_returns_tuple`** — for each problem, `problem.input_factory(10)` returns a tuple matching what the variants accept (callable with `*args` unpacking succeeds).

### `test_bigo_report.py`

1. **`test_build_complexity_chart`** — feed a fake `ProblemResult` with two variants, assert the returned `plotly.graph_objects.Figure` has 2 data traces (plus optional dashed theoretical traces), `xaxis.type == "log"`, `yaxis.type == "log"`.

### Running

```bash
cd dashboard && python -m pytest tests/test_bigo*.py -v
```

**Total test cases: ~50.**

## Nav integration

Modify `dashboard/lib/nav.py` to add a new section between "Word Tools" and the bottom divider:

```python
# Tech Understanding
st.sidebar.caption("Tech Understanding")
st.sidebar.page_link("pages/60_Big_O.py", label="Big O Notation")
```

The new section sits below "Word Tools" and above the System Health link.

## Explainer content

### Fibonacci

```markdown
The Fibonacci sequence is one of the most famous in mathematics:
**0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...** Each number is the sum of
the previous two. The sequence appears in nature (sunflower seed
spirals, pinecones, nautilus shells), in art, and in computer science
as the canonical example of a recursive problem with dramatically
different solutions.

We compute **F(n)** — the nth number in the sequence — four ways:

- **Naive recursive** — the textbook definition `F(n) = F(n-1) + F(n-2)`.
  Looks elegant, runs in **O(2ⁿ)** because it recomputes the same values
  exponentially many times. F(35) takes seconds; F(50) takes hours.
- **Iterative** — a single loop tracking the last two values. **O(n)**,
  uses constant memory. The boring, correct solution.
- **Memoized recursive** — same recursion as naive but caches results.
  **O(n)** time and O(n) memory. Demonstrates how a one-line decorator
  collapses an exponential algorithm to linear.
- **Matrix exponentiation** — uses the identity that the Fibonacci
  numbers can be computed via powers of the matrix `[[1,1],[1,0]]`.
  Combined with fast exponentiation it runs in **O(log n)**, which is
  what lets you compute F(1,000,000) in milliseconds.

The whole point of this demo is the gap. On a log-log plot the naive
version curves up sharply and falls off the right side; the iterative
and memoized lines run nearly flat across; the matrix line is the
flattest of all.
```

### Pair-sum

```markdown
The **Two-Sum** problem: given a list of numbers and a target, return
**True** if any two numbers in the list add up to the target. It's a
classic interview question and a great demonstration of how the right
data structure changes the complexity class.

- **Brute force** — two nested loops checking every pair. **O(n²)**,
  works but quadratic. At n=10,000 that's 100 million comparisons.
- **Sort + two-pointer** — sort the array first (O(n log n)), then
  walk a left pointer up and a right pointer down. **O(n log n)** total,
  dominated by the sort.
- **Hash set, single pass** — for each number `x`, check if `target - x`
  has already been seen. **O(n)** time, O(n) extra memory. Trades space
  for time and wins.

The lesson: a hash set is one of the cheapest "free upgrades" in
programming. Adding a `set()` and a single membership check turns a
quadratic algorithm into a linear one.
```

## Resource budget

Total worst-case run for one problem on Streamlit Cloud free tier:
- Fibonacci: ~5 seconds (naive variant burns most of this)
- Pair-sum: ~5 seconds (brute force at n=10000)

Plotly chart, expanders, page chrome: negligible.

PyGWalker, parquet, polars: not used.

**Streamlit Cloud impact: trivial.** No memory concerns, no large dependencies, no file uploads.

## Open questions

None. All design decisions locked.

## Next step

Invoke `superpowers:writing-plans` to break this spec into an implementation plan with per-task TDD checkpoints.
