# Pydantic Models for Trading Data — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Learn Pydantic v2 data validation and serialization through TDD, building three financial models (Trade, Position, PortfolioRequest).

**Architecture:** Single exercise directory with one source module (`trade_models.py`) and one test file. TDD cycle: write all tests first, verify they fail, implement, verify they pass, commit. Followed by a teaching conversation and blog post.

**Tech Stack:** Python 3.11+, Pydantic v2 (>=2.7.0), pytest (>=8.0.0)

---

## File Structure

```
exercises/02-pydantic/
├── pyproject.toml              # project config, deps, pytest settings
├── src/
│   └── trade_models.py         # Trade, Position, PortfolioRequest models
└── tests/
    └── test_trade_models.py    # 12 tests across 3 test classes
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/02-pydantic/pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "pydantic-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic>=2.7.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["trade_models"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Note: `[tool.setuptools]` maps `src/` as the package root so tests can `from trade_models import ...` after `pip install -e ".[dev]"`.

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p exercises/02-pydantic/src exercises/02-pydantic/tests
```

---

### Task 2: Write Failing Tests

**Files:**
- Create: `exercises/02-pydantic/tests/test_trade_models.py`

- [ ] **Step 1: Write all 12 tests**

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
        t = Trade(
            ticker="aapl",
            side="buy",
            quantity=100,
            price=150.0,
            trade_date=date(2026, 4, 1),
        )
        assert t.ticker == "AAPL"

    def test_invalid_side_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="hold",
                quantity=100,
                price=150.0,
                trade_date=date(2026, 4, 1),
            )

    def test_negative_quantity_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=-10,
                price=150.0,
                trade_date=date(2026, 4, 1),
            )

    def test_future_date_rejected(self):
        with pytest.raises(ValidationError):
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=100,
                price=150.0,
                trade_date=date(2030, 1, 1),
            )

    def test_serialization_roundtrip(self):
        t = Trade(
            ticker="AAPL",
            side="buy",
            quantity=100,
            price=150.25,
            trade_date=date(2026, 4, 1),
        )
        data = t.model_dump()
        t2 = Trade(**data)
        assert t == t2

    def test_from_json(self):
        json_str = '{"ticker":"AAPL","side":"buy","quantity":100,"price":150.25,"trade_date":"2026-04-01"}'
        t = Trade.model_validate_json(json_str)
        assert t.ticker == "AAPL"
        assert t.notional == 15025.0


