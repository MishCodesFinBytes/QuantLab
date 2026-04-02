# PostgreSQL + SQLAlchemy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Learn async SQLAlchemy 2.0 by building a ScanRecord model with save/query functions, tested with SQLite in-memory and backed by PostgreSQL via Docker Compose.

**Architecture:** A single `ScanRecord` model mapped with SQLAlchemy 2.0 declarative style. Two async functions (`save_scan`, `get_recent_scans`) operate on async sessions. Tests use SQLite in-memory for speed. PostgreSQL runs via Docker Compose for real-world verification.

**Tech Stack:** Python 3.11, SQLAlchemy 2.0 (async), asyncpg, aiosqlite, pytest, pytest-asyncio, Docker Compose, PostgreSQL 16

---

## File Structure

```
exercises/08-postgres-sqlalchemy/
├── pyproject.toml              # project config, deps, pytest settings
├── src/
│   ├── models.py               # Base + ScanRecord model
│   └── db.py                   # save_scan + get_recent_scans functions
├── tests/
│   └── test_db.py              # 3 async tests with SQLite in-memory
└── docker-compose.yml          # PostgreSQL 16 service with named volume
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/08-postgres-sqlalchemy/pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "postgres-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0", "aiosqlite>=0.20.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy/src
mkdir -p C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy/tests
```

- [ ] **Step 3: Install dev dependencies**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
pip install -e ".[dev]"
```

---

### Task 2: ScanRecord Model (TDD)

**Files:**
- Create: `exercises/08-postgres-sqlalchemy/tests/test_db.py`
- Create: `exercises/08-postgres-sqlalchemy/src/models.py`

- [ ] **Step 1: Write the test fixture and first failing test**

```python
# exercises/08-postgres-sqlalchemy/tests/test_db.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
async def session():
    """In-memory SQLite for fast tests."""
    from src.models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


class TestScanRecord:
    async def test_save_and_retrieve(self, session):
        from src.db import save_scan, get_recent_scans

        await save_scan(session, tickers=["AAPL", "MSFT"], var_pct=-2.15, narrative="Test narrative")
        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 1
        assert scans[0].tickers == "AAPL,MSFT"
        assert scans[0].var_pct == pytest.approx(-2.15)
        assert scans[0].narrative == "Test narrative"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
python -m pytest tests/test_db.py::TestScanRecord::test_save_and_retrieve -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 3: Create the ScanRecord model**

```python
# exercises/08-postgres-sqlalchemy/src/models.py
from datetime import datetime, UTC
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
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
```

- [ ] **Step 4: Create minimal db.py to make the test pass**

```python
# exercises/08-postgres-sqlalchemy/src/db.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ScanRecord


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

- [ ] **Step 5: Run test to verify it passes**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
python -m pytest tests/test_db.py::TestScanRecord::test_save_and_retrieve -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd C:/codebase/quant_lab
git add exercises/08-postgres-sqlalchemy/
git commit -m "feat(08): ScanRecord model + save/query with first test"
```

---

### Task 3: Ordering Test (TDD)

**Files:**
- Modify: `exercises/08-postgres-sqlalchemy/tests/test_db.py`

- [ ] **Step 1: Add the ordering test**

Add this method inside the `TestScanRecord` class in `tests/test_db.py`:

```python
    async def test_recent_scans_ordered_by_date(self, session):
        from src.db import save_scan, get_recent_scans

        await save_scan(session, tickers=["AAPL"], var_pct=-1.0, narrative="First")
        await save_scan(session, tickers=["MSFT"], var_pct=-2.0, narrative="Second")
        scans = await get_recent_scans(session, limit=10)
        assert scans[0].narrative == "Second"  # most recent first
        assert scans[1].narrative == "First"
```

- [ ] **Step 2: Run test to verify it passes**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
python -m pytest tests/test_db.py::TestScanRecord::test_recent_scans_ordered_by_date -v
```

Expected: PASS (ordering already implemented in `get_recent_scans`)

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add exercises/08-postgres-sqlalchemy/tests/test_db.py
git commit -m "test(08): verify scan ordering by date"
```

---

### Task 4: Limit Test (TDD)

