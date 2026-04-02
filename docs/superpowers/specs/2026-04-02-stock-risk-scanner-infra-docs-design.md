# Capstone Sub-project C: Infrastructure + Docs — Design Spec

**Date:** 2026-04-02
**Project:** `projects/stock-risk-scanner/`
**Concept:** Dockerize the scanner, add GitHub Actions CI, write the capstone blog post with 6 tabs, and update the repo README.

**Sub-project scope:** Part 3 of 3 (final). Sub-projects A (core modules) and B (API + database) are complete.

---

## Dockerfile (Multi-Stage)

Same pattern as exercise 07.

### Stage 1: Builder
- Base: `python:3.11-slim`
- Copies `pyproject.toml`, installs dependencies with `pip install --no-cache-dir .`

### Stage 2: Runtime
- Base: `python:3.11-slim`
- Copies installed packages + uvicorn binary from builder
- Copies `src/`, `alembic/`, `alembic.ini`
- Exposes port 8000
- CMD: `uvicorn src.scanner.main:app --host 0.0.0.0 --port 8000`

---

## docker-compose.yml

| Service | Image | Ports | Config |
|---------|-------|-------|--------|
| scanner | build from Dockerfile | 8000:8000 | `env_file: .env`, `depends_on: db`, `restart: unless-stopped` |
| db | postgres:16 | 5432:5432 | `POSTGRES_USER=quantlab`, `POSTGRES_PASSWORD=quantlab_dev`, `POSTGRES_DB=quantlab` |

**Named volume:** `pgdata` for PostgreSQL data persistence.

---

## .dockerignore

```
__pycache__
*.pyc
.git
.env
.venv
tests/
```

---

## .env.example

```
DATABASE_URL=postgresql+asyncpg://quantlab:quantlab_dev@db/quantlab
ANTHROPIC_API_KEY=your-key-here
```

Note: In docker-compose, the PostgreSQL host is `db` (the service name), not `localhost`.

---

## GitHub Actions CI

**File:** `.github/workflows/test.yml`

**Triggers:**
- Push to `working`
- PR to `master`

**Job:** `test` on `ubuntu-latest`
1. `actions/checkout@v4`
2. `actions/setup-python@v5` with `python-version: "3.11"`
3. `pip install -e ".[dev]"` (working-directory: `projects/stock-risk-scanner`)
4. `pytest -v` (working-directory: `projects/stock-risk-scanner`)

No PostgreSQL service needed — tests use SQLite in-memory.

---

## Blog Post

**File:** `finbytes_git/docs/_quant_lab/stock-risk-scanner.html`

**Layout:** `quant-lab-project` — tabbed layout with JavaScript tab switching. Create this layout if it doesn't exist at `finbytes_git/docs/_layouts/quant-lab-project.html`.

### 6 Tabs

| Tab | Content |
|-----|---------|
| Project Brief | What it is, why, architecture overview (text-based), tech stack list, how the pieces connect |
| Exercises | Summary table of exercises 01-08: topic, key concepts, how each feeds into the capstone |
| Math Concepts | VaR (95%), CVaR, max drawdown, volatility, Sharpe ratio — formulas + plain English explanations |
| Sub-project A | Core modules: models.py (Pydantic), risk.py (calculations), market_data.py (yfinance), narrative.py (Claude), scanner.py (orchestrator) |
| Infrastructure | API endpoints + background tasks, SQLAlchemy + Alembic, Docker + compose, GitHub Actions CI |
| How to Run | Prerequisites, clone, docker compose up, curl examples, sample screenshots |

### Screenshots to capture

- `curl /health` output
- `curl POST /api/scan` output (pending response)
- `curl GET /api/scans/{id}` with completed scan
- `docker compose ps` showing both services running
- `pytest -v` output (26 tests passing)

---

## README.md

**File:** `README.md` at repo root (`C:/codebase/quant_lab/README.md`)

### Content

- Project title and one-line description
- Exercises table (01-08): number, topic link, key concepts
- Projects table: Stock Risk Scanner (active) — no CDS Pricing
- Quick start section pointing to project directory

---

## Smoke Test

Before committing Docker files, verify:

```bash
cd projects/stock-risk-scanner
docker compose up --build -d
# Wait for services to start
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/scan -H "Content-Type: application/json" \
  -d '{"tickers":["AAPL","MSFT"],"weights":[0.6,0.4]}'
docker compose down
```

---

## Files Summary

| File | Location | Purpose |
|------|----------|---------|
| Dockerfile | `projects/stock-risk-scanner/` | Multi-stage build |
| docker-compose.yml | `projects/stock-risk-scanner/` | App + PostgreSQL |
| .dockerignore | `projects/stock-risk-scanner/` | Build context exclusions |
| .env.example | `projects/stock-risk-scanner/` | Environment template |
| test.yml | `.github/workflows/` | CI pipeline |
| stock-risk-scanner.html | `finbytes_git/docs/_quant_lab/` | Capstone blog post |
| quant-lab-project.html | `finbytes_git/docs/_layouts/` | Tab layout (if needed) |
| quant-lab.html | `finbytes_git/docs/_quant_lab/` | Index page (update) |
| README.md | repo root | Repo overview |
