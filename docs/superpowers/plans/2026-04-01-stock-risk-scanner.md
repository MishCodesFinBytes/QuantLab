# QuantLab Learning Path — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upskill to senior Python backend/fintech contractor level (FastAPI, async, PostgreSQL, Claude AI, Docker) through a series of focused concept posts, each with a working exercise, culminating in a Stock Risk Scanner capstone project.

**Architecture:** Learn-by-building approach. Each concept gets: a focused exercise in `quant_lab/exercises/<topic>/`, a blog post in `finbytes_git/docs/_posts/`, and tests. Each step builds on the last. The capstone project in `quant_lab/projects/stock-risk-scanner/` assembles all concepts into one service.

**Tech Stack:** Python 3.11+, pytest, Pydantic, FastAPI, uvicorn, async/await, yfinance, numpy, Anthropic SDK, Docker, PostgreSQL, SQLAlchemy, Alembic

---

## Repos

| Repo | Path | Purpose |
|------|------|---------|
| quant_lab | `C:\codebase\quant_lab` | Exercises + capstone project code |
| finbytes_git | `C:\codebase\finbytes_git` | Blog posts (`_posts` for concepts, `_quant_lab` for capstone) |

## Directory Structure

```
quant_lab/
├── exercises/
│   ├── 01-pytest-tdd/
│   │   ├── src/
│   │   │   └── portfolio.py
│   │   ├── tests/
│   │   │   └── test_portfolio.py
│   │   └── pyproject.toml
│   ├── 02-pydantic/
│   │   ├── src/
│   │   │   └── trade_models.py
│   │   ├── tests/
│   │   │   └── test_trade_models.py
│   │   └── pyproject.toml
│   ├── 03-fastapi/
│   │   ├── src/
│   │   │   └── app.py
│   │   ├── tests/
│   │   │   └── test_app.py
│   │   └── pyproject.toml
│   ├── 04-async/
│   │   ├── src/
│   │   │   └── async_prices.py
│   │   ├── tests/
│   │   │   └── test_async_prices.py
│   │   └── pyproject.toml
│   ├── 05-yfinance/
│   │   ├── src/
│   │   │   └── market_data.py
│   │   ├── tests/
│   │   │   └── test_market_data.py
│   │   └── pyproject.toml
│   ├── 06-claude-api/
│   │   ├── src/
│   │   │   └── analyst.py
│   │   ├── tests/
│   │   │   └── test_analyst.py
│   │   └── pyproject.toml
│   ├── 07-docker/
│   │   ├── src/
│   │   │   └── app.py
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── pyproject.toml
│   └── 08-postgres-sqlalchemy/
│       ├── src/
│       │   ├── models.py
│       │   └── db.py
│       ├── tests/
│       │   └── test_db.py
│       ├── alembic/
│       ├── alembic.ini
│       └── pyproject.toml
└── projects/
    └── stock-risk-scanner/    # Capstone — assembles all concepts
        ├── src/scanner/
        ├── templates/
        ├── tests/
        ├── Dockerfile
        ├── docker-compose.yml
        └── pyproject.toml
```

Blog posts:
```
finbytes_git/docs/_posts/
├── 2026-04-XX-pytest-tdd-for-financial-python.html
├── 2026-04-XX-pydantic-models-for-trading-data.html
├── 2026-04-XX-fastapi-your-first-financial-api.html
├── 2026-04-XX-async-python-for-market-data.html
├── 2026-05-XX-yfinance-fetching-market-data.html
├── 2026-05-XX-claude-api-ai-risk-analysis.html
├── 2026-05-XX-docker-for-python-services.html
└── 2026-05-XX-postgres-sqlalchemy-trade-storage.html

finbytes_git/docs/_quant_lab/
└── stock-risk-scanner.html    # Capstone blog post (Concept/Python/Comparative tabs)
```

---

## Phase 1: Concept Posts (Weeks 1-8)

Each concept follows the workflow: **build it -> understand it -> document it**

---

### Task 1: pytest & TDD for Financial Python

**Concept:** Write tests first, then implement. Fixtures, parametrize, mocking. Apply to a simple portfolio returns calculator.

**Files:**
- Create: `exercises/01-pytest-tdd/pyproject.toml`
- Create: `exercises/01-pytest-tdd/src/portfolio.py`
- Create: `exercises/01-pytest-tdd/tests/test_portfolio.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-pytest-tdd-for-financial-python.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "pytest-tdd-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests first — the TDD way**

```python
import numpy as np
import pytest
from portfolio import daily_returns, cumulative_return, max_drawdown


# --- daily_returns ---

