# Stock Risk Scanner Dashboard — Design Spec

**Date:** 2026-04-03
**Project:** `projects/stock-risk-scanner/dashboard/`
**Concept:** Interactive Streamlit web dashboard for the stock risk scanner. Users enter tickers (or pick presets), run risk scans via the FastAPI backend, and see results with metrics, AI narrative, and interactive Plotly charts.

---

## Architecture

- **Frontend:** Streamlit app hosted on Streamlit Community Cloud (deploys from GitHub)
- **Backend:** Existing FastAPI scanner API hosted on Render free tier (with PostgreSQL)
- **Charts:** Streamlit fetches price data directly via yfinance (no API change needed)
- **Communication:** Dashboard calls the Render-hosted API for scans, calls yfinance directly for chart data

---

## Page Layout

### Sidebar

- App title / logo
- Your name + link to FinBytes blog
- "Built with" tech stack list (Python, FastAPI, SQLAlchemy, Docker, Claude API, Streamlit)
- Link to GitHub repo
- Link to capstone blog post

### Main Area — Input Section

**Preset portfolio buttons (3):**

| Preset | Tickers | Weights |
|--------|---------|---------|
| Tech Giants | AAPL, MSFT, GOOG | Equal |
| Safe Haven | JNJ, PG, KO | Equal |
| Balanced | AAPL, JNJ, BND | Equal |

Clicking a preset fills the ticker input and sets equal weights.

**Custom input:**
- Ticker input: free-form text, comma-separated, max 5 tickers
- Validation: verify tickers exist via yfinance before scanning
- Weight sliders: one per ticker, auto-generated, must sum to 100%
- "Equal Weight" button: sets all sliders to equal
- Period selector: 6mo, 1y, 2y (radio buttons)
- "Scan" button

### Main Area — Loading State

Progress indicators showing pipeline steps:
1. "Fetching market data..."
2. "Calculating risk..."
3. "Generating narrative..."

### Main Area — Results (after scan completes)

**Metrics row:** 5 `st.metric` cards with color-coded deltas

| Metric | Color logic |
|--------|------------|
| VaR (95%) | Red if < -3%, amber if < -1.5%, green otherwise |
| CVaR | Red if < -4%, amber if < -2%, green otherwise |
| Max Drawdown | Red if < -20%, amber if < -10%, green otherwise |
| Volatility | Red if > 30%, amber if > 20%, green otherwise |
| Sharpe Ratio | Green if > 1, amber if > 0.5, red otherwise |

**AI Narrative:** Text block with Claude-generated narrative (or fallback summary).

**Charts (3, Plotly interactive):**

1. **Price History** — multi-line chart, one colored line per ticker, shared x-axis (dates), y-axis (price). Each ticker has a distinct color.
2. **Portfolio Cumulative Return** — single line chart showing weighted portfolio value over time (starting at 1.0).
3. **Drawdown** — red filled area chart showing peak-to-trough decline over time.

**Portfolio Weight Pie Chart:** Simple pie chart showing the allocation.

**Scan History:** Collapsible section (`st.expander`) showing last 5 scans from `GET /api/scans`. Each entry shows tickers, date, key metrics.

---

## Backend Integration

The dashboard calls the Render-hosted API:

| Action | API Call | Notes |
|--------|----------|-------|
| Submit scan | `POST /api/scan` | Returns `{id, status: "pending"}` |
| Poll result | `GET /api/scans/{id}` | Poll every 2 seconds until status != "pending" |
| Scan history | `GET /api/scans` | Last 5 completed scans |
| Health check | `GET /health` | Show backend status in sidebar |

**API base URL** read from environment variable `API_URL` (configured in Streamlit Cloud secrets).

**Cold start handling:** Render free tier sleeps after 15min idle. First request may take 30-60 seconds. Show a "Backend is waking up, this may take a moment..." message if health check fails initially.

---

## Chart Data

Charts are generated client-side in Streamlit — **no API change needed**.

After a successful scan:
1. Streamlit calls `yfinance.download(tickers, period=period)` directly
2. Computes weighted portfolio returns + cumulative return + drawdown locally
3. Renders Plotly charts

This avoids adding price-data endpoints to the API and keeps chart rendering fast (no round-trip to Render).

---

## Files

```
projects/stock-risk-scanner/dashboard/
├── app.py                    # Streamlit application
├── requirements.txt          # Dependencies for Streamlit Cloud
└── .streamlit/
    └── config.toml           # Theme configuration
```

### requirements.txt

```
streamlit>=1.30.0
plotly>=5.18.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.26.0
requests>=2.31.0
```

### .streamlit/config.toml

```toml
[theme]
primaryColor = "#2a7ae2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

---

## Ticker Validation

Before submitting a scan:
1. Split input by commas, strip whitespace, uppercase
2. Check count <= 5
3. For each ticker, call `yfinance.Ticker(t).info` — if it raises or returns empty, show error
4. Only enable "Scan" button when all tickers are valid and weights sum to 100%

---

## Render Deployment (Backend)

The existing `projects/stock-risk-scanner/` Docker setup deploys directly to Render:
- Create a Web Service from the GitHub repo
- Set root directory to `projects/stock-risk-scanner`
- Render auto-detects Dockerfile
- Set environment variables: `DATABASE_URL`, `ANTHROPIC_API_KEY`
- Add a Render PostgreSQL database (free tier, 90 days)

---

## Streamlit Cloud Deployment (Frontend)

- Connect GitHub repo to Streamlit Community Cloud
- Set app file path: `projects/stock-risk-scanner/dashboard/app.py`
- Set secrets: `API_URL = https://your-render-app.onrender.com`

---

## UX Polish

### Rate Limiting
Max 10 scans per hour per session. Tracked via `st.session_state` counter with timestamp. Show "Rate limit reached — try again in X minutes" when exceeded.

### Caching
Cache scan results for 24 hours using `st.cache_data`. Key on (tickers, weights, period). Avoids redundant API calls and yfinance fetches for the same portfolio.

### Error UX
Friendly messages for all failure modes:
- Invalid ticker: "Ticker XYZ not found — check the symbol and try again"
- API timeout: "The scan is taking longer than expected — the backend may be waking up"
- yfinance down: "Unable to fetch market data — please try again in a few minutes"
- API unreachable: "Backend is offline — please try again later"

No raw Python tracebacks shown to the user.

### Mobile Responsive
Use `st.set_page_config(layout="wide")`. Metrics cards and charts stack vertically on small screens (Streamlit handles this by default). Test that the layout is usable on phone-sized viewports.

### Sample Output on Load
Pre-load the "Tech Giants" (AAPL, MSFT, GOOG) scan result on first visit so the page isn't empty. Show results immediately with a "Try your own portfolio" prompt above the input section. Use cached/precomputed data for instant load.

### Backend Status Indicator
Green/red dot in sidebar showing API health status. On page load, call `GET /health`. If it fails, show "Backend warming up..." with a spinner. Retry every 5 seconds until healthy.

### Page Config
```python
st.set_page_config(
    page_title="Stock Risk Scanner",
    page_icon="📊",
    layout="wide",
)
```

---

## Out of Scope

- User authentication
- Compare mode (side-by-side scans)
- Candlestick charts
- Real-time streaming / WebSocket updates
- Return distribution histogram
- Export/download results
