# FastAPI Portfolio API — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a simple financial API with FastAPI, learning routes, request/response models, status codes, and TestClient through TDD.

**Architecture:** Single FastAPI app with in-memory storage. Three endpoint groups: health check, watchlist CRUD, and portfolio analysis stub. All models self-contained in app.py. Tests use FastAPI's TestClient (no running server needed).

**Tech Stack:** Python 3.11+, FastAPI (>=0.115.0), uvicorn, Pydantic v2, pytest, httpx

---

## File Structure

```
exercises/03-fastapi/
├── pyproject.toml              # project config, deps, pytest settings
├── src/
│   └── app.py                  # FastAPI app with all endpoints and models
└── tests/
    └── test_app.py             # 9 tests across 3 test classes
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/03-fastapi/pyproject.toml`

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

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p exercises/03-fastapi/src exercises/03-fastapi/tests
```

---

### Task 2: Write Failing Tests

**Files:**
- Create: `exercises/03-fastapi/tests/test_app.py`

- [ ] **Step 1: Write all 9 tests**

```python
import pytest
from fastapi.testclient import TestClient
from app import app, _watchlist


@pytest.fixture(autouse=True)
def clear_watchlist():
    _watchlist.clear()


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

- [ ] **Step 2: Install dependencies and run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\03-fastapi
pip install -e ".[dev]"
python -m pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

---

### Task 3: Implement Health and Watchlist Endpoints

**Files:**
- Create: `exercises/03-fastapi/src/app.py`

- [ ] **Step 1: Implement app.py with health check, models, and watchlist CRUD**

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

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd C:\codebase\quant_lab\exercises\03-fastapi
python -m pytest -v
```

Expected: 9 passed

---

### Task 4: Commit

- [ ] **Step 1: Commit exercise to quant_lab**

```bash
cd C:\codebase\quant_lab
git add exercises/03-fastapi/
git commit -m "feat(exercises): 03 FastAPI portfolio API"
```

---

### Task 5: Understand It — Teaching Conversation

No code changes. Interactive discussion covering:

- **FastAPI vs Flask vs Django REST** — why FastAPI for financial APIs (async-ready, auto-docs, Pydantic integration)
- **Path params, query params, request bodies** — when to use which
- **Dependency injection** — intro (used more in capstone)
- **Auto-generated OpenAPI docs** — available at `/docs` automatically
- **TestClient** — why it doesn't need a running server (ASGI in-process)
- **Status codes that matter** — 201 (created), 204 (no content), 404 (not found), 409 (conflict), 422 (validation error)

---

### Task 6: Document It — Write Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_posts\2026-04-02-fastapi-your-first-financial-api.html`

- [ ] **Step 1: Write the blog post**

Use this frontmatter (clean format):

```yaml
---
layout: post
title: "FastAPI — Your First Financial API"
date: 2026-04-02
tags: [fastapi, api, python, finance, quant-lab]
categories:
- Python fundamentals
permalink: "/2026/04/02/fastapi-your-first-financial-api/"
---
```

Sections to cover:
- Why FastAPI for financial services (async, auto-docs, Pydantic)
- Building a health check endpoint
- Watchlist CRUD — POST/GET/DELETE with proper status codes
- Request validation with Pydantic models
- Testing with TestClient (no server needed)
- Status codes: when to use 201, 204, 404, 409, 422
- Link to the exercise code in quant_lab repo

---

### Task 7: Commit Blog Post

- [ ] **Step 1: Commit blog post in finbytes_git**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-02-fastapi-your-first-financial-api.html
git commit -m "post: FastAPI — your first financial API"
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

Check: `https://mish-codes.github.io/FinBytes/2026/04/02/fastapi-your-first-financial-api/`

---

### Task 8: Commit quant_lab docs and push

- [ ] **Step 1: Commit spec and plan files**

```bash
cd C:\codebase\quant_lab
git add docs/superpowers/specs/2026-04-02-fastapi-portfolio-api-design.md
git add docs/superpowers/plans/2026-04-02-fastapi-portfolio-api.md
git push origin working
```

- [ ] **Step 2: Create PR from working to master**

```bash
gh pr create --title "feat: exercise 03 FastAPI portfolio API" --body "..." --base master --head working
```

- [ ] **Step 3: Merge PR and sync locally**

After merge on GitHub:

```bash
git fetch origin
git checkout master && git pull origin master
git checkout working
```
