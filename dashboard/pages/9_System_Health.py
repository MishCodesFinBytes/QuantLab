from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
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
            params={"per_page": 5},
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

# --- Deployment Pipeline Diagram ---
st.markdown("---")
st.markdown("## Deployment Pipeline")

# Determine RAG colors for each node
def rag(status):
    if status == "ok":
        return "#28a745", "#fff"  # green
    elif status == "error":
        return "#dc3545", "#fff"  # red
    else:
        return "#ffc107", "#333"  # amber

api_bg, api_fg = rag(api["status"])
db_bg, db_fg = rag(db.get("status", "unknown"))
ci_bg, ci_fg = rag(ci["status"])
dash_bg, dash_fg = "#28a745", "#fff"  # always green
gh_bg, gh_fg = "#28a745", "#fff"  # always green

mermaid_html = f"""
<div style="background:white;padding:16px;border-radius:8px;border:1px solid #e8e8e8;">
<div class="mermaid">
graph LR
    DEV["👩‍💻 Code Push"]:::neutral --> WK["working branch"]:::neutral
    WK --> PR["Pull Request"]:::neutral
    PR --> MASTER["master branch"]:::neutral
    MASTER --> CI["GitHub Actions<br/>CI Tests"]:::ci_status
    MASTER --> RENDER["Render API<br/>Auto-deploy"]:::api_status
    MASTER --> STREAM["Streamlit Cloud<br/>Auto-deploy"]:::dash_status
    RENDER --> DB[("PostgreSQL<br/>Database")]:::db_status
    RENDER --> YF["yfinance<br/>Market Data"]:::neutral
    RENDER --> CLAUDE["Claude API<br/>Narratives"]:::neutral

    classDef neutral fill:#f0f2f6,stroke:#ccc,color:#333
    classDef api_status fill:{api_bg},stroke:{api_bg},color:{api_fg}
    classDef db_status fill:{db_bg},stroke:{db_bg},color:{db_fg}
    classDef ci_status fill:{ci_bg},stroke:{ci_bg},color:{ci_fg}
    classDef dash_status fill:{dash_bg},stroke:{dash_bg},color:{dash_fg}
</div>
<p style="text-align:center;font-size:12px;color:#888;margin-top:8px;">
    🟢 Online &nbsp;&nbsp; 🟡 Unknown &nbsp;&nbsp; 🔴 Offline &nbsp;&nbsp; ⬜ External service
</p>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad: true, theme: 'default'}});</script>
"""

components.html(mermaid_html, height=400)

# --- CI Details ---
st.markdown("---")
st.markdown("## CI Pipeline")

ci_data = get_ci_status()

if ci_data.get("status") == "unknown":
    st.warning(f"Could not fetch CI status: {ci_data.get('detail', 'Unknown error')}")
else:
    conclusion = ci_data.get("conclusion", "in_progress")
    icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"

    col_badge, col_info = st.columns([1, 2])
    with col_badge:
        st.image(
            f"https://github.com/{GITHUB_REPO}/actions/workflows/test.yml/badge.svg",
            width=150,
        )
    with col_info:
        st.markdown(
            f"**{icon} {ci_data.get('name', 'Tests')} #{ci_data.get('run_number', '?')}** — "
            f"**{conclusion}** — {ci_data.get('created_at', '')}"
        )
        if ci_data.get("url"):
            st.markdown(f"[View full run on GitHub]({ci_data['url']})")

# --- Test Runner Display ---
st.markdown("---")
st.markdown("## Test Suite — 27 tests")

ci_passing = ci_data.get("conclusion") == "success" if ci_data.get("status") != "unknown" else None

# Group tests by module
TEST_MODULES = {
    "API Endpoints (test_api.py)": {
        "icon": "🌐",
        "tests": [
            ("test_health", "GET /health returns 200"),
            ("test_db_connected", "GET /api/health/db returns connected"),
            ("test_returns_pending", "POST /api/scan returns 202 + pending"),
            ("test_returns_scan_by_id", "GET /api/scans/{id} returns scan"),
            ("test_returns_404_for_missing_id", "GET /api/scans/9999 returns 404"),
            ("test_returns_list", "GET /api/scans returns list"),
        ],
    },
    "Database Layer (test_db_layer.py)": {
        "icon": "🗄️",
        "tests": [
            ("test_creates_pending_record", "Insert pending scan record"),
            ("test_updates_to_complete", "Update scan to complete with metrics"),
            ("test_updates_to_failed", "Update scan to failed with error"),
            ("test_returns_record_by_id", "Fetch scan by ID"),
            ("test_returns_none_for_missing_id", "Returns None for missing ID"),
            ("test_returns_completed_scans_newest_first", "Recent scans ordered newest first"),
        ],
    },
    "Pydantic Models (test_models.py)": {
        "icon": "📋",
        "tests": [
            ("test_valid_request", "Valid request accepted"),
            ("test_tickers_uppercased", "Tickers auto-uppercased"),
            ("test_mismatched_lengths_raises", "Mismatched tickers/weights raises ValueError"),
            ("test_weights_not_summing_to_one_raises", "Bad weight sum raises ValueError"),
            ("test_risk_metrics_fields", "RiskMetrics stores all 5 fields"),
            ("test_scan_result_fields", "ScanResult stores all fields"),
        ],
    },
    "Risk Calculations (test_risk.py)": {
        "icon": "📊",
        "tests": [
            ("test_var_and_cvar", "VaR is negative, CVaR worse than VaR"),
            ("test_max_drawdown", "Max drawdown calculation correct"),
            ("test_sharpe_ratio_sign", "Sharpe positive for uptrend, negative for downtrend"),
        ],
    },
    "Market Data (test_market_data.py)": {
        "icon": "📈",
        "tests": [
            ("test_successful_fetch", "yfinance download returns correct DataFrame"),
            ("test_empty_data_raises", "Empty data raises ValueError"),
        ],
    },
    "AI Narrative (test_narrative.py)": {
        "icon": "🤖",
        "tests": [
            ("test_generate_with_api", "Claude API returns narrative"),
            ("test_generate_api_error_returns_fallback", "API error returns fallback string"),
            ("test_generate_no_api_key_returns_fallback", "No API key returns fallback string"),
        ],
    },
    "Scanner Pipeline (test_scanner.py)": {
        "icon": "🔄",
        "tests": [
            ("test_full_pipeline", "Full pipeline: fetch → risk → narrative → result"),
        ],
    },
}

# Status indicator
if ci_passing is True:
    st.success("All 27 tests passing")
elif ci_passing is False:
    st.error("Some tests failing — check CI for details")
else:
    st.info("CI status unavailable — showing test inventory")

# Expandable modules
for module_name, module_data in TEST_MODULES.items():
    test_count = len(module_data["tests"])
    if ci_passing is True:
        header = f"{module_data['icon']} {module_name} — ✅ {test_count}/{test_count} passed"
    elif ci_passing is False:
        header = f"{module_data['icon']} {module_name} — ⚠️ {test_count} tests (check CI)"
    else:
        header = f"{module_data['icon']} {module_name} — {test_count} tests"

    with st.expander(header):
        for test_name, test_desc in module_data["tests"]:
            if ci_passing is True:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ `{test_name}` — {test_desc}")
            elif ci_passing is False:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ `{test_name}` — {test_desc}")
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⬜ `{test_name}` — {test_desc}")

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
