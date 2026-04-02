# Capstone Sub-project B: API + Database — Design Spec

**Date:** 2026-04-02
**Project:** `projects/stock-risk-scanner/`
**Concept:** FastAPI endpoints with background task processing, SQLAlchemy persistence, Alembic migrations, and structured logging. Builds on Sub-project A's core modules.

**Sub-project scope:** Part 2 of 3. Sub-project A (core modules) is complete. Sub-project C adds Docker + CI + docs.

---

## New Files

```
projects/stock-risk-scanner/
├── src/scanner/
│   ├── db_models.py        # SQLAlchemy ScanRecord model (NEW)
│   ├── db.py               # DB functions: create, complete, fail, query (NEW)
│   └── main.py             # FastAPI app with endpoints + background tasks (NEW)
├── alembic.ini             # Alembic config (NEW)
├── alembic/
│   └── env.py              # Alembic async env (NEW)
└── tests/
    ├── test_db_layer.py    # DB function tests (NEW)
    └── test_api.py         # Endpoint tests (NEW)
```

**Modified files:**
- `pyproject.toml` — add FastAPI, SQLAlchemy, Alembic, structlog, httpx deps

---

## Database Model: ScanRecord (`src/scanner/db_models.py`)

SQLAlchemy 2.0 style, same pattern as exercise 08.

| Column | Type | SQLAlchemy | Notes |
|--------|------|------------|-------|
| id | int | `mapped_column(primary_key=True)` | auto-increment |
| tickers | str | `mapped_column(String(200))` | comma-joined ticker symbols |
| weights | str | `mapped_column(String(200))` | comma-joined floats |
| period | str | `mapped_column(String(10))` | e.g., "1y" |
| status | str | `mapped_column(String(20))` | "pending", "complete", "failed" |
| var_pct | float | `mapped_column(Float, nullable=True)` | populated on completion |
| cvar_pct | float | `mapped_column(Float, nullable=True)` | populated on completion |
| max_drawdown_pct | float | `mapped_column(Float, nullable=True)` | populated on completion |
| volatility_pct | float | `mapped_column(Float, nullable=True)` | populated on completion |
| sharpe_ratio | float | `mapped_column(Float, nullable=True)` | populated on completion |
| narrative | str | `mapped_column(String(2000), nullable=True)` | populated on completion |
| error_message | str | `mapped_column(String(500), nullable=True)` | populated on failure |
| created_at | datetime | `mapped_column(DateTime(timezone=True))` | `datetime.now(UTC)` |
| completed_at | datetime | `mapped_column(DateTime(timezone=True), nullable=True)` | when scan finished |

---

## Database Layer (`src/scanner/db.py`)

### Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `create_pending_scan` | `async def create_pending_scan(session: AsyncSession, request: ScanRequest) -> ScanRecord` | Insert pending record, return with ID |
| `complete_scan` | `async def complete_scan(session: AsyncSession, scan_id: int, result: ScanResult) -> None` | Update with metrics + narrative, status="complete", set completed_at |
| `fail_scan` | `async def fail_scan(session: AsyncSession, scan_id: int, error: str) -> None` | Update with error_message, status="failed", set completed_at |
| `get_scan` | `async def get_scan(session: AsyncSession, scan_id: int) -> ScanRecord \| None` | Get single scan by ID |
| `get_recent_scans` | `async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]` | Recent completed scans, newest first |

### Session dependency

`get_session` — async generator yielding `AsyncSession`, used as FastAPI `Depends()`.

Engine and session factory created in app lifespan, stored in `app.state`.

---

## FastAPI App (`src/scanner/main.py`)

### Endpoints

| Route | Method | Request | Response | Notes |
|-------|--------|---------|----------|-------|
| `/health` | GET | — | `{"status": "ok"}` | Health check |
| `/api/scan` | POST | `ScanRequest` JSON body | `{"id": 1, "status": "pending"}` | Creates pending record, starts background task |
| `/api/scans/{id}` | GET | path param `id` | Full scan record JSON | Returns pending/complete/failed scan |
| `/api/scans` | GET | query param `limit` (default 10) | List of scan records | Recent completed scans |

### Background task flow

1. `POST /api/scan`: validate request → insert pending `ScanRecord` → add background task → return `{id, status}`
2. Background task: create new session → run `scan(request)` → `complete_scan(session, id, result)`
3. On exception: `fail_scan(session, id, str(error))`

### App lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(DATABASE_URL)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield
    await engine.dispose()
```

`DATABASE_URL` read from environment, defaults to `sqlite+aiosqlite:///scanner.db` for local dev.

### Structured logging

structlog configured at module level:
- `TimeStamper(fmt="iso")`
- `JSONRenderer()`
- Log scan start, completion, and failures in endpoints/background task

---

## Alembic

- `alembic.ini`: `sqlalchemy.url = postgresql+asyncpg://quantlab:quantlab_dev@localhost/quantlab`
- `alembic/env.py`: imports `Base` from `db_models.py`, async config with `run_async`
- Initial migration: auto-generated `create scan_records table`
- Tests do NOT use Alembic — they use `Base.metadata.create_all()` with SQLite in-memory

---

## Updated Dependencies

Add to `pyproject.toml` dependencies:
- `fastapi>=0.115.0`
- `uvicorn[standard]>=0.32.0`
- `sqlalchemy[asyncio]>=2.0.30`
- `asyncpg>=0.29.0`
- `alembic>=1.13.0`
- `structlog>=24.1.0`

Add to dev dependencies:
- `httpx>=0.27.0`

---

## Tests

### test_db_layer.py (5 tests, SQLite in-memory)

| Test | Asserts |
|------|---------|
| `test_create_pending_scan` | Record created with status="pending", id assigned |
| `test_complete_scan` | Status changes to "complete", metrics populated, completed_at set |
| `test_fail_scan` | Status changes to "failed", error_message set, completed_at set |
| `test_get_scan` | Returns record by ID, returns None for missing ID |
| `test_get_recent_scans` | Returns completed scans, newest first, respects limit |

### test_api.py (4 tests, httpx.AsyncClient + SQLite in-memory)

| Test | Asserts |
|------|---------|
| `test_health` | GET /health returns 200 + `{"status": "ok"}` |
| `test_create_scan` | POST /api/scan returns 202 + `{id, status: "pending"}` |
| `test_get_scan` | GET /api/scans/{id} returns the scan record |
| `test_list_scans` | GET /api/scans returns a list |

API tests mock the scanner pipeline (no real yfinance/Claude calls).

### Test total: 9 new tests + 15 existing = 24 total

---

## Out of Scope (Sub-project C)

- Dockerfile and docker-compose (app + PostgreSQL)
- GitHub Actions CI
- Blog post
- README update
