# Stock Risk Scanner — Infrastructure + Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dockerize the stock risk scanner, add GitHub Actions CI, write the capstone blog post with 6 tabs, and update the repo README.

**Architecture:** Multi-stage Dockerfile + docker-compose (app + PostgreSQL). GitHub Actions runs pytest on push to `working` and PRs to `master`. Capstone blog post uses a new 6-tab layout. README provides exercises and projects overview.

**Tech Stack:** Docker, Docker Compose, GitHub Actions, Jekyll (blog)

---

## File Structure

```
quant_lab/
├── .github/workflows/test.yml         # NEW: CI pipeline
├── README.md                           # MODIFY: full overview
└── projects/stock-risk-scanner/
    ├── Dockerfile                      # NEW: multi-stage build
    ├── docker-compose.yml              # NEW: app + PostgreSQL
    ├── .dockerignore                   # NEW: build context exclusions
    └── .env.example                    # NEW: env template

finbytes_git/docs/
├── _layouts/quant-lab-capstone.html    # NEW: 6-tab layout
└── _quant_lab/stock-risk-scanner.html  # NEW: capstone blog post
```

---

### Task 1: Dockerfile + .dockerignore

**Files:**
- Create: `projects/stock-risk-scanner/Dockerfile`
- Create: `projects/stock-risk-scanner/.dockerignore`

