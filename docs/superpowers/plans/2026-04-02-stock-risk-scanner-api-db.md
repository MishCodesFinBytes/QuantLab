# Stock Risk Scanner — API + Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add FastAPI endpoints with background task processing, SQLAlchemy persistence, Alembic migrations, and structured logging to the stock risk scanner.

**Architecture:** FastAPI app with 4 endpoints. `POST /api/scan` creates a pending DB record and fires a background task that runs the scanner pipeline, then updates the record to complete/failed. SQLAlchemy 2.0 async models persisted to PostgreSQL (SQLite in-memory for tests). Alembic manages schema migrations. structlog provides JSON-formatted logging.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic, asyncpg, aiosqlite, structlog, httpx, pytest

---

## File Structure

```
projects/stock-risk-scanner/
├── pyproject.toml                    # MODIFY: add new deps
├── src/scanner/
│   ├── db_models.py                  # NEW: SQLAlchemy ScanRecord
│   ├── db.py                         # NEW: DB functions + session dependency
│   └── main.py                       # NEW: FastAPI app + endpoints
├── alembic.ini                       # NEW: Alembic config
├── alembic/
│   └── env.py                        # NEW: async Alembic env
└── tests/
    ├── test_db_layer.py              # NEW: 5 DB function tests
    └── test_api.py                   # NEW: 4 endpoint tests
```

---

### Task 1: Update Dependencies

**Files:**
- Modify: `projects/stock-risk-scanner/pyproject.toml`

- [ ] **Step 1: Update pyproject.toml with new dependencies**

Replace the entire file content:

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
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Install updated dependencies**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
pip install -e ".[dev]"
```

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/pyproject.toml
git commit -m "feat(scanner): add FastAPI, SQLAlchemy, Alembic, structlog deps"
```

---

### Task 2: SQLAlchemy ScanRecord Model (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_db_layer.py`
- Create: `projects/stock-risk-scanner/src/scanner/db_models.py`

- [ ] **Step 1: Write failing test for pending scan creation**

```python
# projects/stock-risk-scanner/tests/test_db_layer.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
async def session():
    from src.scanner.db_models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


class TestCreatePendingScan:
    async def test_creates_pending_record(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan

        request = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        record = await create_pending_scan(session, request)
        assert record.id is not None
        assert record.status == "pending"
        assert record.tickers == "AAPL,MSFT"
        assert record.weights == "0.6,0.4"
        assert record.var_pct is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_db_layer.py::TestCreatePendingScan -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.db_models'`

- [ ] **Step 3: Create db_models.py**

```python
# projects/stock-risk-scanner/src/scanner/db_models.py
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    tickers: Mapped[str] = mapped_column(String(200))
    weights: Mapped[str] = mapped_column(String(200))
    period: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    var_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cvar_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volatility_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    narrative: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

- [ ] **Step 4: Create db.py with create_pending_scan**

```python
# projects/stock-risk-scanner/src/scanner/db.py
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.scanner.db_models import ScanRecord
from src.scanner.models import ScanRequest, ScanResult


