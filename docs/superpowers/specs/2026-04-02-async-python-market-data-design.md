# Task 4: Async Python for Market Data — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/04-async/`
**Concept:** async/await, asyncio, aiohttp. Concurrent price fetching with graceful error handling.

---

## Functions

### fetch_price
| | |
|--|--|
| **Signature** | `async def fetch_price(ticker: str) -> float` |
| **Purpose** | Fetch the current market price for a single ticker |
| **API** | Yahoo Finance chart API (`https://query1.finance.yahoo.com/v8/finance/chart/{ticker}`) |
| **Returns** | `float` — the `regularMarketPrice` from the response |
| **Errors** | Raises on HTTP errors via `response.raise_for_status()` |

### fetch_many_prices
| | |
|--|--|
| **Signature** | `async def fetch_many_prices(tickers: list[str]) -> dict[str, float]` |
| **Purpose** | Fetch prices for multiple tickers concurrently |
| **Concurrency** | Uses `asyncio.gather` to run all fetches in parallel |
| **Error handling** | Failed tickers silently skipped — returns only successful results |
| **Returns** | `dict[str, float]` — mapping of ticker to price |

## Async Concepts Covered

- `async def` / `await` — defining and calling coroutines
- `asyncio.gather` — running multiple coroutines concurrently
- `aiohttp.ClientSession` — async HTTP client
- `async with` — async context managers for session and response lifecycle
- Graceful partial failure — `try/except` inside gathered tasks

## Tests (3 total)

### TestFetchPrice (1 test)
1. `test_returns_float` — mock full aiohttp session chain (ClientSession, response, json), verify fetch_price returns correct float value (150.25)

### TestFetchManyPrices (2 tests)
2. `test_fetches_concurrently` — patch fetch_price with 50ms sleep mock, call with 3 tickers, verify all started within 30ms of each other (proving concurrent not sequential execution)
3. `test_partial_failure_returns_available` — one ticker raises ValueError, verify other two tickers still returned, failing ticker excluded from results

## Test Infrastructure

- `pytest-asyncio` with `asyncio_mode = "auto"` — test functions can be `async def` directly
- `AsyncMock` for mocking async functions and context managers
- `patch` for replacing `aiohttp.ClientSession` and `fetch_price`

## File Structure

```
exercises/04-async/
├── pyproject.toml              # aiohttp, pytest, pytest-asyncio
├── src/
│   └── async_prices.py         # fetch_price, fetch_many_prices
└── tests/
    └── test_async_prices.py    # 3 tests across 2 test classes
```

## TDD Flow

1. Create pyproject.toml
2. Write failing tests (3 tests)
3. Run tests — verify they fail (ModuleNotFoundError)
4. Implement async_prices.py
5. Run tests — verify all 3 pass
6. Commit to quant_lab (working branch)
7. Teaching conversation (async concepts)
8. Write blog post to finbytes_git
9. Commit blog post (working → master via merge)
