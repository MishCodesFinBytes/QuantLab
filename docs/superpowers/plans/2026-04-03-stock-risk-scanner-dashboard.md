# Stock Risk Scanner Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive Streamlit dashboard at `finbytes.streamlit.app` that lets users run risk scans via the Render-hosted FastAPI backend, with Plotly charts and color-coded metrics.

**Architecture:** Multi-page Streamlit app (ready for future projects). The Stock Risk Scanner page calls the FastAPI API on Render for scans, fetches price data directly via yfinance for charts, and computes portfolio metrics locally for visualization. Config and API URL come from Streamlit secrets.

**Tech Stack:** Streamlit, Plotly, yfinance, pandas, numpy, requests

---

## File Structure

```
projects/stock-risk-scanner/dashboard/
├── app.py                    # Main entry — page config, sidebar, landing page
├── pages/
│   └── 1_Stock_Risk_Scanner.py   # Scanner page — input, scan, results, charts
├── lib/
│   ├── api_client.py         # Backend API calls (scan, poll, history, health)
│   ├── charts.py             # Plotly chart builders (price, cumulative, drawdown, pie)
│   └── risk_colors.py        # Color-coding logic for metrics
├── requirements.txt          # Streamlit Cloud dependencies
└── .streamlit/
    └── config.toml           # Theme configuration
```

---

### Task 1: Project Scaffold + Config

**Files:**
- Create: `projects/stock-risk-scanner/dashboard/requirements.txt`
- Create: `projects/stock-risk-scanner/dashboard/.streamlit/config.toml`
- Create: `projects/stock-risk-scanner/dashboard/app.py`
- Create: `projects/stock-risk-scanner/dashboard/pages/` (directory)
- Create: `projects/stock-risk-scanner/dashboard/lib/` (directory)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/dashboard/pages
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/dashboard/lib
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/dashboard/.streamlit
```

- [ ] **Step 2: Create requirements.txt**

```
streamlit>=1.30.0
plotly>=5.18.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.26.0
requests>=2.31.0
```

- [ ] **Step 3: Create .streamlit/config.toml**

```toml
[theme]
primaryColor = "#2a7ae2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

- [ ] **Step 4: Create app.py (landing page + sidebar)**

```python
# projects/stock-risk-scanner/dashboard/app.py
import streamlit as st

st.set_page_config(
    page_title="FinBytes Labs",
    page_icon="📊",
    layout="wide",
)

# Sidebar — persistent across all pages
st.sidebar.title("FinBytes Labs")
st.sidebar.markdown("**Built by** [Manisha](https://mish-codes.github.io/FinBytes/)")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built with:** Python, FastAPI, SQLAlchemy, "
    "Docker, Claude API, Streamlit"
)
st.sidebar.markdown(
    "[GitHub Repo](https://github.com/mish-codes/QuantLab) · "
    "[Blog Post](https://mish-codes.github.io/FinBytes/quant-lab/stock-risk-scanner/)"
)

# Main landing page
st.title("Welcome to FinBytes Labs")
st.markdown(
    "Interactive demos of quantitative finance projects. "
    "Select a project from the sidebar to get started."
)

st.markdown("### Available Projects")
st.markdown("- **Stock Risk Scanner** — Enter stock tickers, see risk metrics, AI narrative, and interactive charts")
```

- [ ] **Step 5: Create empty __init__.py for lib**

```python
# projects/stock-risk-scanner/dashboard/lib/__init__.py
# (empty)
```

- [ ] **Step 6: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/
git commit -m "feat(dashboard): scaffold with config, landing page, directory structure"
```

---

### Task 2: API Client

**Files:**
- Create: `projects/stock-risk-scanner/dashboard/lib/api_client.py`

- [ ] **Step 1: Create api_client.py**

```python
# projects/stock-risk-scanner/dashboard/lib/api_client.py
import time
import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")


