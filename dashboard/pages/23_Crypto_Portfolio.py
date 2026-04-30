"""Crypto Portfolio — track holdings, allocation, and 24h changes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import pandas as pd
import plotly.express as px
from data import fetch_crypto_prices
from page_init import setup_page
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Crypto Portfolio", "Live crypto valuation, allocation pie, 24-hour change")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Price source:** fetches live prices from the CoinGecko free API
        - **Valuation:** `value = quantity * current_price` for each holding
        - **24h change:** weighted average of each coin's 24-hour percentage change, weighted by portfolio value
        - **Coin IDs:** use CoinGecko IDs (e.g., "bitcoin", "ethereum", "solana")
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Total Portfolio Value:** sum of all holdings in USD
        - **24h Weighted Change:** overall portfolio movement in the last 24 hours
        - **Allocation donut:** shows what percentage of your portfolio each coin represents
        - **Holdings Detail table:** per-coin price, value, 24h change, and market cap
        """)

    # -- Holdings Editor (main area) ----------------------------------------------
    st.subheader("Your Holdings")
    default_holdings = pd.DataFrame({
        "coin": ["bitcoin", "ethereum", "solana"],
        "quantity": [0.5, 5.0, 50.0],
    })
    holdings = st.data_editor(
        default_holdings,
        num_rows="dynamic",
        column_config={
            "coin": st.column_config.TextColumn("Coin (CoinGecko ID)"),
            "quantity": st.column_config.NumberColumn("Quantity", min_value=0.0, format="%.4f"),
        },
        key="holdings_editor",
    )

    holdings = holdings.dropna(subset=["coin"]).query("quantity > 0").reset_index(drop=True)

    st.divider()

    if holdings.empty:
        st.info("Add crypto holdings above to get started.")
        st.stop()

    # -- Fetch Prices -------------------------------------------------------------
    coin_list = holdings["coin"].str.strip().str.lower().tolist()

    with st.spinner("Fetching prices from CoinGecko..."):
        prices = fetch_crypto_prices(coin_list)

    if not prices:
        st.error("Could not fetch crypto prices. CoinGecko may be rate-limiting. Try again shortly.")
        st.stop()

    # -- Build Portfolio Table ----------------------------------------------------
    rows = []
    for _, row in holdings.iterrows():
        coin = row["coin"].strip().lower()
        info = prices.get(coin, {})
        price = info.get("usd", 0)
        change_24h = info.get("usd_24h_change", 0)
        market_cap = info.get("usd_market_cap", 0)
        value = price * row["quantity"]
        rows.append({
            "Coin": coin.title(),
            "Quantity": row["quantity"],
            "Price (USD)": price,
            "Value (USD)": value,
            "24h Change %": round(change_24h, 2) if change_24h else 0,
            "Market Cap": market_cap,
        })

    portfolio_df = pd.DataFrame(rows)
    total_value = portfolio_df["Value (USD)"].sum()

    # -- Summary Metrics ----------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Portfolio Value", f"${total_value:,.2f}")

    weighted_change = (
        (portfolio_df["Value (USD)"] * portfolio_df["24h Change %"]).sum() / total_value
        if total_value > 0 else 0
    )
    col2.metric("24h Weighted Change", f"{weighted_change:.2f}%")
    col3.metric("Assets Tracked", len(portfolio_df))

    # -- Charts -------------------------------------------------------------------
    chart_tab1, chart_tab2 = st.tabs(["Allocation by Value", "Holdings Detail"])

    with chart_tab1:
        fig = px.pie(
            portfolio_df, names="Coin", values="Value (USD)",
            hole=0.45, title="Portfolio Allocation",
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, width='stretch')

    with chart_tab2:
        st.dataframe(
            portfolio_df.style.format({
                "Quantity": "{:.4f}",
                "Price (USD)": "${:,.2f}",
                "Value (USD)": "${:,.2f}",
                "24h Change %": "{:+.2f}%",
                "Market Cap": "${:,.0f}",
            }),
            width='stretch',
        )

with tab_tests:
    render_test_tab("test_crypto_portfolio.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "CoinGecko API", "Plotly", "Streamlit"])