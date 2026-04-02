# Task 3: FastAPI — Your First Financial API — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/03-fastapi/`
**Concept:** Build a simple API that serves portfolio data. Routes, path/query params, request bodies, status codes, TestClient. Builds on Pydantic patterns from Task 2.

---

## Endpoints

| Method | Path | Request Body | Response | Success Status | Error Status |
|--------|------|-------------|----------|----------------|--------------|
| GET | `/health` | — | `{"status": "ok"}` | 200 | — |
| GET | `/watchlist` | — | `list[TickerOut]` | 200 | — |
| POST | `/watchlist` | `TickerIn` | `TickerOut` | 201 | 409 (duplicate) |
| DELETE | `/watchlist/{ticker}` | — (path param) | — | 204 | 404 (not found) |
| POST | `/analyze` | `PortfolioIn` | `AnalysisOut` | 200 | 422 (validation) |

## Models (self-contained in app.py)

### TickerIn
| Field | Type | Constraints |
|-------|------|-------------|
| ticker | str | min_length=1, max_length=10 |

### TickerOut
| Field | Type | Notes |
|-------|------|-------|
| ticker | str | uppercased ticker symbol |

### PortfolioIn
| Field | Type | Constraints |
|-------|------|-------------|
| tickers | list[str] | min_length=1 |
| weights | list[float] | min_length=1 |
| period | str | default="1y" |

**Model validator:** tickers and weights must have the same length.

### AnalysisOut
| Field | Type | Notes |
|-------|------|-------|
| tickers | list[str] | echoed from request |
| weights | list[float] | echoed from request |
| period | str | echoed from request |
| message | str | stub message (real analysis in Task 5+) |

## Storage

In-memory `dict[str, dict]` keyed by uppercase ticker. Replaced by PostgreSQL in exercise 08.

## FastAPI Features Covered

- Route decorators (`@app.get`, `@app.post`, `@app.delete`)
- Path parameters (`/watchlist/{ticker}`)
- Request bodies (Pydantic models auto-validated)
- Response models (`response_model=`)
- Status codes (200, 201, 204, 404, 409, 422)
- `HTTPException` for error responses
- `TestClient` for testing without a running server
- Auto-generated OpenAPI docs at `/docs`

## Tests (9 total)

### TestHealthCheck (1 test)
1. `test_health_returns_ok` — GET /health returns 200 with `{"status": "ok"}`

### TestWatchlist (6 tests)
2. `test_get_empty_watchlist` — GET /watchlist returns 200 with `[]`
3. `test_add_ticker` — POST /watchlist with `{"ticker": "AAPL"}` returns 201
4. `test_add_and_list` — add two tickers, GET /watchlist returns both
5. `test_duplicate_ticker_rejected` — POST same ticker twice returns 409
6. `test_delete_ticker` — DELETE /watchlist/GOOG returns 204
7. `test_delete_missing_returns_404` — DELETE /watchlist/ZZZZ returns 404

### TestPortfolioAnalysis (2 tests)
8. `test_analyze_validates_weights` — mismatched lengths returns 422
9. `test_analyze_returns_summary` — valid request returns 200 with tickers and message

### Test Infrastructure
- `client` fixture providing `TestClient(app)`
- `clear_watchlist` autouse fixture resetting `_watchlist` before each test to prevent state leakage

## File Structure

```
exercises/03-fastapi/
├── pyproject.toml              # fastapi, uvicorn, pydantic, pytest, httpx
├── src/
│   └── app.py                  # FastAPI app with all endpoints and models
└── tests/
    └── test_app.py             # 9 tests across 3 test classes
```

## TDD Flow

1. Create pyproject.toml
2. Write failing tests (9 tests)
3. Run tests — verify they fail (ModuleNotFoundError)
4. Implement app.py
5. Run tests — verify all 9 pass
6. Commit to quant_lab (working branch)
7. Teaching conversation (FastAPI concepts)
8. Write blog post to finbytes_git
9. Commit blog post (working → master via merge)
