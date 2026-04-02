# Task 8: PostgreSQL + SQLAlchemy — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/08-postgres-sqlalchemy/`
**Concept:** Async SQLAlchemy 2.0 ORM with PostgreSQL via Docker Compose. Build a ScanRecord model with save/query functions. Tests use SQLite in-memory for speed.

---

## Model: ScanRecord

| Column | Type | SQLAlchemy | Notes |
|--------|------|------------|-------|
| id | int | `mapped_column(primary_key=True)` | auto-increment |
| tickers | str | `mapped_column(String(200))` | comma-joined ticker symbols (e.g., "AAPL,MSFT") |
| var_pct | float | `mapped_column(Float)` | Value at Risk percentage |
| narrative | str | `mapped_column(String(2000))` | risk narrative text |
| created_at | datetime | `mapped_column(DateTime(timezone=True), default=...)` | timezone-aware, uses `datetime.now(datetime.UTC)` |

Uses SQLAlchemy 2.0 style: `DeclarativeBase`, `Mapped`, `mapped_column`.

---

## Functions

### save_scan

| | |
|--|--|
| **Signature** | `async def save_scan(session: AsyncSession, tickers: list[str], var_pct: float, narrative: str) -> ScanRecord` |
| **Purpose** | Create and persist a ScanRecord |
| **Behavior** | Joins tickers with comma, creates record, commits, refreshes, returns record |

### get_recent_scans

| | |
|--|--|
| **Signature** | `async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]` |
| **Purpose** | Query most recent scan records |
| **Behavior** | Orders by `created_at` descending, applies limit, returns list |

---

## Tests

All tests use async SQLite in-memory via `aiosqlite`. No Docker dependency for tests.

### Fixture: session

Creates an in-memory SQLite async engine, runs `Base.metadata.create_all`, yields an `AsyncSession`, disposes engine after.

### Test cases

| Test | Asserts |
|------|---------|
| `test_save_and_retrieve` | Save one record, query it back, verify tickers/var_pct match |
| `test_recent_scans_ordered_by_date` | Save two records, verify newest comes first |
| `test_limit_works` | Save 5 records, query with limit=3, verify only 3 returned |

---

## Docker Compose

PostgreSQL 16 service for manual verification and capstone use.

| Key | Value |
|-----|-------|
| image | `postgres:16` |
| ports | `5432:5432` |
| environment | `POSTGRES_USER=quantlab`, `POSTGRES_PASSWORD=quantlab_dev`, `POSTGRES_DB=quantlab` |
| volumes | `pgdata:/var/lib/postgresql/data` (named volume for persistence) |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| sqlalchemy[asyncio] | >=2.0.30 | Async ORM |
| asyncpg | >=0.29.0 | PostgreSQL async driver |
| pytest | >=8.0.0 | Testing |
| pytest-asyncio | >=0.24.0 | Async test support |
| aiosqlite | >=0.20.0 | SQLite async driver for tests |

Python version: 3.11

---

## Files to Create

| File | Purpose |
|------|---------|
| `exercises/08-postgres-sqlalchemy/pyproject.toml` | Project metadata + dependencies |
| `exercises/08-postgres-sqlalchemy/src/models.py` | Base + ScanRecord model |
| `exercises/08-postgres-sqlalchemy/src/db.py` | save_scan + get_recent_scans functions |
| `exercises/08-postgres-sqlalchemy/tests/test_db.py` | 3 async tests with SQLite in-memory |
| `exercises/08-postgres-sqlalchemy/docker-compose.yml` | PostgreSQL 16 service |

---

## Blog Post

Covers the exercise walkthrough plus an **Alembic explainer section** (conceptual — what migrations are, why they matter, how Alembic works with SQLAlchemy). Hands-on Alembic deferred to capstone.

---

## Out of Scope

- Alembic setup and migrations (capstone)
- Relationships / foreign keys (capstone)
- CLI scripts
- Synchronous SQLAlchemy
- Testing against real PostgreSQL
