"""Cached GitHub Actions CI status fetch."""
import requests
import streamlit as st

GITHUB_REPO = "mish-codes/QuantLab"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ci_status() -> dict:
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
            params={"per_page": 3},
            timeout=10,
        )
        runs = r.json().get("workflow_runs", [])
        if runs:
            latest = runs[0]
            conclusion = latest.get("conclusion", "in_progress")
            return {
                "status": "ok" if conclusion == "success" else "error" if conclusion == "failure" else "unknown",
                "conclusion": conclusion,
                "run_number": latest["run_number"],
                "url": latest["html_url"],
                "created_at": latest["created_at"][:10],
            }
    except Exception:
        pass
    return {"status": "unknown", "detail": ""}
