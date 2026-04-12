# Async Python for Market Data — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Learn async/await and asyncio.gather through TDD, building a concurrent price fetcher with aiohttp.

**Architecture:** Single module with two async functions. `fetch_price` fetches a single ticker via aiohttp. `fetch_many_prices` uses `asyncio.gather` to run multiple fetches concurrently with graceful error handling. All tests use mocks (no real HTTP calls).

**Tech Stack:** Python 3.11+, aiohttp (>=3.9.0), pytest (>=8.0.0), pytest-asyncio (>=0.24.0)

---

## File Structure

```
exercises/04-async/
├── pyproject.toml              # project config, deps, pytest-asyncio settings
├── src/
│   └── async_prices.py         # fetch_price, fetch_many_prices
└── tests/
    └── test_async_prices.py    # 3 tests across 2 test classes
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/04-async/pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "async-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["aiohttp>=3.9.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["async_prices"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

Note: `asyncio_mode = "auto"` lets test functions be `async def` without needing `@pytest.mark.asyncio` on each one.

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p exercises/04-async/src exercises/04-async/tests
```

---

### Task 2: Write Failing Tests

**Files:**
- Create: `exercises/04-async/tests/test_async_prices.py`

- [ ] **Step 1: Write all 3 tests**

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from async_prices import fetch_price, fetch_many_prices


class TestFetchPrice:
    async def test_returns_float(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "chart": {"result": [{"meta": {"regularMarketPrice": 150.25}}]}
        })
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("async_prices.aiohttp.ClientSession", return_value=mock_session):
            price = await fetch_price("AAPL")
            assert price == 150.25
            assert isinstance(price, float)


class TestFetchManyPrices:
    async def test_fetches_concurrently(self):
        call_times = []

        async def mock_fetch(ticker):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.05)  # simulate network delay
            return {"AAPL": 150.0, "MSFT": 300.0, "GOOG": 140.0}[ticker]

        with patch("async_prices.fetch_price", side_effect=mock_fetch):
            results = await fetch_many_prices(["AAPL", "MSFT", "GOOG"])

        assert len(results) == 3
        assert results["AAPL"] == 150.0
        assert results["MSFT"] == 300.0
        # All started at roughly the same time (concurrent)
        assert max(call_times) - min(call_times) < 0.03

    async def test_partial_failure_returns_available(self):
        async def mock_fetch(ticker):
            if ticker == "BAD":
                raise ValueError("Unknown ticker")
            return 100.0

        with patch("async_prices.fetch_price", side_effect=mock_fetch):
            results = await fetch_many_prices(["AAPL", "BAD", "MSFT"])

        assert "AAPL" in results
        assert "MSFT" in results
        assert "BAD" not in results
```

- [ ] **Step 2: Install dependencies and run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\04-async
pip install -e ".[dev]"
python -m pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'async_prices'`

---

### Task 3: Implement async_prices.py

**Files:**
- Create: `exercises/04-async/src/async_prices.py`

- [ ] **Step 1: Implement both async functions**

```python
import asyncio
import aiohttp


async def fetch_price(ticker: str) -> float:
    """Fetch the current market price for a single ticker.

    Uses Yahoo Finance's chart API endpoint.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])


async def fetch_many_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch prices for multiple tickers concurrently.

    Failed tickers are silently skipped — returns only successful results.
    """
    async def safe_fetch(ticker: str) -> tuple[str, float | None]:
        try:
            price = await fetch_price(ticker)
            return ticker, price
        except Exception:
            return ticker, None

    tasks = [safe_fetch(t) for t in tickers]
    results = await asyncio.gather(*tasks)
    return {ticker: price for ticker, price in results if price is not None}
```

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd C:\codebase\quant_lab\exercises\04-async
python -m pytest -v
```

Expected: 3 passed

---

### Task 4: Commit

- [ ] **Step 1: Commit exercise to quant_lab**

```bash
cd C:\codebase\quant_lab
git add exercises/04-async/
git commit -m "feat(exercises): 04 async Python for market data"
```

---

### Task 5: Understand It — Teaching Conversation

No code changes. Interactive discussion covering:

- **Event loop mental model** — why async is faster for I/O, not for CPU
- **`async def` / `await`** — what actually happens at each `await`
- **`asyncio.gather`** — concurrent execution pattern
- **`aiohttp` vs `requests`** — when to use which
- **Async context managers** — `async with` for session and response lifecycle
- **How FastAPI uses async** — under the hood
- **Common pitfall** — accidentally blocking the event loop with sync code

---

### Task 6: Document It — Write Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_posts\2026-04-02-async-python-for-market-data.html`

- [ ] **Step 1: Write the blog post**

Use this frontmatter (clean format):

```yaml
---
layout: post
title: "Async Python for Market Data"
date: 2026-04-02
tags: [async, asyncio, aiohttp, python, finance, quant-lab]
categories:
- Python fundamentals
permalink: "/2026/04/02/async-python-for-market-data/"
---
```

Sections to cover:
- Why async matters for financial data (fetching 50 tickers sequentially = slow)
- async/await basics — coroutines and the event loop
- aiohttp — async HTTP client with context managers
- asyncio.gather — running tasks concurrently
- Graceful partial failure — don't lose 49 results because 1 ticker failed
- Testing async code — AsyncMock and pytest-asyncio
- Link to the exercise code in quant_lab repo

---

### Task 7: Commit Blog Post

- [ ] **Step 1: Commit blog post in finbytes_git**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-02-async-python-for-market-data.html
git commit -m "post: Async Python for market data"
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

Check: `https://mish-codes.github.io/FinBytes/2026/04/02/async-python-for-market-data/`

---

### Task 8: Commit quant_lab docs and push

- [ ] **Step 1: Commit spec and plan files**

```bash
cd C:\codebase\quant_lab
git add docs/superpowers/specs/2026-04-02-async-python-market-data-design.md
git add docs/superpowers/plans/2026-04-02-async-python-market-data.md
git push origin working
```

- [ ] **Step 2: Create PR from working to master**

```bash
gh pr create --title "feat: exercise 04 async Python for market data" --body "..." --base master --head working
```

- [ ] **Step 3: Merge PR and sync locally**

After merge on GitHub:

```bash
git fetch origin
git checkout master && git pull origin master
git checkout working
```