async def create_pending_scan(session: AsyncSession, request: ScanRequest) -> ScanRecord:
    record = ScanRecord(
        tickers=",".join(request.tickers),
        weights=",".join(str(w) for w in request.weights),
        period=request.period,
        status="pending",
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def complete_scan(session: AsyncSession, scan_id: int, result: ScanResult) -> None:
    record = await session.get(ScanRecord, scan_id)
    record.status = "complete"
    record.var_pct = result.metrics.var_pct
    record.cvar_pct = result.metrics.cvar_pct
    record.max_drawdown_pct = result.metrics.max_drawdown_pct
    record.volatility_pct = result.metrics.volatility_pct
    record.sharpe_ratio = result.metrics.sharpe_ratio
    record.narrative = result.narrative
    record.completed_at = datetime.now(UTC)
    await session.commit()


async def fail_scan(session: AsyncSession, scan_id: int, error: str) -> None:
    record = await session.get(ScanRecord, scan_id)
    record.status = "failed"
    record.error_message = error
    record.completed_at = datetime.now(UTC)
    await session.commit()


async def get_scan(session: AsyncSession, scan_id: int) -> ScanRecord | None:
    return await session.get(ScanRecord, scan_id)


async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]:
    stmt = (
        select(ScanRecord)
        .where(ScanRecord.status == "complete")
        .order_by(ScanRecord.created_at.desc(), ScanRecord.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_db_layer.py::TestCreatePendingScan -v
```

Expected: 1 passed

- [ ] **Step 6: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): ScanRecord model + DB functions"
```

---

### Task 3: Complete and Fail Scan Tests (TDD)

**Files:**
- Modify: `projects/stock-risk-scanner/tests/test_db_layer.py`

- [ ] **Step 1: Add complete_scan and fail_scan tests**

Add these classes after `TestCreatePendingScan` in `test_db_layer.py`:

```python
class TestCompleteScan:
    async def test_updates_to_complete(self, session):
        from src.scanner.models import ScanRequest, ScanResult, RiskMetrics
        from src.scanner.db import create_pending_scan, complete_scan, get_scan
        from datetime import datetime, UTC

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        metrics = RiskMetrics(
            var_pct=-2.15, cvar_pct=-3.42, max_drawdown_pct=-18.7,
            volatility_pct=22.5, sharpe_ratio=1.2,
        )
        result = ScanResult(
            tickers=["AAPL"], weights=[1.0], metrics=metrics,
            narrative="Looks good.", generated_at=datetime.now(UTC),
        )
        await complete_scan(session, record.id, result)

        updated = await get_scan(session, record.id)
        assert updated.status == "complete"
        assert updated.var_pct == pytest.approx(-2.15)
        assert updated.narrative == "Looks good."
        assert updated.completed_at is not None


class TestFailScan:
    async def test_updates_to_failed(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan, fail_scan, get_scan

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        await fail_scan(session, record.id, "yfinance timeout")

        updated = await get_scan(session, record.id)
        assert updated.status == "failed"
        assert updated.error_message == "yfinance timeout"
        assert updated.completed_at is not None
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_db_layer.py -v
```

Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/tests/test_db_layer.py
git commit -m "test(scanner): complete and fail scan DB operations"
```

---

### Task 4: Query Function Tests (TDD)

**Files:**
- Modify: `projects/stock-risk-scanner/tests/test_db_layer.py`

- [ ] **Step 1: Add get_scan and get_recent_scans tests**

Add these classes to `test_db_layer.py`:

```python
class TestGetScan:
    async def test_returns_record_by_id(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan, get_scan

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        found = await get_scan(session, record.id)
        assert found is not None
        assert found.id == record.id

    async def test_returns_none_for_missing_id(self, session):
        from src.scanner.db import get_scan

        found = await get_scan(session, 9999)
        assert found is None


class TestGetRecentScans:
    async def test_returns_completed_scans_newest_first(self, session):
        from src.scanner.models import ScanRequest, ScanResult, RiskMetrics
        from src.scanner.db import create_pending_scan, complete_scan, get_recent_scans
        from datetime import datetime, UTC

        metrics = RiskMetrics(
            var_pct=-1.0, cvar_pct=-2.0, max_drawdown_pct=-10.0,
            volatility_pct=15.0, sharpe_ratio=0.5,
        )

        # Create 3 scans: 2 completed, 1 pending
        for ticker in ["AAPL", "MSFT"]:
            req = ScanRequest(tickers=[ticker], weights=[1.0])
            rec = await create_pending_scan(session, req)
            result = ScanResult(
                tickers=[ticker], weights=[1.0], metrics=metrics,
                narrative=f"{ticker} scan", generated_at=datetime.now(UTC),
            )
            await complete_scan(session, rec.id, result)

        pending_req = ScanRequest(tickers=["GOOG"], weights=[1.0])
        await create_pending_scan(session, pending_req)

        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 2  # only completed, not pending
        assert scans[0].tickers == "MSFT"  # newest first
```

- [ ] **Step 2: Run all DB tests**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_db_layer.py -v
```

Expected: 6 passed

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/tests/test_db_layer.py
git commit -m "test(scanner): query functions — get_scan and get_recent_scans"
```

---

### Task 5: FastAPI App + Endpoints (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_api.py`
- Create: `projects/stock-risk-scanner/src/scanner/main.py`

- [ ] **Step 1: Write failing API tests**

```python
# projects/stock-risk-scanner/tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd


@pytest.fixture
async def app():
    from src.scanner.db_models import Base
    from src.scanner.main import create_app

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    app = create_app()
    app.state.session_factory = factory
    yield app
    await engine.dispose()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestHealthEndpoint:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestCreateScan:
    async def test_returns_pending(self, client):
        resp = await client.post(
            "/api/scan",
            json={"tickers": ["AAPL", "MSFT"], "weights": [0.6, 0.4]},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "pending"
        assert "id" in data


class TestGetScan:
    async def test_returns_scan_by_id(self, client):
        # Create a scan first
        resp = await client.post(
            "/api/scan",
            json={"tickers": ["AAPL"], "weights": [1.0]},
        )
        scan_id = resp.json()["id"]

        resp = await client.get(f"/api/scans/{scan_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == scan_id
        assert resp.json()["status"] == "pending"

    async def test_returns_404_for_missing_id(self, client):
        resp = await client.get("/api/scans/9999")
        assert resp.status_code == 404


class TestListScans:
    async def test_returns_list(self, client):
        resp = await client.get("/api/scans")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_api.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.main'`

- [ ] **Step 3: Implement main.py**

```python
# projects/stock-risk-scanner/src/scanner/main.py
import os
from contextlib import asynccontextmanager
from datetime import datetime, UTC

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.scanner.db import (
    complete_scan,
    create_pending_scan,
    fail_scan,
    get_recent_scans,
    get_scan,
)
from src.scanner.models import ScanRequest, ScanResult
from src.scanner.scanner import scan

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///scanner.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(DATABASE_URL)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    log.info("app_started", database=DATABASE_URL)
    yield
    await engine.dispose()
    log.info("app_stopped")


def create_app() -> FastAPI:
    return FastAPI(title="Stock Risk Scanner", lifespan=lifespan)


app = create_app()


async def get_session() -> AsyncSession:
    factory: async_sessionmaker = app.state.session_factory
    async with factory() as session:
        yield session


def _record_to_dict(record) -> dict:
    return {
        "id": record.id,
        "tickers": record.tickers.split(","),
        "weights": [float(w) for w in record.weights.split(",")],
        "period": record.period,
        "status": record.status,
        "var_pct": record.var_pct,
        "cvar_pct": record.cvar_pct,
        "max_drawdown_pct": record.max_drawdown_pct,
        "volatility_pct": record.volatility_pct,
        "sharpe_ratio": record.sharpe_ratio,
        "narrative": record.narrative,
        "error_message": record.error_message,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
    }


async def _run_scan(scan_id: int, request: ScanRequest, session_factory):
    async with session_factory() as session:
        try:
            log.info("scan_started", scan_id=scan_id, tickers=request.tickers)
            result = scan(request)
            await complete_scan(session, scan_id, result)
            log.info("scan_completed", scan_id=scan_id, var=result.metrics.var_pct)
        except Exception as e:
            await fail_scan(session, scan_id, str(e))
            log.error("scan_failed", scan_id=scan_id, error=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/scan", status_code=202)
async def create_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    record = await create_pending_scan(session, request)
    background_tasks.add_task(_run_scan, record.id, request, app.state.session_factory)
    return {"id": record.id, "status": "pending"}


@app.get("/api/scans/{scan_id}")
async def read_scan(scan_id: int, session: AsyncSession = Depends(get_session)):
    record = await get_scan(session, scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _record_to_dict(record)


@app.get("/api/scans")
async def list_scans(limit: int = 10, session: AsyncSession = Depends(get_session)):
    records = await get_recent_scans(session, limit=limit)
    return [_record_to_dict(r) for r in records]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_api.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): FastAPI app with background scan tasks"
```

---

### Task 6: Alembic Setup

**Files:**
- Create: `projects/stock-risk-scanner/alembic.ini`
- Create: `projects/stock-risk-scanner/alembic/env.py`

- [ ] **Step 1: Create alembic.ini**

```ini
# projects/stock-risk-scanner/alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://quantlab:quantlab_dev@localhost/quantlab

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 2: Create alembic directory and env.py**

```bash
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/alembic/versions
```

```python
# projects/stock-risk-scanner/alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.scanner.db_models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Generate initial migration (requires PostgreSQL running)**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
docker compose up -d
```

Wait a few seconds, then:

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
alembic revision --autogenerate -m "create scan_records table"
```

Expected: A migration file created in `alembic/versions/`

- [ ] **Step 4: Apply migration**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
alembic upgrade head
```

Expected: `scan_records` table created in PostgreSQL

- [ ] **Step 5: Verify table exists**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
docker compose exec db psql -U quantlab -c "\dt scan_records"
```

Expected: Shows the `scan_records` table

- [ ] **Step 6: Stop PostgreSQL**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
docker compose down
```

- [ ] **Step 7: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/alembic.ini projects/stock-risk-scanner/alembic/
git commit -m "feat(scanner): Alembic setup with initial migration"
```

---

### Task 7: Full Test Suite Verification

- [ ] **Step 1: Run all tests**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/ -v
```

Expected: 24 passed (15 existing + 6 db_layer + 5 api = 26... but TestGetScan has 2 tests so: 15 + 6 + 5 = 26 total)

- [ ] **Step 2: Final commit if needed**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): capstone sub-project B complete — API + database"
```
