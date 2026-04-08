from pathlib import Path
import streamlit as st
import requests

HERE = Path(__file__).parent
GITHUB_REPO = "MishCodesFinBytes/QuantLab"

st.set_page_config(
    page_title="FinBytes QuantLabs",
    layout="wide",
)

# ============================================================
# Sidebar — custom grouped navigation
# ============================================================
st.sidebar.image(str(HERE / "assets" / "logo.png"), width=180)
st.sidebar.title("FinBytes QuantLabs")
st.sidebar.markdown("**Built by** [Manisha](https://mishcodesfinbytes.github.io/FinBytes/)")
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

# Mini Projects — Dashboards
st.sidebar.caption("Dashboards")
st.sidebar.page_link("pages/20_Currency_Dashboard.py", label="Currency Dashboard")
st.sidebar.page_link("pages/21_Stock_Tracker.py", label="Stock Tracker")
st.sidebar.page_link("pages/22_Stock_Analysis.py", label="Stock Analysis")
st.sidebar.page_link("pages/23_Crypto_Portfolio.py", label="Crypto Portfolio")
st.sidebar.page_link("pages/24_Personal_Finance.py", label="Personal Finance")
st.sidebar.page_link("pages/25_ESG_Tracker.py", label="ESG Tracker")
st.sidebar.page_link("pages/26_Financial_Reporting.py", label="Financial Reporting")

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

st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="System Health")
st.sidebar.markdown(
    "[GitHub](https://github.com/MishCodesFinBytes/QuantLab) · "
    "[Blog](https://mishcodesfinbytes.github.io/FinBytes/)"
)

# ============================================================
# Main content — System-level health checks
# ============================================================
st.title("System Health")
st.markdown("Shared infrastructure status for all FinBytes QuantLabs projects.")

st.markdown("---")

st.markdown("### Shared Infrastructure")

ci_status = {"status": "unknown", "detail": ""}
try:
    r = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
        params={"per_page": 3},
        timeout=10,
    )
    runs = r.json().get("workflow_runs", [])
    if runs:
        latest = runs[0]
        ci_status = {
            "status": "ok" if latest.get("conclusion") == "success" else "error" if latest.get("conclusion") == "failure" else "unknown",
            "conclusion": latest.get("conclusion", "in_progress"),
            "run_number": latest["run_number"],
            "url": latest["html_url"],
            "created_at": latest["created_at"][:10],
        }
except Exception as e:
    ci_status = {"status": "unknown", "detail": str(e)}

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**GitHub Repository**")
    st.success("Active")
    st.caption(f"[MishCodesFinBytes/QuantLab](https://github.com/{GITHUB_REPO})")

with c2:
    st.markdown("**CI Pipeline**")
    if ci_status["status"] == "ok":
        st.success(f"Passing (#{ci_status.get('run_number', '?')})")
    elif ci_status["status"] == "error":
        st.error(f"Failing (#{ci_status.get('run_number', '?')})")
    else:
        st.warning("Unknown")
    if ci_status.get("url"):
        st.caption(f"[View run]({ci_status['url']}) — {ci_status.get('created_at', '')}")

with c3:
    st.markdown("**Dashboard**")
    st.success("Running")
    st.caption("[finbytes.streamlit.app](https://finbytes.streamlit.app)")

st.markdown("---")

st.markdown("### All Services")

st.markdown(f"""
| Service | URL | Hosting | Notes |
|---------|-----|---------|-------|
| Dashboard | [finbytes.streamlit.app](https://finbytes.streamlit.app) | Streamlit Cloud | Free, auto-deploys from master |
| Scanner API | [finbytes-scanner.onrender.com](https://finbytes-scanner.onrender.com) | Render Free Tier | Sleeps after 15min idle |
| Scanner DB | Internal (Render) | Render PostgreSQL Free | **Expires 90 days after creation** |
| CI | [GitHub Actions](https://github.com/{GITHUB_REPO}/actions) | GitHub Free | 2000 mins/month |
| Blog | [FinBytes](https://mishcodesfinbytes.github.io/FinBytes/) | GitHub Pages | Free |
""")

st.warning(
    "**Render PostgreSQL free tier expires after 90 days.** "
    "If a project's Database check shows red, recreate the database on Render. "
    "See `docs/MAINTENANCE.md` for step-by-step instructions."
)

st.markdown("---")
st.markdown("### Per-Project Health")
st.markdown("Each project has its own **System Health** tab with API, database, and test checks.")
st.page_link("pages/1_Stock_Risk_Scanner.py", label="Stock Risk Scanner")
