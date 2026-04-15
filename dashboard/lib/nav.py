"""Shared sidebar navigation for all dashboard pages."""

import logging
from pathlib import Path
import streamlit as st


# Silence Streamlit deprecation noise that spams Cloud logs every page render.
# We can't migrate yet — local Streamlit is older than Cloud and the
# replacements (width="stretch", st.iframe) either don't exist locally or
# don't have a drop-in equivalent for inline HTML. Revisit when Streamlit
# ships stable replacements that work across versions.
class _DeprecationNoiseFilter(logging.Filter):
    _NOISY_SUBSTRINGS = (
        "use_container_width",
        "st.components.v1.html",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(s in msg for s in self._NOISY_SUBSTRINGS)


for _logger_name in ("streamlit", "streamlit.runtime", "streamlit.elements"):
    logging.getLogger(_logger_name).addFilter(_DeprecationNoiseFilter())

ASSETS = Path(__file__).resolve().parent.parent / "assets"


_GLOBAL_STYLES = """
<style>
:root {
    --ql-accent: #d97706;
    --ql-text: #1a1a1a;
    --ql-muted: #6b6b6b;
    --ql-bg: #ffffff;
    --ql-bg2: #fafafa;
    --ql-border: #e5e5e5;
    --ql-font-display: 'Fraunces', Georgia, serif;
    --ql-font-body: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Body font override — universal selector with !important.
   Streamlit's emotion CSS injects font-family on every wrapper class,
   so the only reliable override is to bomb everything with * !important
   and then re-set headings + icons to their proper fonts. */
* {
    font-family: var(--ql-font-body) !important;
}

/* Restore Material Icons fonts so Streamlit's sidebar collapse arrow
   and other icon-based UI elements still render as glyphs, not text. */
.material-icons, [class*="material-icons"],
.material-symbols-rounded, .material-symbols-outlined,
[data-testid="stIconMaterial"], [data-testid*="Icon"] i {
    font-family: 'Material Icons', 'Material Symbols Rounded' !important;
}

/* Target the heading elements AND any descendants (spans, etc.) because
   Streamlit wraps heading text in an inner <span> that the universal
   * { !important } rule catches directly — inheritance doesn't help when
   the override is set directly on the child. */
h1, h1 *, h2, h2 *, h3, h3 *, h4, h4 *, h5, h5 *, h6, h6 *,
.ql-page-title, .ql-page-title *,
.ql-hero-title, .ql-hero-title *,
.ql-section-heading, .ql-section-heading *,
.ql-featured-card-title, .ql-featured-card-title *,
.ql-sidebar-title, .ql-sidebar-title * {
    font-family: var(--ql-font-display) !important;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--ql-text);
}

.ql-stats-bar {
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace !important;
}

/* Page header helper classes */
.ql-page-title {
    font-family: var(--ql-font-display);
    font-size: 2rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0.5rem 0 0.25rem;
    color: var(--ql-text);
}
.ql-page-subtitle {
    font-family: var(--ql-font-body);
    font-size: 1rem;
    color: var(--ql-muted);
    margin: 0 0 1.5rem;
    font-weight: 400;
}

/* Sidebar branding */
.ql-sidebar-brand {
    padding: 0.5rem 0 0.25rem;
    margin-bottom: 0.5rem;
}
.ql-sidebar-title {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
    letter-spacing: -0.01em !important;
    line-height: 1.1 !important;
    margin: 0.5rem 0 0.2rem !important;
    padding: 0 !important;
}
.ql-sidebar-title * {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
}
/* Higher-specificity selectors that pierce Streamlit's emotion CSS
   for the sidebar brand specifically. The brand is the only h2 inside
   the sidebar's stMarkdownContainer, so this is unambiguous. */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 *,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 span {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
}
.ql-sidebar-byline {
    font-family: var(--ql-font-body);
    font-size: 0.78rem;
    color: var(--ql-muted);
    margin-top: 0.2rem;
}
.ql-sidebar-byline a {
    color: var(--ql-accent);
    text-decoration: none;
}
.ql-sidebar-byline a:hover { text-decoration: underline; }

/* Landing page hero */
.ql-hero {
    text-align: center;
    padding: 4rem 0 3rem;
    border-bottom: 1px solid var(--ql-border);
    margin-bottom: 2rem;
    background-image: radial-gradient(circle, #e8e8e8 1px, transparent 1.5px);
    background-size: 22px 22px;
    background-position: center top;
}
.ql-hero-title {
    font-family: var(--ql-font-display);
    font-size: 4.5rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    margin: 0 0 1rem;
    color: var(--ql-text);
    font-variation-settings: "opsz" 144;
}
.ql-hero-subtitle {
    font-family: var(--ql-font-body);
    font-size: 1.15rem;
    color: var(--ql-muted);
    font-weight: 400;
    margin: 0;
}

/* Section headings on the landing page */
.ql-section-heading {
    font-family: var(--ql-font-display);
    font-size: 1.75rem;
    font-weight: 500;
    color: var(--ql-text);
    margin: 3rem 0 1.25rem;
    letter-spacing: -0.01em;
}

/* Featured grid */
.ql-featured-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 1rem;
}
.ql-featured-card {
    background: var(--ql-bg);
    border: 1px solid var(--ql-border);
    border-radius: 4px;
    padding: 1.6rem 1.5rem;
    transition: border-color 0.15s;
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}
.ql-featured-card:hover { border-color: var(--ql-accent); }
.ql-featured-card-title {
    font-family: var(--ql-font-display);
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--ql-accent);
    margin: 0 0 0.5rem;
    line-height: 1.2;
    letter-spacing: -0.01em;
}
.ql-featured-card-desc {
    font-family: var(--ql-font-body);
    font-size: 0.92rem;
    line-height: 1.5;
    color: var(--ql-text);
    margin: 0 0 0.9rem;
}
.ql-featured-card-tech {
    font-family: var(--ql-font-body);
    font-size: 0.74rem;
    color: var(--ql-muted);
    letter-spacing: 0.01em;
}

/* Categorised grid */
.ql-cat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
@media (max-width: 768px) {
    .ql-featured-grid { grid-template-columns: 1fr; }
    .ql-cat-grid { grid-template-columns: 1fr; }
}
.ql-cat-card {
    background: var(--ql-bg);
    border: 1px solid var(--ql-border);
    border-radius: 4px;
    padding: 0.9rem 1rem;
    transition: border-color 0.15s;
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}
.ql-cat-card:hover { border-color: var(--ql-accent); }
.ql-cat-card-title {
    font-family: var(--ql-font-body);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ql-accent);
    margin: 0 0 0.25rem;
}
.ql-cat-card-desc {
    font-family: var(--ql-font-body);
    font-size: 0.78rem;
    color: var(--ql-text);
    margin: 0 0 0.5rem;
    line-height: 1.4;
}
.ql-cat-card-tech {
    font-family: var(--ql-font-body);
    font-size: 0.68rem;
    color: var(--ql-muted);
}
.ql-capstone-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ql-accent);
    border: 1px solid var(--ql-accent);
    padding: 1px 5px;
    border-radius: 2px;
    margin-left: 0.4rem;
    vertical-align: middle;
}

/* Stats bar under hero */
.ql-stats-bar {
    text-align: center;
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace;
    font-size: 0.78rem;
    color: var(--ql-muted);
    letter-spacing: 0.04em;
    margin: -2.5rem 0 3rem;
}

/* Search box wrapper */
.ql-search-wrap {
    max-width: 480px;
    margin: 0 auto 2rem;
}
.ql-search-wrap input[type="text"] {
    font-family: var(--ql-font-body) !important;
    border-color: var(--ql-border) !important;
    background: var(--ql-bg) !important;
    color: var(--ql-text) !important;
}
.ql-search-wrap label { display: none !important; }

/* Tech marquee — horizontal infinite scroll */
.ql-marquee-wrap {
    overflow: hidden;
    border-top: 1px solid var(--ql-border);
    border-bottom: 1px solid var(--ql-border);
    padding: 0.85rem 0;
    margin: 1.5rem 0 3rem;
    background: var(--ql-bg2);
    mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
}
.ql-marquee-track {
    display: flex;
    width: max-content;
    animation: ql-marquee-scroll 55s linear infinite;
}
.ql-marquee-content {
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace !important;
    font-size: 0.82rem;
    color: var(--ql-muted);
    letter-spacing: 0.04em;
    padding-right: 2.5rem;
    white-space: nowrap;
}
@keyframes ql-marquee-scroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}

/* Smaller, greyer text inside expanders */
[data-testid="stExpander"] details > div p,
[data-testid="stExpander"] details > div li,
[data-testid="stExpander"] details > div td,
[data-testid="stExpander"] details > div th {
    font-size: 0.86rem;
    color: var(--ql-muted);
}
[data-testid="stExpander"] details > div strong {
    color: var(--ql-text);
}
[data-testid="stExpander"] details > div table {
    font-size: 0.86rem;
}

/* Tighten sidebar page_link spacing to match the mockup.
   Structure: <a stPageLink-NavLink> > <span> > <div stMarkdownContainer>
   > <p>label</p>. Every layer can contribute spacing, so we flatten
   them all. */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    padding: 0.18rem 0.5rem !important;
    margin: 0 !important;
    min-height: 0 !important;
    line-height: 1.3 !important;
    font-size: 0.82rem !important;
    display: block !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] div,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p {
    padding: 0 !important;
    margin: 0 !important;
    min-height: 0 !important;
    line-height: 1.3 !important;
    font-size: 0.82rem !important;
}
</style>
"""


def render_sidebar():
    """Render the shared sidebar navigation. Call this at the top of every page.

    Also injects global CSS that applies to all dashboard pages — currently
    just the smaller/greyer expander-content styling.

    Wrapped in try/except because st.page_link fails in AppTest (testing mode).
    """
    # Fonts are loaded via [[theme.fontFaces]] in .streamlit/config.toml,
    # which is the only reliable way to get custom fonts into the real
    # Streamlit <head> on Cloud (cross-origin iframes block parent access).
    # Use st.html instead of st.markdown so the CSS isn't run through the
    # markdown processor — otherwise `*` characters inside the <style> block
    # (universal selector, comments, attribute selectors like [class*=...])
    # get interpreted as emphasis/list markers and the stylesheet renders as
    # raw text on the page. st.html passes HTML straight through.
    try:
        if hasattr(st, "html"):
            st.html(_GLOBAL_STYLES)
        else:
            st.markdown(_GLOBAL_STYLES, unsafe_allow_html=True)
    except Exception:
        pass
    try:
        _render_sidebar_impl()
    except Exception:
        pass  # graceful fallback in test mode


_SIDEBAR_LABEL_STYLE = (
    "font-family:'Inter',system-ui,sans-serif !important;font-size:0.7rem;"
    "text-transform:uppercase;letter-spacing:0.08em;color:#6b6b6b;"
    "margin:0.8rem 0 0.4rem;font-weight:500;"
)


def _sidebar_section_label(text: str) -> None:
    st.sidebar.markdown(
        f'<div style="{_SIDEBAR_LABEL_STYLE}">{text}</div>',
        unsafe_allow_html=True,
    )


def _render_sidebar_impl():
    # Local import to avoid a circular dependency: projects.py is a leaf
    # registry, nav.py is imported from many places.
    from projects import PROJECTS_BY_CATEGORY, category_with_capstones_last

    # Render the brand as an <h2> with a class so the descendant
    # selector .ql-sidebar-title * in _GLOBAL_STYLES forces Fraunces
    # onto the inner span Streamlit wraps the heading text in.
    # (Same pattern as .ql-hero-title *.)
    st.sidebar.markdown(
        '<h2 class="ql-sidebar-title">QuantLabs</h2>',
        unsafe_allow_html=True,
    )
    byline_style = (
        "font-family:'Inter',system-ui,sans-serif !important;font-size:0.78rem;"
        "color:#6b6b6b;margin:-0.6rem 0 0.5rem;"
    )
    link_style = "color:#d97706;text-decoration:none;"
    st.sidebar.markdown(
        f'<div style="{byline_style}">Built by '
        f'<a style="{link_style}" href="https://mish-codes.github.io/FinBytes/">Manisha</a>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Drive the sidebar from the same registry that builds the landing
    # cards so the grouping always stays in sync.
    for category in PROJECTS_BY_CATEGORY.keys():
        _sidebar_section_label(category)
        for project in category_with_capstones_last(category):
            st.sidebar.page_link(project.page_link, label=project.label)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="font-family:\'Inter\',system-ui,sans-serif !important;'
        'font-size:0.78rem;color:#6b6b6b;">'
        '<a style="color:#d97706;text-decoration:none;" '
        'href="https://github.com/mish-codes/QuantLab">GitHub</a> · '
        '<a style="color:#d97706;text-decoration:none;" '
        'href="https://mish-codes.github.io/FinBytes/">Blog</a>'
        '</div>',
        unsafe_allow_html=True,
    )
