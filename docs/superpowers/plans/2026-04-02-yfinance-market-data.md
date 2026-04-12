# yfinance Market Data — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Learn yfinance data fetching and pandas/numpy wrangling through TDD, building a market data pipeline (fetch → clean → compute returns).

**Architecture:** Single module with three functions forming a pipeline. `fetch_closing_prices` wraps yfinance, `validate_data` cleans NaN/gaps, `compute_returns` converts to numpy percentage returns. Tests mock yfinance to avoid network calls.

**Tech Stack:** Python 3.11+, yfinance (>=0.2.40), numpy (>=1.26.0), pandas (>=2.2.0), pytest (>=8.0.0)

---

## File Structure

```
exercises/05-yfinance/
├── pyproject.toml              # project config, deps, pytest settings
├── src/
│   └── market_data.py          # fetch_closing_prices, validate_data, compute_returns
└── tests/
    └── test_market_data.py     # 7 tests across 3 test classes
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/05-yfinance/pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "yfinance-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["yfinance>=0.2.40", "numpy>=1.26.0", "pandas>=2.2.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["market_data"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p exercises/05-yfinance/src exercises/05-yfinance/tests
```

---

### Task 2: Write Failing Tests

**Files:**
- Create: `exercises/05-yfinance/tests/test_market_data.py`

- [ ] **Step 1: Write all 7 tests**

```python
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch
from market_data import fetch_closing_prices, compute_returns, validate_data


@pytest.fixture
def mock_prices():
    """Realistic price data with some NaN values (like real market data)."""
    dates = pd.date_range("2025-01-01", periods=10, freq="B")
    return pd.DataFrame({
        "AAPL": [150.0, 152.0, np.nan, 155.0, 153.0, 157.0, 156.0, 160.0, 158.0, 162.0],
        "MSFT": [300.0, 305.0, 308.0, 310.0, 307.0, 312.0, 315.0, 318.0, 316.0, 320.0],
    }, index=dates)


@pytest.fixture
def clean_prices():
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    return pd.DataFrame({
        "AAPL": [100.0, 105.0, 103.0, 108.0, 110.0],
        "MSFT": [200.0, 210.0, 205.0, 215.0, 220.0],
    }, index=dates)


class TestFetchClosingPrices:
    def test_returns_dataframe(self, mock_prices):
        with patch("market_data.yf.download") as mock_dl:
            mock_dl.return_value = mock_prices
            result = fetch_closing_prices(["AAPL", "MSFT"], period="1y")
            assert isinstance(result, pd.DataFrame)
            assert list(result.columns) == ["AAPL", "MSFT"]

    def test_empty_data_raises(self):
        with patch("market_data.yf.download") as mock_dl:
            mock_dl.return_value = pd.DataFrame()
            with pytest.raises(ValueError, match="No data"):
                fetch_closing_prices(["INVALID"], period="1y")


class TestValidateData:
    def test_fills_nan_forward(self, mock_prices):
        clean = validate_data(mock_prices)
        assert not clean.isna().any().any()

    def test_drops_leading_nans(self):
        dates = pd.date_range("2025-01-01", periods=3, freq="B")
        df = pd.DataFrame({"A": [np.nan, 100.0, 105.0]}, index=dates)
        clean = validate_data(df)
        assert len(clean) == 2


class TestComputeReturns:
    def test_shape(self, clean_prices):
        returns = compute_returns(clean_prices)
        assert returns.shape == (4, 2)  # 5 prices -> 4 returns

    def test_no_nans(self, clean_prices):
        returns = compute_returns(clean_prices)
        assert not np.isnan(returns).any()

    def test_returns_are_percentages(self, clean_prices):
        returns = compute_returns(clean_prices)
        # First return for AAPL: (105-100)/100 = 0.05
        assert returns[0, 0] == pytest.approx(0.05)
```

- [ ] **Step 2: Install dependencies and run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\05-yfinance
pip install -e ".[dev]"
python -m pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'market_data'`

---

### Task 3: Implement market_data.py

**Files:**
- Create: `exercises/05-yfinance/src/market_data.py`

- [ ] **Step 1: Implement all three functions**

```python
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_closing_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """Download closing prices from Yahoo Finance.

    Args:
        tickers: List of stock symbols.
        period: History period (e.g. "1y", "6mo", "5y").

    Returns:
        DataFrame with date index and one column per ticker.
    """
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f"No data returned for tickers: {tickers}")

    # yfinance returns MultiIndex for multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    elif "Close" in data.columns:
        data = data[["Close"]]
        data.columns = tickers

    return data


