"""Financial Reporting — summary statistics, returns analysis, and CSV export."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from page_init import setup_page
from stock_inputs import stock_input_panel
from cached_data import load_stock_data
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Financial Reporting", "Auto-generated stats, charts, and CSV export")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Data source:** fetches historical stock data from yfinance
        - **Daily returns:** `(close_today - close_yesterday) / close_yesterday`
        - **Cumulative return:** the compounded total return over the period
        - **Sharpe ratio:** annualized `mean(daily_return) / std(daily_return) * sqrt(252)`
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Total Return:** cumulative percentage gain or loss over the period
        - **Avg Daily Return / Volatility:** the mean and standard deviation of daily returns
        - **Sharpe Ratio:** risk-adjusted return -- higher is better; above 1.0 is generally good
        - **Returns Histogram:** distribution of daily returns; wider spread = higher volatility
        - **CSV Export:** download raw price data or summary statistics for further analysis
        """)

    # -- Inputs (main area) ------------------------------------------------------
    ticker, period = stock_input_panel()

    st.divider()

    if not ticker:
        st.info("Enter a ticker symbol above.")
        st.stop()

    # -- Fetch Data ---------------------------------------------------------------
    df = load_stock_data(ticker, period)

    if df.empty:
        st.error(f"No data found for **{ticker}**.")
        st.stop()

    # -- Compute Returns ----------------------------------------------------------
    df["Daily_Return"] = df["Close"].pct_change()
    df["Cumulative_Return"] = (1 + df["Daily_Return"]).cumprod() - 1

    # -- Key Metrics --------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    total_return = df["Cumulative_Return"].iloc[-1] * 100 if len(df) > 1 else 0
    avg_daily = df["Daily_Return"].mean() * 100
    volatility = df["Daily_Return"].std() * 100
    sharpe = (df["Daily_Return"].mean() / df["Daily_Return"].std() * (252 ** 0.5)
              if df["Daily_Return"].std() > 0 else 0)

    c1.metric("Total Return", f"{total_return:.2f}%")
    c2.metric("Avg Daily Return", f"{avg_daily:.4f}%")
    c3.metric("Daily Volatility", f"{volatility:.4f}%")
    c4.metric("Sharpe Ratio (ann.)", f"{sharpe:.2f}")

    # -- Summary Statistics -------------------------------------------------------
    with st.expander("Summary Statistics"):
        stats = df[["Open", "High", "Low", "Close", "Volume"]].describe().T
        stats["range"] = stats["max"] - stats["min"]
        st.dataframe(stats.style.format("{:.2f}"), width='stretch')

    # -- Charts -------------------------------------------------------------------
    chart_tab1, chart_tab2 = st.tabs(["Price History", "Daily Returns Distribution"])

    with chart_tab1:
        fig_price = px.line(df, x=df.index, y="Close", title=f"{ticker} Closing Price")
        fig_price.update_layout(xaxis_title="Date", yaxis_title="Price ($)")
        st.plotly_chart(fig_price, width='stretch')

    with chart_tab2:
        returns_clean = df["Daily_Return"].dropna()
        fig_hist = px.histogram(
            returns_clean, nbins=50,
            title="Daily Returns Histogram",
            labels={"value": "Daily Return", "count": "Frequency"},
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, width='stretch')

    # -- Export Data --------------------------------------------------------------
    st.subheader("Export Data")
    col_a, col_b = st.columns(2)

    with col_a:
        csv_data = df.to_csv()
        st.download_button(
            label="Download Price Data (CSV)",
            data=csv_data,
            file_name=f"{ticker}_{period}_data.csv",
            mime="text/csv",
        )

    with col_b:
        stats = df[["Open", "High", "Low", "Close", "Volume"]].describe().T
        stats["range"] = stats["max"] - stats["min"]
        csv_stats = stats.to_csv()
        st.download_button(
            label="Download Summary Stats (CSV)",
            data=csv_stats,
            file_name=f"{ticker}_{period}_stats.csv",
            mime="text/csv",
        )

with tab_tests:
    render_test_tab("test_financial_reporting.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "pandas", "Plotly", "Streamlit"])