class TestDailyReturns:
    def test_basic_returns(self):
        prices = np.array([100.0, 105.0, 103.0])
        result = daily_returns(prices)
        expected = np.array([0.05, -0.01904762])
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_single_price_returns_empty(self):
        prices = np.array([100.0])
        result = daily_returns(prices)
        assert len(result) == 0

    def test_zero_price_raises(self):
        prices = np.array([100.0, 0.0, 50.0])
        with pytest.raises(ValueError, match="zero"):
            daily_returns(prices)


# --- cumulative_return ---

class TestCumulativeReturn:
    @pytest.mark.parametrize("prices,expected", [
        (np.array([100.0, 110.0]), 0.10),
        (np.array([100.0, 90.0]), -0.10),
        (np.array([100.0, 100.0]), 0.0),
    ])
    def test_cumulative_return(self, prices, expected):
        assert cumulative_return(prices) == pytest.approx(expected, rel=1e-5)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            cumulative_return(np.array([]))


# --- max_drawdown ---

class TestMaxDrawdown:
    def test_no_drawdown(self):
        prices = np.array([100.0, 110.0, 120.0])
        assert max_drawdown(prices) == 0.0

    def test_simple_drawdown(self):
        prices = np.array([100.0, 120.0, 90.0, 110.0])
        # Peak 120, trough 90 → drawdown = -30/120 = -0.25
        assert max_drawdown(prices) == pytest.approx(-0.25)

    def test_drawdown_at_end(self):
        prices = np.array([100.0, 200.0, 100.0])
        assert max_drawdown(prices) == pytest.approx(-0.50)
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\01-pytest-tdd
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'portfolio'`

- [ ] **Step 4: Implement portfolio.py — minimal code to pass tests**

```python
import numpy as np