def validate_data(prices: pd.DataFrame) -> pd.DataFrame:
    """Clean price data: drop leading NaN rows, forward-fill gaps.

    Args:
        prices: Raw price DataFrame from yfinance.

    Returns:
        Cleaned DataFrame with no NaN values.
    """
    # Drop rows where ALL values are NaN (market holidays, etc.)
    prices = prices.dropna(how="all")

    # Drop leading rows with any NaN (ticker didn't exist yet)
    first_valid = prices.apply(lambda col: col.first_valid_index()).max()
    if first_valid is not None:
        prices = prices.loc[first_valid:]

    # Forward-fill remaining gaps (stock halts, missing data)
    prices = prices.ffill()

    return prices


def compute_returns(prices: pd.DataFrame) -> np.ndarray:
    """Convert price DataFrame to numpy array of daily returns.

    Args:
        prices: Cleaned price DataFrame.

    Returns:
        (n_days-1, n_tickers) numpy array of daily percentage returns.
    """
    values = prices.values
    returns = np.diff(values, axis=0) / values[:-1]
    return np.nan_to_num(returns, nan=0.0)
```

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd C:\codebase\quant_lab\exercises\05-yfinance
python -m pytest -v
```

Expected: 7 passed

---

### Task 4: Commit

- [ ] **Step 1: Commit exercise to quant_lab**

```bash
cd C:\codebase\quant_lab
git add exercises/05-yfinance/
git commit -m "feat(exercises): 05 yfinance market data fetching"
```

---

### Task 5: Understand It — Teaching Conversation

No code changes. Interactive discussion covering:

- **yfinance API quirks** — MultiIndex columns, `auto_adjust`, splits and dividends
- **Data quality in real market data** — NaN, halts, holidays, delistings
- **Forward-fill vs interpolation** — why ffill is standard for prices
- **Pandas vs numpy** — when to use which for financial data
- **Market data gotchas** — survivorship bias, look-ahead bias

---

### Task 6: Document It — Write Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_posts\2026-04-02-yfinance-fetching-market-data.html`

- [ ] **Step 1: Write the blog post**

Use this frontmatter (clean format):

```yaml
---
layout: post
title: "yfinance — Fetching & Wrangling Market Data"
date: 2026-04-02
tags: [yfinance, pandas, numpy, market-data, finance, python, quant-lab]
categories:
- Python fundamentals
permalink: "/2026/04/02/yfinance-fetching-market-data/"
---
```

Sections to cover:
- What yfinance does and why it's useful for prototyping
- Fetching closing prices — the `yf.download` API and its quirks
- Data quality issues — NaN, gaps, leading nulls in real market data
- Cleaning data — forward-fill, dropping leading NaN, why not interpolate
- Computing returns — prices to percentage changes with numpy
- Pandas vs numpy — when to use which
- Link to the exercise code in quant_lab repo

---

### Task 7: Commit Blog Post

- [ ] **Step 1: Commit blog post in finbytes_git**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-02-yfinance-fetching-market-data.html
git commit -m "post: yfinance — fetching & wrangling market data"
```

- [ ] **Step 2: Push working branch**

```bash
git push origin working
```

- [ ] **Step 3: Merge to master and push**

```bash
git checkout master
git merge working --no-edit
git push origin master
git checkout working
```

- [ ] **Step 4: Verify blog post is live**

Check: `https://mish-codes.github.io/FinBytes/2026/04/02/yfinance-fetching-market-data/`

---

### Task 8: Commit quant_lab docs and push

- [ ] **Step 1: Commit spec and plan files**

```bash
cd C:\codebase\quant_lab
git add docs/superpowers/specs/2026-04-02-yfinance-market-data-design.md
git add docs/superpowers/plans/2026-04-02-yfinance-market-data.md
git push origin working
```

- [ ] **Step 2: Create PR from working to master**

```bash
gh pr create --title "feat: exercise 05 yfinance market data" --body "..." --base master --head working
```

- [ ] **Step 3: Merge PR and sync locally**

After merge on GitHub:

```bash
git fetch origin
git checkout master && git pull origin master
git checkout working
```