class TestPosition:
    def test_position_from_trades(self):
        trades = [
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=100,
                price=150.0,
                trade_date=date(2026, 3, 1),
            ),
            Trade(
                ticker="AAPL",
                side="buy",
                quantity=50,
                price=155.0,
                trade_date=date(2026, 3, 15),
            ),
        ]
        pos = Position(ticker="AAPL", trades=trades)
        assert pos.net_quantity == 150
        assert pos.avg_price == pytest.approx(151.6667, rel=1e-3)

    def test_mixed_buy_sell(self):
        trades = [
            Trade(
                ticker="MSFT",
                side="buy",
                quantity=200,
                price=300.0,
                trade_date=date(2026, 3, 1),
            ),
            Trade(
                ticker="MSFT",
                side="sell",
                quantity=50,
                price=310.0,
                trade_date=date(2026, 3, 10),
            ),
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

- [ ] **Step 2: Install dependencies and run tests to verify they fail**

```bash
cd exercises/02-pydantic
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'trade_models'`

---

### Task 3: Implement Trade Model

**Files:**
- Create: `exercises/02-pydantic/src/trade_models.py`

- [ ] **Step 1: Implement Trade model**

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
```

- [ ] **Step 2: Run Trade tests to verify they pass**

```bash
cd exercises/02-pydantic
pytest tests/test_trade_models.py::TestTrade -v
```

Expected: 7 passed

---

### Task 4: Implement Position Model

**Files:**
- Modify: `exercises/02-pydantic/src/trade_models.py`

- [ ] **Step 1: Add Position model below Trade**

Append to `trade_models.py`:

```python
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
```

- [ ] **Step 2: Run Position tests to verify they pass**

```bash
cd exercises/02-pydantic
pytest tests/test_trade_models.py::TestPosition -v
```

Expected: 2 passed

---

### Task 5: Implement PortfolioRequest Model

**Files:**
- Modify: `exercises/02-pydantic/src/trade_models.py`

- [ ] **Step 1: Add PortfolioRequest model below Position**

Append to `trade_models.py`:

```python
class PortfolioRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    weights: list[float] = Field(..., min_length=1, max_length=10)
    period: str = Field(default="1y", pattern=r"^\d+(d|mo|y)$")
    confidence: float = Field(default=0.95, ge=0.9, le=0.99)

    @model_validator(mode="after")
    def validate_portfolio(self):
        if len(self.tickers) != len(self.weights):
            raise ValueError(
                f"tickers length ({len(self.tickers)}) must match "
                f"weights length ({len(self.weights)})"
            )
        if abs(sum(self.weights) - 1.0) > 0.01:
            raise ValueError(
                f"weights must sum to 1.0, got {sum(self.weights):.4f}"
            )
        return self
```

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd exercises/02-pydantic
pytest -v
```

Expected: 12 passed

---

### Task 6: Commit

- [ ] **Step 1: Commit exercise to quant_lab**

```bash
cd C:\codebase\quant_lab
git add exercises/02-pydantic/
git commit -m "feat(exercises): 02 Pydantic models for trading data"
```

---

### Task 7: Understand It — Teaching Conversation

No code changes. Interactive discussion covering:

- **Pydantic v2 vs v1** — what changed (performance, `field_validator` replaces `@validator`, `model_dump` replaces `.dict()`)
- **`field_validator` vs `model_validator`** — single-field transforms/checks vs cross-field validation
- **`computed_field`** — derived values that appear in serialization without being stored
- **`Literal` types** — constraining values to an explicit set (buy/sell)
- **`model_dump()` / `model_validate_json()`** — serialization for API use
- **Why Pydantic matters for FastAPI** — auto-validation of request bodies, auto-generated OpenAPI docs

---

### Task 8: Document It — Write Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_posts\2026-04-02-pydantic-models-for-trading-data.html`

- [ ] **Step 1: Write the blog post**

Use this frontmatter (clean format, no WordPress-legacy fields):

```yaml
---
layout: post
title: "Pydantic v2 Models for Trading Data"
date: 2026-04-02
tags: [pydantic, validation, models, finance, python, quant-lab]
categories:
- Python fundamentals
permalink: "/2026/04/02/pydantic-models-trading-data/"
---
```

Sections to cover:
- What Pydantic does and why it matters for financial data
- Field validators — transforming and validating individual fields (uppercase ticker, reject future dates)
- Computed fields — derived values like notional and average price
- Model validators — cross-field rules (weights sum to 1, lengths match)
- Serialization — `model_dump()` and `model_validate_json()` for API readiness
- Link to the exercise code in quant_lab repo

---

### Task 9: Commit Blog Post

- [ ] **Step 1: Commit blog post in finbytes_git**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-02-pydantic-models-for-trading-data.html
git commit -m "post: Pydantic v2 models for trading data"
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

Check: `https://mish-codes.github.io/FinBytes/2026/04/02/pydantic-models-trading-data/`

---

### Task 10: Commit quant_lab docs and push

- [ ] **Step 1: Commit spec and plan files**

```bash
cd C:\codebase\quant_lab
git add docs/superpowers/specs/2026-04-02-pydantic-trading-models-design.md
git add docs/superpowers/plans/2026-04-02-pydantic-trading-models.md
git push origin working
```

- [ ] **Step 2: Create PR from working to master**

Create a PR for the exercise code + docs, then merge.
