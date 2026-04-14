"""Portfolio Optimization -- efficient frontier via Monte Carlo simulation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data import fetch_multiple_stocks
from nav import render_sidebar
from page_header import render_page_header
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="Portfolio Optimization", page_icon="assets/logo.png", layout="wide")
render_page_header("Portfolio Optimization", "Efficient frontier, max Sharpe and min volatility portfolios")

tab_app, tab_tests = st.tabs(["App", "Tests"])

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Monte Carlo simulation:** generates thousands of random portfolio weight combinations
        - **For each portfolio:** computes annualized return and volatility from historical data
        - **Sharpe Ratio:** `(portfolio_return - risk_free_rate) / portfolio_volatility` -- higher is better
        - **Efficient frontier:** the upper-left boundary of the scatter -- best return per unit of risk
        - **Two optimal points:** Max Sharpe (best risk-adjusted return) and Min Volatility (lowest risk)
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Max Sharpe portfolio:** the weight allocation that maximizes risk-adjusted return
        - **Min Volatility portfolio:** the weight allocation that minimizes overall portfolio risk
        - **Scatter plot:** each dot is a random portfolio; color = Sharpe ratio (yellow = high, purple = low)
        - **Red/blue stars:** mark the Max Sharpe and Min Volatility portfolios on the frontier
        - **Weights expander:** shows the exact percentage allocation to each ticker for each optimal portfolio
        """)

    # -- Inputs -------------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        default_tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
        tickers = st.multiselect("Tickers", options=[
            "AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA",
            "JPM", "GS", "V", "JNJ", "XOM", "PG", "KO",
        ], default=default_tickers)

    with col2:
        period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)

    col3, col4 = st.columns(2)

    with col3:
        num_portfolios = st.slider("Simulated Portfolios", 1000, 50000, 10000, 1000)

    with col4:
        risk_free = st.number_input("Risk-Free Rate (%)", 0.0, 10.0, 4.5, 0.5) / 100

    if len(tickers) < 2:
        st.warning("Select at least 2 tickers.")
        st.stop()

    st.divider()


    @st.cache_data(show_spinner=False)
    def load_prices(tkrs: list[str], per: str) -> pd.DataFrame:
        return fetch_multiple_stocks(tkrs, per).dropna()


    with st.spinner("Fetching price data..."):
        prices = load_prices(tickers, period)

    if prices.empty or prices.shape[1] < 2:
        st.error("Could not fetch data for selected tickers.")
        st.stop()

    returns = prices.pct_change().dropna()
    mean_ret = returns.mean() * 252
    cov_matrix = returns.cov() * 252


    # -- Simulate random portfolios -----------------------------------------------
    @st.cache_data(show_spinner=False)
    def simulate(mean_r, cov, n_assets: int, n_port: int, rf: float):
        rng = np.random.default_rng(42)
        results = np.zeros((n_port, 3))
        weights_arr = np.zeros((n_port, n_assets))
        cov_np = cov.values

        for i in range(n_port):
            w = rng.random(n_assets)
            w /= w.sum()
            weights_arr[i] = w
            port_ret = np.dot(w, mean_r.values)
            port_vol = np.sqrt(np.dot(w, np.dot(cov_np, w)))
            sharpe = (port_ret - rf) / port_vol if port_vol > 0 else 0
            results[i] = [port_ret, port_vol, sharpe]

        return results, weights_arr


    with st.spinner("Running Monte Carlo simulation..."):
        results, weights_arr = simulate(mean_ret, cov_matrix, len(tickers),
                                         num_portfolios, risk_free)

    # -- Find optimal portfolios --------------------------------------------------
    max_sharpe_idx = results[:, 2].argmax()
    min_vol_idx = results[:, 1].argmin()

    st.subheader("Optimal Portfolios")
    col_ms, col_mv = st.columns(2)

    with col_ms:
        st.markdown("**Max Sharpe Ratio**")
        ms_w = weights_arr[max_sharpe_idx]
        st.metric("Return", f"{results[max_sharpe_idx, 0]:.2%}")
        st.metric("Volatility", f"{results[max_sharpe_idx, 1]:.2%}")
        st.metric("Sharpe Ratio", f"{results[max_sharpe_idx, 2]:.2f}")
        with st.expander("Weights"):
            st.dataframe(pd.DataFrame({"Ticker": tickers, "Weight": ms_w}).set_index("Ticker")
                         .style.format("{:.2%}"), use_container_width=True)

    with col_mv:
        st.markdown("**Min Volatility**")
        mv_w = weights_arr[min_vol_idx]
        st.metric("Return", f"{results[min_vol_idx, 0]:.2%}")
        st.metric("Volatility", f"{results[min_vol_idx, 1]:.2%}")
        st.metric("Sharpe Ratio", f"{results[min_vol_idx, 2]:.2f}")
        with st.expander("Weights"):
            st.dataframe(pd.DataFrame({"Ticker": tickers, "Weight": mv_w}).set_index("Ticker")
                         .style.format("{:.2%}"), use_container_width=True)

    # -- Scatter plot -------------------------------------------------------------
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=results[:, 1], y=results[:, 0], mode="markers",
        marker=dict(size=3, color=results[:, 2], colorscale="Viridis",
                    colorbar=dict(title="Sharpe"), opacity=0.6),
        name="Portfolios",
    ))
    fig.add_trace(go.Scatter(
        x=[results[max_sharpe_idx, 1]], y=[results[max_sharpe_idx, 0]],
        mode="markers", marker=dict(size=15, color="red", symbol="star"),
        name="Max Sharpe",
    ))
    fig.add_trace(go.Scatter(
        x=[results[min_vol_idx, 1]], y=[results[min_vol_idx, 0]],
        mode="markers", marker=dict(size=15, color="blue", symbol="star"),
        name="Min Vol",
    ))
    fig.update_layout(
        title="Efficient Frontier", xaxis_title="Annualized Volatility",
        yaxis_title="Annualized Return", height=550, margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_tests:
    render_test_tab("test_portfolio_optimization.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "NumPy", "Plotly", "Streamlit"])