"""Retirement Savings Calculator with optional Monte Carlo simulation."""

import streamlit as st
from tech_footer import render_tech_footer
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import retirement_projection
from page_init import setup_page
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Retirement Calculator", "Compound growth projection with Monte Carlo simulation")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Compound growth:** each month, balance grows by `balance * (1 + monthly_rate)` plus your contribution
        - **Monte Carlo mode:** runs 500 simulations with randomized returns to show a range of outcomes
        - **Reverse mode:** uses the future-value formula to solve for the monthly contribution needed to hit a target
        - **Formula:** `FV = PV * (1+r)^n + PMT * ((1+r)^n - 1) / r`
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Projected Balance:** your estimated savings at retirement age (deterministic path)
        - **Total Contributions:** the sum of your initial savings plus all monthly deposits
        - **P10 / P50 / P90 bands:** Monte Carlo percentile outcomes -- P10 is pessimistic, P50 median, P90 optimistic
        - **Target line:** green dotted line showing your goal; green/red message tells you if you are on track
        """)

    # -- Mode selection ------------------------------------------------------------
    mode = st.radio(
        "What do you want to calculate?",
        ["Project my retirement balance",
         "How much should I save monthly to hit a target?"],
        horizontal=True,
    )

    st.divider()

    # -- Inputs (main area) -------------------------------------------------------
    col_in1, col_in2, col_in3 = st.columns(3)

    with col_in1:
        current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
        retirement_age = st.number_input("Retirement Age", min_value=current_age + 1, max_value=100, value=65)

    with col_in2:
        current_savings = st.number_input("Current Savings ($)", min_value=0.0, value=50000.0, step=1000.0)
        expected_return = st.number_input("Expected Annual Return (%)", min_value=1.0, max_value=12.0, value=7.0, step=0.5)

    with col_in3:
        if "project" in mode.lower():
            monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0, step=50.0)
            target_amount = st.number_input("Target Amount ($)", min_value=0.0, value=1000000.0, step=50000.0)
        else:
            target_amount = st.number_input("Target Amount ($)", min_value=1000.0, value=1000000.0, step=50000.0)

    run_mc = st.checkbox("Run Monte Carlo Simulation (500 paths)", value=False)

    # -- Compute -------------------------------------------------------------------
    years = retirement_age - current_age

    if "project" in mode.lower():
        simulations = 500 if run_mc else 0
        result = retirement_projection(current_savings, monthly_contribution, expected_return, years, simulations=simulations)

        c1, c2, c3 = st.columns(3)
        c1.metric("Years to Retirement", years)
        c2.metric("Projected Balance", f"${result['final']:,.0f}")
        total_contributed = current_savings + monthly_contribution * 12 * years
        c3.metric("Total Contributions", f"${total_contributed:,.0f}")

        # Target check
        if target_amount > 0:
            if result["final"] >= target_amount:
                st.success(
                    f"You are projected to reach your target of **${target_amount:,.0f}** "
                    f"with **${result['final'] - target_amount:,.0f}** to spare."
                )
            else:
                shortfall = target_amount - result["final"]
                st.error(
                    f"You are projected to fall short of your target by **${shortfall:,.0f}**. "
                    "Consider increasing contributions or delaying retirement."
                )
    else:
        # Reverse-solve: find required monthly contribution via binary search
        monthly_rate = expected_return / 100 / 12
        n_months = years * 12

        if current_savings >= target_amount:
            required_monthly = 0.0
        elif monthly_rate == 0:
            required_monthly = (target_amount - current_savings) / n_months
        else:
            # FV = PV*(1+r)^n + PMT*((1+r)^n - 1)/r
            # Solve for PMT: PMT = (target - PV*(1+r)^n) * r / ((1+r)^n - 1)
            fv_savings = current_savings * (1 + monthly_rate) ** n_months
            if fv_savings >= target_amount:
                required_monthly = 0.0
            else:
                required_monthly = (target_amount - fv_savings) * monthly_rate / ((1 + monthly_rate) ** n_months - 1)

        monthly_contribution = required_monthly
        simulations = 500 if run_mc else 0
        result = retirement_projection(current_savings, monthly_contribution, expected_return, years, simulations=simulations)

        c1, c2, c3 = st.columns(3)
        c1.metric("Required Monthly Savings", f"${required_monthly:,.2f}")
        c2.metric("Projected Balance", f"${result['final']:,.0f}")
        total_contributed = current_savings + monthly_contribution * 12 * years
        c3.metric("Total Contributions", f"${total_contributed:,.0f}")

        st.info(f"To reach **${target_amount:,.0f}** in **{years} years**, save **${required_monthly:,.2f}/month**.")

    # -- Chart ---------------------------------------------------------------------
    months_range = list(range(len(result["deterministic"])))
    ages = [current_age + m / 12 for m in months_range]

    fig = go.Figure()

    if run_mc and "p10" in result:
        fig.add_trace(go.Scatter(
            x=ages, y=result["p90"], mode="lines", name="P90 (optimistic)",
            line=dict(width=0), showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=ages, y=result["p10"], mode="lines", name="P10-P90 range",
            fill="tonexty", fillcolor="rgba(99,110,250,0.15)", line=dict(width=0),
        ))
        fig.add_trace(go.Scatter(
            x=ages, y=result["p50"], mode="lines", name="P50 (median)",
            line=dict(color="#AB63FA", dash="dash"),
        ))

    fig.add_trace(go.Scatter(
        x=ages, y=result["deterministic"], mode="lines", name="Deterministic",
        line=dict(color="#636EFA", width=2),
    ))

    if target_amount > 0:
        fig.add_hline(y=target_amount, line_dash="dot", line_color="green",
                      annotation_text=f"Target ${target_amount:,.0f}")

    fig.update_layout(
        title="Projected Retirement Savings",
        xaxis_title="Age", yaxis_title="Balance ($)", hovermode="x unified",
    )
    st.plotly_chart(fig, width='stretch')

    # -- Monte Carlo distribution -------------------------------------------------
    if run_mc and "finals" in result:
        import plotly.express as px
        with st.expander("Monte Carlo Final Balance Distribution"):
            fig_hist = px.histogram(
                x=result["finals"], nbins=50,
                labels={"x": "Final Balance ($)", "y": "Count"},
                title="Distribution of Final Balances (500 simulations)",
            )
            fig_hist.add_vline(x=result["final"], line_dash="dash", line_color="red",
                               annotation_text="Deterministic")
            st.plotly_chart(fig_hist, width='stretch')

with tab_tests:
    render_test_tab("test_retirement_calculator.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "NumPy", "Plotly", "Streamlit"])