"""Credit Card Payoff Calculator."""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import credit_card_payoff

st.set_page_config(page_title="Credit Card Calculator", page_icon="💳", layout="wide")
st.title("💳 Credit Card Payoff Calculator")
st.caption("See how long it takes to pay off your credit card and how much interest you'll pay.")

# ── Sidebar inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    balance = st.number_input("Current Balance ($)", min_value=0.0, value=5000.0, step=100.0)
    apr = st.slider("APR (%)", min_value=5.0, max_value=30.0, value=19.99, step=0.01)
    monthly_payment = st.number_input(
        "Monthly Payment ($)", min_value=0.0, value=150.0, step=10.0
    )

# ── Compute ─────────────────────────────────────────────────────────────────
if balance <= 0:
    st.info("Enter a balance above zero to get started.")
    st.stop()

if monthly_payment <= 0:
    st.error("Monthly payment must be greater than zero.")
    st.stop()

result = credit_card_payoff(balance, apr, monthly_payment)

if result["months"] == -1:
    min_interest = balance * (apr / 100 / 12)
    st.error(
        f"Your monthly payment of **${monthly_payment:,.2f}** does not cover the "
        f"monthly interest of **${min_interest:,.2f}**. Increase your payment."
    )
    st.stop()

# ── Metrics ─────────────────────────────────────────────────────────────────
total_paid = balance + result["total_interest"]
c1, c2, c3 = st.columns(3)
c1.metric("Months to Payoff", result["months"])
c2.metric("Total Interest", f"${result['total_interest']:,.2f}")
c3.metric("Total Amount Paid", f"${total_paid:,.2f}")

# ── Balance chart ───────────────────────────────────────────────────────────
df = pd.DataFrame(result["schedule"])

fig = px.line(
    df, x="month", y="balance",
    title="Remaining Balance Over Time",
    labels={"month": "Month", "balance": "Balance ($)"},
)
fig.update_traces(fill="tozeroy", line_color="#636EFA")
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ── Interest vs Principal breakdown ─────────────────────────────────────────
fig2 = px.bar(
    df, x="month", y=["principal", "interest"],
    title="Monthly Principal vs Interest",
    labels={"value": "Amount ($)", "month": "Month", "variable": "Component"},
    barmode="stack",
)
st.plotly_chart(fig2, use_container_width=True)

# ── Full schedule ───────────────────────────────────────────────────────────
with st.expander("Full Amortization Schedule"):
    display_df = df.copy()
    for col in ["payment", "principal", "interest", "balance"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
