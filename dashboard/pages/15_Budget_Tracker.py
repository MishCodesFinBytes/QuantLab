"""Interactive Budget Tracker -- two modes."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from finance import budget_summary

st.set_page_config(page_title="Budget Tracker", layout="wide")
st.title("Budget Tracker")

# -- Mode selection ------------------------------------------------------------
mode = st.radio(
    "What do you want to do?",
    ["Track my monthly budget",
     "Plan a budget from a savings target"],
    horizontal=True,
)

st.divider()

# -- Inputs (main area) -------------------------------------------------------
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    income = st.number_input("Monthly Income ($)", min_value=0.0, value=5000.0, step=100.0)

with col_in2:
    if "plan" in mode.lower():
        savings_target = st.number_input("Monthly Savings Target ($)", min_value=0.0, value=800.0, step=50.0)
    else:
        st.write("")  # spacer

with col_in3:
    if "plan" in mode.lower():
        spending_budget = income - savings_target if income > savings_target else 0.0
        st.metric("Available for Spending", f"${spending_budget:,.2f}")
    else:
        st.write("")  # spacer

# -- Editable expense table ----------------------------------------------------
st.subheader("Monthly Expenses")
st.caption("Edit the amounts below or add new categories.")

default_expenses = pd.DataFrame({
    "Category": ["Housing", "Food", "Transport", "Utilities", "Entertainment", "Savings", "Other"],
    "Amount": [1500.0, 600.0, 300.0, 200.0, 150.0, 500.0, 100.0],
})

edited_df = st.data_editor(
    default_expenses,
    num_rows="dynamic",
    column_config={
        "Category": st.column_config.TextColumn("Category", required=True),
        "Amount": st.column_config.NumberColumn("Amount ($)", min_value=0.0, format="%.2f", required=True),
    },
    use_container_width=True,
    hide_index=True,
)

# -- Build expenses dict and compute ------------------------------------------
expenses_dict = {}
for _, row in edited_df.iterrows():
    cat = str(row["Category"]).strip()
    amt = float(row["Amount"]) if pd.notna(row["Amount"]) else 0.0
    if cat:
        expenses_dict[cat] = expenses_dict.get(cat, 0) + amt

if income <= 0:
    st.info("Enter a positive income to see your budget summary.")
    st.stop()

result = budget_summary(income, expenses_dict)

st.divider()

# -- Metrics -------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Monthly Income", f"${result['income']:,.2f}")
c2.metric("Total Expenses", f"${result['total_expenses']:,.2f}")

surplus = result["surplus"]
c3.metric(
    "Surplus / Deficit",
    f"${surplus:,.2f}",
    delta=f"${surplus:,.2f}",
    delta_color="normal" if surplus >= 0 else "inverse",
)

if "plan" in mode.lower():
    if surplus >= savings_target:
        st.success(
            f"You meet your savings target of **${savings_target:,.2f}** "
            f"with **${surplus - savings_target:,.2f}** extra."
        )
    elif surplus >= 0:
        st.warning(
            f"Your surplus of **${surplus:,.2f}** is below your savings target of **${savings_target:,.2f}**. "
            f"Reduce spending by **${savings_target - surplus:,.2f}** to hit your goal."
        )
    else:
        st.error(f"You are overspending by **${abs(surplus):,.2f}** per month.")
else:
    if surplus < 0:
        st.error(f"You are overspending by **${abs(surplus):,.2f}** per month.")
    elif surplus == 0:
        st.warning("Your budget is exactly balanced with no room for unexpected costs.")
    else:
        st.success(f"You have **${surplus:,.2f}** left over each month.")

# -- Charts --------------------------------------------------------------------
breakdown_df = pd.DataFrame(result["breakdown"])

tab1, tab2 = st.tabs(["Spending by Category", "Spending as % of Income"])

with tab1:
    fig_pie = px.pie(
        breakdown_df, names="category", values="amount",
        title="Spending by Category",
        hole=0.4,
    )
    fig_pie.update_traces(textinfo="label+percent")
    st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=breakdown_df["category"], x=breakdown_df["pct"],
        orientation="h", marker_color="#636EFA",
        text=breakdown_df["pct"].map(lambda v: f"{v:.1f}%"),
        textposition="auto",
    ))
    fig_bar.update_layout(
        title="Spending as % of Income",
        xaxis_title="Percentage of Income (%)",
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -- Breakdown table -----------------------------------------------------------
with st.expander("Detailed Breakdown"):
    detail_df = breakdown_df.copy()
    detail_df["amount"] = detail_df["amount"].map(lambda x: f"${x:,.2f}")
    detail_df["pct"] = detail_df["pct"].map(lambda x: f"{x:.1f}%")
    detail_df.columns = ["Category", "Amount", "% of Income"]
    st.dataframe(detail_df, use_container_width=True, hide_index=True)
