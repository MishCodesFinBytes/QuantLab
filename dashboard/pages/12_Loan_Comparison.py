"""Side-by-side Loan Comparison Calculator."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import loan_amortization

st.set_page_config(page_title="Loan Comparison", page_icon="⚖️", layout="wide")
st.title("⚖️ Loan Comparison")
st.caption("Compare two loan options side by side to find the better deal.")

# ── Sidebar inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Shared")
    principal = st.number_input("Loan Principal ($)", min_value=0.0, value=250000.0, step=5000.0)

    st.header("Loan A")
    rate_a = st.slider("Rate A (%)", 1.0, 15.0, 6.5, step=0.1, key="ra")
    term_a = st.selectbox("Term A (years)", [5, 10, 15, 20, 25, 30], index=5, key="ta")

    st.header("Loan B")
    rate_b = st.slider("Rate B (%)", 1.0, 15.0, 5.0, step=0.1, key="rb")
    term_b = st.selectbox("Term B (years)", [5, 10, 15, 20, 25, 30], index=2, key="tb")

if principal <= 0:
    st.info("Enter a principal above zero to get started.")
    st.stop()

# ── Compute ─────────────────────────────────────────────────────────────────
sched_a = loan_amortization(principal, rate_a, term_a)
sched_b = loan_amortization(principal, rate_b, term_b)
df_a, df_b = pd.DataFrame(sched_a), pd.DataFrame(sched_b)

monthly_a, monthly_b = df_a["payment"].iloc[0], df_b["payment"].iloc[0]
interest_a, interest_b = df_a["interest"].sum(), df_b["interest"].sum()
total_a, total_b = principal + interest_a, principal + interest_b

# ── Side-by-side metrics ───────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    st.subheader(f"Loan A — {rate_a}% / {term_a}yr")
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly Payment", f"${monthly_a:,.2f}")
    m2.metric("Total Interest", f"${interest_a:,.2f}")
    m3.metric("Total Cost", f"${total_a:,.2f}")

with col_b:
    st.subheader(f"Loan B — {rate_b}% / {term_b}yr")
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly Payment", f"${monthly_b:,.2f}")
    m2.metric("Total Interest", f"${interest_b:,.2f}")
    m3.metric("Total Cost", f"${total_b:,.2f}")

# ── Grouped bar comparison ─────────────────────────────────────────────────
categories = ["Monthly Payment", "Total Interest", "Total Cost"]
fig = go.Figure(data=[
    go.Bar(name="Loan A", x=categories, y=[monthly_a, interest_a, total_a], marker_color="#636EFA"),
    go.Bar(name="Loan B", x=categories, y=[monthly_b, interest_b, total_b], marker_color="#EF553B"),
])
fig.update_layout(title="Loan A vs Loan B", barmode="group", yaxis_title="Amount ($)")
st.plotly_chart(fig, use_container_width=True)

# ── Balance over time ──────────────────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_a["period"], y=df_a["balance"], name="Loan A", line_color="#636EFA"))
fig2.add_trace(go.Scatter(x=df_b["period"], y=df_b["balance"], name="Loan B", line_color="#EF553B"))
fig2.update_layout(
    title="Remaining Balance Over Time",
    xaxis_title="Payment Period", yaxis_title="Balance ($)", hovermode="x unified",
)
st.plotly_chart(fig2, use_container_width=True)

# ── Month-by-month comparison ──────────────────────────────────────────────
with st.expander("Month-by-Month Comparison"):
    max_len = max(len(df_a), len(df_b))
    compare = pd.DataFrame({"period": range(1, max_len + 1)})
    for label, df in [("A", df_a), ("B", df_b)]:
        temp = df[["period", "payment", "balance"]].rename(
            columns={"payment": f"payment_{label}", "balance": f"balance_{label}"}
        )
        compare = compare.merge(temp, on="period", how="left")
    compare = compare.fillna("—")
    st.dataframe(compare, use_container_width=True, hide_index=True)
