"""Credit Card Payoff Calculator — two modes."""

import streamlit as st
from tech_footer import render_tech_footer
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import credit_card_payoff, credit_card_payment_for_months
from page_init import setup_page
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Credit Card Calculator", "Payoff schedule and total interest, two calculation modes")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Monthly cycle:** interest = remaining balance x monthly rate (APR / 12)
        - **Principal portion:** payment minus that month's interest goes toward the balance
        - **Balance decreases** each month as principal chips away at the debt
        - **Two modes:** calculate time-to-payoff from a fixed payment, or the payment needed for a target payoff date
        - **Formula:** `monthly_interest = balance * (APR / 12)`
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Months to Payoff:** how many months until the balance reaches zero
        - **Total Interest:** the cumulative interest paid over the life of the debt
        - **Total Amount Paid:** principal + total interest
        - **Balance Over Time chart:** shows the declining balance each month
        - **Principal vs Interest chart:** stacked bars showing how each payment splits between principal and interest
        """)

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
        st.plotly_chart(fig, width='stretch')

    with tab2:
        fig2 = px.bar(
            df, x="month", y=["principal", "interest"],
            title="Monthly Breakdown",
            labels={"value": "Amount ($)", "month": "Month", "variable": "Component"},
            barmode="stack",
        )
        st.plotly_chart(fig2, width='stretch')

    # ── Full schedule ──────────────────────────────────────────────────────────
    with st.expander("Full Amortization Schedule"):
        display_df = df.copy()
        for col in ["payment", "principal", "interest", "balance"]:
            display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
        st.dataframe(display_df, width='stretch', hide_index=True)

with tab_tests:
    render_test_tab("test_credit_card_calculator.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "NumPy", "Plotly", "Streamlit"])