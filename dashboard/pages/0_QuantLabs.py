"""QuantLabs — All projects + System Health.

Lives at /QuantLabs. The app root (/) is the resume page in app.py; this
page is the actual project hub that users reach by clicking `ENTER
QUANTLABS →` on the resume (or the QuantLabs brand in the sidebar).
"""

from pathlib import Path
import sys
import time

import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from html import escape as _escape
from nav import render_sidebar
from test_tab import render_test_tab
from ci_status import fetch_ci_status
from projects import (
    PROJECTS_BY_CATEGORY,
    category_with_capstones_last,
)

GITHUB_REPO = "mish-codes/QuantLab"

st.set_page_config(
    page_title="QuantLabs — Projects",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()


# ─────────────────────────────────────────────────────────────
# HTML rendering helpers
# ─────────────────────────────────────────────────────────────

import re as _re


def _page_url(page_link: str) -> str:
    """Convert a page_link like 'pages/16_Rent_vs_Buy.py' to the Streamlit
    URL slug '/Rent_vs_Buy' that an <a href="..."> can navigate to."""
    name = page_link.replace("pages/", "").replace(".py", "")
    name = _re.sub(r"^\d+_", "", name)
    return "/" + name


_CAT_CARD_STYLE = (
    "display:block;text-decoration:none;color:#1a1a1a;"
    "background:#ffffff;border:1px solid #e5e5e5;border-radius:4px;"
    "padding:0.9rem 1rem;transition:border-color 0.15s;"
)
_CAT_TITLE_STYLE = (
    "font-family:'Inter',system-ui,sans-serif !important;font-size:0.95rem;font-weight:600;"
    "color:#d97706;margin:0 0 0.25rem;"
)
_CAT_DESC_STYLE = (
    "font-family:'Inter',system-ui,sans-serif !important;font-size:0.78rem;color:#1a1a1a;"
    "margin:0 0 0.5rem;line-height:1.4;"
)
_CAT_TECH_STYLE = (
    "font-family:'Inter',system-ui,sans-serif !important;font-size:0.68rem;color:#6b6b6b;"
)
_CAPSTONE_STYLE = (
    "display:inline-block;font-size:0.62rem;font-weight:500;text-transform:uppercase;"
    "letter-spacing:0.05em;color:#d97706;border:1px solid #d97706;padding:1px 5px;"
    "border-radius:2px;margin-left:0.4rem;vertical-align:middle;"
)
_CAT_CHIP_BASE_STYLE = (
    "display:inline-block;font-size:0.62rem;font-weight:500;text-transform:uppercase;"
    "letter-spacing:0.05em;padding:2px 6px;border-radius:2px;margin-bottom:0.4rem;"
)
# Pastel background + saturated text per category. Unknown categories fall
# back to neutral grey so new categories don't need a palette update before
# they render.
_CAT_CHIP_PALETTE = {
    "Geopolitics & risk":              {"bg": "#fee2e2", "fg": "#991b1b"},
    "Personal finance & property":     {"bg": "#dcfce7", "fg": "#166534"},
    "Quantitative finance & markets":  {"bg": "#dbeafe", "fg": "#1e40af"},
    "Data science & analytics":        {"bg": "#f3e8ff", "fg": "#6b21a8"},
    "Tech demos & references":         {"bg": "#fef3c7", "fg": "#92400e"},
    "Half-baked":                      {"bg": "#f4f4f4", "fg": "#6b6b6b"},
}
_CAT_GRID_STYLE = (
    "display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-bottom:0.5rem;"
)


def _cat_card_html(p) -> str:
    tech = " · ".join(_escape(t) for t in p.tech)
    capstone = (
        f'<span style="{_CAPSTONE_STYLE}">Capstone</span>' if p.is_capstone else ""
    )
    return (
        f'<a style="{_CAT_CARD_STYLE}" href="{_escape(_page_url(p.page_link))}" target="_self">'
        f'<div style="{_CAT_TITLE_STYLE}">{_escape(p.label)}{capstone}</div>'
        f'<div style="{_CAT_DESC_STYLE}">{_escape(p.description)}</div>'
        f'<div style="{_CAT_TECH_STYLE}">{tech}</div>'
        f'</a>'
    )


# ─────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────

tab_all, tab_health = st.tabs(["All projects", "System Health"])

def _ql_html(html: str) -> None:
    """Render raw HTML without Streamlit's markdown processor eating class
    attributes on <a>/<div> elements. Falls back to st.markdown on older
    Streamlit versions."""
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# All projects — collapsible category sections
# ─────────────────────────────────────────────────────────────

with tab_all:
    st.markdown(
        '<h1 class="ql-page-title">All projects</h1>'
        '<p class="ql-page-subtitle">Every QuantLabs project, grouped by category</p>',
        unsafe_allow_html=True,
    )

    _ql_html(
        """
        <style>
        @keyframes ql-card-in {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .ql-all-card {
            animation: ql-card-in 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
            transition: transform 0.18s ease, box-shadow 0.18s ease,
                        border-color 0.18s ease !important;
            will-change: transform;
        }
        .ql-all-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(26, 26, 26, 0.08);
            border-color: #d97706 !important;
        }
        .ql-all-card:nth-child(1)  { animation-delay: 0.00s; }
        .ql-all-card:nth-child(2)  { animation-delay: 0.03s; }
        .ql-all-card:nth-child(3)  { animation-delay: 0.06s; }
        .ql-all-card:nth-child(4)  { animation-delay: 0.09s; }
        .ql-all-card:nth-child(5)  { animation-delay: 0.12s; }
        .ql-all-card:nth-child(6)  { animation-delay: 0.15s; }
        .ql-all-card:nth-child(7)  { animation-delay: 0.18s; }
        .ql-all-card:nth-child(8)  { animation-delay: 0.21s; }
        .ql-all-card:nth-child(9)  { animation-delay: 0.24s; }
        .ql-all-card:nth-child(10) { animation-delay: 0.27s; }
        .ql-all-card:nth-child(n+11) { animation-delay: 0.30s; }
        </style>
        """
    )

    for category in PROJECTS_BY_CATEGORY:
        projs = category_with_capstones_last(category)
        with st.expander(f"{category}  ({len(projs)})", expanded=(category != "Half-baked")):
            _ql_html(
                f'<div style="{_CAT_GRID_STYLE}">'
                + ''.join(_cat_card_html(p) for p in projs)
                + '</div>'
            )

# ─────────────────────────────────────────────────────────────
# System Health — preserved from original
# ─────────────────────────────────────────────────────────────

with tab_health:
    tab_app, tab_tests = st.tabs(["App", "Tests"])

    with tab_app:
        st.markdown("---")

        st.markdown("### Shared Infrastructure")

        ci_status = fetch_ci_status()

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
            st.caption("[quantlabs.streamlit.app](https://quantlabs.streamlit.app)")

        st.markdown("---")

        st.markdown("### All Services")

        st.markdown(f"""
| Service | URL | Hosting | Notes |
|---------|-----|---------|-------|
| Dashboard | [quantlabs.streamlit.app](https://quantlabs.streamlit.app) | Streamlit Cloud | Free, auto-deploys from master |
| Scanner API | [finbytes-scanner.onrender.com](https://finbytes-scanner.onrender.com) | Render Free Tier | Sleeps after 15min idle |
| Scanner DB | Internal (Render) | Render PostgreSQL Free | **Expires 30 days after creation** |
| CI | [GitHub Actions](https://github.com/{GITHUB_REPO}/actions) | GitHub Free | 2000 mins/month |
| Blog | [FinBytes](https://mish-codes.github.io/FinBytes/) | GitHub Pages | Free |
""")

        st.warning(
            "**Render PostgreSQL free tier expires after 30 days.** "
            "If a project's Database check shows red, recreate the database via the "
            "Churros admin page (Render DB tab) — one-click delete/create/redeploy. "
            "See `docs/MAINTENANCE.md`."
        )

        st.markdown("---")

        st.markdown("### External APIs & Data Sources")
        st.caption("Live checks — each API is pinged with a minimal request to verify availability.")

        def check_api(name, url, timeout=8):
            """Return 'ok', 'slow', or 'down' with response time."""
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