def check_health() -> bool:
    """Return True if the backend API is healthy."""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def submit_scan(tickers: list[str], weights: list[float], period: str) -> dict:
    """Submit a scan request. Returns {id, status} or raises."""
    resp = requests.post(
        f"{API_URL}/api/scan",
        json={"tickers": tickers, "weights": weights, "period": period},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def poll_scan(scan_id: int, max_wait: int = 120) -> dict:
    """Poll until scan completes or fails. Returns the scan dict."""
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{API_URL}/api/scans/{scan_id}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["status"] != "pending":
            return data
        time.sleep(2)
    raise TimeoutError(f"Scan {scan_id} did not complete within {max_wait}s")


def get_recent_scans(limit: int = 5) -> list[dict]:
    """Fetch recent completed scans."""
    try:
        resp = requests.get(
            f"{API_URL}/api/scans", params={"limit": limit}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/lib/api_client.py
git commit -m "feat(dashboard): API client for backend communication"
```

---

### Task 3: Risk Color Logic

**Files:**
- Create: `projects/stock-risk-scanner/dashboard/lib/risk_colors.py`

- [ ] **Step 1: Create risk_colors.py**

```python
# projects/stock-risk-scanner/dashboard/lib/risk_colors.py


def var_color(val: float) -> str:
    """Color for VaR (95%). More negative = worse."""
    if val < -3:
        return "🔴"
    elif val < -1.5:
        return "🟡"
    return "🟢"


def cvar_color(val: float) -> str:
    """Color for CVaR. More negative = worse."""
    if val < -4:
        return "🔴"
    elif val < -2:
        return "🟡"
    return "🟢"


def drawdown_color(val: float) -> str:
    """Color for Max Drawdown. More negative = worse."""
    if val < -20:
        return "🔴"
    elif val < -10:
        return "🟡"
    return "🟢"


def volatility_color(val: float) -> str:
    """Color for Volatility. Higher = worse."""
    if val > 30:
        return "🔴"
    elif val > 20:
        return "🟡"
    return "🟢"


def sharpe_color(val: float) -> str:
    """Color for Sharpe Ratio. Higher = better."""
    if val > 1:
        return "🟢"
    elif val > 0.5:
        return "🟡"
    return "🔴"
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/lib/risk_colors.py
git commit -m "feat(dashboard): risk metric color-coding logic"
```

---

### Task 4: Chart Builders

**Files:**
- Create: `projects/stock-risk-scanner/dashboard/lib/charts.py`

- [ ] **Step 1: Create charts.py**

```python
# projects/stock-risk-scanner/dashboard/lib/charts.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def price_history_chart(prices: pd.DataFrame) -> go.Figure:
    """Multi-line price chart, one colored line per ticker."""
    fig = go.Figure()
    for col in prices.columns:
        fig.add_trace(go.Scatter(
            x=prices.index, y=prices[col], mode="lines", name=col
        ))
    fig.update_layout(
        title="Price History",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def cumulative_return_chart(prices: pd.DataFrame, weights: list[float]) -> go.Figure:
    """Single line showing weighted portfolio cumulative return."""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    portfolio_returns = log_returns.values @ np.array(weights)
    cumulative = np.exp(np.cumsum(portfolio_returns))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices.index[1:],
        y=cumulative,
        mode="lines",
        name="Portfolio",
        line=dict(color="#2a7ae2", width=2),
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="Portfolio Cumulative Return",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (1.0 = start)",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def drawdown_chart(prices: pd.DataFrame, weights: list[float]) -> go.Figure:
    """Red filled area chart showing portfolio drawdown over time."""
    log_returns = np.log(prices / prices.shift(1)).dropna()
    portfolio_returns = log_returns.values @ np.array(weights)
    cumulative = np.exp(np.cumsum(portfolio_returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices.index[1:],
        y=drawdown,
        mode="lines",
        name="Drawdown",
        fill="tozeroy",
        line=dict(color="red", width=1),
        fillcolor="rgba(255, 0, 0, 0.2)",
    ))
    fig.update_layout(
        title="Portfolio Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def weight_pie_chart(tickers: list[str], weights: list[float]) -> go.Figure:
    """Pie chart showing portfolio allocation."""
    fig = go.Figure(data=[go.Pie(
        labels=tickers,
        values=[w * 100 for w in weights],
        textinfo="label+percent",
        hole=0.3,
    )])
    fig.update_layout(
        title="Portfolio Allocation",
        template="plotly_white",
        showlegend=False,
    )
    return fig
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/lib/charts.py
git commit -m "feat(dashboard): Plotly chart builders — price, cumulative, drawdown, pie"
```

---

### Task 5: Scanner Page — Input Section

**Files:**
- Create: `projects/stock-risk-scanner/dashboard/pages/1_Stock_Risk_Scanner.py`

- [ ] **Step 1: Create scanner page with input section**

```python
# projects/stock-risk-scanner/dashboard/pages/1_Stock_Risk_Scanner.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

from lib.api_client import check_health, submit_scan, poll_scan, get_recent_scans
from lib.charts import price_history_chart, cumulative_return_chart, drawdown_chart, weight_pie_chart
from lib.risk_colors import var_color, cvar_color, drawdown_color, volatility_color, sharpe_color

st.set_page_config(page_title="Stock Risk Scanner", page_icon="📊", layout="wide")

# --- Backend status in sidebar ---
if check_health():
    st.sidebar.success("Backend: Online")
else:
    st.sidebar.warning("Backend: Warming up...")

# --- Rate limiting ---
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0
    st.session_state.scan_reset_time = datetime.now()

def _check_rate_limit() -> bool:
    elapsed = (datetime.now() - st.session_state.scan_reset_time).total_seconds()
    if elapsed > 3600:
        st.session_state.scan_count = 0
        st.session_state.scan_reset_time = datetime.now()
    return st.session_state.scan_count < 10

# --- Title ---
st.title("Stock Risk Scanner")
st.markdown("Enter stock tickers and portfolio weights to analyse risk metrics with AI-powered commentary.")

# --- Preset buttons ---
PRESETS = {
    "Tech Giants": (["AAPL", "MSFT", "GOOG"], "Tech heavyweights"),
    "Safe Haven": (["JNJ", "PG", "KO"], "Defensive consumer stocks"),
    "Balanced": (["AAPL", "JNJ", "BND"], "Growth + defense + bonds"),
}

st.markdown("#### Quick Presets")
preset_cols = st.columns(len(PRESETS))
for i, (name, (tickers, desc)) in enumerate(PRESETS.items()):
    with preset_cols[i]:
        if st.button(f"{name}", help=desc, use_container_width=True):
            st.session_state.tickers_input = ", ".join(tickers)
            st.session_state.use_equal_weights = True

# --- Custom input ---
st.markdown("#### Custom Portfolio")

tickers_input = st.text_input(
    "Tickers (comma-separated, max 5)",
    value=st.session_state.get("tickers_input", "AAPL, MSFT, GOOG"),
    key="tickers_field",
)

period = st.radio("Period", ["6mo", "1y", "2y"], index=1, horizontal=True)

# Parse tickers
raw_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = raw_tickers[:5]

if len(raw_tickers) > 5:
    st.warning("Maximum 5 tickers allowed. Using first 5.")

# Weight sliders
st.markdown("#### Portfolio Weights")

equal_weight = st.button("Equal Weight")
if equal_weight or st.session_state.get("use_equal_weights"):
    st.session_state.use_equal_weights = False
    for i, t in enumerate(tickers):
        st.session_state[f"weight_{i}"] = 100.0 / len(tickers)

weights = []
weight_cols = st.columns(len(tickers)) if tickers else []
for i, t in enumerate(tickers):
    with weight_cols[i]:
        w = st.slider(
            f"{t}",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.get(f"weight_{i}", 100.0 / max(len(tickers), 1)),
            step=1.0,
            key=f"weight_slider_{i}",
        )
        weights.append(w)

weight_sum = sum(weights)
if tickers and abs(weight_sum - 100.0) > 1.0:
    st.error(f"Weights must sum to 100% (currently {weight_sum:.0f}%)")
    can_scan = False
elif not tickers:
    can_scan = False
else:
    can_scan = True

# Normalize weights to 0-1
norm_weights = [w / 100.0 for w in weights] if weight_sum > 0 else []

# --- Scan button ---
if st.button("Scan", type="primary", disabled=not can_scan, use_container_width=True):
    if not _check_rate_limit():
        st.error("Rate limit reached — max 10 scans per hour. Try again later.")
    else:
        st.session_state.scan_count += 1

        # Validate tickers
        with st.spinner("Validating tickers..."):
            invalid = []
            for t in tickers:
                try:
                    info = yf.Ticker(t).info
                    if not info or info.get("regularMarketPrice") is None:
                        invalid.append(t)
                except Exception:
                    invalid.append(t)

            if invalid:
                st.error(f"Ticker(s) not found: {', '.join(invalid)} — check the symbols and try again.")
                st.stop()

        # Submit scan
        try:
            with st.status("Running scan...", expanded=True) as status:
                st.write("Submitting scan request...")
                result = submit_scan(tickers, norm_weights, period)
                scan_id = result["id"]

                st.write("Fetching market data & calculating risk...")
                scan_data = poll_scan(scan_id)

                if scan_data["status"] == "failed":
                    status.update(label="Scan failed", state="error")
                    st.error(f"Scan failed: {scan_data.get('error_message', 'Unknown error')}")
                    st.stop()

                st.write("Fetching chart data...")
                prices = yf.download(tickers, period=period, auto_adjust=True, progress=False)
                if isinstance(prices.columns, pd.MultiIndex):
                    prices = prices["Close"]
                else:
                    prices = prices[["Close"]].rename(columns={"Close": tickers[0]})
                prices = prices.dropna(how="all").ffill()

                status.update(label="Scan complete!", state="complete")

            # Store results in session state for display
            st.session_state.scan_result = scan_data
            st.session_state.scan_prices = prices
            st.session_state.scan_tickers = tickers
            st.session_state.scan_weights = norm_weights

        except requests.exceptions.ConnectionError:
            st.error("Backend is offline — please try again later.")
        except TimeoutError:
            st.error("The scan is taking longer than expected — the backend may be waking up. Try again in a minute.")
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# --- Display results if available ---
if "scan_result" in st.session_state:
    data = st.session_state.scan_result
    prices = st.session_state.scan_prices
    tickers = st.session_state.scan_tickers
    weights = st.session_state.scan_weights

    st.markdown("---")
    st.markdown("## Results")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(f"{var_color(data['var_pct'])} VaR (95%)", f"{data['var_pct']:.2f}%")
    with m2:
        st.metric(f"{cvar_color(data['cvar_pct'])} CVaR", f"{data['cvar_pct']:.2f}%")
    with m3:
        st.metric(f"{drawdown_color(data['max_drawdown_pct'])} Max Drawdown", f"{data['max_drawdown_pct']:.2f}%")
    with m4:
        st.metric(f"{volatility_color(data['volatility_pct'])} Volatility", f"{data['volatility_pct']:.2f}%")
    with m5:
        st.metric(f"{sharpe_color(data['sharpe_ratio'])} Sharpe", f"{data['sharpe_ratio']:.2f}")

    # Narrative
    st.markdown("### AI Risk Narrative")
    st.info(data.get("narrative", "No narrative available."))

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(price_history_chart(prices), use_container_width=True)
    with chart_col2:
        st.plotly_chart(cumulative_return_chart(prices, weights), use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.plotly_chart(drawdown_chart(prices, weights), use_container_width=True)
    with chart_col4:
        st.plotly_chart(weight_pie_chart(tickers, weights), use_container_width=True)

# --- Scan History ---
st.markdown("---")
with st.expander("Recent Scans"):
    history = get_recent_scans(limit=5)
    if history:
        for scan in history:
            tks = ", ".join(scan["tickers"]) if isinstance(scan["tickers"], list) else scan["tickers"]
            st.markdown(
                f"**{tks}** — VaR: {scan.get('var_pct', 'N/A')}%, "
                f"Sharpe: {scan.get('sharpe_ratio', 'N/A')} — "
                f"_{scan.get('created_at', '')[:10]}_"
            )
    else:
        st.markdown("No recent scans available.")
```

- [ ] **Step 2: Test locally**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner/dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open browser, verify landing page loads, click "Stock Risk Scanner" in sidebar, verify input section renders. (Backend won't work locally without API running — that's OK for now.)

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/
git commit -m "feat(dashboard): Stock Risk Scanner page with input, results, charts"
```

---

### Task 6: Sample Output on Load

**Files:**
- Modify: `projects/stock-risk-scanner/dashboard/pages/1_Stock_Risk_Scanner.py`

- [ ] **Step 1: Add precomputed sample data**

Add this near the top of the file, after imports but before the title:

```python
# Precomputed sample result for instant display on first load
SAMPLE_RESULT = {
    "id": 0,
    "tickers": ["AAPL", "MSFT", "GOOG"],
    "weights": [0.333, 0.333, 0.334],
    "period": "1y",
    "status": "complete",
    "var_pct": -2.14,
    "cvar_pct": -3.19,
    "max_drawdown_pct": -19.37,
    "volatility_pct": 23.89,
    "sharpe_ratio": 0.61,
    "narrative": "Portfolio AAPL, MSFT, GOOG: VaR -2.14%, CVaR -3.19%, Max Drawdown -19.37%, Volatility 23.89%, Sharpe 0.61. This is a moderately volatile tech-heavy portfolio with acceptable risk-adjusted returns.",
    "error_message": None,
}
```

Then, right before the `# --- Display results if available ---` section, add:

```python
# Load sample data on first visit
if "scan_result" not in st.session_state:
    st.info("Here's a sample scan of Tech Giants (AAPL, MSFT, GOOG). Try your own portfolio above!")
    st.session_state.scan_result = SAMPLE_RESULT
    st.session_state.scan_tickers = SAMPLE_RESULT["tickers"]
    st.session_state.scan_weights = SAMPLE_RESULT["weights"]
    try:
        sample_prices = yf.download(
            SAMPLE_RESULT["tickers"], period="1y", auto_adjust=True, progress=False
        )
        if isinstance(sample_prices.columns, pd.MultiIndex):
            sample_prices = sample_prices["Close"]
        sample_prices = sample_prices.dropna(how="all").ffill()
        st.session_state.scan_prices = sample_prices
    except Exception:
        pass  # Charts won't show, but metrics + narrative still will
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/dashboard/pages/1_Stock_Risk_Scanner.py
git commit -m "feat(dashboard): sample output on first load"
```

---

### Task 7: Backend Deployment to Render

This task is manual — done through the Render web UI, not code.

- [ ] **Step 1: Create Render account at render.com**

- [ ] **Step 2: Create a PostgreSQL database**
  - Name: `finbytes-scanner-db`
  - Plan: Free
  - Note the internal database URL

- [ ] **Step 3: Create a Web Service**
  - Connect to GitHub repo `mish-codes/QuantLab`
  - Name: `finbytes-scanner`
  - Root directory: `projects/stock-risk-scanner`
  - Runtime: Docker
  - Set environment variables:
    - `DATABASE_URL` = the internal PostgreSQL URL from step 2 (use the asyncpg format: replace `postgres://` with `postgresql+asyncpg://`)
    - `ANTHROPIC_API_KEY` = your API key (or `skip` for fallback mode)
  - Deploy

- [ ] **Step 4: Run Alembic migration**

After the service deploys, open the Render shell and run:
```bash
alembic upgrade head
```

- [ ] **Step 5: Verify API is live**

```bash
curl https://finbytes-scanner.onrender.com/health
```

Expected: `{"status": "ok"}`

---

### Task 8: Streamlit Cloud Deployment

This task is manual — done through the Streamlit Cloud web UI.

- [ ] **Step 1: Go to share.streamlit.io and sign in with GitHub**

- [ ] **Step 2: Deploy new app**
  - Repository: `mish-codes/QuantLab`
  - Branch: `master`
  - Main file path: `projects/stock-risk-scanner/dashboard/app.py`
  - App URL: `finbytes.streamlit.app`

- [ ] **Step 3: Set secrets**

In the Streamlit Cloud app settings, add secrets:
```toml
API_URL = "https://finbytes-scanner.onrender.com"
```

- [ ] **Step 4: Verify dashboard is live**

Open `https://finbytes.streamlit.app`, verify:
1. Landing page loads
2. Stock Risk Scanner page shows in sidebar
3. Sample data displays on first load
4. Preset buttons fill input
5. Custom scan works (may take 30-60s on first call due to Render cold start)

---

### Task 9: Blog Embed (Part B)

**Files:**
- Modify: `C:/codebase/finbytes_git/docs/_quant_lab/stock-risk-scanner.html`

- [ ] **Step 1: Add "Try Live Demo" section to the capstone blog post**

Add this at the very top of the `tab-run` div content, before the prerequisites:

```html
<h2>Live Demo</h2>
<p>Try the scanner right now — no installation needed:</p>
<p><a href="https://finbytes.streamlit.app/Stock_Risk_Scanner" target="_blank" style="display:inline-block;padding:10px 24px;background:#2a7ae2;color:white;border-radius:4px;text-decoration:none;font-weight:600;">Launch Live Demo</a></p>
<p>Or try it embedded below:</p>
<iframe src="https://finbytes.streamlit.app/Stock_Risk_Scanner?embedded=true" width="100%" height="800" style="border:1px solid #e8e8e8;border-radius:4px;"></iframe>
<hr/>
```

- [ ] **Step 2: Commit and push**

```bash
cd C:/codebase/finbytes_git
git add docs/_quant_lab/stock-risk-scanner.html
git commit -m "feat: embed live Streamlit demo in capstone blog post"
git push
```

- [ ] **Step 3: Create PR and merge**

---

### Task 10: Final PR for Dashboard Code

- [ ] **Step 1: Push and create PR for quant_lab**

```bash
cd C:/codebase/quant_lab
git push -u origin working
gh pr create --title "feat(dashboard): Streamlit dashboard for stock risk scanner" --body "..."
```

- [ ] **Step 2: Merge, sync branches**
