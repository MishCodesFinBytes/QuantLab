# Bond Pricing & Credit Risk on AWS — Design Spec

> **Date:** 2026-04-04
> **Status:** Approved
> **Scope:** QuantLab Learning Path Phase 2

---

## 1. Overview

A second learning path building on QuantLab Phase 1 (exercises 01-08 + Stock Risk Scanner capstone). This phase teaches AWS cloud services and deeper quantitative finance (fixed income pricing, credit risk) through 12 exercises and 2 capstone projects.

**Goal:** Upskill to senior Python backend/fintech contractor with AWS cloud expertise, demonstrated through two deployable capstone projects — a Bond Pricing Engine and a Credit Risk Platform.

**Learning approach:** Each exercise weaves together three layers:
1. **Business context** — who uses this, why it matters, what decisions it informs
2. **Math** — formulas, derivations, intuition (not just plug-and-chug)
3. **Code + AWS** — Python implementation with TDD, deployed to AWS

---

## 2. Repos & Directory Structure

| Repo | Path | Purpose |
|------|------|---------|
| quant_lab | `C:\codebase\quant_lab` | Exercises + capstone project code |
| finbytes_git | `C:\codebase\finbytes_git` | Blog posts (`_posts` for concepts, `_quant_lab` for capstones) |

### New directories

```
quant_lab/
├── exercises/
│   ├── 09-aws-fundamentals/
│   ├── 10-s3-data-ingestion/
│   ├── 11-rds-postgresql/
│   ├── 12-lambda-api-gateway/
│   ├── 13-cicd-github-actions/
│   ├── 14-terraform-curve-fitting/
│   ├── 15-sqs-sns-credit-spreads/
│   ├── 16-websockets-realtime/
│   ├── 17-elasticache-redis/
│   ├── 18-terraform-advanced/
│   ├── 19-cloudwatch-oas/
│   └── 20-integration-testing-var/
└── projects/
    ├── stock-risk-scanner/          # Existing capstone (Phase 1)
    ├── bond-pricing-engine/         # Capstone A (rates & curves)
    └── credit-risk-platform/        # Capstone B (credit risk, builds on A)
```

### Blog posts

```
finbytes_git/docs/_posts/
├── 2026-XX-XX-aws-fundamentals-treasury-data.html
├── 2026-XX-XX-s3-par-curve-ingestion.html
├── 2026-XX-XX-rds-postgresql-yield-schema.html
├── 2026-XX-XX-lambda-spot-curve-bootstrapping.html
├── 2026-XX-XX-cicd-forward-rate-curve.html
├── 2026-XX-XX-terraform-nelson-siegel.html
├── 2026-XX-XX-bond-pricing-engine-capstone.html       # Capstone A
├── 2026-XX-XX-sqs-sns-credit-spreads.html
├── 2026-XX-XX-websockets-realtime-spreads.html
├── 2026-XX-XX-elasticache-bond-caching.html
├── 2026-XX-XX-terraform-advanced-default-probs.html
├── 2026-XX-XX-cloudwatch-oas-zspreads.html
├── 2026-XX-XX-integration-testing-credit-var.html
└── 2026-XX-XX-credit-risk-platform-capstone.html      # Capstone B
```

---

## 3. Tech Stack

### Carried forward from Phase 1
- Python 3.11+, pytest, Pydantic v2, FastAPI, uvicorn, async/await
- yfinance, numpy, pandas, Anthropic SDK
- Docker, PostgreSQL, SQLAlchemy, Alembic
- Streamlit (dashboard)

### New in Phase 2
- **AWS:** IAM, S3, RDS PostgreSQL, Lambda, API Gateway (REST + WebSocket), SQS, SNS, ElastiCache (Redis), CloudWatch
- **Terraform:** Infrastructure as Code for all AWS resources
- **GitHub Actions:** CI/CD pipeline deploying to AWS
- **FRED API:** Federal Reserve Economic Data — treasury yields, credit spread indices (free, requires API key)
- **scipy:** `scipy.optimize` for Nelson-Siegel / Svensson curve fitting
- **boto3:** AWS SDK for Python
- **moto / LocalStack:** Local AWS mocking/emulation for development and testing
- **MiroFish:** Stretch goal — swarm intelligence for credit event prediction

---

## 4. Data Sources & Storage

### Data sources
- **US Treasury par yields:** FRED series (DGS1MO, DGS3MO, DGS6MO, DGS1, DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30). Free, daily, rate-limited to 120 req/min.
- **Credit spread indices:** FRED ICE BofA series (BAMLC0A1CAAA for AAA, BAMLC0A2CAA for AA, etc.). Free, daily.
- **CDS spreads:** For exercise purposes, synthetic/generated data based on realistic term structures. Production CDS data requires paid feeds.

