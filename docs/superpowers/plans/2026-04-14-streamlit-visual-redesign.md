# Streamlit Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply a unified minimalist-chic visual identity to the QuantLab Streamlit dashboard in two passes: rewrite the landing page (`app.py`) into a typographic portfolio front door, then propagate the same visual language to all 31 existing pages via a shared `render_page_header()` helper.

**Architecture:** All visual identity (palette, fonts, component classes) lives in one global `<style>` block injected by `nav.render_sidebar()`, so every page picks it up automatically. The landing page is a self-contained rewrite. Every other page swaps `st.title("X")` for `render_page_header("X", "subtitle")` — a single function call — and inherits everything else for free.

**Tech Stack:** Python 3.11, Streamlit, Google Fonts (Fraunces + Inter via CDN), CSS via `st.markdown(unsafe_allow_html=True)`. No new Python dependencies. No tests (UI-only changes, manual verification).

**Spec reference:** [docs/superpowers/specs/2026-04-14-streamlit-visual-redesign-design.md](../specs/2026-04-14-streamlit-visual-redesign-design.md)

**Mockup reference:** [docs/superpowers/mockups/2026-04-14-streamlit-landing.html](../mockups/2026-04-14-streamlit-landing.html) — open in a browser to see the target visual.

---

## File Structure

**Quant_lab repo — created files:**

| Path | Purpose |
|---|---|
| `dashboard/lib/projects.py` | Project registry: dataclass + categorised dict + featured key list |
| `dashboard/lib/page_header.py` | `render_page_header(title, subtitle)` helper |

**Quant_lab repo — modified files (Pass A):**

| Path | Change |
|---|---|
| `dashboard/.streamlit/config.toml` | Update palette to amber + monochrome |
| `dashboard/lib/nav.py` | Replace logo image with text title; expand global CSS injection |
| `dashboard/app.py` | Full rewrite — Welcome tab (landing) + System Health tab |

**Quant_lab repo — modified files (Pass B):** all 31 pages in `dashboard/pages/`.

| Path | Change |
|---|---|
| `dashboard/pages/1_Stock_Risk_Scanner.py` | `st.title(...)` → `render_page_header(...)` |
| `dashboard/pages/10_Credit_Card_Calculator.py` | same |
| ... all 31 pages | same |

**Not modified:** `dashboard/assets/logo.png` stays in repo as the favicon (`page_icon` in `set_page_config`). Only its rendering as visible UI content is removed.

---

# PASS A — Landing page

## Task 1: Update the Streamlit theme config

**Files:**
- Modify: `dashboard/.streamlit/config.toml`

- [ ] **Step 1: Read the current config**

```bash
cat dashboard/.streamlit/config.toml
```

Expected: existing `[theme]` block with `primaryColor = "#2a7ae2"`.

- [ ] **Step 2: Replace the theme block**

Overwrite `dashboard/.streamlit/config.toml` with:

```toml
[theme]
primaryColor = "#d97706"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#fafafa"
textColor = "#1a1a1a"

[client]
showSidebarNavigation = false
```

