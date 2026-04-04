from pathlib import Path
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="System Health | FinBytes QuantLabs", page_icon="🩺", layout="wide")

st.title("System Health")
st.markdown("Live status of all services powering FinBytes QuantLabs.")

API_URL = st.secrets.get("API_URL", "http://localhost:8000")
GITHUB_REPO = "MishCodesFinBytes/QuantLab"


def check_api() -> dict:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=10)
        if resp.status_code == 200:
            return {"status": "ok", "detail": "API is responding"}
        return {"status": "error", "detail": f"HTTP {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "detail": "Cannot connect — backend may be sleeping (Render free tier wakes on first request)"}
    except requests.exceptions.Timeout:
        return {"status": "error", "detail": "Request timed out"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def check_db() -> dict:
    try:
        resp = requests.get(f"{API_URL}/api/health/db", timeout=10)
        data = resp.json()
        return data
    except requests.exceptions.ConnectionError:
        return {"status": "error", "database": "API offline — cannot check database"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


def get_ci_status() -> dict:
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
            params={"per_page": 5, "branch": "master"},
            timeout=10,
        )
        if resp.status_code != 200:
            return {"status": "unknown", "detail": "Could not fetch CI status"}
        runs = resp.json().get("workflow_runs", [])
        if not runs:
            return {"status": "unknown", "detail": "No CI runs found"}

        latest = runs[0]
        return {
            "status": "ok" if latest["conclusion"] == "success" else "error",
            "conclusion": latest.get("conclusion", "in_progress"),
            "name": latest["name"],
            "run_number": latest["run_number"],
            "url": latest["html_url"],
            "created_at": latest["created_at"][:10],
        }
    except Exception as e:
        return {"status": "unknown", "detail": str(e)}


# --- Run all checks ---
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

# API check
with col1:
    st.markdown("### API")
    api = check_api()
    if api["status"] == "ok":
        st.success("Online")
    else:
        st.error("Offline")
    st.caption(api.get("detail", ""))

# DB check
with col2:
    st.markdown("### Database")
    db = check_db()
    if db.get("status") == "ok":
        st.success("Connected")
    else:
        st.error("Disconnected")
    st.caption(db.get("database", db.get("detail", "")))

# CI check
with col3:
    st.markdown("### CI Pipeline")
    ci = get_ci_status()
    if ci["status"] == "ok":
        st.success(f"Passing (#{ci.get('run_number', '?')})")
    elif ci["status"] == "error":
        st.error(f"Failing (#{ci.get('run_number', '?')})")
    else:
        st.warning("Unknown")
    if "url" in ci:
        st.caption(f"[View run]({ci['url']}) — {ci.get('created_at', '')}")
    else:
        st.caption(ci.get("detail", ""))

# Dashboard check
with col4:
    st.markdown("### Dashboard")
    st.success("Running")
    st.caption("You're seeing this page")

# --- Test Results from CI ---
st.markdown("---")
st.markdown("## Latest Test Results")

st.markdown(
    f"![Tests](https://github.com/{GITHUB_REPO}/actions/workflows/test.yml/badge.svg?branch=master)"
)

ci_data = get_ci_status()
if ci_data.get("url"):
    st.markdown(f"**Last run:** [{ci_data['name']} #{ci_data['run_number']}]({ci_data['url']}) — {ci_data.get('created_at', '')}")

st.markdown("### Test Suite Coverage")
st.markdown("""
| Module | Tests | What's covered |
|--------|-------|---------------|
| `models.py` | 6 | Valid request, uppercase, mismatched lengths, bad weights, RiskMetrics, ScanResult |
| `risk.py` | 3 | VaR/CVaR values, max drawdown, Sharpe ratio sign |
| `market_data.py` | 2 | Successful fetch (mocked), empty data error |
| `narrative.py` | 3 | API success (mocked), API error fallback, no key fallback |
| `scanner.py` | 1 | Full pipeline with mocks |
| `db.py` | 6 | Create pending, complete, fail, get by ID, get missing, recent scans |
| `main.py` (API) | 5 | Health, create scan, get scan, 404, list scans |
| **Total** | **26** | |
""")

# --- Service details ---
st.markdown("---")
st.markdown("## Service Details")

st.markdown(f"""
| Service | URL | Hosting | Notes |
|---------|-----|---------|-------|
| Dashboard | [finbytes.streamlit.app](https://finbytes.streamlit.app) | Streamlit Community Cloud | Free, auto-deploys from master |
| API | [finbytes-scanner.onrender.com]({API_URL}) | Render Free Tier | Sleeps after 15min idle |
| Database | Internal (Render) | Render PostgreSQL Free | **Expires 90 days after creation** |
| CI | [GitHub Actions](https://github.com/{GITHUB_REPO}/actions) | GitHub Free | 2000 mins/month |
| Blog | [FinBytes](https://mishcodesfinbytes.github.io/FinBytes/) | GitHub Pages | Free |
""")

st.warning(
    "**Render PostgreSQL free tier expires after 90 days.** "
    "If the Database check above shows red, recreate the database on Render "
    "and update the DATABASE_URL environment variable."
)
