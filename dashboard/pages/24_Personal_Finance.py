"""Personal Finance — net worth tracker with assets, liabilities, and ratios."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Personal Finance", layout="wide")
st.title("Personal Finance Dashboard")

# -- Inputs (main area) ------------------------------------------------------
monthly_income = st.number_input(
    "Monthly Income ($)", min_value=0.0, value=6000.0, step=500.0
)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Assets")
    default_assets = pd.DataFrame({
        "name": ["Savings", "Investments", "Property", "Retirement"],
        "value": [25000.0, 40000.0, 150000.0, 60000.0],
    })
    assets = st.data_editor(
        default_assets, num_rows="dynamic", key="assets_editor",
        column_config={
            "name": st.column_config.TextColumn("Asset"),
            "value": st.column_config.NumberColumn("Value ($)", min_value=0.0, format="$%.0f"),
        },
    )

with col_right:
    st.subheader("Liabilities")
    default_liabilities = pd.DataFrame({
        "name": ["Mortgage", "Student Loan", "Credit Card"],
        "value": [120000.0, 15000.0, 3000.0],
    })
    liabilities = st.data_editor(
        default_liabilities, num_rows="dynamic", key="liabilities_editor",
        column_config={
            "name": st.column_config.TextColumn("Liability"),
            "value": st.column_config.NumberColumn("Value ($)", min_value=0.0, format="$%.0f"),
        },
    )

st.divider()

# -- Calculations -------------------------------------------------------------
assets = assets.dropna(subset=["name"]).query("value > 0").reset_index(drop=True)
liabilities = liabilities.dropna(subset=["name"]).query("value > 0").reset_index(drop=True)

total_assets = assets["value"].sum() if not assets.empty else 0
total_liabilities = liabilities["value"].sum() if not liabilities.empty else 0
net_worth = total_assets - total_liabilities

monthly_expenses = total_liabilities * 0.01  # rough proxy for min payments
savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100
                if monthly_income > 0 else 0)
dti = (monthly_expenses / monthly_income * 100 if monthly_income > 0 else 0)

# -- Key Metrics --------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net Worth", f"${net_worth:,.0f}")
c2.metric("Total Assets", f"${total_assets:,.0f}")
c3.metric("Total Liabilities", f"${total_liabilities:,.0f}")
c4.metric("Savings Rate (est.)", f"{savings_rate:.1f}%")

st.metric("Debt-to-Income Ratio (est.)", f"{dti:.1f}%")

# -- Charts -------------------------------------------------------------------
bar_data = []
for _, r in assets.iterrows():
    bar_data.append({"Category": r["name"], "Value": r["value"], "Type": "Asset"})
for _, r in liabilities.iterrows():
    bar_data.append({"Category": r["name"], "Value": r["value"], "Type": "Liability"})

if bar_data:
    tab1, tab2 = st.tabs(["Assets vs Liabilities", "Net Worth Breakdown"])

    with tab1:
        bar_df = pd.DataFrame(bar_data)
        fig_bar = px.bar(
            bar_df, y="Category", x="Value", color="Type", orientation="h",
            color_discrete_map={"Asset": "#2ecc71", "Liability": "#e74c3c"},
            title="Assets & Liabilities Breakdown",
        )
        fig_bar.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        donut_data = []
        for _, r in assets.iterrows():
            donut_data.append({"Item": f"+ {r['name']}", "Value": r["value"]})
        for _, r in liabilities.iterrows():
            donut_data.append({"Item": f"- {r['name']}", "Value": r["value"]})

        if donut_data:
            donut_df = pd.DataFrame(donut_data)
            fig_donut = px.pie(
                donut_df, names="Item", values="Value", hole=0.45,
                title="Composition",
            )
            fig_donut.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True)