### Storage estimates
- Treasury par yields: ~3,000 rows/year (12 maturities × 252 trading days)
- Computed curves (spot, forward, fitted): same dimensions per curve type
- Credit spread indices: ~2,500 rows/year (10 rating buckets × 252 days)
- Bond pricing results: on-demand, user-initiated
- Alert history: sparse, event-driven

**Total: under 100MB** even with several years of history. Well within AWS free tier (20GB RDS, 5GB S3).

---

## 5. Exercises (09-20)

### Exercise 09 — AWS Account Setup, IAM, CLI + Treasury Data Landscape

**AWS concepts:**
- Create AWS account
- Set up IAM user with least-privilege (not root)
- Configure AWS CLI with named profiles
- Create billing alarm ($5 threshold via CloudWatch)

**Finance concepts:**
- Survey of treasury data sources (FRED API, Treasury.gov direct)
- What par yields represent — coupon rate at which a bond prices at par for each maturity
- Yield curve shapes: normal, inverted, flat, humped — what each signals about the economy

**Build:** Python script using `fredapi` that fetches current treasury par yields from FRED, prints a formatted yield curve table.

---

### Exercise 10 — S3 + Par Curve Data Ingestion

**AWS concepts:**
- Create S3 bucket with versioning enabled
- Upload/download with boto3
- Lifecycle rules (transition old data to cheaper storage)
- Bucket policies and access control

**Finance concepts:**
- Par curve — the foundation for all other curves
- Daily data cadence — why markets care about daily curve updates
- Data quality: handling missing maturities, holidays, weekends

**Build:** Script that fetches daily treasury par yields from FRED, stores as dated JSON files in S3 (`s3://bucket/par-yields/2026-04-04.json`), reads back and validates.

---

### Exercise 11 — RDS PostgreSQL on AWS + Yield/Bond Schema Design

**AWS concepts:**
- Provision RDS `db.t3.micro` (free tier) with PostgreSQL
- Security groups — allow access from Lambda and local machine
- Connection via SQLAlchemy async engine with `asyncpg`
- Automated backups, storage auto-scaling

**Finance concepts:**
- Relational data modeling for fixed income
- Tables: `par_yields`, `spot_curves`, `forward_curves`, `fitted_curves`, `bonds`, `pricing_results`
- Why time-series financial data needs careful schema design (point-in-time queries, no look-ahead bias)

**Build:** SQLAlchemy models + Alembic migrations. Seed DB with historical par yields loaded from S3. Query: "give me the par curve for 2026-03-15."

---

### Exercise 12 — Lambda + API Gateway + Spot Curve Bootstrapping

**AWS concepts:**
- Create Lambda function with Python runtime
- Package dependencies as Lambda layer
- Wire API Gateway REST endpoint to Lambda
- Lambda execution role (IAM) with access to S3 + RDS
- Cold starts — why they matter, how to mitigate

**Finance concepts:**
- Bootstrap method: derive zero-coupon (spot) rates from par yields
- Iterative solving: each maturity uses all previously solved shorter maturities
- Math: for a par bond: 100 = Σ(c / (1+sᵢ)ⁱ) + 100/(1+sₙ)ⁿ — solve for sₙ
- Why spot rates matter: they're the actual discount factors for cash flows

**Build:** `POST /curves/bootstrap` — takes par yields (or date to fetch from DB), returns spot curve. Deployed as Lambda behind API Gateway.

---

### Exercise 13 — CI/CD (GitHub Actions → AWS) + Forward Rate Curve

**AWS concepts:**
- GitHub Actions workflow: test → package → deploy Lambda
- AWS credentials in GitHub Secrets (OIDC preferred over access keys)
- Deployment strategies: update Lambda code, update API Gateway stage
- Rollback on failure

**Finance concepts:**
- Forward rates: implied future interest rates derived from spot curve
- Math: (1+s₂)² = (1+s₁)(1+f₁,₂) → f₁,₂ = (1+s₂)²/(1+s₁) − 1
- Instantaneous forward rate vs discrete forward rate
- Business use: pricing FRAs (Forward Rate Agreements), swap valuation, rate expectations

**Build:** `GET /curves/forward?date=` endpoint. CI/CD pipeline auto-deploys on push to `working` branch, promotes to production on merge to `master`.

---

### Exercise 14 — Terraform Basics + Nelson-Siegel / Svensson Curve Fitting

**AWS concepts:**
- Terraform init, plan, apply, destroy
- State management (S3 backend for remote state)
- Terraform modules: reusable S3 + RDS + Lambda configs
- Variables, outputs, workspaces

