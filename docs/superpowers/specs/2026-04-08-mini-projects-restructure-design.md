# Mini Projects Restructure — Design Spec

**Date:** 2026-04-08
**Purpose:** Move 23 mini project blog posts into the QuantLab section of the FinBytes website as tabbed project pages (Concept / Code / Demo), add tech badges, and add contextual help panels to each Streamlit page.

---

## Part 1: Website restructure (FinBytes)

### Current state
- 23 mini project posts live in `docs/_posts/` as regular blog posts
- They appear in the main blog feed, not under Quant Lab
- No tabbed layout, no inline demos

### Target state
- 23 mini projects live in `docs/_quant_lab/mini/` as collection items
- Each uses a new `quant-lab-mini` layout with 3 tabs
- They appear on the Quant Lab index page under the capstone
- Old blog posts deleted from `_posts/`

### New layout: `_layouts/quant-lab-mini.html`

Extends `page`. Lighter than the capstone layout (3 tabs vs 9):

```
Title
Tech badges: Python · Plotly · NumPy
─────────────────────────────────────
[ Concept ] [ Code ] [ Demo ]

Tab content here
```

Tab structure:
- `tab-concept`: What it does, the math/formula, when you'd use it
- `tab-code`: Core function with imports, copy-pasteable
- `tab-demo`: Iframe to the Streamlit page

### Collection structure

```
docs/_quant_lab/
├── quant-lab.html          (existing — collection index)
├── stock-risk-scanner.html (existing — capstone)
└── mini/
    ├── credit-card-calculator.html
    ├── loan-amortization.html
    ├── loan-comparison.html
    ├── retirement-calculator.html
    ├── investment-planner.html
    ├── budget-tracker.html
    ├── currency-dashboard.html
    ├── stock-tracker.html
    ├── stock-analysis.html
    ├── crypto-portfolio.html
    ├── personal-finance.html
    ├── esg-tracker.html
    ├── financial-reporting.html
    ├── var-cvar.html
    ├── time-series.html
    ├── sentiment-analysis.html
    ├── anomaly-detection.html
    ├── loan-default.html
    ├── clustering.html
    ├── portfolio-optimization.html
    ├── algo-trading.html
    ├── stock-prediction.html
    └── market-insights.html
```

### Front matter for each mini project

```yaml
---
layout: quant-lab-mini
title: "Credit Card Calculator"
description: "Calculate payoff time, total interest, and amortization schedule."
date: 2026-08-01
permalink: /quant-lab/credit-card-calculator/
tech: [Python, Plotly, NumPy]
demo_url: "https://finbytes.streamlit.app/Credit_Card_Calculator"
category: calculators
---
```

### Quant Lab index page update

Flat list — all projects at the same level. Category shown as an inline badge/label next to each name:

```
Quant Lab

Stock Risk Scanner — Capstone
Credit Card Calculator · Mini Project · Calculator
Loan Amortization · Mini Project · Calculator
Loan Comparison · Mini Project · Calculator
Retirement Calculator · Mini Project · Calculator
Investment Planner · Mini Project · Calculator
Budget Tracker · Mini Project · Calculator
Currency Dashboard · Mini Project · Dashboard
Stock Tracker · Mini Project · Dashboard
Stock Analysis · Mini Project · Dashboard
Crypto Portfolio · Mini Project · Dashboard
Personal Finance · Mini Project · Dashboard
ESG Tracker · Mini Project · Dashboard
Financial Reporting · Mini Project · Dashboard
VaR & CVaR · Mini Project · ML & Quant
Time Series · Mini Project · ML & Quant
Sentiment Analysis · Mini Project · ML & Quant
Anomaly Detection · Mini Project · ML & Quant
Loan Default Prediction · Mini Project · ML & Quant
Customer Clustering · Mini Project · ML & Quant
Portfolio Optimization · Mini Project · ML & Quant
Algo Trading Backtest · Mini Project · ML & Quant
Stock Prediction · Mini Project · ML & Quant
Market Insights · Mini Project · ML & Quant
```

Badge styling: `Mini Project` in a neutral badge, category (`Calculator` / `Dashboard` / `ML & Quant`) in a colored badge.

