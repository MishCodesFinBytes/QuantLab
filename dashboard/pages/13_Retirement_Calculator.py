"""Retirement Savings Calculator with optional Monte Carlo simulation."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import retirement_projection

st.set_page_config(page_title="Retirement Calculator", page_icon="🏖️", layout="wide")
st.title("🏖️ Retirement Calculator")
st.caption("Project your retirement savings with deterministic and Monte Carlo estimates.")

# ── Sidebar inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
    retirement_age = st.number_input("Retirement Age", min_value=current_age + 1, max_value=100, value=65)
    current_savings = st.number_input("Current Savings ($)", min_value=0.0, value=50000.0, step=1000.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=500.0, step=50.0)
    expected_return = st.slider("Expected Annual Return (%)", 1.0, 12.0, 7.0, step=0.5)
    run_mc = st.checkbox("Run Monte Carlo Simulation", value=False)

    st.header("What-If Target")
    target_amount = st.number_input("Target Amount ($)", min_value=0.0, value=1000000.0, step=50000.0)

# ── Compute ─────────────────────────────────────────────────────────────────
years = retirement_age - current_age
simulations = 500 if run_mc else 0
result = retirement_projection(current_savings, monthly_contribution, expected_return, years, simulations=simulations)

# ── Metrics ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Years to Retirement", years)
c2.metric("Projected Balance", f"${result['final']:,.0f}")
total_contributed = current_savings + monthly_contribution * 12 * years
c3.metric("Total Contributions", f"${total_contributed:,.0f}")

# ── Target check ────────────────────────────────────────────────────────────
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

# ── Chart ───────────────────────────────────────────────────────────────────
months_range = list(range(len(result["deterministic"])))
ages = [current_age + m / 12 for m in months_range]

fig = go.Figure()

if run_mc and "p10" in result:
    fig.add_trace(go.Scatter(
        x=ages, y=result["p90"], mode="lines", name="P90 (optimistic)",
        line=dict(width=0), showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=ages, y=result["p10"], mode="lines", name="P10–P90 range",
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
st.plotly_chart(fig, use_container_width=True)

# ── Monte Carlo distribution ───────────────────────────────────────────────
if run_mc and "finals" in result:
    st.subheader("Monte Carlo Final Balance Distribution")
    import plotly.express as px
    fig_hist = px.histogram(
        x=result["finals"], nbins=50,
        labels={"x": "Final Balance ($)", "y": "Count"},
        title="Distribution of Final Balances (500 simulations)",
    )
    fig_hist.add_vline(x=result["final"], line_dash="dash", line_color="red",
                       annotation_text="Deterministic")
    st.plotly_chart(fig_hist, use_container_width=True)