**Finance concepts:**
- Why parametric curve models? Smoothing noisy market data, interpolating between observed maturities
- Nelson-Siegel (4 parameters): y(τ) = β₀ + β₁[(1−e^(−τ/λ))/(τ/λ)] + β₂[(1−e^(−τ/λ))/(τ/λ) − e^(−τ/λ)]
  - β₀ = long-term level, β₁ = slope, β₂ = curvature, λ = decay rate
- Nelson-Siegel-Svensson (6 parameters): adds a second hump term for better long-end fit
- Cubic spline: exact fit through observed points, but can oscillate
- scipy.optimize.minimize for parameter fitting

**Build:** `POST /curves/fit` — fits Nelson-Siegel + Svensson to par yields, returns parameters + fitted curve. All infrastructure (S3, RDS, Lambda, API GW) defined in Terraform.

---

### --- Capstone A: Bond Pricing Engine ---

**Assembles exercises 09-14 into `projects/bond-pricing-engine/`.**

**Core services:**

1. **Data ingestion** — daily Lambda fetches treasury par yields from FRED → S3 → RDS
2. **Curve engine** — bootstraps spot curve, derives forward curve, fits Nelson-Siegel/Svensson
3. **Bond pricer** — discounted cash flow pricing from spot curve:
   - Bond price = Σ(cᵢ / (1+sᵢ)ⁱ) + FV/(1+sₙ)ⁿ
   - Z-spread: constant spread z where price = Σ(cᵢ / (1+sᵢ+z)ⁱ) + FV/(1+sₙ+z)ⁿ — solved iteratively
   - Macaulay duration: weighted average time to cash flows
   - Modified duration: Macaulay / (1+y/k) — price sensitivity to yield
   - Convexity: second derivative of price/yield — captures curvature
4. **Claude AI narrative** — explains curve shape, pricing breakdown, what duration/convexity mean for the position
5. **Real bond universe** — pre-loaded US Treasury bonds from FRED, plus user-submitted custom bonds

**API endpoints:**
- `GET /health` — health check
- `GET /curves/{date}` — par, spot, forward, fitted curves for a date
- `GET /curves/latest` — most recent curves
- `GET /curves/history?start=&end=` — historical curve data
- `POST /curves/fit` — fit Nelson-Siegel/Svensson to par yields
- `POST /price` — price a bond (inputs: coupon rate, maturity date, face value, frequency → outputs: clean price, dirty price, YTM, Z-spread, duration, convexity)
- `POST /analyze` — full analysis with Claude AI narrative

**AWS architecture:**
- S3: raw FRED data (JSON files by date)
- Lambda: curve construction + bond pricing (stateless)
- API Gateway: REST API
- RDS PostgreSQL: historical curves, bond definitions, pricing results
- GitHub Actions: CI/CD
- Terraform: all infra as code
- CloudWatch: basic logging (expanded in Capstone B)

**Dashboard:** new "Bond Pricing" page in existing Streamlit app — curve visualizations, bond pricer form, pricing history.

---

### Exercise 15 — SQS/SNS + Credit Spreads & CDS Curves

**AWS concepts:**
- Create SQS queue (standard + FIFO), publish and consume messages with boto3
- Dead letter queues for failed messages
- SNS topic with email subscription
- Fan-out pattern: SNS → multiple SQS queues

**Finance concepts:**
- Credit spread = corporate bond yield − treasury yield at same maturity
- Spread curves by rating: AAA trades tight (low spread), BB trades wide (high spread)
- CDS (Credit Default Swap): buyer pays periodic premium, seller pays on default
- CDS spread = annual premium in basis points — market's price for default risk
- Hazard rate model: λ(t) = instantaneous default intensity
- Survival probability: P(survive to T) = exp(−∫₀ᵀ λ(t)dt)
- Default probability: P(default by T) = 1 − exp(−λT) under constant hazard
- Bootstrapping default probabilities from CDS term structure (1Y, 3Y, 5Y, 7Y, 10Y CDS spreads)

**Build:** Credit spread calculation service. Fetches ICE BofA indices from FRED, calculates spreads by rating. SQS queues recalculation jobs. SNS sends email alert when BBB spreads exceed a configurable threshold.

---

### Exercise 16 — WebSockets (API Gateway WS) + Real-Time Spread Monitoring

**AWS concepts:**
- API Gateway WebSocket API ($connect, $disconnect, $default routes)
- Lambda handlers for WebSocket lifecycle
- DynamoDB (or in-memory) connection tracking
- Pushing messages to connected clients via `@connections` API

