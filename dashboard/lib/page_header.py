"""Shared page header — call at the top of every dashboard page.

Renders a typographic h1 + optional subtitle styled by the global
CSS injected from nav.render_sidebar(). One function call replaces
the per-page st.title()/st.caption() pattern.
"""

import streamlit as st


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """Render a styled page header.

    Args:
        title: page title (renders as serif Fraunces h1)
        subtitle: optional one-line tagline (renders as Inter sans, muted)
    """
    st.markdown(
        f'<h1 class="ql-page-title">{title}</h1>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<p class="ql-page-subtitle">{subtitle}</p>',
            unsafe_allow_html=True,
        )
