# FinBytes Finance Tools — Design Spec

**Date:** 2026-04-08
**Purpose:** Rewrite 23 old blog posts as concise references, rewrite accompanying Python code, and add each as an interactive Streamlit page in the existing QuantLab dashboard at finbytes.streamlit.app.
**Audience:** Personal learning reference + interactive portfolio showcase.

---

## Architecture

### Three deliverables per topic
1. **Blog post** (FinBytes `docs/_posts/`) — concise, pattern→code style, replaces old WordPress-imported post
2. **Python module** (QuantLab `dashboard/lib/`) — clean, tested, importable. All code lives in QuantLab, not FinBytes.
3. **Streamlit page** (QuantLab `dashboard/pages/`) — interactive UI with user inputs, charts, outputs

### Code migration
Old Python files in FinBytes repo (CreditCardRepaymentCalculator/, CryptoPortfolioAnalysis_APIs/, Clustering/, etc.) are deleted after their functionality is rewritten in QuantLab. FinBytes becomes a pure blog — no Python code.

### Streamlit app structure
Pages added to existing dashboard at `c:\codebase\quant_lab\dashboard\pages\`.
Current pages: `1_Stock_Risk_Scanner.py`, `99_Admin.py`.
New pages use numbered prefixes for grouping and sort order.

### Data sources
Free APIs only — no API keys required:
- **yfinance** — stock prices, historical data
- **FRED via fredapi** — interest rates, economic data (uses existing FRED key in env)
- **CoinGecko free tier** — crypto prices
- **Exchange rates** — exchangerate-api.com or similar free endpoint
- **Sample/synthetic data** — for ML training datasets

### ML stack
Scikit-learn only. No deep learning. Models train on-demand in Streamlit (small datasets).

---

## Batch 1: Calculators (6 pages)

Simple input→compute→display. No external APIs. Pure math + Plotly charts.

| # | Page file | Topic | Inputs | Outputs |
|---|-----------|-------|--------|---------|
| 1 | `10_Credit_Card_Calculator.py` | Credit card debt payoff | Balance, APR, monthly payment | Months to payoff, total interest, amortization chart |
| 2 | `11_Loan_Amortization.py` | Loan amortization schedule | Principal, rate, term, frequency | Payment schedule table, principal vs interest stacked chart |
| 3 | `12_Loan_Comparison.py` | Compare loan repayment options | Principal, rate, term for 2-3 loans | Side-by-side table, total cost bar chart |
| 4 | `13_Retirement_Calculator.py` | Retirement savings projection | Current age/savings, monthly contribution, return rate, target age | Growth curve, Monte Carlo fan chart (random returns), "will you make it?" verdict |
| 5 | `14_Investment_Planner.py` | Investment planner | Lump sum, monthly add, rate, years | Growth chart, compound interest breakdown, what-if slider |
| 6 | `15_Budget_Tracker.py` | Personal budget tracker | Income, expense categories (editable table) | Pie chart of spending, surplus/deficit, category breakdown |

### Blog posts (Batch 1)
Delete the 6 old posts, write 6 new concise references with the same pattern→code style.
Each post: ~150-200 lines, includes the core calculation function + a Plotly chart example.

### Old posts to delete (Batch 1)
- `2023-04-14-calculate-monthly-payments-for-credit-card-debt-with-python.html`
- `2023-03-25-mastering-loan-amortization-schedules-in-python-empowering-fintech-with-efficient-calculation-methods.html`
- `2023-04-09-automate-and-compare-loan-repayment-calculations-using-python.html`
- `2023-04-11-build-your-own-retirement-calculator-in-python.html`
- `2023-04-15-build-your-investment-planner-with-python-today.html`
- `2023-03-23-build-a-budget-tracker-with-python-a-step-by-step-guide.html`

---

## Batch 2: Data-Driven Dashboards (7 pages)

Fetch real data from free APIs. Display with Plotly. User picks tickers/parameters.

| # | Page file | Topic | Data source | Key features |
|---|-----------|-------|-------------|--------------|
| 7 | `20_Currency_Dashboard.py` | Live currency rates | exchangerate-api (free) | Currency converter, historical chart, rate matrix |
| 8 | `21_Stock_Tracker.py` | Real-time stock prices | yfinance | Ticker search, candlestick chart, volume, 52-week range |
| 9 | `22_Stock_Analysis.py` | Technical stock analysis | yfinance | Moving averages, RSI, MACD, Bollinger bands — toggle each |
| 10 | `23_Crypto_Portfolio.py` | Crypto portfolio tracker | CoinGecko free | Enter holdings, live valuation, allocation pie, 24h change |
| 11 | `24_Personal_Finance.py` | Personal finance dashboard | User input + sample data | Net worth tracker, savings rate, expense trends |
| 12 | `25_ESG_Tracker.py` | ESG score comparison | Sample dataset (no free ESG API) | Company comparison radar chart, sector averages |
| 13 | `26_Financial_Reporting.py` | Automated financial reports | yfinance + user upload (CSV) | Summary stats, charts auto-generated, downloadable PDF/CSV |

### Blog posts (Batch 2)
Delete 7 old posts, write 7 new concise references.

### Old posts to delete (Batch 2)
- `2023-04-12-build-a-currency-dashboard-using-python.html`
- `2023-03-31-build-a-real-time-stock-price-tracker-with-python.html`
- `2023-04-07-automate-stock-analysis-with-python-libraries.html`
- `2023-04-10-automate-crypto-portfolio-management-using-python.html`
- `2023-04-16-designing-a-personal-finance-dashboard-with-python.html`
- `2023-04-13-esg-score-tracking-capabilities-with-python-in-fintech.html`
- `2023-04-03-streamlining-financial-data-reporting-how-python-automates-tasks-in-fintech.html`

---

## Batch 3: ML / Quantitative (10 pages)

Scikit-learn models, financial algorithms, interactive parameter tuning.

| # | Page file | Topic | Model/Algorithm | Key features |
|---|-----------|-------|-----------------|--------------|
| 14 | `30_VaR_CVaR.py` | VaR & CVaR calculator | Historical + parametric | Ticker input, confidence slider, histogram with VaR/CVaR lines |
| 15 | `31_Time_Series.py` | Time series analysis | Decomposition, autocorrelation | Trend/seasonal/residual decomposition chart, ACF/PACF plots |
| 16 | `32_Sentiment_Analysis.py` | Market sentiment | TextBlob/VADER | Enter headlines or fetch from sample, sentiment scores, word cloud |
| 17 | `33_Anomaly_Detection.py` | Financial anomaly detection | Isolation Forest, Z-score | Upload or sample data, flagged anomalies highlighted on chart |
| 18 | `34_Loan_Default.py` | Loan default prediction | Logistic Regression, Random Forest | Feature inputs (income, credit score, etc.), prediction + probability, feature importance chart |
| 19 | `35_Clustering.py` | Customer clustering | K-Means, DBSCAN | Sample customer data, elbow chart, cluster scatter plot, cluster profiles |
| 20 | `36_Portfolio_Optimization.py` | Portfolio optimization | Efficient frontier (scipy) | Enter tickers, compute frontier, plot risk/return, optimal weights |
| 21 | `37_Algo_Trading.py` | Algo trading backtest | Moving avg crossover, momentum | Ticker + strategy params, backtest equity curve, trade log, Sharpe |
| 22 | `38_Stock_Prediction.py` | Stock price prediction | Linear regression, Random Forest | Train/test split viz, prediction chart, metrics (MAE, RMSE) |
| 23 | `39_Market_Insights.py` | Market sentiment dashboard | VADER + yfinance | Combine price data with sentiment scores, correlation chart |

### Blog posts (Batch 3)
Delete 10 old posts, write 10 new concise references.

### Old posts to delete (Batch 3)
- `2023-03-30-mastering-risk-metrics-in-python-a-guide-to-var-and-conditional-var.html`
- `2023-03-29-mastering-time-series-analysis-in-finance-with-python.html`
- `2023-03-27-unlocking-market-insights-with-python-sentiment-analysis.html`
- `2023-04-02-mastering-anomaly-detection-in-finance-with-python-techniques.html`
- `2023-04-06-machine-learning-in-fintech-loan-default-prediction.html`
- `2023-04-05-clustering-techniques-for-fintech-enhancing-customer-insight.html`
- `2023-04-04-python-power-a-comprehensive-guide-to-enhancing-investment-portfolios-in-fintech.html`
- `2023-04-01-mastering-fintech-unleashing-the-power-of-python-in-algorithmic-trading-strategies-with-moving-averages-and-momentum.html`
- `2023-03-28-predicting-stock-prices-with-machine-learning-in-python.html`
- `2023-04-08-track-personal-expenses-with-python-a-comprehensive-guide.html`

---

## Streamlit Page Template

Every page follows the same structure:

```python
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Tool Name", page_icon="💰")
st.title("💰 Tool Name")
st.caption("One-line description")

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Parameters")
    param1 = st.number_input("Label", value=default)
    param2 = st.slider("Label", min, max, default)