**Finance concepts:**
- Why real-time matters for credit: spreads can gap 50-100bps in a single session during stress events (Lehman, COVID, SVB)
- Spread monitoring workflows on a risk desk
- Threshold-based alerting vs continuous streaming

**Build:** WebSocket endpoint `wss://api/ws/spreads` that streams spread level updates to connected clients. Lambda pushes updates when new spread data is ingested.

---

### Exercise 17 — ElastiCache/Redis + Caching Bond Prices & Curves

**AWS concepts:**
- Provision ElastiCache Redis cluster (single-node, `cache.t3.micro`)
- Connect from Lambda (VPC configuration)
- TTL strategies: different TTLs for different data freshness requirements
- Cache-aside pattern vs write-through

**Finance concepts:**
- Which calculations are expensive and worth caching:
  - Curve fitting (Nelson-Siegel optimization): cache for the day
  - Bond pricing: cache for minutes (input-dependent)
  - Monte Carlo VaR: cache for the session (expensive computation)
- Cache invalidation: new curve data → invalidate all derived calculations

**Build:** Redis cache layer for curve and pricing endpoints. Benchmark: cached vs uncached response times. Redis is optional — app falls back to direct DB queries if Redis unavailable.

---

### Exercise 18 — Terraform Advanced + Default Probabilities

**AWS concepts:**
- Multi-service Terraform: Lambda + API GW + RDS + SQS + SNS + ElastiCache + WebSocket API
- Terraform modules for reusable patterns
- Environments (dev/prod) via workspaces or variable files
- Remote state with S3 backend + DynamoDB lock table

**Finance concepts:**
- Term structure of default probabilities: how default risk varies by time horizon
- Survival curves: plot P(survival) vs time — convex shape means front-loaded risk
- Recovery rate: what bondholders get back after default (typically 40% for senior unsecured)
- Loss Given Default (LGD) = 1 − recovery rate
- Expected Loss = PD × LGD × EAD (Exposure at Default)

**Build:** `/credit/cds` endpoint — takes CDS spreads by tenor, returns bootstrapped default probabilities, survival curve, and expected loss. Full infrastructure for Capstone B defined in Terraform.

---

### Exercise 19 — CloudWatch + OAS & Z-Spread

**AWS concepts:**
- Custom CloudWatch metrics (calculation latency, spread levels, error counts)
- CloudWatch dashboards with graphs and widgets
- Log Insights queries for debugging
- Alarms → SNS notifications (e.g., alert if API error rate > 5%)

**Finance concepts:**
- Z-spread recap: constant spread over spot curve matching market price (no optionality)
- OAS (Option-Adjusted Spread): spread after removing embedded option value
  - Callable bonds: issuer can redeem early → investor bears reinvestment risk
  - OAS < Z-spread for callable bonds (option has value to issuer)
- Binomial interest rate tree construction:
  - Each node branches up/down by σ√Δt
  - Calibrate tree to match spot curve (no-arbitrage)
  - Price callable bond by backward induction: at each node, issuer calls if call price < continuation value
- OAS = spread added to each tree node rate such that model price = market price

**Build:** `/credit/oas` endpoint — prices callable bonds using binomial tree, returns OAS, Z-spread, and the difference. CloudWatch dashboard tracking calculation latency and API health.

---

### Exercise 20 — Integration Testing + Duration, Convexity, Portfolio Credit VaR

**AWS concepts:**
- End-to-end testing patterns for distributed AWS services
- moto library for mocking S3, SQS, SNS, Lambda in pytest
- LocalStack for higher-fidelity local AWS emulation
- Test fixtures for RDS (test database, transaction rollback)

**Finance concepts:**
- Spread duration (CS01): price change for 1bp spread move — like DV01 but for credit
- Credit convexity: second-order spread sensitivity
- Portfolio credit VaR via Monte Carlo:
  1. Model spread changes as correlated normal variables
  2. Cholesky decomposition: L where LLᵀ = Σ (correlation matrix)
  3. Generate correlated random spread shocks: ΔS = L × Z (Z ~ N(0,1))
  4. Reprice portfolio under each scenario
  5. VaR = 5th percentile of simulated P&L distribution
- Business: "if spreads blow out like 2008, what does our portfolio lose?"

**Build:** `/portfolio/var` endpoint with full test suite covering all AWS integrations. Monte Carlo simulation with configurable scenarios (1,000 or 10,000 paths).

---

### --- Capstone B: Credit Risk Platform ---

**Assembles exercises 15-20 into `projects/credit-risk-platform/`. Imports curve and pricing engine from Capstone A.**

**Core services (adds to Capstone A):**