def daily_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate daily percentage returns from a price series.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        1D array of daily returns (length = len(prices) - 1).

    Raises:
        ValueError: If any price is zero (can't compute return from zero).
    """
    if np.any(prices == 0):
        raise ValueError("Price series contains zero — cannot compute returns from zero price")
    if len(prices) <= 1:
        return np.array([])
    return np.diff(prices) / prices[:-1]


def cumulative_return(prices: np.ndarray) -> float:
    """Total return from first price to last price.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        Cumulative return as a decimal (e.g. 0.10 for 10%).
    """
    if len(prices) == 0:
        raise ValueError("Price series is empty")
    return float((prices[-1] - prices[0]) / prices[0])


def max_drawdown(prices: np.ndarray) -> float:
    """Maximum peak-to-trough decline as a negative decimal.

    Args:
        prices: 1D array of daily closing prices.

    Returns:
        Max drawdown as negative decimal (e.g. -0.25 for 25% drop). 0.0 if no drawdown.
    """
    running_max = np.maximum.accumulate(prices)
    drawdowns = (prices - running_max) / running_max
    return float(drawdowns.min())
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 9 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/01-pytest-tdd/
git commit -m "feat(exercises): 01 pytest TDD with portfolio returns calculator"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- Why TDD matters in financial code (wrong calculation = real money lost)
- `pytest.approx` for floating-point comparison (critical in finance)
- `@pytest.mark.parametrize` — table-driven tests for financial scenarios
- Fixtures vs test classes — when to use which
- `np.testing.assert_allclose` vs `pytest.approx` — both useful, different contexts

- [ ] **Step 8: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-pytest-tdd-for-financial-python.html` using the standard FinBytes post frontmatter. Content drawn from the teaching conversation:

```yaml
---
layout: post
title: "TDD with pytest for Financial Python"
date: 2026-04-XX
published: true
status: publish
categories:
  - Python fundamentals
  - Testing
tags:
  - pytest
  - TDD
  - testing
  - finance
permalink: "/2026/04/XX/pytest-tdd-financial-python/"
---
```

Sections to cover:
- Why TDD for financial code (the "wrong number = real money" argument)
- Red-green-refactor cycle with a portfolio example
- Key pytest features: fixtures, parametrize, approx, mocking
- Common patterns for financial test cases
- Link to the exercise code in quant_lab repo

- [ ] **Step 9: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-pytest-tdd-for-financial-python.html
git commit -m "post: TDD with pytest for financial Python"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 2: Pydantic Models for Trading Data

**Concept:** Data validation and serialization with Pydantic v2. Model financial entities: trades, positions, portfolio requests. Validators, computed fields, nested models.

**Files:**
- Create: `exercises/02-pydantic/pyproject.toml`
- Create: `exercises/02-pydantic/src/trade_models.py`
- Create: `exercises/02-pydantic/tests/test_trade_models.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-pydantic-models-for-trading-data.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "pydantic-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic>=2.7.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
import pytest
from datetime import date
from pydantic import ValidationError
from trade_models import Trade, Position, PortfolioRequest


class TestTrade:
    def test_valid_trade(self):
        t = Trade(
            ticker="AAPL",
            side="buy",
            quantity=100,
            price=150.25,
            trade_date=date(2026, 4, 1),
        )
        assert t.ticker == "AAPL"
        assert t.notional == 15025.0  # computed field

    def test_ticker_uppercased(self):
        t = Trade(ticker="aapl", side="buy", quantity=100, price=150.0, trade_date=date(2026, 4, 1))
        assert t.ticker == "AAPL"

    def test_invalid_side_rejected(self):
        with pytest.raises(ValidationError):
            Trade(ticker="AAPL", side="hold", quantity=100, price=150.0, trade_date=date(2026, 4, 1))

    def test_negative_quantity_rejected(self):
        with pytest.raises(ValidationError):
            Trade(ticker="AAPL", side="buy", quantity=-10, price=150.0, trade_date=date(2026, 4, 1))

    def test_future_date_rejected(self):
        with pytest.raises(ValidationError):
            Trade(ticker="AAPL", side="buy", quantity=100, price=150.0, trade_date=date(2030, 1, 1))

    def test_serialization_roundtrip(self):
        t = Trade(ticker="AAPL", side="buy", quantity=100, price=150.25, trade_date=date(2026, 4, 1))
        data = t.model_dump()
        t2 = Trade(**data)
        assert t == t2


class TestPosition:
    def test_position_from_trades(self):
        trades = [
            Trade(ticker="AAPL", side="buy", quantity=100, price=150.0, trade_date=date(2026, 3, 1)),
            Trade(ticker="AAPL", side="buy", quantity=50, price=155.0, trade_date=date(2026, 3, 15)),
        ]
        pos = Position(ticker="AAPL", trades=trades)
        assert pos.net_quantity == 150
        assert pos.avg_price == pytest.approx(151.6667, rel=1e-3)

    def test_mixed_buy_sell(self):
        trades = [
            Trade(ticker="MSFT", side="buy", quantity=200, price=300.0, trade_date=date(2026, 3, 1)),
            Trade(ticker="MSFT", side="sell", quantity=50, price=310.0, trade_date=date(2026, 3, 10)),
        ]
        pos = Position(ticker="MSFT", trades=trades)
        assert pos.net_quantity == 150


class TestPortfolioRequest:
    def test_valid_request(self):
        req = PortfolioRequest(
            tickers=["AAPL", "MSFT", "GOOG"],
            weights=[0.4, 0.35, 0.25],
        )
        assert len(req.tickers) == 3

    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValidationError, match="sum to 1"):
            PortfolioRequest(tickers=["AAPL", "MSFT"], weights=[0.5, 0.3])

    def test_lengths_must_match(self):
        with pytest.raises(ValidationError, match="length"):
            PortfolioRequest(tickers=["AAPL", "MSFT"], weights=[1.0])
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\02-pydantic
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement trade_models.py**

```python
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field


class Trade(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    side: Literal["buy", "sell"]
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    trade_date: date

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper()

    @field_validator("trade_date")
    @classmethod
    def not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("trade_date cannot be in the future")
        return v

    @computed_field
    @property
    def notional(self) -> float:
        return self.quantity * self.price


class Position(BaseModel):
    ticker: str
    trades: list[Trade]

    @computed_field
    @property
    def net_quantity(self) -> int:
        total = 0
        for t in self.trades:
            total += t.quantity if t.side == "buy" else -t.quantity
        return total

    @computed_field
    @property
    def avg_price(self) -> float:
        buys = [t for t in self.trades if t.side == "buy"]
        if not buys:
            return 0.0
        total_cost = sum(t.quantity * t.price for t in buys)
        total_qty = sum(t.quantity for t in buys)
        return total_cost / total_qty


class PortfolioRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    weights: list[float] = Field(..., min_length=1, max_length=10)
    period: str = Field(default="1y", pattern=r"^\d+(d|mo|y)$")
    confidence: float = Field(default=0.95, ge=0.9, le=0.99)

    @model_validator(mode="after")
    def validate_portfolio(self):
        if len(self.tickers) != len(self.weights):
            raise ValueError(f"tickers length ({len(self.tickers)}) must match weights length ({len(self.weights)})")
        if abs(sum(self.weights) - 1.0) > 0.01:
            raise ValueError(f"weights must sum to 1.0, got {sum(self.weights):.4f}")
        return self
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 10 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/02-pydantic/
git commit -m "feat(exercises): 02 Pydantic models for trading data"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- Pydantic v2 vs v1 (what changed, why it matters)
- `field_validator` vs `model_validator` — when to use which
- `computed_field` — derived values without storing them
- `Literal` types for constrained values (buy/sell)
- `model_dump()` / `model_validate()` — serialization for APIs
- Why Pydantic matters for FastAPI (auto-validation, auto-docs)

- [ ] **Step 8: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-pydantic-models-for-trading-data.html`

```yaml
---
layout: post
title: "Pydantic v2 Models for Trading Data"
date: 2026-04-XX
published: true
status: publish
categories:
  - Python fundamentals
tags:
  - pydantic
  - validation
  - models
  - finance
permalink: "/2026/04/XX/pydantic-models-trading-data/"
---
```

Sections: What Pydantic does, validators, computed fields, model-level validation, serialization, connection to FastAPI.

- [ ] **Step 9: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-pydantic-models-for-trading-data.html
git commit -m "post: Pydantic v2 models for trading data"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 3: FastAPI — Your First Financial API

**Concept:** Build a simple API that serves portfolio data. Routes, path/query params, request bodies, dependency injection, auto-generated docs. Builds on Pydantic from Task 2.

**Files:**
- Create: `exercises/03-fastapi/pyproject.toml`
- Create: `exercises/03-fastapi/src/app.py`
- Create: `exercises/03-fastapi/tests/test_app.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-fastapi-your-first-financial-api.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "fastapi-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "httpx>=0.27.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestWatchlist:
    def test_get_empty_watchlist(self, client):
        resp = client.get("/watchlist")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_ticker(self, client):
        resp = client.post("/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 201
        assert resp.json()["ticker"] == "AAPL"

    def test_add_and_list(self, client):
        client.post("/watchlist", json={"ticker": "AAPL"})
        client.post("/watchlist", json={"ticker": "MSFT"})
        resp = client.get("/watchlist")
        tickers = [item["ticker"] for item in resp.json()]
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_duplicate_ticker_rejected(self, client):
        client.post("/watchlist", json={"ticker": "AAPL"})
        resp = client.post("/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 409

    def test_delete_ticker(self, client):
        client.post("/watchlist", json={"ticker": "GOOG"})
        resp = client.delete("/watchlist/GOOG")
        assert resp.status_code == 204

    def test_delete_missing_returns_404(self, client):
        resp = client.delete("/watchlist/ZZZZ")
        assert resp.status_code == 404


class TestPortfolioAnalysis:
    def test_analyze_validates_weights(self, client):
        resp = client.post("/analyze", json={
            "tickers": ["AAPL", "MSFT"],
            "weights": [0.5],
        })
        assert resp.status_code == 422

    def test_analyze_returns_summary(self, client):
        resp = client.post("/analyze", json={
            "tickers": ["AAPL"],
            "weights": [1.0],
            "period": "1y",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "tickers" in data
        assert "message" in data
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\03-fastapi
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement app.py**

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Portfolio API", version="0.1.0")

# In-memory store (replaced by PostgreSQL in exercise 08)
_watchlist: dict[str, dict] = {}


class TickerIn(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)


class TickerOut(BaseModel):
    ticker: str


class PortfolioIn(BaseModel):
    tickers: list[str] = Field(..., min_length=1)
    weights: list[float] = Field(..., min_length=1)
    period: str = Field(default="1y")

    @model_validator(mode="after")
    def validate_lengths(self):
        if len(self.tickers) != len(self.weights):
            raise ValueError("tickers and weights must have the same length")
        return self


class AnalysisOut(BaseModel):
    tickers: list[str]
    weights: list[float]
    period: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/watchlist", response_model=list[TickerOut])
def list_watchlist():
    return list(_watchlist.values())


@app.post("/watchlist", response_model=TickerOut, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(body: TickerIn):
    ticker = body.ticker.upper()
    if ticker in _watchlist:
        raise HTTPException(status_code=409, detail=f"{ticker} already in watchlist")
    _watchlist[ticker] = {"ticker": ticker}
    return _watchlist[ticker]


@app.delete("/watchlist/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(ticker: str):
    ticker = ticker.upper()
    if ticker not in _watchlist:
        raise HTTPException(status_code=404, detail=f"{ticker} not in watchlist")
    del _watchlist[ticker]


@app.post("/analyze", response_model=AnalysisOut)
def analyze_portfolio(body: PortfolioIn):
    return AnalysisOut(
        tickers=body.tickers,
        weights=body.weights,
        period=body.period,
        message=f"Analysis stub for {len(body.tickers)} tickers over {body.period}",
    )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/03-fastapi/
git commit -m "feat(exercises): 03 FastAPI portfolio API"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- FastAPI vs Flask vs Django REST — why FastAPI for financial APIs
- Path params, query params, request bodies — when to use which
- Dependency injection (intro — used more in capstone)
- Auto-generated OpenAPI docs at `/docs`
- TestClient and why it doesn't need a running server
- Status codes that matter: 201, 204, 404, 409, 422

- [ ] **Step 8: Document it — write blog post**

- [ ] **Step 9: Commit blog post (working -> master -> push)**

---

### Task 4: Async Python for Market Data

**Concept:** async/await, asyncio, aiohttp. Why async matters for I/O-bound financial services. Refactor a sync price fetcher to async. Compare performance.

**Files:**
- Create: `exercises/04-async/pyproject.toml`
- Create: `exercises/04-async/src/async_prices.py`
- Create: `exercises/04-async/tests/test_async_prices.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-async-python-for-market-data.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "async-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["aiohttp>=3.9.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Write failing tests**

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

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\04-async
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement async_prices.py**

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

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/04-async/
git commit -m "feat(exercises): 04 async Python for market data"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- Event loop mental model — why async is faster for I/O, not for CPU
- `async def` / `await` — what actually happens at each `await`
- `asyncio.gather` — concurrent execution pattern
- `aiohttp` vs `requests` — when to use which
- Async context managers (`async with`)
- How FastAPI uses async under the hood
- Common pitfall: accidentally blocking the event loop with sync code

- [ ] **Step 8: Document it — write blog post**

- [ ] **Step 9: Commit blog post (working -> master -> push)**

---

### Task 5: yfinance — Fetching & Wrangling Market Data

**Concept:** yfinance library for historical prices, tickers, and financial data. Pandas basics for financial data wrangling. Data quality issues (NaN, splits, dividends).

**Files:**
- Create: `exercises/05-yfinance/pyproject.toml`
- Create: `exercises/05-yfinance/src/market_data.py`
- Create: `exercises/05-yfinance/tests/test_market_data.py`
- Create: `finbytes_git/docs/_posts/2026-05-XX-yfinance-fetching-market-data.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "yfinance-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["yfinance>=0.2.40", "numpy>=1.26.0", "pandas>=2.2.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests (mocked yfinance)**

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

- [ ] **Step 3: Run tests, verify fail, implement, verify pass**

- [ ] **Step 4: Implement market_data.py**

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

- [ ] **Step 5: Run tests, commit**

```bash
pytest -v
cd C:\codebase\quant_lab
git add exercises/05-yfinance/
git commit -m "feat(exercises): 05 yfinance market data fetching"
```

- [ ] **Step 6: Understand it — teaching conversation**

Topics to cover:
- yfinance API quirks: MultiIndex columns, auto_adjust, splits
- Data quality in real market data: NaN, halts, holidays, delistings
- Forward-fill vs interpolation — why ffill is standard for prices
- Pandas vs numpy — when to use which for financial data
- Market data gotchas: survivorship bias, look-ahead bias

- [ ] **Step 7: Document it — write blog post, commit (working -> master -> push)**

---

### Task 6: Claude API — AI-Powered Risk Analysis

**Concept:** Anthropic SDK, messages API, system prompts, structured output. Build a financial analyst that takes metrics and produces plain-English risk commentary.

**Files:**
- Create: `exercises/06-claude-api/pyproject.toml`
- Create: `exercises/06-claude-api/src/analyst.py`
- Create: `exercises/06-claude-api/tests/test_analyst.py`
- Create: `finbytes_git/docs/_posts/2026-05-XX-claude-api-ai-risk-analysis.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "claude-api-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["anthropic>=0.40.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests (mocked Claude client)**

```python
import pytest
from unittest.mock import patch, MagicMock
from analyst import RiskAnalyst


@pytest.fixture
def mock_anthropic():
    with patch("analyst.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="The portfolio shows elevated risk due to concentration.")]
        mock_client.messages.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def analyst():
    return RiskAnalyst()


@pytest.fixture
def sample_metrics():
    return {
        "var_pct": -2.15,
        "cvar_pct": -3.42,
        "max_drawdown_pct": -18.7,
        "annualized_vol": 22.5,
        "sharpe_ratio": 0.85,
    }


class TestRiskAnalyst:
    def test_generate_returns_string(self, mock_anthropic, analyst, sample_metrics):
        result = analyst.analyze(tickers=["AAPL", "MSFT"], metrics=sample_metrics)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_uses_system_prompt(self, mock_anthropic, analyst, sample_metrics):
        analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "system" in call_kwargs
        assert "risk" in call_kwargs["system"].lower()

    def test_includes_metrics_in_prompt(self, mock_anthropic, analyst, sample_metrics):
        analyst.analyze(tickers=["AAPL", "MSFT"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        user_msg = call_kwargs["messages"][0]["content"]
        assert "VaR" in user_msg or "var" in user_msg.lower()
        assert "AAPL" in user_msg

    def test_fallback_on_api_error(self, analyst, sample_metrics):
        with patch("analyst.anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = Exception("API timeout")
            result = analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
            assert "unable" in result.lower() or "error" in result.lower()

    def test_custom_model(self, mock_anthropic, sample_metrics):
        analyst = RiskAnalyst(model="claude-haiku-4-5-20251001")
        analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 3: Run tests, verify fail**

- [ ] **Step 4: Implement analyst.py**

```python
import anthropic


class RiskAnalyst:
    """AI-powered risk analyst using Claude API."""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    def analyze(self, tickers: list[str], metrics: dict) -> str:
        """Generate a plain-English risk narrative from portfolio metrics.

        Args:
            tickers: List of stock symbols in the portfolio.
            metrics: Dict with keys: var_pct, cvar_pct, max_drawdown_pct,
                     annualized_vol, sharpe_ratio.

        Returns:
            Risk narrative string. Falls back to generic message on API failure.
        """
        system_prompt = (
            "You are a senior risk analyst at an investment bank. "
            "Summarize portfolio risk in 3-4 sentences for a trader. "
            "Be direct, specific, and flag any concerning metrics. "
            "Use plain English, not jargon."
        )

        user_prompt = (
            f"Portfolio: {', '.join(tickers)}\n"
            f"VaR (95%): {metrics['var_pct']:.2f}%\n"
            f"CVaR (Expected Shortfall): {metrics['cvar_pct']:.2f}%\n"
            f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%\n"
            f"Annualized Volatility: {metrics['annualized_vol']:.2f}%\n"
            f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}"
        )

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception:
            return (
                f"Unable to generate AI analysis. Key metrics — "
                f"VaR: {metrics['var_pct']:.2f}%, "
                f"CVaR: {metrics['cvar_pct']:.2f}%, "
                f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%."
            )
```

- [ ] **Step 5: Run tests, verify pass**

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/06-claude-api/
git commit -m "feat(exercises): 06 Claude API risk analyst"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- Anthropic SDK: client, messages.create, system vs user prompts
- Model selection: Opus vs Sonnet vs Haiku — cost/speed/quality trade-offs
- Prompt engineering for financial output: specificity, tone, constraints
- Structured output: getting JSON back from Claude (for future use)
- Error handling: timeouts, rate limits, graceful degradation
- API key management: env vars, .env files, never in code

- [ ] **Step 8: Document it — write blog post, commit (working -> master -> push)**

---

### Task 7: Docker for Python Services

**Concept:** Containerize a FastAPI app. Dockerfile, docker-compose, volumes, env vars, multi-stage builds. Takes the FastAPI exercise from Task 3 and dockerizes it.

**Files:**
- Create: `exercises/07-docker/pyproject.toml`
- Create: `exercises/07-docker/src/app.py`
- Create: `exercises/07-docker/Dockerfile`
- Create: `exercises/07-docker/docker-compose.yml`
- Create: `finbytes_git/docs/_posts/2026-05-XX-docker-for-python-services.html`

- [ ] **Step 1: Create pyproject.toml and a minimal FastAPI app**

```toml
[project]
name = "docker-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.115.0", "uvicorn[standard]>=0.32.0"]
```

```python
# src/app.py
import os
from fastapi import FastAPI

app = FastAPI(title="Dockerized API")


@app.get("/health")
def health():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "development")}


@app.get("/")
def root():
    return {"message": "Hello from Docker!"}
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY src/ src/

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=docker
    restart: unless-stopped
```

- [ ] **Step 4: Build and run**

```bash
cd C:\codebase\quant_lab\exercises\07-docker
docker compose up --build -d
curl http://localhost:8000/health
docker compose down
```

Expected: `{"status":"ok","environment":"docker"}`

- [ ] **Step 5: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/07-docker/
git commit -m "feat(exercises): 07 Docker for FastAPI services"
```

- [ ] **Step 6: Understand it — teaching conversation**

Topics to cover:
- Why containers matter for financial services (reproducibility, deployment)
- Dockerfile anatomy: FROM, WORKDIR, COPY, RUN, CMD
- Multi-stage builds — why and when
- docker-compose for multi-service setups (will use in capstone with PostgreSQL)
- Volumes for persistent data
- Environment variables and secrets management
- .dockerignore — what to exclude

- [ ] **Step 7: Document it — write blog post, commit (working -> master -> push)**

---

### Task 8: PostgreSQL + SQLAlchemy + Alembic

**Concept:** Relational database for financial data. SQLAlchemy ORM, async sessions, Alembic migrations. Store and query trade/scan history.

**Files:**
- Create: `exercises/08-postgres-sqlalchemy/pyproject.toml`
- Create: `exercises/08-postgres-sqlalchemy/src/models.py`
- Create: `exercises/08-postgres-sqlalchemy/src/db.py`
- Create: `exercises/08-postgres-sqlalchemy/tests/test_db.py`
- Create: `exercises/08-postgres-sqlalchemy/alembic.ini`
- Create: `exercises/08-postgres-sqlalchemy/alembic/env.py`
- Create: `exercises/08-postgres-sqlalchemy/docker-compose.yml` (PostgreSQL service)
- Create: `finbytes_git/docs/_posts/2026-05-XX-postgres-sqlalchemy-trade-storage.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "postgres-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0", "aiosqlite>=0.20.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create docker-compose.yml for PostgreSQL**

```yaml
services:
  db:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: quantlab
      POSTGRES_PASSWORD: quantlab_dev
      POSTGRES_DB: quantlab
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- [ ] **Step 3: Write failing tests (using SQLite for test speed)**

```python
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base, ScanRecord
from db import save_scan, get_recent_scans


@pytest.fixture
async def session():
    """In-memory SQLite for fast tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


class TestScanRecord:
    async def test_save_and_retrieve(self, session):
        await save_scan(session, tickers=["AAPL", "MSFT"], var_pct=-2.15, narrative="Test narrative")
        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 1
        assert scans[0].tickers == "AAPL,MSFT"
        assert scans[0].var_pct == pytest.approx(-2.15)

    async def test_recent_scans_ordered_by_date(self, session):
        await save_scan(session, tickers=["AAPL"], var_pct=-1.0, narrative="First")
        await save_scan(session, tickers=["MSFT"], var_pct=-2.0, narrative="Second")
        scans = await get_recent_scans(session, limit=10)
        assert scans[0].narrative == "Second"  # most recent first

    async def test_limit_works(self, session):
        for i in range(5):
            await save_scan(session, tickers=[f"T{i}"], var_pct=-float(i), narrative=f"Scan {i}")
        scans = await get_recent_scans(session, limit=3)
        assert len(scans) == 3
```

- [ ] **Step 4: Implement models.py and db.py**

```python
# models.py
from datetime import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    tickers: Mapped[str] = mapped_column(String(200))
    var_pct: Mapped[float] = mapped_column(Float)
    narrative: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.utcnow
    )
