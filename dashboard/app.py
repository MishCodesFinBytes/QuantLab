"""Root landing — renders the resume page with an `ENTER QUANTLABS →` CTA.

The project grid and System Health tabs that used to live here have moved
to `pages/0_QuantLabs.py`. This file is deliberately thin: its only job is
to serve the static resume HTML from `static/resume.html` as the app root,
so visitors to `quantlabs.streamlit.app/` see the CV first.
"""

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from nav import render_sidebar

HERE = Path(__file__).parent
STATIC_DIR = HERE / "static"

# Absolute URL to the QuantLabs project hub. Hardcoded to the production
# Streamlit Cloud host so the `ENTER QUANTLABS →` CTA inside the
# components.html iframe can target the parent frame with a full URL.
# Override via env var for local dev.
QUANTLABS_URL = os.environ.get(
    "QUANTLABS_URL",
    "https://quantlabs.streamlit.app/QuantLabs",
)

st.set_page_config(
    page_title="Manisha Shetty — Python Developer",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_sidebar()

# Full-bleed resume: hide Streamlit's sidebar, header, and default padding
# on the root page only so the embedded resume renders edge-to-edge. Pages
# under /pages still get the normal QuantLabs sidebar because this CSS is
# injected here, not in nav.py's global styles.
st.markdown(
    """
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container,
    [data-testid="stMain"] .block-container,
    section.main > div.block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        margin-left: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

_resume_html = (STATIC_DIR / "resume.html").read_text(encoding="utf-8")
_resume_html = _resume_html.replace("{{QUANTLABS_URL}}", QUANTLABS_URL)

st.iframe(_resume_html, height=4200, scrolling=True)