1. **Credit data ingestion** — daily Lambda fetches ICE BofA spread indices from FRED → S3 → RDS
2. **Credit spread engine** — spread curves by rating, historical spread analysis
3. **CDS engine** — bootstrap default probabilities from CDS term structure, survival curves
4. **OAS calculator** — binomial tree pricing for callable bonds, OAS vs Z-spread comparison
5. **Portfolio credit VaR** — Monte Carlo simulation with correlated spread shocks
6. **Real-time monitoring** — WebSocket spread stream, SQS job queue, SNS alert notifications
7. **Caching** — Redis for expensive calculations (curve fitting, Monte Carlo)
8. **Claude AI narratives** — credit condition commentary, alert context, historical comparison

**API endpoints (adds to Capstone A's):**
- `GET /spreads/{rating}` — credit spread curve for a rating bucket
- `GET /spreads/history?rating=&start=&end=` — historical spreads
- `POST /credit/price` — price a corporate bond (uses spread over treasury curve)
- `POST /credit/cds` — default probabilities from CDS spreads
- `POST /credit/oas` — OAS calculation for callable bonds
- `POST /portfolio/var` — portfolio credit VaR (Monte Carlo)
- `WS /ws/spreads` — real-time spread stream
- `GET /alerts` — recent threshold breach alerts

**AWS architecture (full stack):**
- S3: raw data (treasury + credit), Terraform state
- Lambda: all compute (curve, pricing, credit, VaR)
- API Gateway: REST + WebSocket APIs
- RDS PostgreSQL: all persistent data
- SQS: job queue for credit recalculations
- SNS: alert notifications (email/webhook)
- ElastiCache (Redis): calculation caching (optional, app falls back gracefully)
- CloudWatch: custom metrics, dashboards, alarms
- Terraform: all infrastructure as code
- GitHub Actions: CI/CD pipeline

**Dashboard:** new "Credit Risk" page in Streamlit app — spread charts by rating, default probability curves, OAS/Z-spread comparison, VaR simulation results, alert history.

**MiroFish (stretch goal):** swarm-based prediction of spread direction, compared against realized moves. Separate page in dashboard if implemented.

---

## 6. AWS Cost Strategy

**Free tier (12 months from account creation):**
- RDS: 750 hours/month of `db.t3.micro`, 20GB storage
- Lambda: 1M invocations/month, 400,000 GB-seconds
- S3: 5GB storage, 20,000 GET, 2,000 PUT
- API Gateway: 1M REST API calls/month
- ElastiCache: 750 hours/month of `cache.t3.micro`
- CloudWatch: 10 custom metrics, 3 dashboards, 10 alarms
- SQS: 1M requests/month
- SNS: 1M publishes, 1,000 emails

**Cost controls:**
- Exercise 09: set up $5 billing alarm immediately
- Terraform includes `terraform destroy` for full teardown
- RDS auto-stop when idle (dev environment)
- ElastiCache is optional — app falls back to direct queries
- No NAT Gateway (use VPC endpoints or public subnets for exercises)

**Post free-tier estimate:** ~$15-30/month if resources left running. Tear down when not actively learning.

---

## 7. Security

- Never commit AWS credentials — use environment variables + AWS CLI named profiles
- `.env` files in `.gitignore` from day one
- IAM least-privilege throughout — each Lambda gets only the permissions it needs
- FRED API key stored in AWS Secrets Manager (or environment variable for exercises)
- GitHub Actions uses OIDC for AWS authentication (no long-lived access keys)
- RDS security groups restrict access to Lambda + developer IP only

---

## 8. Local Development

- **moto:** AWS mocking library for unit tests (S3, SQS, SNS, DynamoDB)
- **LocalStack:** local AWS emulation for integration tests (requires Docker)
- **Docker Desktop:** already installed from Phase 1 exercise 07
- **Test database:** local PostgreSQL via Docker for RDS-dependent tests
- All exercises include local-first development workflow before deploying to AWS

---

## 9. Dashboard Integration

Extend the existing FinBytes Streamlit dashboard (`finbytes.streamlit.app`) with:

**Bond Pricing page (Capstone A):**
- Live yield curve chart (par, spot, forward, fitted)
- Nelson-Siegel parameter display
- Bond pricer form: input coupon/maturity/face value → price, YTM, duration, convexity, Z-spread
- Historical curve comparison

**Credit Risk page (Capstone B):**
- Credit spread charts by rating (AAA through B)
- Default probability / survival curves from CDS
- OAS vs Z-spread comparison tool
- Portfolio credit VaR simulation results
- Alert history and status

**System Health:** extend existing health monitoring for bond-pricing-engine and credit-risk-platform APIs.
