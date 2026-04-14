"""Shared sidebar navigation for all dashboard pages."""

from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"


_GLOBAL_STYLES = """
<style>
/* Smaller, greyer text inside expanders so explanatory content stays
   visually subordinate to headline numbers. Bold labels stay readable. */
[data-testid="stExpander"] details > div p,
[data-testid="stExpander"] details > div li,
[data-testid="stExpander"] details > div td,
[data-testid="stExpander"] details > div th {
    font-size: 0.86rem;
    color: var(--text-muted-color, #888);
}
[data-testid="stExpander"] details > div strong {
    color: var(--text-color, #555);
}
[data-testid="stExpander"] details > div table {
    font-size: 0.86rem;
}
</style>
"""


def render_sidebar():
    """Render the shared sidebar navigation. Call this at the top of every page.

    Also injects global CSS that applies to all dashboard pages — currently
    just the smaller/greyer expander-content styling.

    Wrapped in try/except because st.page_link fails in AppTest (testing mode).
    """
    try:
        st.markdown(_GLOBAL_STYLES, unsafe_allow_html=True)
    except Exception:
        pass
    try:
        _render_sidebar_impl()
    except Exception:
        pass  # graceful fallback in test mode


def _render_sidebar_impl():
    st.sidebar.image(str(ASSETS / "logo.png"), width=180)
    st.sidebar.title("FinBytes QuantLabs")
    st.sidebar.markdown("**Built by** [Manisha](https://mish-codes.github.io/FinBytes/)")
    st.sidebar.markdown("---")

    # Projects
    st.sidebar.markdown("### Projects")
    st.sidebar.page_link("pages/1_Stock_Risk_Scanner.py", label="Stock Risk Scanner")

    # Mini Projects — Calculators
    st.sidebar.markdown("### Mini Projects")
    st.sidebar.caption("Calculators")
    st.sidebar.page_link("pages/10_Credit_Card_Calculator.py", label="Credit Card Calculator")
    st.sidebar.page_link("pages/11_Loan_Amortization.py", label="Loan Amortization")
    st.sidebar.page_link("pages/12_Loan_Comparison.py", label="Loan Comparison")
    st.sidebar.page_link("pages/13_Retirement_Calculator.py", label="Retirement Calculator")
    st.sidebar.page_link("pages/14_Investment_Planner.py", label="Investment Planner")
    st.sidebar.page_link("pages/15_Budget_Tracker.py", label="Budget Tracker")
    st.sidebar.page_link("pages/16_Rent_vs_Buy.py", label="Rent vs Buy London")

    # Mini Projects — Dashboards
    st.sidebar.caption("Dashboards")
    st.sidebar.page_link("pages/20_Currency_Dashboard.py", label="Currency Dashboard")
    st.sidebar.page_link("pages/21_Stock_Tracker.py", label="Stock Tracker")
    st.sidebar.page_link("pages/22_Stock_Analysis.py", label="Stock Analysis")
    st.sidebar.page_link("pages/23_Crypto_Portfolio.py", label="Crypto Portfolio")
    st.sidebar.page_link("pages/24_Personal_Finance.py", label="Personal Finance")
    st.sidebar.page_link("pages/25_ESG_Tracker.py", label="ESG Tracker")
    st.sidebar.page_link("pages/26_Financial_Reporting.py", label="Financial Reporting")
    st.sidebar.page_link("pages/40_Benchmark_Rates.py", label="Benchmark Rates")
    st.sidebar.page_link("pages/41_Plotting_Libraries.py", label="Plotting Libraries")
    st.sidebar.page_link("pages/42_London_House_Prices.py", label="London House Prices")

    # Mini Projects — ML & Quant
    st.sidebar.caption("ML & Quantitative")
    st.sidebar.page_link("pages/30_VaR_CVaR.py", label="VaR & CVaR")
    st.sidebar.page_link("pages/31_Time_Series.py", label="Time Series")
    st.sidebar.page_link("pages/32_Sentiment_Analysis.py", label="Sentiment Analysis")
    st.sidebar.page_link("pages/33_Anomaly_Detection.py", label="Anomaly Detection")
    st.sidebar.page_link("pages/34_Loan_Default.py", label="Loan Default Prediction")
    st.sidebar.page_link("pages/35_Clustering.py", label="Customer Clustering")
    st.sidebar.page_link("pages/36_Portfolio_Optimization.py", label="Portfolio Optimization")
    st.sidebar.page_link("pages/37_Algo_Trading.py", label="Algo Trading Backtest")
    st.sidebar.page_link("pages/38_Stock_Prediction.py", label="Stock Prediction")
    st.sidebar.page_link("pages/39_Market_Insights.py", label="Market Insights")

    # Word Tools
    st.sidebar.caption("Word Tools")
    st.sidebar.page_link("pages/50_Etymology.py", label="Etymology")

    # Tech Understanding
    st.sidebar.caption("Tech Understanding")
    st.sidebar.page_link("pages/60_Big_O.py", label="Big O Notation")

    st.sidebar.markdown("---")
    st.sidebar.page_link("app.py", label="System Health")
    st.sidebar.markdown(
        "[GitHub](https://github.com/mish-codes/QuantLab) · "
        "[Blog](https://mish-codes.github.io/FinBytes/)"
    )
