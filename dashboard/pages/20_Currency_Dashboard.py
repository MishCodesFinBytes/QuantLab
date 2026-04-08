"""Currency Dashboard — live exchange rates, converter, and comparison charts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import plotly.express as px
from data import fetch_exchange_rates

st.set_page_config(page_title="Currency Dashboard", page_icon="💱", layout="wide")
st.title("Currency Dashboard")

# ── Sidebar ──────────────────────────────────────────────────────────────────
base = st.sidebar.selectbox("Base Currency", ["USD", "EUR", "GBP", "JPY", "CHF"])
ALL_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "INR", "BRL",
    "KRW", "SGD", "HKD", "SEK", "NOK", "MXN", "ZAR", "TRY", "NZD", "DKK",
]
targets = st.sidebar.multiselect(
    "Target Currencies",
    [c for c in ALL_CURRENCIES if c != base],
    default=[c for c in ["EUR", "GBP", "JPY", "CHF", "CAD"] if c != base][:4],
)
amount = st.sidebar.number_input("Amount to Convert", min_value=0.0, value=1000.0, step=100.0)

# ── Fetch Rates ──────────────────────────────────────────────────────────────
rates = fetch_exchange_rates(base)

if not rates:
    st.error("Could not fetch exchange rates. Please try again later.")
    st.stop()

# ── Conversion Calculator ────────────────────────────────────────────────────
st.subheader("Conversion Calculator")
if targets:
    cols = st.columns(min(len(targets), 4))
    for i, cur in enumerate(targets):
        rate = rates.get(cur, 0)
        cols[i % len(cols)].metric(
            f"{base} → {cur}",
            f"{amount * rate:,.2f} {cur}",
            f"Rate: {rate:.4f}",
        )
else:
    st.info("Select target currencies in the sidebar.")

# ── Bar Chart of Selected Rates ──────────────────────────────────────────────
st.subheader("Exchange Rate Comparison")
if targets:
    chart_df = pd.DataFrame(
        {"Currency": targets, "Rate": [rates.get(c, 0) for c in targets]}
    )
    fig = px.bar(
        chart_df, x="Currency", y="Rate", color="Currency",
        title=f"Exchange Rates vs {base}",
        text_auto=".4f",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Full Rate Matrix ─────────────────────────────────────────────────────────
st.subheader("Full Rate Table")
rate_df = (
    pd.DataFrame(
        {"Currency": list(rates.keys()), "Rate": list(rates.values())}
    )
    .sort_values("Currency")
    .reset_index(drop=True)
)
rate_df["Converted"] = rate_df["Rate"] * amount
st.dataframe(rate_df, use_container_width=True, height=400)
