# Blog Reorganisation — Design Spec

## Goal
Clean up all blog URLs (remove dates), restructure Python and Tech Stack tabs with proper post assignments, create a Phase 2 capstone page for Quant Lab, and add an Obsidian-style D3.js graph as the site homepage.

## Deliverables
1. **URL cleanup** — all 31 date-based permalinks migrated to clean `/python/` or `/tech-stack/` prefixes
2. **`/misc/` → `/tech-stack/` migration** — all 11 existing `/misc/` permalinks updated
3. **Tab restructure** — Python and Tech Stack tabs reorganised with correct post assignments
4. **Phase 2 capstone** — new capstone page on Quant Lab tab for AWS & Bond/Credit Risk
5. **Explainer relocation** — Phase 1 Explained, Phase 2 Explained, Architecture Deep Dive moved to Quant Lab tab
6. **Graph homepage** — D3.js force-directed graph as site landing page at `/`
7. **Tab permalink update** — `_tabs/misc.md` permalink changes from `/misc/` to `/tech-stack/`

---

## 1. URL Cleanup — Permalink Changes

### Python tab posts (exercises 01–06, 08) — date URLs → `/python/`

| File | Old Permalink | New Permalink |
|------|--------------|---------------|
| 2026-04-01-pytest-tdd-for-financial-python.html | /2026/04/01/pytest-tdd-financial-python/ | /python/pytest-tdd-financial-python/ |
| 2026-04-02-pydantic-models-for-trading-data.html | /2026/04/02/pydantic-models-trading-data/ | /python/pydantic-models-trading-data/ |
| 2026-04-02-fastapi-your-first-financial-api.html | /2026/04/02/fastapi-your-first-financial-api/ | /python/fastapi-your-first-financial-api/ |
| 2026-04-02-async-python-for-market-data.html | /2026/04/02/async-python-for-market-data/ | /python/async-python-for-market-data/ |
| 2026-04-02-yfinance-fetching-market-data.html | /2026/04/02/yfinance-fetching-market-data/ | /python/yfinance-fetching-market-data/ |
| 2026-04-02-claude-api-ai-risk-analysis.html | /2026/04/02/claude-api-ai-risk-analysis/ | /python/claude-api-ai-risk-analysis/ |
| 2026-04-02-postgresql-sqlalchemy-async.html | /2026/04/02/postgresql-sqlalchemy-async/ | /python/postgresql-sqlalchemy-async/ |

### Tech Stack posts (exercises 07, 09–20) — date URLs → `/tech-stack/`

| File | Old Permalink | New Permalink |
|------|--------------|---------------|
| 2026-04-02-docker-for-python-services.html | /2026/04/02/docker-for-python-services/ | /tech-stack/docker-for-python-services/ |
| 2026-04-04-aws-fundamentals-treasury-data.html | /2026/04/04/aws-fundamentals-treasury-data/ | /tech-stack/aws-fundamentals-treasury-data/ |
| 2026-04-05-s3-par-curve-ingestion.html | /2026/04/05/s3-par-curve-ingestion/ | /tech-stack/s3-par-curve-ingestion/ |
| 2026-04-06-rds-postgresql-yield-schema.html | /2026/04/06/rds-postgresql-yield-schema/ | /tech-stack/rds-postgresql-yield-schema/ |
| 2026-04-07-lambda-spot-curve-bootstrapping.html | /2026/04/07/lambda-spot-curve-bootstrapping/ | /tech-stack/lambda-spot-curve-bootstrapping/ |
| 2026-04-08-cicd-forward-rate-curve.html | /2026/04/08/cicd-forward-rate-curve/ | /tech-stack/cicd-forward-rate-curve/ |
| 2026-04-09-terraform-nelson-siegel.html | /2026/04/09/terraform-nelson-siegel/ | /tech-stack/terraform-nelson-siegel/ |
| 2026-04-10-sqs-sns-credit-spreads.html | /2026/04/10/sqs-sns-credit-spreads/ | /tech-stack/sqs-sns-credit-spreads/ |
| 2026-04-11-websockets-realtime-spreads.html | /2026/04/11/websockets-realtime-spreads/ | /tech-stack/websockets-realtime-spreads/ |
| 2026-04-12-elasticache-bond-caching.html | /2026/04/12/elasticache-bond-caching/ | /tech-stack/elasticache-bond-caching/ |
| 2026-04-13-terraform-advanced-default-probs.html | /2026/04/13/terraform-advanced-default-probs/ | /tech-stack/terraform-advanced-default-probs/ |
| 2026-04-14-cloudwatch-oas-zspreads.html | /2026/04/14/cloudwatch-oas-zspreads/ | /tech-stack/cloudwatch-oas-zspreads/ |
| 2026-04-15-integration-testing-credit-var.html | /2026/04/15/integration-testing-credit-var/ | /tech-stack/integration-testing-credit-var/ |