**Files:**
- Modify: `exercises/08-postgres-sqlalchemy/tests/test_db.py`

- [ ] **Step 1: Add the limit test**

Add this method inside the `TestScanRecord` class in `tests/test_db.py`:

```python
    async def test_limit_works(self, session):
        from src.db import save_scan, get_recent_scans

        for i in range(5):
            await save_scan(session, tickers=[f"T{i}"], var_pct=-float(i), narrative=f"Scan {i}")
        scans = await get_recent_scans(session, limit=3)
        assert len(scans) == 3
```

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
python -m pytest tests/test_db.py -v
```

Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add exercises/08-postgres-sqlalchemy/tests/test_db.py
git commit -m "test(08): verify scan limit parameter"
```

---

### Task 5: Docker Compose for PostgreSQL

**Files:**
- Create: `exercises/08-postgres-sqlalchemy/docker-compose.yml`

- [ ] **Step 1: Create docker-compose.yml**

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

- [ ] **Step 2: Start PostgreSQL and verify**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
docker compose up -d
```

Wait a few seconds for PostgreSQL to initialize, then verify:

```bash
docker compose exec db psql -U quantlab -c "SELECT 1;"
```

Expected: a result with `1` confirming PostgreSQL is running.

- [ ] **Step 3: Stop PostgreSQL**

```bash
docker compose down
```

- [ ] **Step 4: Commit**

```bash
cd C:/codebase/quant_lab
git add exercises/08-postgres-sqlalchemy/docker-compose.yml
git commit -m "feat(08): Docker Compose for PostgreSQL 16"
```

---

### Task 6: Final Commit

- [ ] **Step 1: Run all tests one final time**

```bash
cd C:/codebase/quant_lab/exercises/08-postgres-sqlalchemy
python -m pytest tests/test_db.py -v
```

Expected: 3 passed

- [ ] **Step 2: Commit exercise**

```bash
cd C:/codebase/quant_lab
git add exercises/08-postgres-sqlalchemy/
git commit -m "feat(exercises): 08 PostgreSQL + SQLAlchemy async"
```

---

### Task 7: Teaching Conversation

Cover these concepts interactively:

- [ ] **Step 1: SQLAlchemy 2.0 style** — `Mapped`, `mapped_column`, `DeclarativeBase` vs legacy `Column`/`declarative_base()`
- [ ] **Step 2: Async SQLAlchemy** — `create_async_engine`, `async_sessionmaker`, why `await` on DB calls
- [ ] **Step 3: Why async DB in financial services** — high-throughput, non-blocking I/O, handling many concurrent requests
- [ ] **Step 4: Testing with SQLite in-memory vs real PostgreSQL** — speed vs accuracy trade-offs, when each is appropriate
- [ ] **Step 5: Connection pooling** — why it matters under load, how SQLAlchemy handles it
- [ ] **Step 6: PostgreSQL vs SQLite** — when each makes sense, production vs development
- [ ] **Step 7: Alembic conceptual overview** — what migrations are, why they matter, how Alembic autogenerates them (hands-on in capstone)

---

### Task 8: Blog Post

**Files:**
- Create: blog post in `C:/codebase/finbytes_git/docs/_posts/`

- [ ] **Step 1: Write blog post**

Content sections:
1. **What we're building** — ScanRecord model, save/query functions, async SQLAlchemy
2. **SQLAlchemy 2.0 style** — Mapped, mapped_column, DeclarativeBase
3. **The model** — ScanRecord walkthrough
4. **Async functions** — save_scan, get_recent_scans
5. **Testing with SQLite in-memory** — why and how
6. **Docker Compose for PostgreSQL** — setup, named volumes for persistence
7. **What is Alembic?** — conceptual explainer: migrations, autogenerate, upgrade/downgrade (no hands-on code)
8. **Key takeaways**

- [ ] **Step 2: Commit blog post**

```bash
cd C:/codebase/finbytes_git
git add docs/_posts/
git commit -m "docs(blog): 08 PostgreSQL + SQLAlchemy"
```

- [ ] **Step 3: PR working -> master for both repos, merge, sync**

Follow standard workflow: create PR from `working` to `master`, merge, pull master, rebase working. Do this for both `quant_lab` and `finbytes_git`.
