from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime

st.set_page_config(page_title="System Health | FinBytes QuantLabs", page_icon="🩺", layout="wide")

st.title("System Health")
st.markdown("Live status of all services powering FinBytes QuantLabs.")

GITHUB_REPO = "MishCodesFinBytes/QuantLab"

# ============================================================
# Project registry — add new projects here
# ============================================================
PROJECTS = {
    "Stock Risk Scanner": {
        "api_url": st.secrets.get("API_URL", "http://localhost:8000"),
        "health_endpoint": "/health",
        "db_endpoint": "/api/health/db",
        "render_name": "finbytes-scanner",
        "icon": "📊",
        "tests": {
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
        },
    },
    # Future projects go here:
    # "CDS Pricing": {
    #     "api_url": st.secrets.get("CDS_API_URL", "http://localhost:8001"),
    #     ...
    # },
}


# ============================================================
# Health check functions
# ============================================================
def check_endpoint(url: str, timeout: int = 10) -> dict:
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            return {"status": "ok", "detail": data.get("detail", "Responding"), **data}
        return {"status": "error", "detail": f"HTTP {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "detail": "Cannot connect — service may be sleeping"}
    except requests.exceptions.Timeout:
        return {"status": "error", "detail": "Request timed out"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


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


def rag_color(status):
    if status == "ok":
        return "#28a745", "#fff"
    elif status == "error":
        return "#dc3545", "#fff"
    return "#ffc107", "#333"


# ============================================================
# Shared Infrastructure
# ============================================================
st.markdown("---")
st.markdown("## Shared Infrastructure")

ci = get_ci_status()

col_gh, col_ci, col_dash = st.columns(3)

with col_gh:
    st.markdown("### GitHub")
    st.success("Repository")
    st.caption(f"[MishCodesFinBytes/QuantLab](https://github.com/{GITHUB_REPO})")

with col_ci:
    st.markdown("### CI Pipeline")
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

with col_dash:
    st.markdown("### Dashboard")
    st.success("Running")
    st.caption("[finbytes.streamlit.app](https://finbytes.streamlit.app)")


# ============================================================
# Per-Project Health
# ============================================================
for project_name, project in PROJECTS.items():
    st.markdown("---")
    st.markdown(f"## {project['icon']} {project_name}")

    api_url = project["api_url"]

    # Service checks
    api_result = check_endpoint(f"{api_url}{project['health_endpoint']}")
    db_result = check_endpoint(f"{api_url}{project['db_endpoint']}")

    col_api, col_db = st.columns(2)

    with col_api:
        st.markdown("### API")
        if api_result["status"] == "ok":
            st.success("Online")
        else:
            st.error("Offline")
        st.caption(api_result.get("detail", ""))

    with col_db:
        st.markdown("### Database")
        if db_result.get("status") == "ok":
            st.success("Connected")
        else:
            st.error("Disconnected")
        st.caption(db_result.get("database", db_result.get("detail", "")))

    # Pipeline diagram
    api_bg, api_fg = rag_color(api_result["status"])
    db_bg, db_fg = rag_color(db_result.get("status", "unknown"))
    ci_bg, ci_fg = rag_color(ci["status"])

    mermaid_html = f"""
    <div style="background:white;padding:16px;border-radius:8px;border:1px solid #e8e8e8;">
    <div class="mermaid">
    graph LR
        DEV["Code Push"]:::neutral --> WK["working"]:::neutral
        WK --> PR["PR"]:::neutral
        PR --> MASTER["master"]:::neutral
        MASTER --> CI["CI Tests"]:::ci_s
        MASTER --> API["{project_name}<br/>API"]:::api_s
        MASTER --> DASH["Streamlit<br/>Dashboard"]:::dash_s
        API --> DB[("PostgreSQL")]:::db_s
        API --> EXT["External<br/>Services"]:::neutral

        classDef neutral fill:#f0f2f6,stroke:#ccc,color:#333
        classDef api_s fill:{api_bg},stroke:{api_bg},color:{api_fg}
        classDef db_s fill:{db_bg},stroke:{db_bg},color:{db_fg}
        classDef ci_s fill:{ci_bg},stroke:{ci_bg},color:{ci_fg}
        classDef dash_s fill:#28a745,stroke:#28a745,color:#fff
    </div>
    <p style="text-align:center;font-size:12px;color:#888;margin-top:8px;">
        🟢 Online &nbsp;&nbsp; 🟡 Unknown &nbsp;&nbsp; 🔴 Offline &nbsp;&nbsp; ⬜ External
    </p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad: true, theme: 'default'}});</script>
    """
    components.html(mermaid_html, height=350)

    # Test runner
    total_tests = sum(len(m["tests"]) for m in project["tests"].values())
    ci_passing = ci.get("conclusion") == "success" if ci.get("status") != "unknown" else None

    st.markdown(f"### Test Suite — {total_tests} tests")

    if ci_passing is True:
        st.success(f"All {total_tests} tests passing")
    elif ci_passing is False:
        st.error("Some tests failing — check CI for details")
    else:
        st.info("CI status unavailable — showing test inventory")

    for module_name, module_data in project["tests"].items():
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


# ============================================================
# Service Details
# ============================================================
st.markdown("---")
st.markdown("## Service Details")

st.markdown(f"""
| Service | URL | Hosting | Notes |
|---------|-----|---------|-------|
| Dashboard | [finbytes.streamlit.app](https://finbytes.streamlit.app) | Streamlit Community Cloud | Free, auto-deploys from master |
| Scanner API | [finbytes-scanner.onrender.com]({PROJECTS['Stock Risk Scanner']['api_url']}) | Render Free Tier | Sleeps after 15min idle |
| Scanner DB | Internal (Render) | Render PostgreSQL Free | **Expires 90 days after creation** |
| CI | [GitHub Actions](https://github.com/{GITHUB_REPO}/actions) | GitHub Free | 2000 mins/month |
| Blog | [FinBytes](https://mishcodesfinbytes.github.io/FinBytes/) | GitHub Pages | Free |
""")

st.warning(
    "**Render PostgreSQL free tier expires after 90 days.** "
    "If the Database check above shows red, recreate the database on Render "
    "and update the DATABASE_URL environment variable."
)