### Posts to delete from `_posts/`

All 23 posts dated 2026-08-01 through 2026-08-29 (the finance tool posts).

### Config update

Add permalink for mini projects in `_config.yml` collections:

```yaml
quant_lab:
  output: true
  permalink: /quant-lab/:name/
```

This already exists — mini project files just need unique names that don't collide with existing items.

---

## Part 2: Streamlit context panels (QuantLab)

### What to add

Each of the 23 Streamlit pages gets 2 expandable panels at the top, right below the title:

```python
with st.expander("How it works"):
    st.markdown("""
    - **Step 1:** ...
    - **Step 2:** ...
    - **Formula:** ...
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Months to Payoff:** ...
    - **Total Interest:** ...
    """)
```

### Content per page (summary)

**Calculators:**
| Page | How it works | Key outputs |
|------|-------------|-------------|
| Credit Card | Iterative payoff: balance × monthly_rate = interest, payment - interest = principal | Months, total interest, amortization chart |
| Loan Amortization | PMT formula, fixed payment split between principal and interest | Monthly payment, schedule, P vs I chart |
| Loan Comparison | Same PMT formula applied to different rate/term combos | Side-by-side metrics, savings amount |
| Retirement | Compound growth + optional Monte Carlo (random returns) | Projected balance, P10/P50/P90 fan chart |
| Investment Planner | FV of lump sum + annuity | Final balance, contributions vs growth |
| Budget | Income minus categorized expenses | Surplus/deficit, spending breakdown |

**Dashboards:**
| Page | How it works | Key outputs |
|------|-------------|-------------|
| Currency | Fetches from exchangerate API, applies rate × amount | Converted amounts, rate chart |
| Stock Tracker | yfinance OHLCV data, candlestick rendering | Price chart, volume, 52-week range |
| Stock Analysis | Technical indicators: SMA, EMA, RSI, MACD, Bollinger | Overlaid price chart with indicators |
| Crypto Portfolio | CoinGecko prices × your holdings | Portfolio value, allocation pie |
| Personal Finance | Assets - liabilities = net worth | Net worth, savings rate, ratios |
| ESG Tracker | yfinance sustainability data (with fallback) | Radar chart, sector comparison |
| Financial Reporting | yfinance data → descriptive stats | Summary table, return distribution |

**ML & Quant:**
| Page | How it works | Key outputs |
|------|-------------|-------------|
| VaR/CVaR | Historical percentile (VaR) + mean of tail (CVaR) | Risk metrics, histogram with lines |
| Time Series | statsmodels decompose into trend/seasonal/residual | 4-panel decomposition, ACF |
| Sentiment | VADER/TextBlob polarity scoring on text | Sentiment scores, distribution |
| Anomaly Detection | Z-score threshold or Isolation Forest outlier detection | Flagged anomalies on chart |
| Loan Default | Logistic Regression / Random Forest on synthetic features | Accuracy, feature importance, prediction |
| Clustering | K-Means / DBSCAN on numeric features | Scatter by cluster, elbow chart, profiles |
| Portfolio Optimization | Monte Carlo random weights → efficient frontier | Risk/return scatter, optimal weights |
| Algo Trading | SMA crossover or momentum signals → backtest P&L | Equity curve, Sharpe, trade markers |
| Stock Prediction | Lagged features → regression model → forecast | Predicted vs actual, MAE/RMSE |
| Market Insights | VADER sentiment on headlines + stock price correlation | Dual-axis chart, correlation metric |

---

## Implementation order

1. Create `_layouts/quant-lab-mini.html` layout
2. Create 23 mini project files in `_quant_lab/mini/`
3. Update `_tabs/quant-lab.md` index with grouped mini project links
4. Delete 23 old blog posts from `_posts/`
5. Add context expanders to 23 Streamlit pages
6. Commit, push, PRs

Steps 1-4 are FinBytes repo. Step 5 is QuantLab repo. Can run in parallel.

---

## Out of scope
- No changes to the capstone (Stock Risk Scanner) page
- No changes to the Streamlit page functionality (only adding expanders)
- No changes to the existing blog posts that aren't being moved
- The `_config.yml` quant_lab collection config stays as-is
