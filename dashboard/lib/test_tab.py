"""Shared helper to render test results in a Streamlit tab."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

_RESULTS_PATH = Path(__file__).resolve().parent.parent / "test_results.json"


def render_test_tab(page_file: str) -> None:
    """Display test results for *page_file* (e.g. ``test_stock_tracker.py``).

    Call this inside an ``st.tabs`` block.  If the results file is missing
    or contains no matching tests, a friendly fallback message is shown.
    """
    if not _RESULTS_PATH.exists():
        st.info("No test results available — run the test suite to generate them.")
        return

    try:
        data = json.loads(_RESULTS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        st.warning("Could not read test results file.")
        return

    tests = [
        t for t in data.get("tests", [])
        if page_file in t.get("nodeid", "")
    ]

    if not tests:
        st.info(f"No test results found for `{page_file}`.")
        return

    passed = sum(1 for t in tests if t["outcome"] == "passed")
    total = len(tests)

    if passed == total:
        st.success(f"**{passed}/{total}** tests passing")
    else:
        st.error(f"**{passed}/{total}** tests passing")

    for t in tests:
        name = t["nodeid"].split("::")[-1]
        icon = "✅" if t["outcome"] == "passed" else "❌"
        duration = t.get("duration", 0)
        col1, col2, col3 = st.columns([0.05, 0.75, 0.2])
        with col1:
            st.markdown(icon)
        with col2:
            st.markdown(f"`{name}`")
        with col3:
            st.caption(f"{duration:.2f}s")
        if t["outcome"] != "passed" and t.get("longrepr"):
            with st.expander("Error details"):
                st.code(t["longrepr"])
