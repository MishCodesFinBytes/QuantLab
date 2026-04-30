"""Plotting Libraries Compared — same data rendered by Plotly, Matplotlib, Altair, and Bokeh."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import pandas as pd
import numpy as np
from data import fetch_stock_history
from nav import render_sidebar
from page_header import render_page_header
from test_tab import render_test_tab
from plotting import (
    compute_daily_returns,
    detect_outliers,
    plotly_line_chart,
    plotly_candlestick,
    plotly_volume_bar,
    plotly_returns_histogram,
    matplotlib_line_chart,
    matplotlib_candlestick,
    matplotlib_volume_bar,
    matplotlib_returns_histogram,
    altair_line_chart,
    altair_candlestick,
    altair_volume_bar,
    altair_returns_histogram,
    bokeh_line_chart,
    bokeh_candlestick,
    bokeh_volume_bar,
    bokeh_returns_histogram,
)

st.set_page_config(page_title="Plotting Libraries", page_icon="assets/logo.png", layout="wide")
render_sidebar()
render_page_header("Plotting Libraries Compared", "Plotly, Matplotlib, Altair, and Bokeh side-by-side")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Same dataset, four libraries:** fetch OHLCV data for any ticker, then render
          identical chart types with Plotly, Matplotlib, Altair, and Bokeh
        - **Editable data:** modify values in the table to see how each library handles
          outliers and extreme values
        - **Outlier detection:** rows with any value > 3 standard deviations from the
          column mean are flagged automatically
        - For the full comparison and outlier-handling guide, see the
          [Plotting Libraries blog post](https://mish-codes.github.io/FinBytes/tech-stack/plotting-libraries/)
        """)

    # ── Sidebar inputs ──────────────────────────────────────────────
    with st.sidebar:
        st.subheader("Data Settings")
        ticker = st.text_input("Ticker", value="AAPL").upper().strip()
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)

    if not ticker:
        st.info("Enter a ticker symbol in the sidebar.")
        st.stop()

    # ── Fetch data ──────────────────────────────────────────────────

    @st.cache_data(show_spinner="Fetching market data...")
    def load_data(tkr: str, per: str) -> pd.DataFrame:
        return fetch_stock_history(tkr, per)

    raw_df = load_data(ticker, period)
    if raw_df.empty:
        st.error(f"No data found for {ticker}.")
        st.stop()

    # ── TOP SECTION: Editable data table ────────────────────────────
    st.subheader(f"{ticker} — OHLCV Data")
    st.caption("Edit any cell to see how each library handles the change. Try spiking a Close price to simulate an outlier.")

    edited_df = st.data_editor(
        raw_df.round(2),
        width='stretch',
        num_rows="fixed",
        key="ohlcv_editor",
    )

    # ── Outlier detection ───────────────────────────────────────────
    outlier_flags = detect_outliers(edited_df)
    outlier_rows = outlier_flags.any(axis=1)
    if outlier_rows.any():
        dates = [d.strftime("%Y-%m-%d") for d in edited_df.index[outlier_rows]]
        st.warning(f"Outliers detected (>3\u03c3) on: {', '.join(dates)}")
    else:
        st.success("No outliers detected in the current data.")

    st.divider()

    # ── BOTTOM SECTION: Library tabs ────────────────────────────────
    tab_plotly, tab_mpl, tab_altair, tab_bokeh = st.tabs(
        ["Plotly", "Matplotlib", "Altair", "Bokeh"]
    )

    with tab_plotly:
        st.plotly_chart(plotly_line_chart(edited_df), width='stretch')
        st.plotly_chart(plotly_candlestick(edited_df), width='stretch')
        st.plotly_chart(plotly_volume_bar(edited_df), width='stretch')
        st.plotly_chart(plotly_returns_histogram(edited_df), width='stretch')

    with tab_mpl:
        st.pyplot(matplotlib_line_chart(edited_df))
        st.pyplot(matplotlib_candlestick(edited_df))
        st.pyplot(matplotlib_volume_bar(edited_df))
        st.pyplot(matplotlib_returns_histogram(edited_df))

    with tab_altair:
        st.altair_chart(altair_line_chart(edited_df), width='stretch')
        st.altair_chart(altair_candlestick(edited_df), width='stretch')
        st.altair_chart(altair_volume_bar(edited_df), width='stretch')
        st.altair_chart(altair_returns_histogram(edited_df), width='stretch')

    with tab_bokeh:
        from bokeh.embed import file_html
        from bokeh.resources import CDN
        import streamlit.components.v1 as components

        for chart_fn in [bokeh_line_chart, bokeh_candlestick, bokeh_volume_bar, bokeh_returns_histogram]:
            fig = chart_fn(edited_df)
            html = file_html(fig, CDN)
            components.html(html, height=400)

with tab_tests:
    render_test_tab("test_plotting_libraries.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "Plotly", "Matplotlib", "Altair", "Bokeh", "Streamlit"])
