# New Project Template — FinBytes QuantLabs

Use this checklist when adding a new project to QuantLabs. Every step was learned the hard way from the Stock Risk Scanner build. Don't skip any.

---

## 1. Backend (projects/<project-name>/)

### Scaffold

```
projects/<project-name>/
├── pyproject.toml              # dependencies + pytest config
├── src/<module>/
│   ├── __init__.py
│   ├── models.py               # Pydantic models
│   ├── main.py                 # FastAPI app
│   └── ...                     # business logic modules
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── Dockerfile                  # multi-stage build
├── docker-compose.yml          # app + PostgreSQL (if needed)
├── .dockerignore
├── .env.example                # placeholder credentials only
└── alembic/                    # if using PostgreSQL
    ├── env.py
    └── versions/
```

### pyproject.toml pattern

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "<one-liner>"
requires-python = ">=3.11"
dependencies = [
    # add project-specific deps
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

### Dockerfile pattern (multi-stage)

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY src/ src/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "src.<module>.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .env.example pattern

```
DATABASE_URL=postgresql+asyncpg://user:pass@db/dbname
ANTHROPIC_API_KEY=your-key-here
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=dbname
```

### docker-compose.yml pattern

```yaml
services:
  app:
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
    env_file:
      - .env
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### FastAPI main.py must include

```python
# Auto-create tables on startup (Render free tier has no shell)
from src.<module>.db_models import Base
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

# Health endpoints
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import text
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
```

### .dockerignore

```
__pycache__
*.pyc
.git
.env
.venv
tests/
```

### Security checklist
- [ ] No real credentials in code — use .env + .env.example with placeholders
- [ ] .env in .gitignore
- [ ] DATABASE_URL uses `postgresql+asyncpg://` prefix (not `postgresql://`)
- [ ] No API keys in Dockerfiles or docker-compose.yml

---

## 2. Deploy to Render

### PostgreSQL Database
1. Render dashboard → New → PostgreSQL
2. Name: `finbytes-<project>-db`
3. Plan: Free (30-day expiry — recreate via Churros admin page when it expires)
4. Copy the **Internal Database URL**

### Web Service
1. Render dashboard → New → Web Service
2. Connect GitHub repo: `mish-codes/QuantLab`
3. Name: `finbytes-<project>`
4. Root Directory / Project: `projects/<project-name>`
5. Runtime: Docker
6. Branch: master
7. Auto-Deploy: Yes
8. Environment variables:
   - `DATABASE_URL` = internal DB URL (change `postgres://` to `postgresql+asyncpg://`)
   - Any other secrets (API keys etc.)
9. Deploy — wait for "Live"
10. Verify: `curl https://finbytes-<project>.onrender.com/health`

**No shell on free tier** — tables auto-create on startup via `Base.metadata.create_all()`.

---

## 3. Dashboard Page (dashboard/pages/)

### Create page file

```
dashboard/pages/<N>_<Project_Name>.py
```

Number determines sidebar order. Use next available number after existing pages.

### Page must include
- `st.set_page_config(page_title="<Name> | FinBytes QuantLabs", page_icon="<emoji>", layout="wide")`
- Backend health check in sidebar
- Input section (presets + custom input)
- Results section (metrics, charts, narrative)
- Rate limiting (10/hr via session_state)
- Error handling (connection error, timeout, validation)
- Sample output on first load

### Dashboard tests

Create `dashboard/tests/test_<project>.py`:

```python
from streamlit.testing.v1 import AppTest

class TestProjectPage:
    def test_loads_without_error(self):
        at = AppTest.from_file("pages/<N>_<Project_Name>.py", default_timeout=15)
        at.run()
        assert not at.exception

    def test_shows_title(self):
        at = AppTest.from_file("pages/<N>_<Project_Name>.py", default_timeout=15)
        at.run()
        assert any("<Project Name>" in t.value for t in at.title)

    def test_has_tabs(self):
        at = AppTest.from_file("pages/<N>_<Project_Name>.py", default_timeout=15)
        at.run()
        assert len(at.tabs) == 3  # App, System Health, Architecture
```

Add tests to the System Health tab's test runner display in `dashboard/pages/1_Stock_Risk_Scanner.py` (or the equivalent project page).

### Update app.py sidebar

Add to the Projects list in `dashboard/app.py`:

```python
st.sidebar.markdown("- [<Project Name>](<Page_Name>)")
```

Add a project card on the landing page.

---

## 4. Register in System Health (dashboard/pages/9_System_Health.py)

Add to the `PROJECTS` dict at the top of the file:

```python
"<Project Name>": {
    "api_url": st.secrets.get("<PROJECT>_API_URL", "http://localhost:800X"),
    "health_endpoint": "/health",
    "db_endpoint": "/api/health/db",
    "render_name": "finbytes-<project>",
    "icon": "<emoji>",
    "tests": {
        "<Module> (test_<file>.py)": {
            "icon": "<emoji>",
            "tests": [
                ("test_name", "Description"),
                ...
            ],
        },
        ...
    },
},
```

### Add Streamlit Cloud secret

In Streamlit Cloud app settings → Secrets, add:

```toml
<PROJECT>_API_URL = "https://finbytes-<project>.onrender.com"
```

---

## 5. GitHub Actions CI

### Update .github/workflows/test.yml

Add a new job for the project:

```yaml
  test-<project>:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
        working-directory: projects/<project-name>
      - run: pytest -v --tb=short --junitxml=test-results.xml
        working-directory: projects/<project-name>
```

---

## 6. Blog Post (finbytes_git)

### Exercise blog post

```
finbytes_git/docs/_posts/YYYY-MM-DD-<topic>.html
```

Frontmatter:
```
---
layout: post
title: "<Title>"
date: YYYY-MM-DD
tags: [<tags>]
categories:
- Python fundamentals
permalink: "/YYYY/MM/DD/<slug>/"
---
```

### Capstone/project blog post

```
finbytes_git/docs/_quant_lab/<project-name>.html
```

Use `layout: quant-lab-capstone` for tabbed layout, or `layout: quant-lab-project` for the 5-tab layout.

For Mermaid diagrams, add at the bottom:
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad: true});</script>
```

### Link exercise blog posts
Use actual permalinks from each post's frontmatter — don't guess URLs.

---

## 7. README

Update `README.md` Projects table:

```markdown
| [<Project Name>](projects/<project-name>/) | <Description> | Active |
```

---

## 8. Git Workflow

1. All work on `working` branch
2. Create PR to `master`
3. Merge PR
4. Both Render and Streamlit Cloud auto-deploy from `master`
5. Sync: `git checkout master && git pull && git checkout working && git rebase master`

---

## 9. Naming Conventions

| Thing | Pattern | Example |
|-------|---------|---------|
| Repo directory | `projects/<kebab-case>/` | `projects/stock-risk-scanner/` |
| Render web service | `finbytes-<project>` | `finbytes-scanner` |
| Render database | `finbytes-<project>-db` | `finbytes-scanner-db` |
| Dashboard page | `<N>_<Title_Case>.py` | `1_Stock_Risk_Scanner.py` |
| Streamlit secret | `<PROJECT>_API_URL` | `API_URL`, `CDS_API_URL` |
| Blog post | `YYYY-MM-DD-<slug>.html` | `2026-04-02-stock-risk-scanner.html` |

---

## 10. Cost Summary

| Service | Cost | Limit |
|---------|------|-------|
| GitHub Pages | Free | Unlimited |
| Streamlit Community Cloud | Free | Unlimited |
| Render Web Service | Free per service | Sleeps after 15min idle |
| Render PostgreSQL | Free per DB | **30-day expiry — recreate** |
| GitHub Actions | Free | 2000 mins/month total |
| Anthropic API | $5 free then pay-as-go | Set monthly cap in console |

---

## 11. Render PostgreSQL — 30-Day Renewal

The free PostgreSQL database expires after 30 days. The System Health dashboard will show the Database check as red when this happens.

### How to recreate (automated)

1. Open the [Churros admin page](https://quantlabs.streamlit.app/Churros) and unlock
2. Go to the **Render DB** tab
3. Type the DB name to confirm and click **Recreate database now**
4. Watch the 6-step progress — delete, create, rewire `DATABASE_URL`, redeploy
5. Update `render.postgres_id` in Streamlit secrets to the new `dpg-...` id shown

### How to recreate (manual fallback)

1. Go to [render.com](https://render.com) → Dashboard
2. Delete the expired database
3. Click **New** → **PostgreSQL**
   - Name: `finbytes-<project>-db` (same name as before)
   - Plan: Free · Region: match original
4. Copy the new **Internal Database URL**
5. Go to your **web service** → **Environment**
6. Update `DATABASE_URL`:
   - Take the internal URL (starts with `postgres://`)
   - Change `postgres://` to `postgresql+asyncpg://`
   - Save
