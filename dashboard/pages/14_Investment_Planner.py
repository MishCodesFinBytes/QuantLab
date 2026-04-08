"""Investment Growth Planner."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import compound_growth

st.set_page_config(page_title="Investment Planner", page_icon="📈", layout="wide")
st.title("📈 Investment Growth Planner")
st.caption("Project how your investments grow over time with compound interest.")

# ── Sidebar inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    initial = st.number_input("Initial Investment ($)", min_value=0.0, value=10000.0, step=1000.0)
    monthly_add = st.number_input("Monthly Addition ($)", min_value=0.0, value=500.0, step=50.0)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 8.0, step=0.5)
    years = st.slider("Investment Horizon (years)", 1, 40, 20)

# ── Compute ─────────────────────────────────────────────────────────────────
schedule = compound_growth(initial, monthly_add, annual_return, years)
df = pd.DataFrame(schedule)

final_balance = df["balance"].iloc[-1]
total_contributions = df["contributions"].iloc[-1]
total_growth = df["growth"].iloc[-1]

# ── Metrics ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Final Balance", f"${final_balance:,.2f}")
c2.metric("Total Contributions", f"${total_contributions:,.2f}")
c3.metric("Total Growth", f"${total_growth:,.2f}")

# ── Stacked area chart ─────────────────────────────────────────────────────
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

# ── What-if: return rate slider ────────────────────────────────────────────
st.subheader("What-If: Compare Return Rates")
col1, col2 = st.columns([1, 3])
with col1:
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
with col2:
    st.plotly_chart(fig2, use_container_width=True)

# ── Summary table ───────────────────────────────────────────────────────────
with st.expander("Year-by-Year Schedule"):
    display_df = df.copy()
    display_df["year"] = display_df["year"].map(lambda x: f"{x:.0f}")
    for col in ["balance", "contributions", "growth"]:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
