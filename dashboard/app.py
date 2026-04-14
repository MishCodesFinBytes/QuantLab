"""QuantLab landing page — Welcome (portfolio) + All projects + System Health."""

from pathlib import Path
import sys
import json
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from nav import render_sidebar
from test_tab import render_test_tab
from projects import (
    PROJECTS_BY_CATEGORY,
    all_projects,
    featured,
    category_with_capstones_last,
)

HERE = Path(__file__).parent
GITHUB_REPO = "mish-codes/QuantLab"

st.set_page_config(
    page_title="QuantLab",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()


# ─────────────────────────────────────────────────────────────
# HTML rendering helpers
# ─────────────────────────────────────────────────────────────

import re as _re


def _escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _page_url(page_link: str) -> str:
    """Convert a page_link like 'pages/16_Rent_vs_Buy.py' to the Streamlit
    URL slug '/Rent_vs_Buy' that an <a href="..."> can navigate to."""
    name = page_link.replace("pages/", "").replace(".py", "")
    name = _re.sub(r"^\d+_", "", name)
    return "/" + name


def _featured_card_html(p) -> str:
    tech = " · ".join(_escape(t) for t in p.tech)
    return (
        f'<a class="ql-featured-card" href="{_escape(_page_url(p.page_link))}" target="_self">'
        f'<div class="ql-featured-card-title">{_escape(p.label)}</div>'
        f'<div class="ql-featured-card-desc">{_escape(p.description)}</div>'
        f'<div class="ql-featured-card-tech">{tech}</div>'
        f'</a>'
    )


def _cat_card_html(p) -> str:
    tech = " · ".join(_escape(t) for t in p.tech)
    capstone = (
        '<span class="ql-capstone-tag">Capstone</span>' if p.is_capstone else ""
    )
    return (
        f'<a class="ql-cat-card" href="{_escape(_page_url(p.page_link))}" target="_self">'
        f'<div class="ql-cat-card-title">{_escape(p.label)}{capstone}</div>'
        f'<div class="ql-cat-card-desc">{_escape(p.description)}</div>'
        f'<div class="ql-cat-card-tech">{tech}</div>'
        f'</a>'
    )


def _matches_query(p, query: str) -> bool:
    if not query:
        return True
    q = query.lower()
    if q in p.label.lower():
        return True
    if q in p.description.lower():
        return True
    if any(q in t.lower() for t in p.tech):
        return True
    return False


# ─────────────────────────────────────────────────────────────
# D3 force-directed project graph
# ─────────────────────────────────────────────────────────────

def _build_project_graph_html() -> str:
    """Return a self-contained HTML+JS string for the project graph."""
    category_colors = {
        "Personal finance & property": "#d97706",
        "Stocks & markets": "#2563eb",
        "Analytics & Fintech": "#059669",
        "Tech demos & references": "#7c3aed",
    }

    projs = all_projects()
    nodes = []
    for p in projs:
        cat = next(
            (c for c, lst in PROJECTS_BY_CATEGORY.items() if p in lst),
            "Tech demos & references",
        )
        nodes.append({
            "id": p.key,
            "label": p.label,
            "color": category_colors.get(cat, "#888"),
            "url": _page_url(p.page_link),
        })

    # Edges only between projects in the SAME category — gives 4 clean
    # clusters instead of a tech-stack hairball where everything connects
    # to everything via Python/Plotly/yfinance.
    project_to_cat = {}
    for cat, lst in PROJECTS_BY_CATEGORY.items():
        for p in lst:
            project_to_cat[p.key] = cat

    edges = []
    for i, a in enumerate(projs):
        for b in projs[i + 1:]:
            if project_to_cat[a.key] == project_to_cat[b.key]:
                edges.append({"source": a.key, "target": b.key})

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    return f"""
<!doctype html>
<html><head><meta charset="utf-8"><style>
  body {{ margin: 0; font-family: 'Inter', sans-serif; background: #fafafa; }}
  #graph {{ width: 100%; height: 540px; }}
  text {{ font-size: 11px; fill: #1a1a1a; pointer-events: none; }}
  a {{ text-decoration: none; }}
  .node {{ cursor: pointer; }}
  .node:hover circle {{ stroke: #d97706; stroke-width: 2; }}
</style></head>
<body>
<div id="graph"></div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = {nodes_json};
const links = {edges_json};
const W = document.getElementById('graph').clientWidth || 800;
const H = 540;

const svg = d3.select('#graph').append('svg')
  .attr('viewBox', [0, 0, W, H])
  .attr('preserveAspectRatio', 'xMidYMid meet');

// Zoom + pan layer
const g = svg.append('g');
svg.call(d3.zoom()
  .scaleExtent([0.4, 4])
  .on('zoom', (ev) => g.attr('transform', ev.transform))
);

const sim = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(70).strength(0.4))
  .force('charge', d3.forceManyBody().strength(-220))
  .force('center', d3.forceCenter(W / 2, H / 2))
  .force('collide', d3.forceCollide().radius(26));

const link = g.append('g').attr('stroke', '#d4d4d4').attr('stroke-opacity', 0.45)
  .selectAll('line').data(links).enter().append('line').attr('stroke-width', 1);

// Each node is wrapped in an SVG <a target="_blank"> — Streamlit's
// components iframe is sandboxed without allow-top-navigation, so
// _top/_parent throw SecurityError. _blank is the only target the
// sandbox allows. Opens the project page in a new tab.
const node = g.append('g').selectAll('a').data(nodes).enter().append('a')
  .attr('href', d => d.url)
  .attr('target', '_blank')
  .attr('rel', 'noopener')
  .attr('class', 'node');

node.append('circle').attr('r', 11).attr('fill', d => d.color)
  .attr('stroke', '#ffffff').attr('stroke-width', 1.5);
node.append('text').attr('dy', 24).attr('text-anchor', 'middle')
  .text(d => d.label.length > 18 ? d.label.slice(0,17)+'…' : d.label);

sim.on('tick', () => {{
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
}});
</script>
</body></html>
"""


# ─────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────

tab_welcome, tab_all, tab_health = st.tabs(["Welcome", "All projects", "System Health"])

# ─────────────────────────────────────────────────────────────
# Welcome — landing portfolio view
# ─────────────────────────────────────────────────────────────

with tab_welcome:
    # Hero
    st.markdown(
        '<div class="ql-hero">'
        '<h1 class="ql-hero-title">QuantLab</h1>'
        '<p class="ql-hero-subtitle">Interactive finance and data experiments in Python</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Stats bar
    total = len(all_projects())
    n_cats = len(PROJECTS_BY_CATEGORY)
    n_featured = len(featured())
    st.markdown(
        f'<div class="ql-stats-bar">{total} projects · {n_cats} categories · '
        f'{n_featured} featured · open source</div>',
        unsafe_allow_html=True,
    )

    # Search box
    st.markdown('<div class="ql-search-wrap">', unsafe_allow_html=True)
    search_query = st.text_input(
        "Search",
        value="",
        placeholder="Search projects by name, description, or tech…",
        label_visibility="collapsed",
        key="ql_landing_search",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Force-directed graph
    st.markdown('<div class="ql-graph-container">', unsafe_allow_html=True)
    try:
        components.html(_build_project_graph_html(), height=560, scrolling=False)
    except Exception as exc:
        st.info(f"Graph unavailable: {exc}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Featured grid
    st.markdown('<h2 class="ql-section-heading">Featured</h2>', unsafe_allow_html=True)
    featured_html = '<div class="ql-featured-grid">'
    for p in featured():
        featured_html += _featured_card_html(p)
    featured_html += '</div>'
    st.markdown(featured_html, unsafe_allow_html=True)

    # Categorised grids (filtered by search)
    for category in PROJECTS_BY_CATEGORY.keys():
        matching = [
            p for p in category_with_capstones_last(category)
            if _matches_query(p, search_query)
        ]
        if not matching:
            continue
        st.markdown(
            f'<h2 class="ql-section-heading">{_escape(category)}</h2>',
            unsafe_allow_html=True,
        )
        grid_html = '<div class="ql-cat-grid">'
        for p in matching:
            grid_html += _cat_card_html(p)
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    if search_query and not any(
        _matches_query(p, search_query) for p in all_projects()
    ):
        st.markdown(
            f'<p style="text-align:center;color:#6b6b6b;margin-top:2rem;">'
            f'No projects match "{_escape(search_query)}".</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 4rem;"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# All projects — sortable table view
# ─────────────────────────────────────────────────────────────

with tab_all:
    st.markdown(
        '<h1 class="ql-page-title">All projects</h1>'
        '<p class="ql-page-subtitle">Sortable directory of every QuantLab project</p>',
        unsafe_allow_html=True,
    )

    rows = []
    for category, projs in PROJECTS_BY_CATEGORY.items():
        for p in projs:
            rows.append({
                "Name": p.label,
                "Category": category,
                "Tech": " · ".join(p.tech),
                "Capstone": "✓" if p.is_capstone else "",
                "Link": p.page_link,
            })
    df = pd.DataFrame(rows).sort_values("Name").reset_index(drop=True)
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Link": st.column_config.LinkColumn(
                "Open",
                display_text="open →",
            ),
        },
    )

# ─────────────────────────────────────────────────────────────
# System Health — preserved from original
# ─────────────────────────────────────────────────────────────

with tab_health:
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
