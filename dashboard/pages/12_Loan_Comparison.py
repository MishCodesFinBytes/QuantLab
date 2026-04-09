"""Side-by-side Loan Comparison Calculator."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import loan_amortization
from nav import render_sidebar
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="Loan Comparison", layout="wide")
st.title("Loan Comparison")

with st.expander("How it works"):
    st.markdown("""
    - **Runs full amortization** for two loans independently using the same principal
    - **Compares totals:** monthly payment, total interest, and total cost side by side
    - **Two modes:** compare two completely different loans, or the same loan at different interest rates
    - **Savings callout:** highlights which loan costs less overall and by how much
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Monthly Payment:** fixed payment for each loan option
    - **Total Interest:** cumulative interest over the life of each loan
    - **Total Cost:** principal + interest for each loan
    - **Summary chart:** grouped bars comparing the two loans on each metric
    - **Balance Over Time chart:** shows how quickly each loan's balance declines
    """)

# -- Mode selection ------------------------------------------------------------
mode = st.radio(
    "What do you want to compare?",
    ["Two specific loans",
     "Same loan at different rates (rate sensitivity)"],
    horizontal=True,
)

st.divider()

# -- Inputs (main area) -------------------------------------------------------
if "specific" in mode.lower():
    col_shared, col_a1, col_a2, col_b1, col_b2 = st.columns(5)

    with col_shared:
        principal = st.number_input("Loan Principal ($)", min_value=100.0, value=250000.0, step=5000.0)

    with col_a1:
        rate_a = st.number_input("Rate A (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1, key="ra")
    with col_a2:
        term_a = st.selectbox("Term A (years)", [5, 10, 15, 20, 25, 30], index=5, key="ta")

    with col_b1:
        rate_b = st.number_input("Rate B (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.1, key="rb")
    with col_b2:
        term_b = st.selectbox("Term B (years)", [5, 10, 15, 20, 25, 30], index=2, key="tb")
else:
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)
    with col_in1:
        principal = st.number_input("Loan Principal ($)", min_value=100.0, value=250000.0, step=5000.0)
    with col_in2:
        rate_a = st.number_input("Rate A (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1, key="rs_a")
    with col_in3:
        rate_b = st.number_input("Rate B (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.1, key="rs_b")
    with col_in4:
        term_both = st.selectbox("Loan Term (years)", [5, 10, 15, 20, 25, 30], index=5)

    term_a = term_both
    term_b = term_both

if principal <= 0:
    st.info("Enter a principal above zero to get started.")
    st.stop()

# -- Compute -------------------------------------------------------------------
sched_a = loan_amortization(principal, rate_a, term_a)
sched_b = loan_amortization(principal, rate_b, term_b)
df_a, df_b = pd.DataFrame(sched_a), pd.DataFrame(sched_b)

monthly_a, monthly_b = df_a["payment"].iloc[0], df_b["payment"].iloc[0]
interest_a, interest_b = df_a["interest"].sum(), df_b["interest"].sum()
total_a, total_b = principal + interest_a, principal + interest_b

# -- Side-by-side metrics -----------------------------------------------------
col_a, col_b = st.columns(2)
with col_a:
    st.subheader(f"Loan A -- {rate_a}% / {term_a}yr")
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly Payment", f"${monthly_a:,.2f}")
    m2.metric("Total Interest", f"${interest_a:,.2f}")
    m3.metric("Total Cost", f"${total_a:,.2f}")

with col_b:
    st.subheader(f"Loan B -- {rate_b}% / {term_b}yr")
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly Payment", f"${monthly_b:,.2f}")
    m2.metric("Total Interest", f"${interest_b:,.2f}")
    m3.metric("Total Cost", f"${total_b:,.2f}")

# -- Savings callout -----------------------------------------------------------
if total_a != total_b:
    cheaper = "A" if total_a < total_b else "B"
    savings = abs(total_a - total_b)
    st.success(f"Loan {cheaper} saves you **${savings:,.2f}** in total cost.")

# -- Charts --------------------------------------------------------------------
tab1, tab2, tab_tests = st.tabs(["Summary Comparison", "Balance Over Time", "Tests"])

with tab1:
    categories = ["Monthly Payment", "Total Interest", "Total Cost"]
    fig = go.Figure(data=[
        go.Bar(name="Loan A", x=categories, y=[monthly_a, interest_a, total_a], marker_color="#636EFA"),
        go.Bar(name="Loan B", x=categories, y=[monthly_b, interest_b, total_b], marker_color="#EF553B"),
    ])
    fig.update_layout(title="Loan A vs Loan B", barmode="group", yaxis_title="Amount ($)")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_a["period"], y=df_a["balance"], name="Loan A", line_color="#636EFA"))
    fig2.add_trace(go.Scatter(x=df_b["period"], y=df_b["balance"], name="Loan B", line_color="#EF553B"))
    fig2.update_layout(
        title="Remaining Balance Over Time",
        xaxis_title="Payment Period", yaxis_title="Balance ($)", hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab_tests:
    render_test_tab("test_loan_comparison.py")

# -- Month-by-month comparison ------------------------------------------------
with st.expander("Month-by-Month Comparison"):
    max_len = max(len(df_a), len(df_b))
    compare = pd.DataFrame({"period": range(1, max_len + 1)})
    for label, df in [("A", df_a), ("B", df_b)]:
        temp = df[["period", "payment", "balance"]].rename(
            columns={"payment": f"payment_{label}", "balance": f"balance_{label}"}
        )
        compare = compare.merge(temp, on="period", how="left")
    compare = compare.fillna("--")
    st.dataframe(compare, use_container_width=True, hide_index=True)

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · NumPy · Plotly · Streamlit")