# --- Compute ---
result = compute_function(param1, param2)

# --- Display ---
col1, col2 = st.columns(2)
col1.metric("Result 1", f"${result.value:,.2f}")
col2.metric("Result 2", f"{result.pct:.1f}%")

fig = px.line(result.df, x="date", y="value", title="Chart Title")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(result.table)
```

### Shared utilities
Common functions go in `dashboard/lib/`:
- `finance.py` — compound interest, amortization, VaR/CVaR calculations
- `data.py` — yfinance wrappers, CoinGecko fetcher, sample data loaders
- `charts.py` — reusable Plotly chart builders (candlestick, pie, histogram)

---

## Requirements updates

### QuantLab dashboard `requirements.txt`
Add to existing:
```
plotly>=5.0
scikit-learn>=1.4
textblob>=0.18
statsmodels>=0.14
```

### FinBytes repo
No new dependencies — blog posts are static HTML.

---

## Implementation order

**Batch 1 first** (Calculators) — simplest, establishes the page template pattern.
**Batch 2 second** (Dashboards) — adds API integration.
**Batch 3 third** (ML/Quant) — heaviest, uses patterns from 1 and 2.

Each batch: delete old posts → write new posts → write Streamlit pages → test → commit → PR.

---

## Out of scope
- No user authentication or data persistence (pages are stateless)
- No custom CSS theming for Streamlit (use defaults)
- No automated tests for Streamlit pages (test the underlying functions, not the UI)
- The existing Stock Risk Scanner and Admin pages are not modified
- No mobile-specific optimization (Streamlit handles basic responsiveness)