The `[client]` section is preserved (existing — disables Streamlit's auto-generated nav since `nav.py` provides a custom one).

- [ ] **Step 3: Commit**

```bash
git add dashboard/.streamlit/config.toml
git status --short
git commit -m "style(theme): switch to monochrome + amber accent palette"
```

---

## Task 2: Create the project registry

**Files:**
- Create: `dashboard/lib/projects.py`

- [ ] **Step 1: Write the registry**

Create `dashboard/lib/projects.py`:

```python
"""Project registry — single source of truth for the landing page.

Edit this file to add or remove projects from the QuantLab landing.
The landing page (app.py) reads PROJECTS_BY_CATEGORY and FEATURED_KEYS
to render the featured grid and the categorised grids.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Project:
    key: str            # short slug; matches FEATURED_KEYS entries
    label: str          # display name
    description: str    # one-line description (~10-15 words)
    tech: list          # list of tech badge strings, joined with " · "
    page_link: str      # streamlit page_link target, e.g. "pages/16_Rent_vs_Buy.py"
    is_capstone: bool = False


PROJECTS_BY_CATEGORY: dict = {
    "Personal finance & property": [
        Project(
            key="london_house_prices",
            label="London House Prices",
            description="Postcode growth, comparison, and brand effect — 10 years of Land Registry data",
            tech=["Python", "Plotly", "GeoPandas", "OpenStreetMap"],
            page_link="pages/42_London_House_Prices.py",
        ),
        Project(
            key="rent_vs_buy",
            label="Rent vs Buy London",
            description="Data-driven calculator using HM Land Registry, ONS, and Bank of England",
            tech=["Python", "Streamlit", "pandas", "Plotly"],
            page_link="pages/16_Rent_vs_Buy.py",
        ),
        Project(
            key="credit_card_calculator",
            label="Credit Card Calculator",
            description="Payoff schedule, total interest, two calculation modes",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/10_Credit_Card_Calculator.py",
        ),
        Project(
            key="loan_amortization",
            label="Loan Amortization",
            description="PMT formula, principal vs interest breakdown, monthly schedule",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/11_Loan_Amortization.py",
        ),
        Project(
            key="loan_comparison",
            label="Loan Comparison",
            description="Side-by-side loan analysis with rate sensitivity",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/12_Loan_Comparison.py",
        ),
        Project(
            key="retirement_calculator",
            label="Retirement Calculator",
            description="Compound growth projection with Monte Carlo simulation",
            tech=["Python", "NumPy", "Plotly", "Monte Carlo"],
            page_link="pages/13_Retirement_Calculator.py",
        ),
        Project(
            key="investment_planner",
            label="Investment Planner",
            description="Compound growth with contributions and what-if scenarios",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/14_Investment_Planner.py",
        ),
        Project(
            key="budget_tracker",
            label="Budget Tracker",
            description="Income vs expenses, spending breakdown, surplus or deficit",
            tech=["Python", "Plotly", "Streamlit"],
            page_link="pages/15_Budget_Tracker.py",
        ),
        Project(
            key="personal_finance",
            label="Personal Finance",
            description="Net worth, savings rate, debt-to-income ratio",
            tech=["Python", "Plotly", "Streamlit"],
            page_link="pages/24_Personal_Finance.py",
        ),
    ],

    "Stocks & markets": [
        Project(
            key="stock_tracker",
            label="Stock Tracker",
            description="Candlestick charts, volume bars, 52-week range",
            tech=["Python", "yfinance", "Plotly", "Streamlit"],
            page_link="pages/21_Stock_Tracker.py",
        ),
        Project(
            key="stock_analysis",
            label="Stock Analysis",
            description="SMA, EMA, RSI, MACD, and Bollinger Bands overlays",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/22_Stock_Analysis.py",
        ),
        Project(
            key="stock_prediction",
            label="Stock Prediction",
            description="Feature engineering and regression for price forecasting",
            tech=["Python", "scikit-learn", "Plotly"],
            page_link="pages/38_Stock_Prediction.py",
        ),
        Project(
            key="portfolio_optimization",
            label="Portfolio Optimization",
            description="Efficient frontier, max Sharpe and min volatility portfolios",
            tech=["Python", "NumPy", "SciPy", "Plotly"],
            page_link="pages/36_Portfolio_Optimization.py",
        ),
        Project(
            key="algo_trading",
            label="Algo Trading Backtest",
            description="SMA crossover and momentum strategies with equity curves",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/37_Algo_Trading.py",
        ),
        Project(
            key="var_cvar",
            label="VaR & CVaR",
            description="Historical and parametric Value at Risk, Conditional VaR",
            tech=["Python", "yfinance", "NumPy", "SciPy"],
            page_link="pages/30_VaR_CVaR.py",
        ),
        Project(
            key="time_series",
            label="Time Series",
            description="Trend, seasonal, and residual decomposition with ACF",
            tech=["Python", "yfinance", "statsmodels"],
            page_link="pages/31_Time_Series.py",
        ),
        Project(
            key="anomaly_detection",
            label="Anomaly Detection",
            description="Z-score and Isolation Forest on stock returns",
            tech=["Python", "yfinance", "scikit-learn"],
            page_link="pages/33_Anomaly_Detection.py",
        ),
        Project(
            key="crypto_portfolio",
            label="Crypto Portfolio",
            description="Live crypto valuation, allocation pie, 24h change",
            tech=["Python", "CoinGecko API", "Plotly"],
            page_link="pages/23_Crypto_Portfolio.py",
        ),
        Project(
            key="stock_risk_scanner",
            label="Stock Risk Scanner",
            description="Full-stack portfolio risk analysis with FastAPI, Postgres, Docker, Claude",
            tech=["Python", "FastAPI", "PostgreSQL", "Docker", "Claude API"],
            page_link="pages/1_Stock_Risk_Scanner.py",
            is_capstone=True,
        ),
    ],

    "Analytics & Fintech": [
        Project(
            key="benchmark_rates",
            label="Benchmark Rates",
            description="SOFR, SONIA, and ESTR — fixed vs floating rate swap value",
            tech=["Python", "pandas", "Plotly"],
            page_link="pages/40_Benchmark_Rates.py",
        ),
        Project(
            key="currency_dashboard",
            label="Currency Dashboard",
            description="Live exchange rates, currency converter, rate comparison",
            tech=["Python", "Exchange Rate API", "Plotly"],
            page_link="pages/20_Currency_Dashboard.py",
        ),
        Project(
            key="sentiment_analysis",
            label="Sentiment Analysis",
            description="VADER and TextBlob applied to financial headlines",
            tech=["Python", "VADER", "TextBlob", "Plotly"],
            page_link="pages/32_Sentiment_Analysis.py",
        ),
        Project(
            key="market_insights",
            label="Market Insights",
            description="Sentiment-price correlation dashboard",
            tech=["Python", "yfinance", "VADER", "Plotly"],
            page_link="pages/39_Market_Insights.py",
        ),
        Project(
            key="esg_tracker",
            label="ESG Tracker",
            description="ESG score comparison, radar chart, sector averages",
            tech=["Python", "yfinance", "Plotly"],
            page_link="pages/25_ESG_Tracker.py",
        ),
        Project(
            key="loan_default",
            label="Loan Default Prediction",
            description="Logistic Regression and Random Forest classification",
            tech=["Python", "scikit-learn", "NumPy", "Plotly"],
            page_link="pages/34_Loan_Default.py",
        ),
        Project(
            key="clustering",
            label="Customer Clustering",
            description="K-Means and DBSCAN segmentation with editable data",
            tech=["Python", "scikit-learn", "NumPy", "Plotly"],
            page_link="pages/35_Clustering.py",
        ),
        Project(
            key="financial_reporting",
            label="Financial Reporting",
            description="Auto-generated stats, charts, and CSV export",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/26_Financial_Reporting.py",
        ),
        Project(
            key="bond_credit_aws",
            label="Bond/Credit Risk AWS",
            description="12-exercise arc — AWS fundamentals through Monte Carlo Credit VaR",
            tech=["Python", "AWS", "Terraform", "WebSockets", "Redis"],
            page_link="pages/40_Benchmark_Rates.py",  # no dedicated page; landing tab
            is_capstone=True,
        ),
    ],

    "Tech demos & references": [
        Project(
            key="big_o",
            label="Big O Notation",
            description="Same problem, different complexities — log-log curves of Fibonacci and Pair-sum",
            tech=["Python", "Plotly", "pytest"],
            page_link="pages/60_Big_O.py",
        ),
        Project(
            key="etymology",
            label="Etymology",
            description="Force-directed graph of English word roots — Greek, Latin, and Proto-Indo-European",
            tech=["D3.js", "vanilla JS", "YAML"],
            page_link="pages/50_Etymology.py",
        ),
        Project(
            key="plotting_libraries",
            label="Plotting Libraries Compared",
            description="Same data rendered in Plotly, Matplotlib, Altair, and Bokeh side-by-side",
            tech=["Python", "Plotly", "Matplotlib", "Altair", "Bokeh"],
            page_link="pages/41_Plotting_Libraries.py",
        ),
    ],
}


FEATURED_KEYS = [
    "london_house_prices",
    "etymology",
    "big_o",
    "rent_vs_buy",
    "portfolio_optimization",
    "plotting_libraries",
]


def all_projects() -> list:
    """Flatten the categorised dict into a single list."""
    return [p for projs in PROJECTS_BY_CATEGORY.values() for p in projs]


def featured() -> list:
    """Return the featured projects in FEATURED_KEYS order."""
    by_key = {p.key: p for p in all_projects()}
    return [by_key[k] for k in FEATURED_KEYS if k in by_key]


def category_with_capstones_last(category: str) -> list:
    """Return projects for one category with capstones bumped to the end."""
    projs = PROJECTS_BY_CATEGORY.get(category, [])
    non_capstones = [p for p in projs if not p.is_capstone]
    capstones = [p for p in projs if p.is_capstone]
    return non_capstones + capstones
```

- [ ] **Step 2: Sanity-check the registry**

```bash
cd dashboard && python -c "
from lib.projects import PROJECTS_BY_CATEGORY, FEATURED_KEYS, all_projects, featured, category_with_capstones_last
total = len(all_projects())
cats = list(PROJECTS_BY_CATEGORY.keys())
print(f'Total projects: {total}')
print(f'Categories: {cats}')
feat = featured()
print(f'Featured: {[p.label for p in feat]}')
for c in cats:
    ordered = category_with_capstones_last(c)
    print(f'  {c}: {len(ordered)} projects, last = {ordered[-1].label}')
"
```

Expected:
- Total projects: 30
- Categories: 4 (Personal finance & property, Stocks & markets, Analytics & Fintech, Tech demos & references)
- Featured: 6 entries (London House Prices, Etymology, Big O Notation, Rent vs Buy London, Portfolio Optimization, Plotting Libraries Compared)
- Stocks & markets last entry = Stock Risk Scanner
- Analytics & Fintech last entry = Bond/Credit Risk AWS
- Other categories last entry is just whatever's last

- [ ] **Step 3: Commit**

```bash
git add dashboard/lib/projects.py
git status --short
git commit -m "feat(landing): add project registry for landing page"
```

---

## Task 3: Create the page header helper

**Files:**
- Create: `dashboard/lib/page_header.py`

- [ ] **Step 1: Write the helper**

Create `dashboard/lib/page_header.py`:

```python
"""Shared page header — call at the top of every dashboard page.

Renders a typographic h1 + optional subtitle styled by the global
CSS injected from nav.render_sidebar(). One function call replaces
the per-page st.title()/st.caption() pattern.
"""

import streamlit as st


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """Render a styled page header.

    Args:
        title: page title (renders as serif Fraunces h1)
        subtitle: optional one-line tagline (renders as Inter sans, muted)
    """
    st.markdown(
        f'<h1 class="ql-page-title">{title}</h1>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<p class="ql-page-subtitle">{subtitle}</p>',
            unsafe_allow_html=True,
        )
```

- [ ] **Step 2: Verify it imports**

```bash
cd dashboard && python -c "from lib.page_header import render_page_header; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add dashboard/lib/page_header.py
git status --short
git commit -m "feat(ui): add render_page_header helper"
```

---

## Task 4: Expand global CSS in nav.py

**Files:**
- Modify: `dashboard/lib/nav.py`

This is the single biggest visual lift in the plan — one large CSS block that defines the entire visual identity.

- [ ] **Step 1: Read the current nav.py**

```bash
cat dashboard/lib/nav.py
```

Locate `_GLOBAL_STYLES` (added in a previous PR — currently has only the expander text styling).

- [ ] **Step 2: Replace `_GLOBAL_STYLES` with the full block**

Open `dashboard/lib/nav.py` and find the existing `_GLOBAL_STYLES = """ ... """` block. Replace ENTIRELY with:

```python
_GLOBAL_STYLES = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --ql-accent: #d97706;
    --ql-text: #1a1a1a;
    --ql-muted: #6b6b6b;
    --ql-bg: #ffffff;
    --ql-bg2: #fafafa;
    --ql-border: #e5e5e5;
    --ql-font-display: 'Fraunces', Georgia, serif;
    --ql-font-body: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Body font override */
html, body, [class*="st-"], [data-testid="stAppViewContainer"] {
    font-family: var(--ql-font-body);
    color: var(--ql-text);
}

/* Streamlit headings → Fraunces */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--ql-font-display);
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--ql-text);
}

/* Page header helper classes */
.ql-page-title {
    font-family: var(--ql-font-display);
    font-size: 2rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0.5rem 0 0.25rem;
    color: var(--ql-text);
}
.ql-page-subtitle {
    font-family: var(--ql-font-body);
    font-size: 1rem;
    color: var(--ql-muted);
    margin: 0 0 1.5rem;
    font-weight: 400;
}

/* Sidebar branding */
.ql-sidebar-brand {
    padding: 0.5rem 0 0.25rem;
    margin-bottom: 0.5rem;
}
.ql-sidebar-title {
    font-family: var(--ql-font-display);
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--ql-text);
    letter-spacing: -0.01em;
    line-height: 1.1;
}
.ql-sidebar-byline {
    font-family: var(--ql-font-body);
    font-size: 0.78rem;
    color: var(--ql-muted);
    margin-top: 0.2rem;
}
.ql-sidebar-byline a {
    color: var(--ql-accent);
    text-decoration: none;
}
.ql-sidebar-byline a:hover { text-decoration: underline; }

/* Landing page hero */
.ql-hero {
    text-align: center;
    padding: 4rem 0 3rem;
    border-bottom: 1px solid var(--ql-border);
    margin-bottom: 3.5rem;
}
.ql-hero-title {
    font-family: var(--ql-font-display);
    font-size: 4.5rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    margin: 0 0 1rem;
    color: var(--ql-text);
    font-variation-settings: "opsz" 144;
}
.ql-hero-subtitle {
    font-family: var(--ql-font-body);
    font-size: 1.15rem;
    color: var(--ql-muted);
    font-weight: 400;
    margin: 0;
}

/* Section headings on the landing page */
.ql-section-heading {
    font-family: var(--ql-font-display);
    font-size: 1.75rem;
    font-weight: 500;
    color: var(--ql-text);
    margin: 3rem 0 1.25rem;
    letter-spacing: -0.01em;
}

/* Featured grid (3 cols, large cards with serif titles) */
.ql-featured-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 1rem;
}
.ql-featured-card {
    background: var(--ql-bg);
    border: 1px solid var(--ql-border);
    border-radius: 4px;
    padding: 1.6rem 1.5rem;
    transition: border-color 0.15s;
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}
.ql-featured-card:hover { border-color: var(--ql-accent); }
.ql-featured-card-title {
    font-family: var(--ql-font-display);
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--ql-accent);
    margin: 0 0 0.5rem;
    line-height: 1.2;
    letter-spacing: -0.01em;
}
.ql-featured-card-desc {
    font-family: var(--ql-font-body);
    font-size: 0.92rem;
    line-height: 1.5;
    color: var(--ql-text);
    margin: 0 0 0.9rem;
}
.ql-featured-card-tech {
    font-family: var(--ql-font-body);
    font-size: 0.74rem;
    color: var(--ql-muted);
    letter-spacing: 0.01em;
}

/* Categorised grid (3 cols on wide, 2 on narrow, compact text cards) */
.ql-cat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
@media (max-width: 768px) {
    .ql-featured-grid { grid-template-columns: 1fr; }
    .ql-cat-grid { grid-template-columns: 1fr; }
}
.ql-cat-card {
    background: var(--ql-bg);
    border: 1px solid var(--ql-border);
    border-radius: 4px;
    padding: 0.9rem 1rem;
    transition: border-color 0.15s;
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}
.ql-cat-card:hover { border-color: var(--ql-accent); }
.ql-cat-card-title {
    font-family: var(--ql-font-body);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ql-accent);
    margin: 0 0 0.25rem;
}
.ql-cat-card-desc {
    font-family: var(--ql-font-body);
    font-size: 0.78rem;
    color: var(--ql-text);
    margin: 0 0 0.5rem;
    line-height: 1.4;
}
.ql-cat-card-tech {
    font-family: var(--ql-font-body);
    font-size: 0.68rem;
    color: var(--ql-muted);
}
.ql-capstone-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ql-accent);
    border: 1px solid var(--ql-accent);
    padding: 1px 5px;
    border-radius: 2px;
    margin-left: 0.4rem;
    vertical-align: middle;
}

/* Existing: smaller, greyer text inside expanders */
[data-testid="stExpander"] details > div p,
[data-testid="stExpander"] details > div li,
[data-testid="stExpander"] details > div td,
[data-testid="stExpander"] details > div th {
    font-size: 0.86rem;
    color: var(--ql-muted);
}
[data-testid="stExpander"] details > div strong {
    color: var(--ql-text);
}
[data-testid="stExpander"] details > div table {
    font-size: 0.86rem;
}
</style>
"""
```

- [ ] **Step 3: Replace the sidebar header to drop the logo**

In the same file, find `_render_sidebar_impl()`. Replace these three lines:

```python
    st.sidebar.image(str(ASSETS / "logo.png"), width=180)
    st.sidebar.title("FinBytes QuantLabs")
    st.sidebar.markdown("**Built by** [Manisha](https://mish-codes.github.io/FinBytes/)")
```

With:

```python
    st.sidebar.markdown(
        '<div class="ql-sidebar-brand">'
        '<div class="ql-sidebar-title">QuantLab</div>'
        '<div class="ql-sidebar-byline">Built by '
        '<a href="https://mish-codes.github.io/FinBytes/">Manisha</a>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
```

The `ASSETS` import at the top of `nav.py` is no longer needed by the sidebar but is left in place — `app.py` and other places may still use it for `page_icon`. No change to the import.

- [ ] **Step 4: Verify nav.py imports**

```bash
cd dashboard && python -c "from lib.nav import render_sidebar; print('ok')"
```

Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/nav.py
git status --short
git commit -m "style(ui): expand global CSS with new visual identity and drop sidebar logo"
```

---

## Task 5: Rewrite app.py landing page

**Files:**
- Modify: `dashboard/app.py`

This is the largest single file rewrite. The existing System Health content is preserved verbatim inside the `tab_health` block.

- [ ] **Step 1: Read the current app.py to preserve System Health logic**

```bash
cat dashboard/app.py
```

Note the existing content of the System Health checks (CI status, GitHub API calls, test_results, etc). All of this needs to be preserved.

- [ ] **Step 2: Write the new app.py**

Overwrite `dashboard/app.py` with:

```python
"""QuantLab landing page — Welcome (portfolio) + System Health tabs."""

from pathlib import Path
import sys

import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from nav import render_sidebar
from test_tab import render_test_tab
from projects import (
    PROJECTS_BY_CATEGORY,
    featured,
    category_with_capstones_last,
)

HERE = Path(__file__).parent
GITHUB_REPO = "mish-codes/QuantLab"

st.set_page_config(
    page_title="QuantLab",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()


# ─────────────────────────────────────────────────────────────
# HTML rendering helpers
# ─────────────────────────────────────────────────────────────

def _escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _featured_card_html(p) -> str:
    tech = " · ".join(_escape(t) for t in p.tech)
    return (
        f'<a class="ql-featured-card" href="{_escape(p.page_link)}" target="_self">'
        f'<div class="ql-featured-card-title">{_escape(p.label)}</div>'
        f'<div class="ql-featured-card-desc">{_escape(p.description)}</div>'
        f'<div class="ql-featured-card-tech">{tech}</div>'
        f'</a>'
    )


def _cat_card_html(p) -> str:
    tech = " · ".join(_escape(t) for t in p.tech)
    capstone = (
        '<span class="ql-capstone-tag">Capstone</span>' if p.is_capstone else ""
    )
    return (
        f'<a class="ql-cat-card" href="{_escape(p.page_link)}" target="_self">'
        f'<div class="ql-cat-card-title">{_escape(p.label)}{capstone}</div>'
        f'<div class="ql-cat-card-desc">{_escape(p.description)}</div>'
        f'<div class="ql-cat-card-tech">{tech}</div>'
        f'</a>'
    )


# ─────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────

tab_welcome, tab_health = st.tabs(["Welcome", "System Health"])

# ─────────────────────────────────────────────────────────────
# Welcome — landing portfolio view
# ─────────────────────────────────────────────────────────────

with tab_welcome:
    st.markdown(
        '<div class="ql-hero">'
        '<h1 class="ql-hero-title">QuantLab</h1>'
        '<p class="ql-hero-subtitle">Interactive finance and data experiments in Python</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Featured grid
    st.markdown('<h2 class="ql-section-heading">Featured</h2>', unsafe_allow_html=True)
    featured_html = '<div class="ql-featured-grid">'
    for p in featured():
        featured_html += _featured_card_html(p)
    featured_html += '</div>'
    st.markdown(featured_html, unsafe_allow_html=True)

    # Categorised grids
    for category in PROJECTS_BY_CATEGORY.keys():
        st.markdown(
            f'<h2 class="ql-section-heading">{_escape(category)}</h2>',
            unsafe_allow_html=True,
        )
        grid_html = '<div class="ql-cat-grid">'
        for p in category_with_capstones_last(category):
            grid_html += _cat_card_html(p)
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    st.markdown('<div style="height: 4rem;"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# System Health — preserved from previous version
# ─────────────────────────────────────────────────────────────

with tab_health:
    st.markdown("### Shared Infrastructure")

    ci_status = {"status": "unknown", "detail": ""}
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
            params={"per_page": 3},
            timeout=10,
        )
        if r.status_code == 200:
            runs = r.json().get("workflow_runs", [])
            if runs:
                latest = runs[0]
                ci_status = {
                    "status": latest.get("conclusion") or latest.get("status"),
                    "detail": f"Run #{latest.get('run_number')} on {latest.get('head_branch')}",
                }
    except Exception as exc:
        ci_status = {"status": "error", "detail": str(exc)}

    cols = st.columns(3)
    with cols[0]:
        st.metric(
            "CI status",
            ci_status["status"],
            ci_status["detail"],
        )
    with cols[1]:
        st.metric("Streamlit Cloud", "live", "auto-deploys from master")
    with cols[2]:
        st.metric("Repo", GITHUB_REPO, "")

    st.markdown("---")
    render_test_tab("test_app.py")
```

Note: this rewrite preserves the System Health functionality (GitHub Actions API call, metrics, test tab) verbatim. If the original `app.py` had additional system checks, copy them into the `with tab_health:` block as well — read the original carefully and preserve everything that was inside the original main content area.

- [ ] **Step 3: Verify the page parses**

```bash
cd dashboard && python -c "
with open('app.py', encoding='utf-8') as f:
    compile(f.read(), 'app.py', 'exec')
print('syntax ok')
"
```

Expected: `syntax ok`

- [ ] **Step 4: Launch and manually verify**

```bash
cd dashboard && streamlit run app.py
```

In the browser:
- [ ] Page loads without Python errors
- [ ] Sidebar shows "QuantLab" text title (no logo image)
- [ ] Welcome tab is the default
- [ ] Big serif "QuantLab" hero renders, with subtitle below
- [ ] "Featured" heading appears, with 6 cards in a 3-column grid
- [ ] Each featured card has serif title in amber, description, tech badges
- [ ] Hovering a featured card shows amber border
- [ ] 4 categorised grids render in order: Personal finance & property, Stocks & markets, Analytics & Fintech, Tech demos & references
- [ ] Stock Risk Scanner appears LAST in Stocks & markets, with a "Capstone" tag
- [ ] Bond/Credit Risk AWS appears LAST in Analytics & Fintech, with a "Capstone" tag
- [ ] Click a card → navigates to the corresponding page
- [ ] Switch to System Health tab → CI status, metrics, test tab all render
- [ ] No console errors

Stop the server (Ctrl+C) when verified.

- [ ] **Step 5: Commit**

```bash
git add dashboard/app.py
git status --short
git commit -m "feat(landing): rewrite app.py with Welcome (portfolio) and System Health tabs"
```

---

## Task 6: PR for Pass A

- [ ] **Step 1: Push the working branch**

```bash
git push origin working
```

- [ ] **Step 2: Open a PR**

```bash
gh pr create --base master --head working --title "feat: Streamlit visual redesign — Pass A (landing page)" --body "$(cat <<'EOF'
## Summary

Pass A of the QuantLab Streamlit visual redesign. Locks in a unified minimalist-chic visual identity by rewriting the landing page as a typographic portfolio front door.

**Visual identity:**
- Drop the FinBytes logo from the UI (kept in repo as page favicon)
- Palette: monochrome + amber accent (\`#d97706\`)
- Typography: Fraunces (display) + Inter (body), via Google Fonts
- All visual identity lives in one global CSS block in \`nav.py\`

**Landing page:**
- Welcome tab (default) with big serif hero, 6 featured cards, and 4 categorised content grids
- System Health tab preserves the existing infrastructure checks
- Categories: Personal finance & property, Stocks & markets, Analytics & Fintech, Tech demos & references
- Capstones bumped to the bottom of their category
- Project metadata centralised in \`lib/projects.py\`
- Page header helper \`lib/page_header.py\` ready for Pass B

**What this PR does NOT do:**
- Pass B (propagating the new header to all 31 sub-pages) is a follow-up PR

## Test Plan
- [x] Page parses
- [ ] Manual: landing page loads, Welcome is default, sidebar is text-only
- [ ] Manual: featured cards render, click navigates correctly
- [ ] Manual: capstone tags appear in correct positions
- [ ] Manual: System Health tab functions normally

## Specs and mockup
- Design: [docs/superpowers/specs/2026-04-14-streamlit-visual-redesign-design.md](docs/superpowers/specs/2026-04-14-streamlit-visual-redesign-design.md)
- Plan: [docs/superpowers/plans/2026-04-14-streamlit-visual-redesign.md](docs/superpowers/plans/2026-04-14-streamlit-visual-redesign.md)
- Mockup: [docs/superpowers/mockups/2026-04-14-streamlit-landing.html](docs/superpowers/mockups/2026-04-14-streamlit-landing.html)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL.

---

# PASS B — Propagate to all pages

Pass B is mechanical: for each of the 31 pages in `dashboard/pages/`, replace the `st.title(...)` call (and any immediately-following intro `st.caption()` or `st.markdown(...)` tagline) with `render_page_header(title, subtitle)`. The subtitle is curated per page using a one-line tagline that complements the title.

Each task touches one page file. Tasks 7–37.

For each task, the steps are identical:

1. **Read the current page** to find the existing `st.title(...)` line.
2. **Add the import** for `render_page_header` near the top (after the existing `from nav import render_sidebar` line).
3. **Replace** `st.title("X")` with `render_page_header("X", "Y")` where Y is the curated subtitle from the table below.
4. **Verify the page parses.**
5. **Commit.**

The subtitle for each page is given in the table inside its task. Use the exact subtitle text — keep them short (5–12 words), no punctuation at the end, complement (don't repeat) the title.

To save space, the steps are spelled out in full only for Task 7; Tasks 8–37 have the same five-step pattern with just the file path, title, and subtitle changing.

---

## Task 7: Migrate page 1_Stock_Risk_Scanner

**Files:**
- Modify: `dashboard/pages/1_Stock_Risk_Scanner.py`

**Title:** `Stock Risk Scanner`
**Subtitle:** `Full-stack portfolio risk analysis with FastAPI, Postgres, and Claude`

- [ ] **Step 1: Read the current page**

```bash
grep -n "st.title\|render_sidebar" dashboard/pages/1_Stock_Risk_Scanner.py
```

Expected: shows the existing `render_sidebar()` line and `st.title("Stock Risk Scanner")` (or similar).

- [ ] **Step 2: Add the import**

In `dashboard/pages/1_Stock_Risk_Scanner.py`, find this line:

```python
from nav import render_sidebar
```

Add directly after it:

```python
from page_header import render_page_header
```

- [ ] **Step 3: Replace the title call**

Find the line `st.title("Stock Risk Scanner")` (the exact title may vary slightly — match whatever's currently there). Replace with:

```python
render_page_header("Stock Risk Scanner", "Full-stack portfolio risk analysis with FastAPI, Postgres, and Claude")
```

If there's an immediately-following `st.caption(...)` or single-line `st.markdown(...)` that acts as an intro tagline, delete it (the subtitle now handles that role). If the next thing is multi-line markdown body content, leave it alone.

- [ ] **Step 4: Verify the page parses**

```bash
cd dashboard && python -c "
with open('pages/1_Stock_Risk_Scanner.py', encoding='utf-8') as f:
    compile(f.read(), 'pages/1_Stock_Risk_Scanner.py', 'exec')
print('syntax ok')
"
```

Expected: `syntax ok`

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/1_Stock_Risk_Scanner.py
git status --short
git commit -m "style(ui): migrate 1_Stock_Risk_Scanner to render_page_header"
```

---

## Tasks 8–37: Migrate remaining pages

Same 5-step pattern as Task 7. For each task:

| # | File | Title | Subtitle |
|---|---|---|---|
| 8 | `pages/10_Credit_Card_Calculator.py` | Credit Card Calculator | Payoff schedule and total interest, two calculation modes |
| 9 | `pages/11_Loan_Amortization.py` | Loan Amortization | PMT formula, principal vs interest, monthly schedule |
| 10 | `pages/12_Loan_Comparison.py` | Loan Comparison | Side-by-side loan analysis with rate sensitivity |
| 11 | `pages/13_Retirement_Calculator.py` | Retirement Calculator | Compound growth projection with Monte Carlo simulation |
| 12 | `pages/14_Investment_Planner.py` | Investment Planner | Compound growth with contributions and what-if scenarios |
| 13 | `pages/15_Budget_Tracker.py` | Budget Tracker | Income vs expenses, spending breakdown, surplus or deficit |
| 14 | `pages/16_Rent_vs_Buy.py` | Rent vs Buy — London | Data-driven calculator using HM Land Registry, ONS, and BoE |
| 15 | `pages/20_Currency_Dashboard.py` | Currency Dashboard | Live exchange rates, currency converter, rate comparison |
| 16 | `pages/21_Stock_Tracker.py` | Stock Tracker | Candlestick charts, volume bars, 52-week range |
| 17 | `pages/22_Stock_Analysis.py` | Stock Analysis | SMA, EMA, RSI, MACD, and Bollinger Bands overlays |
| 18 | `pages/23_Crypto_Portfolio.py` | Crypto Portfolio | Live crypto valuation, allocation pie, 24-hour change |
| 19 | `pages/24_Personal_Finance.py` | Personal Finance | Net worth, savings rate, debt-to-income ratio |
| 20 | `pages/25_ESG_Tracker.py` | ESG Tracker | ESG score comparison, radar chart, sector averages |
| 21 | `pages/26_Financial_Reporting.py` | Financial Reporting | Auto-generated stats, charts, and CSV export |
| 22 | `pages/30_VaR_CVaR.py` | VaR & CVaR | Historical and parametric Value at Risk, Conditional VaR |
| 23 | `pages/31_Time_Series.py` | Time Series | Trend, seasonal, and residual decomposition with ACF |
| 24 | `pages/32_Sentiment_Analysis.py` | Sentiment Analysis | VADER and TextBlob applied to financial headlines |
| 25 | `pages/33_Anomaly_Detection.py` | Anomaly Detection | Z-score and Isolation Forest on stock returns |
| 26 | `pages/34_Loan_Default.py` | Loan Default Prediction | Logistic Regression and Random Forest classification |
| 27 | `pages/35_Clustering.py` | Customer Clustering | K-Means and DBSCAN segmentation with editable data |
| 28 | `pages/36_Portfolio_Optimization.py` | Portfolio Optimization | Efficient frontier, max Sharpe and min volatility portfolios |
| 29 | `pages/37_Algo_Trading.py` | Algo Trading Backtest | SMA crossover and momentum strategies with equity curves |
| 30 | `pages/38_Stock_Prediction.py` | Stock Prediction | Feature engineering and regression for price forecasting |
| 31 | `pages/39_Market_Insights.py` | Market Insights | Sentiment-price correlation dashboard |
| 32 | `pages/40_Benchmark_Rates.py` | Benchmark Rates | SOFR, SONIA, and ESTR — fixed vs floating rate swap value |
| 33 | `pages/41_Plotting_Libraries.py` | Plotting Libraries Compared | Plotly, Matplotlib, Altair, and Bokeh side-by-side |
| 34 | `pages/42_London_House_Prices.py` | London House Prices | Postcode growth, comparison, brand effect, and benchmark lab |
| 35 | `pages/50_Etymology.py` | Etymology | Force-directed graph of English word roots |
| 36 | `pages/60_Big_O.py` | Big O Notation | Same problem, different complexities — see the gap |
| 37 | `pages/99_Churros.py` | Churros | (whatever is currently the description there — read the file and pick a one-liner) |

For each row above, follow the 5-step pattern from Task 7:

- [ ] **Step 1:** `grep -n "st.title\|render_sidebar" dashboard/pages/<file>` to locate the lines
- [ ] **Step 2:** Add `from page_header import render_page_header` directly after the `from nav import render_sidebar` line
- [ ] **Step 3:** Replace `st.title("...")` with `render_page_header("Title", "Subtitle")`. Delete any immediately-following intro caption/markdown tagline if it duplicates the new subtitle.
- [ ] **Step 4:** `python -c "with open('dashboard/pages/<file>', encoding='utf-8') as f: compile(f.read(), '<file>', 'exec')"` and confirm `syntax ok`
- [ ] **Step 5:** `git add dashboard/pages/<file> && git status --short && git commit -m "style(ui): migrate <filename without .py> to render_page_header"`

**Batching tip:** these 31 tasks can all be committed in one PR (Pass B), one commit per page. The plan separates them as 31 task entries so the work is trackable; in execution, dispatch one or two pages per subagent (or do all in one go with inline execution).

---

## Task 38: Pass B PR

After all 31 page migrations are committed:

- [ ] **Step 1: Run the full test suite to verify nothing broke**

```bash
cd dashboard && python -m pytest tests/ 2>&1 | tail -5
```

Expected: full suite passes (no rentbuy/bigo/etc tests should be broken by header migration).

- [ ] **Step 2: Manual spot-check 4 representative pages**

```bash
cd dashboard && streamlit run app.py
```

Click into:
- A calculator (e.g., Credit Card Calculator)
- A dashboard (e.g., Stock Tracker)
- An ML page (e.g., Loan Default)
- A tech demo (e.g., Big O Notation)

Verify each shows:
- [ ] Serif Fraunces title via `render_page_header`
- [ ] Subtitle in muted Inter sans
- [ ] Original page functionality intact
- [ ] No duplicate title (old `st.title` left behind)

Stop the server.

- [ ] **Step 3: Push and open PR**

```bash
git push origin working
gh pr create --base master --head working --title "feat: Streamlit visual redesign — Pass B (propagate to all pages)" --body "$(cat <<'EOF'
## Summary

Pass B: every page in \`dashboard/pages/\` now uses \`render_page_header(title, subtitle)\` instead of \`st.title(...)\`. The page header inherits Fraunces serif + Inter sans typography from the global CSS injected in Pass A.

31 pages migrated, one commit per page.

## Test Plan
- [x] All existing tests pass
- [ ] Manual: spot-check 4 pages (calculator, dashboard, ML, tech demo) for correct header rendering
- [ ] Manual: no duplicate titles, no broken functionality

## Specs and plans
- Design: [docs/superpowers/specs/2026-04-14-streamlit-visual-redesign-design.md](docs/superpowers/specs/2026-04-14-streamlit-visual-redesign-design.md)
- Plan: [docs/superpowers/plans/2026-04-14-streamlit-visual-redesign.md](docs/superpowers/plans/2026-04-14-streamlit-visual-redesign.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL.

---

## Self-Review Notes

**Spec coverage check:**

- ✅ Palette in `config.toml` (Task 1)
- ✅ Drop logo from sidebar (Task 4 step 3)
- ✅ Google Fonts loaded (Task 4 step 2)
- ✅ Fraunces + Inter typography globally (Task 4 step 2)
- ✅ Page header helper (Task 3)
- ✅ Project registry with all 30 projects, 4 categories, capstones marked (Task 2)
- ✅ Featured projects list (Task 2 — FEATURED_KEYS)
- ✅ Capstones bumped to bottom of category (Task 2 — `category_with_capstones_last`)
- ✅ Welcome tab + System Health tab structure (Task 5)
- ✅ Hero with Fraunces title (Task 4 + Task 5)
- ✅ Featured grid with serif card titles (Task 4 + Task 5)
- ✅ Categorised grid with sans card titles (Task 4 + Task 5)
- ✅ Capstone tag rendering (Task 4 + Task 5 + Task 2)
- ✅ Existing expander styling preserved (Task 4 step 2 — at the end of `_GLOBAL_STYLES`)
- ✅ Mobile responsive grid (Task 4 — `@media (max-width: 768px)`)
- ✅ Pass B page migrations (Tasks 7–37)
- ✅ Final manual verification + PR (Tasks 6, 38)

**Placeholder scan:** no TBD/TODO/vague language. All code blocks are complete. The Churros page (Task 37) flags that the implementer should read the file to pick a sensible subtitle since I don't know what Churros is — that's an explicit instruction, not a placeholder.

**Type consistency:**
- `Project` dataclass defined once in `lib/projects.py`, used by `app.py` only. Field names (`key`, `label`, `description`, `tech`, `page_link`, `is_capstone`) consistent across helper functions and HTML rendering.
- `render_page_header(title, subtitle)` signature consistent between `lib/page_header.py` (Task 3) and every page migration (Tasks 7–37).
- CSS class names (`ql-*` prefix) consistent between `nav.py` injection (Task 4) and the HTML rendering helpers in `app.py` (Task 5).
- `_GLOBAL_STYLES` is the same constant referenced in `nav.py` before and after the expansion (Task 4 step 2).

**Scope check:** two passes, one Streamlit dashboard. Pass A is one PR, Pass B is one PR. All implementable in two sessions.

No gaps found.
