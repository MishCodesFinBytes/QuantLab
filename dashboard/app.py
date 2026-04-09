from pathlib import Path
import sys
import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from nav import render_sidebar
from test_tab import render_test_tab

HERE = Path(__file__).parent
GITHUB_REPO = "MishCodesFinBytes/QuantLab"

st.set_page_config(
    page_title="FinBytes QuantLabs",
    layout="wide",
)

render_sidebar()

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

# -- Tests ----------------------------------------------------------------
with st.expander("Test Results"):
    render_test_tab("test_app.py")
