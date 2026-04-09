# Frontend Test Suite Design

## Goal
Add comprehensive AppTest-based frontend tests for all 25 Streamlit pages, with test results visible on each page via a "Tests" tab.

## Architecture

### Test Files
One test file per page in `dashboard/tests/`:

| File | Page |
|------|------|
| `test_app.py` | Landing page (existing) |
| `test_stock_risk_scanner.py` | 1_Stock_Risk_Scanner |
| `test_credit_card_calculator.py` | 10_Credit_Card_Calculator |
| `test_loan_amortization.py` | 11_Loan_Amortization |
| `test_loan_comparison.py` | 12_Loan_Comparison |
| `test_retirement_calculator.py` | 13_Retirement_Calculator |
| `test_investment_planner.py` | 14_Investment_Planner |
| `test_budget_tracker.py` | 15_Budget_Tracker |
| `test_currency_dashboard.py` | 20_Currency_Dashboard |
| `test_stock_tracker.py` | 21_Stock_Tracker |
| `test_stock_analysis.py` | 22_Stock_Analysis |
| `test_crypto_portfolio.py` | 23_Crypto_Portfolio |
| `test_personal_finance.py` | 24_Personal_Finance |
| `test_esg_tracker.py` | 25_ESG_Tracker |
| `test_financial_reporting.py` | 26_Financial_Reporting |
| `test_var_cvar.py` | 30_VaR_CVaR |
| `test_time_series.py` | 31_Time_Series |
| `test_sentiment_analysis.py` | 32_Sentiment_Analysis |
| `test_anomaly_detection.py` | 33_Anomaly_Detection |
| `test_loan_default.py` | 34_Loan_Default |
| `test_clustering.py` | 35_Clustering |
| `test_portfolio_optimization.py` | 36_Portfolio_Optimization |
| `test_algo_trading.py` | 37_Algo_Trading |
| `test_stock_prediction.py` | 38_Stock_Prediction |
| `test_market_insights.py` | 39_Market_Insights |
| `test_admin.py` | 99_Admin |

### Test Pattern (per file)
Each test file contains a test class with:
1. **Smoke test** -- page loads without `at.exception`
2. **Title test** -- correct title string appears
3. **Widget tests** -- expected inputs, buttons, tabs, selectors are present
4. **Edge case tests** -- empty data, missing inputs, error states handled gracefully

### conftest.py (shared fixtures)
Provides pytest fixtures that mock all external dependencies:
- `mock_yfinance` -- patches `yfinance.download` to return a fake OHLCV DataFrame with realistic price data
- `mock_coingecko` -- patches `requests.get` for CoinGecko URLs, returns fake crypto prices
- `mock_exchange_rates` -- patches `requests.get` for exchange rate API, returns fake FX rates
- `mock_vader` -- patches `vaderSentiment` to return deterministic scores
- `mock_textblob` -- patches `textblob.TextBlob` to return deterministic polarity
- `mock_empty_data` -- variant that returns empty DataFrames for testing error states
- `sample_ohlcv_df` -- a reusable fake OHLCV DataFrame (AAPL-like, 252 rows)

### CI Results Export
- Add `pytest-json-report` to dev dependencies
- CI command: `pytest dashboard/tests/ --json-report --json-report-file=dashboard/test_results.json`
- JSON structure keyed by test file so each page can look up its results
- `.github/workflows/test.yml` updated to generate this file and upload as artifact
- A scheduled or post-CI step commits `test_results.json` back to the repo so the deployed app can read it

### "Tests" Tab on Each Page
- New shared helper: `dashboard/lib/test_tab.py`
  - Function: `render_test_tab(page_file: str)` -- reads `test_results.json`, filters to the matching test file, renders results
  - Display: test name, pass/fail icon, duration, error message (if failed)
  - Graceful fallback: if `test_results.json` missing, shows "No test results available"
- Each page adds one tab to its layout and calls `render_test_tab("test_<page_name>.py")`

### Bug Fixes
1. **vaderSentiment missing from requirements.txt** -- added `vaderSentiment>=3.3.2`
2. **VaR page empty data** -- the page already handles empty returns with `st.error()` + `st.stop()`, but the test suite will verify this path works

## Dependencies
- `pytest` (existing)
- `pytest-json-report` (new, dev only)
- `vaderSentiment>=3.3.2` (new, production)

## Out of Scope
- Backend/API tests (only frontend AppTest)
- Live API integration tests
- Performance/load testing