```

```python
# db.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ScanRecord


async def save_scan(
    session: AsyncSession,
    tickers: list[str],
    var_pct: float,
    narrative: str,
) -> ScanRecord:
    record = ScanRecord(
        tickers=",".join(tickers),
        var_pct=var_pct,
        narrative=narrative,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]:
    stmt = select(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
```

- [ ] **Step 5: Run tests, verify pass**

- [ ] **Step 6: Set up Alembic for migrations**

```bash
cd C:\codebase\quant_lab\exercises\08-postgres-sqlalchemy
docker compose up -d
alembic init alembic
# Edit alembic/env.py to import Base and set target_metadata = Base.metadata
# Edit alembic.ini to set sqlalchemy.url = postgresql+asyncpg://quantlab:quantlab_dev@localhost/quantlab
alembic revision --autogenerate -m "create scan_records table"
alembic upgrade head
docker compose down
```

- [ ] **Step 7: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/08-postgres-sqlalchemy/
git commit -m "feat(exercises): 08 PostgreSQL + SQLAlchemy + Alembic"
```

- [ ] **Step 8: Understand it — teaching conversation**

Topics to cover:
- SQLAlchemy 2.0 style: `Mapped`, `mapped_column`, `DeclarativeBase`
- Async SQLAlchemy: `create_async_engine`, `async_sessionmaker`
- Why async DB in financial services (high-throughput, non-blocking)
- Alembic migrations: autogenerate, upgrade, downgrade
- Testing with SQLite in-memory (fast) vs real PostgreSQL (accurate)
- Connection pooling — why it matters under load
- PostgreSQL vs SQLite — when each makes sense

- [ ] **Step 9: Document it — write blog post, commit (working -> master -> push)**

---

## Phase 2: Capstone Project (Weeks 9-10)

### Task 9: Stock Risk Scanner — Assembly

**Goal:** Wire together all 8 concepts into the capstone project. This should feel like assembly, not learning — every piece has been practiced.

**Files:** Same structure as the original plan's file structure (under `projects/stock-risk-scanner/`).

- [ ] **Step 1: Scaffold the project**

Create `projects/stock-risk-scanner/` with the full structure. `pyproject.toml` includes all dependencies from exercises 1-8.

```toml
[project]
name = "stock-risk-scanner"
version = "0.1.0"
description = "Portfolio risk scanner with AI-generated narratives"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "yfinance>=0.2.40",
    "numpy>=1.26.0",
    "anthropic>=0.40.0",
    "jinja2>=3.1.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "aiosqlite>=0.20.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Implement models (from exercises 02 + 08)**

Combine Pydantic models (exercise 02) with SQLAlchemy models (exercise 08) into `src/scanner/models.py` and `src/scanner/db.py`.

- [ ] **Step 3: Implement risk calculations (from exercise 01)**

Copy and enhance `src/scanner/risk.py` from the exercise — same math, just integrated with Pydantic models.

- [ ] **Step 4: Implement market data fetcher (from exercise 05)**

`src/scanner/market_data.py` — same as exercise 05 but with async support.

- [ ] **Step 5: Implement Claude narrative generator (from exercise 06)**

`src/scanner/narrative.py` — same as exercise 06 `RiskAnalyst` class.

- [ ] **Step 6: Wire up FastAPI app with async endpoints (from exercises 03 + 04)**

`src/scanner/main.py` — async endpoints, dependency injection for DB session, Jinja2 dashboard.

- [ ] **Step 7: Write tests for all modules**

One test file per module, using patterns learned in exercises. Mock external services (yfinance, Claude).

- [ ] **Step 8: Run full test suite**

```bash
cd C:\codebase\quant_lab\projects\stock-risk-scanner
pip install -e ".[dev]"
pytest -v
```

Expected: All tests pass

- [ ] **Step 9: Add Docker + PostgreSQL setup (from exercises 07 + 08)**

```yaml
# docker-compose.yml
services:
  scanner:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: quantlab
      POSTGRES_PASSWORD: quantlab_dev
      POSTGRES_DB: quantlab
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- [ ] **Step 10: Add GitHub Actions CI**

Create `.github/workflows/test.yml`:

```yaml
name: Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
        working-directory: projects/stock-risk-scanner
      - run: pytest -v
        working-directory: projects/stock-risk-scanner
```

- [ ] **Step 11: Add structured logging**

Add `structlog` configuration to `main.py`:

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()
```

Use `log.info("scan_completed", tickers=req.tickers, var=metrics.var_pct)` in endpoints.

- [ ] **Step 12: Smoke test with Docker**

```bash
docker compose up --build -d
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/scan -H "Content-Type: application/json" \
  -d '{"tickers":["AAPL","MSFT"],"weights":[0.6,0.4]}'
docker compose down
```

- [ ] **Step 13: Commit everything**

```bash
cd C:\codebase\quant_lab
git add projects/stock-risk-scanner/ .github/
git commit -m "feat(stock-risk-scanner): capstone project — full risk scanner service"
git push origin main
```

---

### Task 10: Capstone Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_quant_lab\stock-risk-scanner.html`

- [ ] **Step 1: Write the capstone blog post**

Uses `quant-lab-project` layout with rich tabs:

- **Concept tab:** Architecture overview, how the pieces fit together, risk theory (drawn from exercise teaching conversations), system design decisions
- **Python tab:** Code walkthrough of the full service — data flow from request to response, key modules, testing strategy
- **C++/C#:** Placeholder
- **Comparative:** Compare this approach to the standalone scripts in FinBytes/RiskMetrics, discuss trade-offs of microservice vs script

- [ ] **Step 2: Update quant-lab.html index page**

Add Stock Risk Scanner to the quant lab landing page.

- [ ] **Step 3: Commit and deploy**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_quant_lab/stock-risk-scanner.html docs/_quant_lab/quant-lab.html
git commit -m "feat: Stock Risk Scanner capstone blog post"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 11: Final README & Cleanup

- [ ] **Step 1: Update quant_lab README**

```markdown
# QuantLab

Quantitative finance projects and exercises.

## Exercises

| # | Topic | Key Concepts |
|---|-------|-------------|
| 01 | [pytest & TDD](exercises/01-pytest-tdd/) | Fixtures, parametrize, approx, TDD cycle |
| 02 | [Pydantic](exercises/02-pydantic/) | Validators, computed fields, serialization |
| 03 | [FastAPI](exercises/03-fastapi/) | Routes, status codes, TestClient |
| 04 | [Async Python](exercises/04-async/) | async/await, gather, aiohttp |
| 05 | [yfinance](exercises/05-yfinance/) | Market data, pandas, data quality |
| 06 | [Claude API](exercises/06-claude-api/) | Anthropic SDK, prompts, error handling |
| 07 | [Docker](exercises/07-docker/) | Dockerfile, compose, multi-stage builds |
| 08 | [PostgreSQL](exercises/08-postgres-sqlalchemy/) | SQLAlchemy 2.0, async, Alembic |

## Projects

| Project | Description | Status |
|---------|------------|--------|
| [Stock Risk Scanner](projects/stock-risk-scanner/) | Portfolio risk + Claude AI narratives | Active |
| [CDS Pricing](projects/cds-pricing/) | Credit Default Swap pricing | Scaffold |

## Quick Start

See each exercise or project directory for setup instructions.
```

- [ ] **Step 2: Commit and push**

```bash
cd C:\codebase\quant_lab
git add -A
git commit -m "docs: update README with exercises and projects"
git push origin main
```

---

## Next Steps (not in this plan)

- **AWS deployment:** Deploy Stock Risk Scanner to EC2/ECS (Phase 2 of 12-week plan)
- **CI/CD pipeline:** Expand GitHub Actions with deploy step
- **Event-driven pipeline:** Add Celery + Redis for automated portfolio monitoring (Phase 3 — this is where queues make sense)
- **CV/LinkedIn update:** Phase 4
