"""Loan Amortization Calculator — two modes."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import loan_amortization

st.set_page_config(page_title="Loan Amortization", layout="wide")
st.title("Loan Amortization Calculator")

# -- Mode selection ------------------------------------------------------------
mode = st.radio(
    "What do you want to calculate?",
    ["I know the loan term -- show me the schedule",
     "I know my budget -- what loan can I afford?"],
    horizontal=True,
)

st.divider()

# -- Inputs (main area) -------------------------------------------------------
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    principal = st.number_input("Loan Principal ($)", min_value=100.0, value=250000.0, step=5000.0)

with col_in2:
    annual_rate = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1)

with col_in3:
    if "term" in mode.lower():
        years = st.selectbox("Loan Term (years)", [5, 10, 15, 20, 25, 30], index=5)
    else:
        monthly_budget = st.number_input("Monthly Budget ($)", min_value=100.0, value=1600.0, step=50.0)

# -- Compute -------------------------------------------------------------------
if principal <= 0:
    st.info("Enter a principal above zero to get started.")
    st.stop()

if "term" in mode.lower():
    schedule = loan_amortization(principal, annual_rate, years)
    df = pd.DataFrame(schedule)

    monthly_payment = df["payment"].iloc[0]
    total_interest = df["interest"].sum()
    total_cost = principal + total_interest

    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    c2.metric("Total Interest", f"${total_interest:,.2f}")
    c3.metric("Total Cost", f"${total_cost:,.2f}")
else:
    # Reverse-solve: find the longest affordable term
    best_term = None
    for t in [30, 25, 20, 15, 10, 5]:
        sched = loan_amortization(principal, annual_rate, t)
        tmp = pd.DataFrame(sched)
        if tmp["payment"].iloc[0] <= monthly_budget:
            best_term = t
            break

    if best_term is None:
        min_payment = pd.DataFrame(loan_amortization(principal, annual_rate, 30))["payment"].iloc[0]
        st.error(
            f"Even a 30-year loan requires **${min_payment:,.2f}/month**, "
            f"which exceeds your budget of **${monthly_budget:,.2f}**. "
            "Increase your budget or reduce the principal."
        )
        st.stop()

    years = best_term
    schedule = loan_amortization(principal, annual_rate, years)
    df = pd.DataFrame(schedule)
    monthly_payment = df["payment"].iloc[0]
    total_interest = df["interest"].sum()
    total_cost = principal + total_interest

    c1, c2, c3 = st.columns(3)
    c1.metric("Shortest Affordable Term", f"{years} years")
    c2.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    c3.metric("Total Interest", f"${total_interest:,.2f}")

    st.info(f"With a budget of **${monthly_budget:,.2f}/month**, the shortest term you can afford is **{years} years** at **${monthly_payment:,.2f}/month**.")

# -- Charts --------------------------------------------------------------------
df["cum_principal"] = df["principal"].cumsum()
df["cum_interest"] = df["interest"].cumsum()

tab1, tab2 = st.tabs(["Cumulative Principal vs Interest", "Monthly Breakdown"])

with tab1:
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

with tab2:
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

# -- Full schedule -------------------------------------------------------------
with st.expander("Full Amortization Schedule"):
    display_df = df[["period", "payment", "principal", "interest", "balance"]].copy()
    for col in ["payment", "principal", "interest", "balance"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
