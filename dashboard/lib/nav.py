"""Shared sidebar navigation for all dashboard pages."""

from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"


_GLOBAL_STYLES = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
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

/* Featured grid */
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

/* Categorised grid */
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

/* Stats bar under hero */
.ql-stats-bar {
    text-align: center;
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace;
    font-size: 0.78rem;
    color: var(--ql-muted);
    letter-spacing: 0.04em;
    margin: -2.5rem 0 3rem;
}

/* Search box wrapper */
.ql-search-wrap {
    max-width: 480px;
    margin: 0 auto 2rem;
}
.ql-search-wrap input[type="text"] {
    font-family: var(--ql-font-body) !important;
    border-color: var(--ql-border) !important;
    background: var(--ql-bg) !important;
    color: var(--ql-text) !important;
}
.ql-search-wrap label { display: none !important; }

/* Project graph container */
.ql-graph-container {
    background: var(--ql-bg2);
    border: 1px solid var(--ql-border);
    border-radius: 6px;
    padding: 0.5rem;
    margin-bottom: 3rem;
}

/* Smaller, greyer text inside expanders */
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
    st.sidebar.markdown(
        '<div class="ql-sidebar-brand">'
        '<div class="ql-sidebar-title">QuantLab</div>'
        '<div class="ql-sidebar-byline">Built by '
        '<a href="https://mish-codes.github.io/FinBytes/">Manisha</a>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
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
