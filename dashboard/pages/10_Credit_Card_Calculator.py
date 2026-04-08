"""Credit Card Payoff Calculator — two modes."""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import credit_card_payoff, credit_card_payment_for_months

st.set_page_config(page_title="Credit Card Calculator", page_icon="💳", layout="wide")
st.title("💳 Credit Card Payoff Calculator")

# ── Mode selection ─────────────────────────────────────────────────────────
mode = st.radio(
    "What do you want to calculate?",
    ["I know my monthly payment — how long to pay off?",
     "I want to pay off in X months — what payment do I need?"],
    horizontal=True,
)

st.divider()

# ── Inputs (main area, not sidebar) ───────────────────────────────────────
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    balance = st.number_input("Current Balance ($)", min_value=100.0, value=5000.0, step=100.0)

with col_in2:
    apr = st.number_input("APR (%)", min_value=1.0, max_value=35.0, value=19.99, step=0.5)

with col_in3:
    if "how long" in mode.lower():
        monthly_payment = st.number_input("Monthly Payment ($)", min_value=10.0, value=150.0, step=10.0)
    else:
        target_months = st.number_input("Target Months", min_value=1, max_value=360, value=24, step=1)

# ── Compute ────────────────────────────────────────────────────────────────
if "how long" in mode.lower():
    result = credit_card_payoff(balance, apr, monthly_payment)

    if result["months"] == -1:
        min_interest = balance * (apr / 100 / 12)
        st.error(
            f"Your payment of **${monthly_payment:,.2f}** doesn't cover the monthly "
            f"interest of **${min_interest:,.2f}**. Increase your payment."
        )
        st.stop()

    total_paid = balance + result["total_interest"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Months to Payoff", result["months"])
    c2.metric("Total Interest", f"${result['total_interest']:,.2f}")
    c3.metric("Total Amount Paid", f"${total_paid:,.2f}")

else:
    monthly_payment = credit_card_payment_for_months(balance, apr, target_months)
    result = credit_card_payoff(balance, apr, monthly_payment)
    total_paid = balance + result["total_interest"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Required Monthly Payment", f"${monthly_payment:,.2f}")
    c2.metric("Total Interest", f"${result['total_interest']:,.2f}")
    c3.metric("Total Amount Paid", f"${total_paid:,.2f}")

# ── Charts ─────────────────────────────────────────────────────────────────
df = pd.DataFrame(result["schedule"])

tab1, tab2 = st.tabs(["Balance Over Time", "Principal vs Interest"])

with tab1:
    fig = px.area(
        df, x="month", y="balance",
        title="Remaining Balance",
        labels={"month": "Month", "balance": "Balance ($)"},
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.bar(
        df, x="month", y=["principal", "interest"],
        title="Monthly Breakdown",
        labels={"value": "Amount ($)", "month": "Month", "variable": "Component"},
        barmode="stack",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Full schedule ──────────────────────────────────────────────────────────
with st.expander("Full Amortization Schedule"):
    display_df = df.copy()
    for col in ["payment", "principal", "interest", "balance"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