### Quant Lab posts (explainers + architecture) — date URLs → `/quant-lab/`

| File | Old Permalink | New Permalink |
|------|--------------|---------------|
| 2026-04-03-quantlab-phase1-explained.html | /2026/04/03/quantlab-phase1-explained/ | /quant-lab/phase1-explained/ |
| 2026-04-16-quantlab-phase2-explained.html | /2026/04/16/quantlab-phase2-explained/ | /quant-lab/phase2-explained/ |
| 2026-04-03-stock-risk-scanner-architecture.html | /2026/04/03/stock-risk-scanner-architecture/ | /quant-lab/stock-risk-scanner-architecture/ |

### Existing `/misc/` posts → `/tech-stack/`

| File | Old Permalink | New Permalink |
|------|--------------|---------------|
| 2026-04-20-aws-services-reference.html | /misc/aws-services/ | /tech-stack/aws-services/ |
| 2026-04-21-terraform-reference.html | /misc/terraform/ | /tech-stack/terraform/ |
| 2026-04-22-fastapi-reference.html | /misc/fastapi/ | /tech-stack/fastapi/ |
| 2026-04-23-postgresql-sqlalchemy-reference.html | /misc/postgresql-sqlalchemy/ | /tech-stack/postgresql-sqlalchemy/ |
| 2026-04-24-streamlit-reference.html | /misc/streamlit/ | /tech-stack/streamlit/ |
| 2026-04-25-github-actions-reference.html | /misc/github-actions/ | /tech-stack/github-actions/ |
| 2026-07-01-redis-caching-reference.html | /misc/redis-caching/ | /tech-stack/redis-caching/ |
| 2026-07-02-message-queues-rabbitmq-reference.html | /misc/message-queues/ | /tech-stack/message-queues/ |
| 2026-07-03-argparse-cli-reference.html | /misc/argparse-cli/ | /tech-stack/argparse-cli/ |
| 2026-07-04-git-workflow-reference.html | /misc/git-workflow/ | /tech-stack/git-workflow/ |
| 2026-07-05-docker-cicd-reference.html | /misc/docker-cicd/ | /tech-stack/docker-cicd/ |

### Posts with no permalink change (already clean)

- `/python/py36-to-311/` — unchanged
- `/python/pytest-mocking/` — unchanged
- `/python/testing-side-effects/` — unchanged
- `/python/pytest-fixtures-ci/` — unchanged
- `/python/decorators/` — unchanged
- `/python/big-o/` — unchanged
- `/tech-stack/plotting-libraries/` — unchanged
- `/math-finance/*` (8 posts) — unchanged
- `/comparisons/*` (4 posts) — unchanged

---

## 2. Tab Restructure

### Python tab (`_tabs/python.md`)

Sections:
1. **Python References** — Decorators, Big O, Python 3.6→3.11 Migration
2. **Testing — pytest** — Mocking & Monkeypatch, Testing Side Effects, Fixtures & CI
3. **QuantLab Exercises** — exercises 01–06, 08 (pytest TDD, Pydantic, FastAPI, async, yfinance, Claude API, PostgreSQL/SQLAlchemy)

Removed from this tab:
- All AWS exercise posts (09–20) → Tech Stack
- Docker exercise (07) → Tech Stack
- Phase 1 Explained → Quant Lab
- Phase 2 Explained → Quant Lab
- Architecture Deep Dive → Quant Lab

