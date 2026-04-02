# Capstone Sub-project A: Core Scanner — Design Spec

**Date:** 2026-04-02
**Project:** `projects/stock-risk-scanner/`
**Concept:** Four focused modules (models, risk, market data, narrative) connected through Pydantic models, with a thin orchestrator. Copied and adapted from exercises 01, 02, 05, 06. No infrastructure — pure Python.

**Sub-project scope:** This is part 1 of 3. Sub-project B adds FastAPI + database. Sub-project C adds Docker + CI + docs.

---

## File Structure

```
projects/stock-risk-scanner/
├── pyproject.toml
├── src/scanner/
│   ├── __init__.py
│   ├── models.py          # Pydantic models (request, metrics, result)
│   ├── risk.py             # Risk calculations (VaR, CVaR, drawdown, vol, Sharpe)
│   ├── market_data.py      # yfinance price fetcher
│   ├── narrative.py        # Claude narrative generator with fallback
│   └── scanner.py          # Orchestrator: fetch → calculate → narrate → result
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_risk.py
    ├── test_market_data.py
    ├── test_narrative.py
    └── test_scanner.py
```

---

## Dependencies

```toml
[project]
name = "stock-risk-scanner"
version = "0.1.0"
description = "Portfolio risk scanner with AI-generated narratives"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.9.0",
    "yfinance>=0.2.40",
    "numpy>=1.26.0",
    "pandas>=2.0.0",
    "anthropic>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

Note: Additional dependencies (FastAPI, SQLAlchemy, etc.) will be added in Sub-project B.

---

## Module: models.py

### ScanRequest

| Field | Type | Validation | Default |
|-------|------|------------|---------|
| tickers | list[str] | min 1 item, uppercase enforced | — |
| weights | list[float] | must sum to ~1.0 (tolerance 0.01) | — |
| period | str | — | "1y" |

**Validators:**
- `len(tickers) == len(weights)` — raise `ValueError` if mismatched
- `abs(sum(weights) - 1.0) <= 0.01` — raise `ValueError` if weights don't sum to 1
- Tickers uppercased via `field_validator`

### RiskMetrics

| Field | Type | Notes |
|-------|------|-------|
| var_pct | float | Value at Risk (95%) as percentage |
| cvar_pct | float | Conditional VaR / Expected Shortfall |
| max_drawdown_pct | float | Maximum peak-to-trough decline |
| volatility_pct | float | Annualized volatility |
| sharpe_ratio | float | Risk-adjusted return (risk-free rate = 0) |

### ScanResult

| Field | Type | Notes |
|-------|------|-------|
| tickers | list[str] | From request |
| weights | list[float] | From request |
| metrics | RiskMetrics | Calculated risk metrics |
| narrative | str | Claude-generated or fallback summary |
| generated_at | datetime | Timezone-aware, `datetime.now(UTC)` |

---

## Module: risk.py

### calculate_risk_metrics

| | |
|--|--|
| **Signature** | `def calculate_risk_metrics(prices: pd.DataFrame, weights: list[float]) -> RiskMetrics` |
| **Input** | DataFrame of daily closing prices (columns = tickers), list of weights |
| **Output** | `RiskMetrics` Pydantic model |

**Calculations:**

| Metric | Method |
|--------|--------|
| Portfolio returns | Weighted sum of daily log returns: `np.log(prices / prices.shift(1))` × weights |
| VaR (95%) | `np.percentile(portfolio_returns, 5)` — 5th percentile |
| CVaR | Mean of all returns ≤ VaR |
| Max drawdown | Largest peak-to-trough decline from cumulative returns |
| Volatility | `portfolio_returns.std() * np.sqrt(252)` — annualized |
| Sharpe ratio | `(portfolio_returns.mean() * 252) / volatility` — annualized, risk-free = 0 |

**Tests (3):**
1. Known returns → verify VaR and CVaR values with `pytest.approx`
2. Simple declining series → verify max drawdown
3. Equal weights → verify Sharpe ratio has expected sign

---

## Module: market_data.py

### fetch_prices

| | |
|--|--|
| **Signature** | `def fetch_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame` |
| **Input** | List of ticker symbols, yfinance period string |
| **Output** | DataFrame of daily closing prices (columns = tickers) |
| **Error handling** | Raise `ValueError` if any ticker returns empty data |

Calls `yfinance.download(tickers, period=period)` and extracts the "Close" column(s).

**Tests (2):**
1. Mock `yfinance.download`, verify DataFrame has correct columns
2. Mock empty data for a ticker, verify `ValueError` raised with ticker name

---

## Module: narrative.py

### RiskNarrator

| | |
|--|--|
| **Constructor** | `def __init__(self, model: str = "claude-sonnet-4-6")` |
| **Behavior** | Tries `anthropic.Anthropic()`. If `ANTHROPIC_API_KEY` not set, sets `self.client = None` |

### generate method

| | |
|--|--|
| **Signature** | `def generate(self, tickers: list[str], metrics: RiskMetrics) -> str` |
| **With API key** | Calls Claude with risk analyst system prompt, returns narrative |
| **Without API key** | Returns fallback string: "Portfolio {tickers}: VaR {var}%, volatility {vol}%, Sharpe {sharpe}" |
| **On API error** | Returns same fallback string |

**System prompt:** Senior risk analyst persona, 3-4 sentences, plain English.

**Tests (3):**
1. Mock Anthropic client → verify narrative from API response
2. Mock API error → verify fallback string
3. No API key (client is None) → verify fallback string

---

## Module: scanner.py

### scan

| | |
|--|--|
| **Signature** | `def scan(request: ScanRequest) -> ScanResult` |
| **Pipeline** | fetch_prices → calculate_risk_metrics → narrator.generate → ScanResult |

Steps:
1. `fetch_prices(request.tickers, request.period)` → DataFrame
2. `calculate_risk_metrics(prices, request.weights)` → RiskMetrics
3. `RiskNarrator().generate(request.tickers, metrics)` → narrative string
4. Return `ScanResult(tickers=request.tickers, weights=request.weights, metrics=metrics, narrative=narrative, generated_at=datetime.now(UTC))`

**Tests (1):**
1. Mock `fetch_prices` and `RiskNarrator.generate`, provide real risk calculation on synthetic prices, verify `ScanResult` has all fields populated

---

## Test Summary

| Module | Tests | Total |
|--------|-------|-------|
| models.py | Validation: valid request, mismatched lengths, bad weights sum, uppercase | 4 |
| risk.py | VaR/CVaR values, max drawdown, Sharpe sign | 3 |
| market_data.py | Successful fetch, empty ticker error | 2 |
| narrative.py | API success, API error fallback, no key fallback | 3 |
| scanner.py | Full pipeline with mocks | 1 |
| **Total** | | **13** |

---

## Out of Scope (Sub-project B & C)

- FastAPI endpoints
- SQLAlchemy models and database layer
- Alembic migrations
- Docker and docker-compose
- GitHub Actions CI
- Structured logging
- Blog post
- README update
