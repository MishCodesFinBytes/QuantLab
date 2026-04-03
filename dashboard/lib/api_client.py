import time
import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")


def check_health() -> bool:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def submit_scan(tickers: list[str], weights: list[float], period: str) -> dict:
    resp = requests.post(
        f"{API_URL}/api/scan",
        json={"tickers": tickers, "weights": weights, "period": period},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def poll_scan(scan_id: int, max_wait: int = 120) -> dict:
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{API_URL}/api/scans/{scan_id}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["status"] != "pending":
            return data
        time.sleep(2)
    raise TimeoutError(f"Scan {scan_id} did not complete within {max_wait}s")


def get_recent_scans(limit: int = 5) -> list[dict]:
    try:
        resp = requests.get(
            f"{API_URL}/api/scans", params={"limit": limit}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []
