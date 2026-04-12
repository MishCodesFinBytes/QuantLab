from pathlib import Path
import sys
import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from nav import render_sidebar
from test_tab import render_test_tab

HERE = Path(__file__).parent
GITHUB_REPO = "mish-codes/QuantLab"

st.set_page_config(
    page_title="FinBytes QuantLabs",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()

# ============================================================
# Main content — System-level health checks
# ============================================================
st.title("System Health")
st.markdown("Shared infrastructure status for all FinBytes QuantLabs projects.")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
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
        st.caption(f"[mish-codes/QuantLab](https://github.com/{GITHUB_REPO})")

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
| Blog | [FinBytes](https://mish-codes.github.io/FinBytes/) | GitHub Pages | Free |
""")

    st.warning(
        "**Render PostgreSQL free tier expires after 90 days.** "
        "If a project's Database check shows red, recreate the database on Render. "
        "See `docs/MAINTENANCE.md` for step-by-step instructions."
    )

    st.markdown("---")

    st.markdown("### External APIs & Data Sources")
    st.caption("Live checks — each API is pinged with a minimal request to verify availability.")

    def check_api(name, url, timeout=8):
        """Return 'ok', 'slow', or 'down' with response time."""
        import time
        try:
            start = time.time()
            r = requests.get(url, timeout=timeout)
            elapsed = time.time() - start
            if r.status_code == 200:
                return ("ok", f"{elapsed:.1f}s") if elapsed < 3 else ("slow", f"{elapsed:.1f}s")
            return ("down", f"HTTP {r.status_code}")
        except requests.exceptions.Timeout:
            return ("slow", "Timeout")
        except Exception as e:
            return ("down", str(e)[:40])

    api_checks = {
        "yfinance (Yahoo Finance)": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=1d",
        "CoinGecko": "https://api.coingecko.com/api/v3/ping",
        "Open Exchange Rates": "https://open.er-api.com/v6/latest/USD",
        "Bank of England (SONIA)": "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/2025&Dateto=02/Jan/2025&SeriesCodes=IUDSNPY&CSVF=TN&UsingCodes=Y",
        "ECB Data API (€STR)": "https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?format=csvdata&startPeriod=2025-01-01&endPeriod=2025-01-02",
        "New York Fed (SOFR)": "https://markets.newyorkfed.org/api/rates/secured/sofr/search.csv?startDate=2025-01-02&endDate=2025-01-02&type=rate",
        "Land Registry PPD": "https://price-paid-data.publicdata.landregistry.gov.uk/pp-monthly-update-new-version.csv",
        "OpenStreetMap Overpass": "https://overpass-api.de/api/status",
        "GitHub API": f"https://api.github.com/repos/{GITHUB_REPO}",
    }

    cols = st.columns(3)
    for i, (name, url) in enumerate(api_checks.items()):
        with cols[i % 3]:
            status, detail = check_api(name, url)
            if status == "ok":
                st.success(f"**{name}**  \n{detail}")
            elif status == "slow":
                st.warning(f"**{name}**  \n{detail}")
            else:
                st.error(f"**{name}**  \n{detail}")

    st.caption(
        "For full documentation on each API, see the "
        "[APIs & Data Sources](https://mish-codes.github.io/FinBytes/tech-stack/apis-data-sources/) reference."
    )

    st.markdown("---")
    st.markdown("### Per-Project Health")
    st.markdown("Each project has its own **System Health** tab with API, database, and test checks.")
    st.page_link("pages/1_Stock_Risk_Scanner.py", label="Stock Risk Scanner")

with tab_tests:
    render_test_tab("test_app.py")
