"""Investment Growth Planner -- two modes."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import compound_growth
from nav import render_sidebar
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="Investment Planner", layout="wide")
st.title("Investment Growth Planner")

with st.expander("How it works"):
    st.markdown("""
    - **Compound growth formula:** `FV = initial * (1+r)^n + monthly * ((1+r)^n - 1) / r`
    - **Each month:** your balance earns interest, then your monthly addition is deposited
    - **Reverse mode:** solves for the monthly investment needed to reach a target balance
    - **Rate comparison tab:** lets you see how a different return rate changes the outcome
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Final Balance:** projected total value at the end of the investment horizon
    - **Total Contributions:** your initial deposit plus all monthly additions
    - **Total Growth:** the compound interest earned (final balance minus contributions)
    - **Growth chart:** shaded area between contributions and total balance shows compound growth
    """)

# -- Mode selection ------------------------------------------------------------
mode = st.radio(
    "What do you want to calculate?",
    ["Project my investment growth",
     "How much should I invest monthly to reach a goal?"],
    horizontal=True,
)

st.divider()

# -- Inputs (main area) -------------------------------------------------------
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    initial = st.number_input("Initial Investment ($)", min_value=0.0, value=10000.0, step=1000.0)

with col_in2:
    annual_return = st.number_input("Annual Return (%)", min_value=1.0, max_value=15.0, value=8.0, step=0.5)
    years = st.slider("Investment Horizon (years)", 1, 40, 20)

with col_in3:
    if "project" in mode.lower():
        monthly_add = st.number_input("Monthly Addition ($)", min_value=0.0, value=500.0, step=50.0)
    else:
        target_balance = st.number_input("Target Balance ($)", min_value=1000.0, value=500000.0, step=10000.0)

# -- Compute -------------------------------------------------------------------
if "project" in mode.lower():
    schedule = compound_growth(initial, monthly_add, annual_return, years)
    df = pd.DataFrame(schedule)

    final_balance = df["balance"].iloc[-1]
    total_contributions = df["contributions"].iloc[-1]
    total_growth = df["growth"].iloc[-1]

    c1, c2, c3 = st.columns(3)
    c1.metric("Final Balance", f"${final_balance:,.2f}")
    c2.metric("Total Contributions", f"${total_contributions:,.2f}")
    c3.metric("Total Growth", f"${total_growth:,.2f}")
else:
    # Reverse-solve for monthly addition
    monthly_rate = annual_return / 100 / 12
    n_months = years * 12

    if initial >= target_balance:
        required_monthly = 0.0
    elif monthly_rate == 0:
        required_monthly = (target_balance - initial) / n_months
    else:
        fv_initial = initial * (1 + monthly_rate) ** n_months
        if fv_initial >= target_balance:
            required_monthly = 0.0
        else:
            required_monthly = (target_balance - fv_initial) * monthly_rate / ((1 + monthly_rate) ** n_months - 1)

    monthly_add = required_monthly
    schedule = compound_growth(initial, monthly_add, annual_return, years)
    df = pd.DataFrame(schedule)

    final_balance = df["balance"].iloc[-1]
    total_contributions = df["contributions"].iloc[-1]
    total_growth = df["growth"].iloc[-1]

    c1, c2, c3 = st.columns(3)
    c1.metric("Required Monthly Investment", f"${required_monthly:,.2f}")
    c2.metric("Projected Final Balance", f"${final_balance:,.2f}")
    c3.metric("Total Growth", f"${total_growth:,.2f}")

    st.info(f"To reach **${target_balance:,.0f}** in **{years} years**, invest **${required_monthly:,.2f}/month**.")

# -- Charts --------------------------------------------------------------------
tab1, tab2, tab_tests = st.tabs(["Growth Over Time", "Compare Return Rates", "Tests"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["contributions"], name="Contributions",
        fill="tozeroy", mode="lines", line_color="#636EFA",
    ))
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["balance"], name="Total Balance",
        fill="tonexty", mode="lines", line_color="#00CC96",
    ))
    fig.update_layout(
        title="Investment Growth Over Time",
        xaxis_title="Year", yaxis_title="Amount ($)", hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    alt_return = st.slider("Alternative Return (%)", 1.0, 15.0, 5.0, step=0.5, key="alt")
    alt_schedule = compound_growth(initial, monthly_add, alt_return, years)
    df_alt = pd.DataFrame(alt_schedule)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["year"], y=df["balance"],
        name=f"{annual_return}% return", mode="lines", line=dict(color="#636EFA", width=2),
    ))
    fig2.add_trace(go.Scatter(
        x=df_alt["year"], y=df_alt["balance"],
        name=f"{alt_return}% return", mode="lines", line=dict(color="#EF553B", width=2, dash="dash"),
    ))
    fig2.update_layout(
        title="Growth Comparison: Base vs Alternative Return",
        xaxis_title="Year", yaxis_title="Balance ($)", hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab_tests:
    render_test_tab("test_investment_planner.py")

# -- Summary table -------------------------------------------------------------
with st.expander("Year-by-Year Schedule"):
    display_df = df.copy()
    display_df["year"] = display_df["year"].map(lambda x: f"{x:.0f}")
    for col in ["balance", "contributions", "growth"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · NumPy · Plotly · Streamlit")