7. Render will auto-redeploy. Tables are auto-created on startup.
8. **Data is lost** — the new DB is empty. Fine for a demo.

### When to do it
- The System Health page shows Database as red
- Roughly every 30 days from creation
- Current scanner DB was created on 2026-04-03, expires 2026-05-03

---

## Quick Start Checklist for New Project

- [ ] Create `projects/<name>/` with pyproject.toml, src/, tests/
- [ ] Write code with TDD (tests first)
- [ ] Add Dockerfile, docker-compose.yml, .dockerignore, .env.example
- [ ] Add /health and /api/health/db endpoints
- [ ] Add auto-create tables in lifespan handler
- [ ] Verify locally: `docker compose up --build -d` + curl health
- [ ] Run tests: `pytest -v`
- [ ] Create Render PostgreSQL database (`finbytes-<name>-db`)
- [ ] Create Render web service (`finbytes-<name>`)
- [ ] Verify: `curl https://finbytes-<name>.onrender.com/health`
- [ ] Create dashboard page (`dashboard/pages/<N>_<Name>.py`)
- [ ] Update `dashboard/app.py` sidebar + landing page
- [ ] Register in `dashboard/pages/9_System_Health.py` PROJECTS dict
- [ ] Add Streamlit Cloud secret (`<NAME>_API_URL`)
- [ ] Add CI job to `.github/workflows/test.yml`
- [ ] Write blog post
- [ ] Update README.md
- [ ] Commit, PR, merge, verify deployment
