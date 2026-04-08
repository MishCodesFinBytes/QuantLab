"""Loan Amortization Calculator."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import loan_amortization

st.set_page_config(page_title="Loan Amortization", page_icon="🏠", layout="wide")
st.title("🏠 Loan Amortization Calculator")
st.caption("Visualize how each payment splits between principal and interest over the life of a loan.")

# ── Sidebar inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    principal = st.number_input("Loan Principal ($)", min_value=0.0, value=250000.0, step=5000.0)
    annual_rate = st.slider("Annual Interest Rate (%)", 1.0, 15.0, 6.5, step=0.1)
    years = st.selectbox("Loan Term (years)", [5, 10, 15, 20, 25, 30], index=5)

# ── Compute ─────────────────────────────────────────────────────────────────
if principal <= 0:
    st.info("Enter a principal above zero to get started.")
    st.stop()

schedule = loan_amortization(principal, annual_rate, years)
df = pd.DataFrame(schedule)

monthly_payment = df["payment"].iloc[0]
total_interest = df["interest"].sum()
total_cost = principal + total_interest

# ── Metrics ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
c2.metric("Total Interest", f"${total_interest:,.2f}")
c3.metric("Total Cost", f"${total_cost:,.2f}")

# ── Stacked area chart ─────────────────────────────────────────────────────
# Cumulative sums for area chart
df["cum_principal"] = df["principal"].cumsum()
df["cum_interest"] = df["interest"].cumsum()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["period"], y=df["cum_principal"], name="Principal Paid",
    fill="tozeroy", mode="lines", line_color="#636EFA",
))
fig.add_trace(go.Scatter(
    x=df["period"], y=df["cum_interest"], name="Interest Paid",
    fill="tozeroy", mode="lines", line_color="#EF553B",
))
fig.update_layout(
    title="Cumulative Principal vs Interest Paid",
    xaxis_title="Payment Period",
    yaxis_title="Amount ($)",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# ── Per-period breakdown ────────────────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df["period"], y=df["principal"], name="Principal",
    stackgroup="one", line_color="#636EFA",
))
fig2.add_trace(go.Scatter(
    x=df["period"], y=df["interest"], name="Interest",
    stackgroup="one", line_color="#EF553B",
))
fig2.update_layout(
    title="Monthly Payment Breakdown (Principal vs Interest)",
    xaxis_title="Payment Period",
    yaxis_title="Amount ($)",
    hovermode="x unified",
)
st.plotly_chart(fig2, use_container_width=True)

# ── Full schedule ───────────────────────────────────────────────────────────
with st.expander("Full Amortization Schedule"):
    display_df = df[["period", "payment", "principal", "interest", "balance"]].copy()
    for col in ["payment", "principal", "interest", "balance"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