- [ ] **Step 1: Create Dockerfile**

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000
CMD ["uvicorn", "src.scanner.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create .dockerignore**

```
__pycache__
*.pyc
.git
.env
.venv
tests/
```

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/Dockerfile projects/stock-risk-scanner/.dockerignore
git commit -m "feat(scanner): Dockerfile with multi-stage build"
```

---

### Task 2: docker-compose + .env.example

**Files:**
- Create: `projects/stock-risk-scanner/docker-compose.yml`
- Create: `projects/stock-risk-scanner/.env.example`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
services:
  scanner:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

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

- [ ] **Step 2: Create .env.example**

```
DATABASE_URL=postgresql+asyncpg://quantlab:quantlab_dev@db/quantlab
ANTHROPIC_API_KEY=your-key-here
```

- [ ] **Step 3: Create .env for local testing (do NOT commit)**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL=postgresql+asyncpg://quantlab:quantlab_dev@db/quantlab` (keep ANTHROPIC_API_KEY as placeholder — fallback will be used).

- [ ] **Step 4: Commit (only .env.example and docker-compose.yml, NOT .env)**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/docker-compose.yml projects/stock-risk-scanner/.env.example
git commit -m "feat(scanner): docker-compose with app + PostgreSQL"
```

---

### Task 3: Smoke Test Docker

- [ ] **Step 1: Build and start**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
docker compose up --build -d
```

Wait 10-15 seconds for PostgreSQL to initialize and the app to start.

- [ ] **Step 2: Run Alembic migration inside the scanner container**

```bash
docker compose exec scanner alembic upgrade head
```

Expected: Migration applies, creates `scan_records` table.

- [ ] **Step 3: Verify health endpoint**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 4: Test scan endpoint**

```bash
curl -X POST http://localhost:8000/api/scan -H "Content-Type: application/json" -d "{\"tickers\":[\"AAPL\",\"MSFT\"],\"weights\":[0.6,0.4]}"
```

Expected: `{"id":1,"status":"pending"}`

- [ ] **Step 5: Wait and check scan result**

Wait 5-10 seconds for the background scan to complete, then:

```bash
curl http://localhost:8000/api/scans/1
```

Expected: Status should be `"complete"` or `"failed"` (if yfinance can't reach the internet from the container, it will fail gracefully).

- [ ] **Step 6: Capture screenshots**

Save screenshots of:
1. `curl /health` output
2. `curl POST /api/scan` output
3. `curl GET /api/scans/1` output (complete or failed)
4. `docker compose ps` output
5. `pytest -v` output (run from host: `cd C:/codebase/quant_lab/projects/stock-risk-scanner && python -m pytest tests/ -v`)

Save screenshots to `C:/codebase/finbytes_git/docs/assets/img/quant-lab/` for the blog post.

- [ ] **Step 7: Stop containers**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
docker compose down
```

---

### Task 4: GitHub Actions CI

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Create CI workflow**

```yaml
name: Tests

on:
  push:
    branches: [working]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
        working-directory: projects/stock-risk-scanner
      - run: pytest -v
        working-directory: projects/stock-risk-scanner
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
mkdir -p .github/workflows
git add .github/workflows/test.yml
git commit -m "ci: GitHub Actions test pipeline for stock risk scanner"
```

---

### Task 5: Capstone Blog Post Layout

**Files:**
- Create: `C:/codebase/finbytes_git/docs/_layouts/quant-lab-capstone.html`

- [ ] **Step 1: Create 6-tab layout**

This layout is based on the existing `quant-lab-project.html` but with 6 custom tabs instead of 5. Copy the existing layout's password gate and styling, but replace the tab buttons and content divs:

```html
---
layout: default
---
<div id="ql-lock">
  <div class="ql-gate">
    <h2>QuantLab</h2>
    <p>This section is password protected.</p>
    <input type="password" id="ql-pwd" placeholder="Enter password" />
    <button onclick="qlUnlock()">Enter</button>
    <p id="ql-err" style="color:red;display:none">Wrong password</p>
  </div>
</div>

<div id="ql-content" style="display:none">
  <article class="post">
    <header class="post-header">
      <h1 class="post-title">{{ page.title }}</h1>
      {% if page.description %}
        <p class="post-description">{{ page.description }}</p>
      {% endif %}
      <p class="post-meta">
        {% if page.date %}<time>{{ page.date | date: "%B %d, %Y" }}</time>{% endif %}
        {% if page.tags.size > 0 %} &middot; {{ page.tags | join: ", " }}{% endif %}
      </p>
    </header>

    <div class="ql-tabs">
      <button class="ql-tab-btn active" onclick="showTab('brief', this)">Project Brief</button>
      <button class="ql-tab-btn" onclick="showTab('exercises', this)">Exercises</button>
      <button class="ql-tab-btn" onclick="showTab('math', this)">Math Concepts</button>
      <button class="ql-tab-btn" onclick="showTab('core', this)">Sub-project A</button>
      <button class="ql-tab-btn" onclick="showTab('infra', this)">Infrastructure</button>
      <button class="ql-tab-btn" onclick="showTab('run', this)">How to Run</button>
    </div>

    <div id="tab-brief" class="ql-tab-content active">
      {{ page.brief_content }}
    </div>
    <div id="tab-exercises" class="ql-tab-content" style="display:none">
      {{ page.exercises_content }}
    </div>
    <div id="tab-math" class="ql-tab-content" style="display:none">
      {{ page.math_content }}
    </div>
    <div id="tab-core" class="ql-tab-content" style="display:none">
      {{ page.core_content }}
    </div>
    <div id="tab-infra" class="ql-tab-content" style="display:none">
      {{ page.infra_content }}
    </div>
    <div id="tab-run" class="ql-tab-content" style="display:none">
      {{ page.run_content }}
    </div>

  </article>
</div>

<style>
.ql-gate {
  max-width: 360px;
  margin: 80px auto;
  text-align: center;
}
.ql-gate input {
  display: block;
  width: 100%;
  padding: 8px 12px;
  margin: 12px 0;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.ql-gate button {
  width: 100%;
  padding: 8px;
  background: #2a7ae2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.ql-tabs {
  display: flex;
  gap: 4px;
  margin: 24px 0 0 0;
  border-bottom: 2px solid #e8e8e8;
  flex-wrap: wrap;
}
.ql-tab-btn {
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}
.ql-tab-btn.active {
  color: #2a7ae2;
  border-bottom: 2px solid #2a7ae2;
  font-weight: 600;
}
.ql-tab-content {
  padding: 24px 0;
}
</style>

<script>
const QL_PASSWORD = 'MyPassw0rd1*';

function qlUnlock() {
  if (document.getElementById('ql-pwd').value === QL_PASSWORD) {
    document.getElementById('ql-lock').style.display = 'none';
    document.getElementById('ql-content').style.display = 'block';
    sessionStorage.setItem('ql_unlocked', 'true');
  } else {
    document.getElementById('ql-err').style.display = 'block';
  }
}

if (sessionStorage.getItem('ql_unlocked') === 'true') {
  document.getElementById('ql-lock').style.display = 'none';
  document.getElementById('ql-content').style.display = 'block';
}

function showTab(name, btn) {
  document.querySelectorAll('.ql-tab-content').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.ql-tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = 'block';
  btn.classList.add('active');
}
</script>
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/finbytes_git
git add docs/_layouts/quant-lab-capstone.html
git commit -m "feat: 6-tab capstone layout for QuantLab"
```

---

### Task 6: Capstone Blog Post

**Files:**
- Create: `C:/codebase/finbytes_git/docs/_quant_lab/stock-risk-scanner.html`

- [ ] **Step 1: Write the blog post**

The file uses `layout: quant-lab-capstone` and defines 6 frontmatter content blocks: `brief_content`, `exercises_content`, `math_content`, `core_content`, `infra_content`, `run_content`.

Content for each tab:

**brief_content:** What the Stock Risk Scanner is, architecture overview (request → fetch prices → calculate risk → generate narrative → store in DB → return result), tech stack list (Python 3.11, FastAPI, SQLAlchemy, Alembic, yfinance, Anthropic SDK, Docker, PostgreSQL, pytest).

**exercises_content:** HTML table of exercises 01-08 with columns: #, Topic, Key Concepts, Capstone Role.

**math_content:** VaR (95%) — 5th percentile of portfolio returns. CVaR — mean of returns below VaR. Max Drawdown — largest peak-to-trough decline. Volatility — annualized standard deviation. Sharpe Ratio — risk-adjusted return (annualized return / volatility). Include formulas and plain English explanations.

**core_content:** Walkthrough of each module: models.py (Pydantic validation), risk.py (numpy calculations), market_data.py (yfinance wrapper), narrative.py (Claude API with fallback), scanner.py (orchestrator pipeline).

**infra_content:** API endpoints table (health, POST scan, GET scan, GET scans). Background task pattern. SQLAlchemy + Alembic for migrations. Docker multi-stage build. docker-compose (app + PostgreSQL). GitHub Actions CI.

**run_content:** Prerequisites (Python 3.11, Docker Desktop). Clone repo. `docker compose up --build -d`. Run Alembic migration. curl examples. Screenshots from Task 3 Step 6.

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/finbytes_git
git add docs/_quant_lab/stock-risk-scanner.html
git commit -m "feat: Stock Risk Scanner capstone blog post"
```

---

### Task 7: README Update

**Files:**
- Modify: `C:/codebase/quant_lab/README.md`

- [ ] **Step 1: Update README.md**

```markdown
# QuantLab

Quantitative finance projects and exercises.

## Exercises

| # | Topic | Key Concepts |
|---|-------|-------------|
| 01 | [pytest & TDD](exercises/01-pytest-tdd/) | Fixtures, parametrize, approx, TDD cycle |
| 02 | [Pydantic](exercises/02-pydantic/) | Validators, computed fields, serialization |
| 03 | [FastAPI](exercises/03-fastapi/) | Routes, status codes, TestClient |
| 04 | [Async Python](exercises/04-async/) | async/await, gather, aiohttp |
| 05 | [yfinance](exercises/05-yfinance/) | Market data, pandas, data quality |
| 06 | [Claude API](exercises/06-claude-api/) | Anthropic SDK, prompts, error handling |
| 07 | [Docker](exercises/07-docker/) | Dockerfile, compose, multi-stage builds |
| 08 | [PostgreSQL](exercises/08-postgres-sqlalchemy/) | SQLAlchemy 2.0, async, migrations |

## Projects

| Project | Description | Status |
|---------|------------|--------|
| [Stock Risk Scanner](projects/stock-risk-scanner/) | Portfolio risk scanner with AI-generated narratives | Active |

## Quick Start

See each exercise or project directory for setup instructions.
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add README.md
git commit -m "docs: update README with exercises and projects"
```

---

### Task 8: Final PR

- [ ] **Step 1: Push and create PR for quant_lab**

```bash
cd C:/codebase/quant_lab
git push -u origin working
gh pr create --title "feat(scanner): capstone sub-project C — infrastructure + docs" --body "..."
```

- [ ] **Step 2: Push and create PR for finbytes_git**

```bash
cd C:/codebase/finbytes_git
git push -u origin working
gh pr create --title "feat: Stock Risk Scanner capstone blog post + layout" --body "..."
```

- [ ] **Step 3: Merge both PRs, sync branches**