### Tech Stack tab (`_tabs/misc.md`)

Permalink changes from `/misc/` to `/tech-stack/`. Title already "Tech Stack".

Sections:
1. **Technology References** — AWS Services, Terraform, FastAPI, PostgreSQL & SQLAlchemy, Streamlit, GitHub Actions & CI/CD, Plotting Libraries Compared
2. **Infrastructure** — Redis & Caching, Message Queues & RabbitMQ, Docker & CI/CD
3. **Tools** — argparse & CLI, Git Workflow
4. **QuantLab — AWS & Credit Risk** — Docker exercise (07), exercises 09–20

All internal links updated from `/misc/` to `/tech-stack/`.

### Quant Lab tab (`_tabs/quant-lab.md`)

Add to capstone section:
- **Capstone — Phase 1: Stock Risk Scanner** (existing) — add links to Phase 1 Explained and Architecture Deep Dive
- **Capstone — Phase 2: AWS & Bond/Credit Risk** (new section) — link to Phase 2 Explained, link to new capstone page

Mini projects sections unchanged.

### Math/Finance tab — unchanged
### Comparisons tab — unchanged

---

## 3. Phase 2 Capstone Page

**File:** `docs/_quant_lab/aws-credit-risk.html`
**Layout:** `quant-lab-capstone` (same as Stock Risk Scanner)
**Permalink:** `/quant-lab/aws-credit-risk/` (via collection config)

Content covers the 12-exercise arc:
- AWS Fundamentals → S3 → RDS → Lambda → CI/CD → Terraform → SQS/SNS → WebSockets → ElastiCache → Terraform Advanced → CloudWatch/OAS → Credit VaR
- Tech stack table (AWS services, Terraform, Python libraries)
- Links to each exercise post and the Phase 2 Explained post

---

## 4. Graph Homepage

**File:** `docs/index.html` (or `docs/_layouts/home.html` override)
**Layout:** `default` (inherits sidebar, header, theme)

### Implementation
- **D3.js v7** loaded from CDN (free, no build step)
- **Data source:** Liquid template generates a JSON object at build time containing:
  - `nodes`: array of `{id, title, permalink, section, tags}` for every post
  - `links`: array of `{source, target}` for posts sharing tags (threshold: 2+ shared tags to avoid noise)
- **Rendering:** Force-directed graph in an SVG filling the main content area
- **Colour coding:** Nodes coloured by tab/section (Python = blue, Tech Stack = green, Math/Finance = orange, Comparisons = purple, Quant Lab = red)
- **Interaction:**
  - Hover: show post title tooltip
  - Click: navigate to post permalink
  - Drag: reposition nodes
  - Zoom/pan: standard D3 zoom behaviour
- **Brief intro:** A one-line tagline above the graph: "Explore FinBytes — click any topic to dive in"
- **Responsive:** Graph resizes with viewport

### Config change
- Set the homepage in `_config.yml` or override via `index.html` with `permalink: /`
- The Quant Lab tab keeps its own permalink `/quant-lab/`

---

## 5. Files Changed Summary

### Post front matter updates (31 + 11 = 42 files)
- 31 date-based posts: update `permalink` field
- 11 `/misc/` posts: update `permalink` field from `/misc/` to `/tech-stack/`

### Tab files (3 files modified)
- `_tabs/misc.md` — permalink `/misc/` → `/tech-stack/`, update all internal links
- `_tabs/python.md` — remove AWS exercises/explainers, update all links to clean permalinks
- `_tabs/quant-lab.md` — add Phase 2 capstone section, add explainer links, update any date-based links

### New files (2 files)
- `_quant_lab/aws-credit-risk.html` — Phase 2 capstone page
- `index.html` (or equivalent) — D3.js graph homepage

### Internal link updates
Any post that links to another post using old date-based or `/misc/` URLs needs those links updated. This includes:
- Exercise posts linking to each other (next/previous)
- Explainer posts linking to exercises
- Tab pages linking to posts
