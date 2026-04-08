"""Clustering -- segment synthetic customers with K-Means or DBSCAN."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN

st.set_page_config(page_title="Clustering", layout="wide")
st.title("Customer Segmentation via Clustering")

# -- Model parameters ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    algorithm = st.radio("Algorithm", ["K-Means", "DBSCAN"], horizontal=True)

with col2:
    n_clusters = st.slider("Number of Clusters (K-Means)", 2, 8, 4,
                            disabled=(algorithm != "K-Means"))

st.divider()

FEATURE_COLS = ["income", "annual_spending", "credit_score", "account_balance"]


# -- Generate synthetic data --------------------------------------------------
@st.cache_data(show_spinner=False)
def generate_customers(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    income = rng.normal(65000, 25000, n).clip(15000, 200000)
    spending = 0.3 * income + rng.normal(0, 8000, n)
    spending = spending.clip(2000, 150000)
    credit = rng.normal(700, 70, n).clip(300, 850)
    balance = 0.2 * income + rng.normal(0, 10000, n)
    balance = balance.clip(0, 200000)
    return pd.DataFrame({
        "income": income, "annual_spending": spending,
        "credit_score": credit, "account_balance": balance,
    })


data = generate_customers()


# -- Clustering ---------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_clustering(df: pd.DataFrame, algo: str, k: int):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURE_COLS])

    if algo == "K-Means":
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        # Elbow data
        inertias = []
        for ki in range(2, 9):
            km = KMeans(n_clusters=ki, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)
        return labels, inertias
    else:
        model = DBSCAN(eps=1.2, min_samples=8)
        labels = model.fit_predict(X_scaled)
        return labels, None


with st.spinner("Clustering..."):
    labels, inertias = run_clustering(data, algorithm, n_clusters)

data["Cluster"] = labels
actual_k = len(set(labels) - {-1})

c1, c2 = st.columns(2)
c1.metric("Algorithm", algorithm)
c2.metric("Clusters Found", actual_k)

# -- Charts -------------------------------------------------------------------
tab1, tab2 = st.tabs(["Scatter Plot", "Elbow Method (K-Means)"])

with tab1:
    plot_df = data.copy()
    plot_df["Cluster"] = plot_df["Cluster"].astype(str)

    fig = px.scatter(
        plot_df, x="income", y="annual_spending", color="Cluster",
        title="Income vs Annual Spending by Cluster",
        labels={"income": "Income ($)", "annual_spending": "Annual Spending ($)"},
        height=500, color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(margin=dict(t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if algorithm == "K-Means" and inertias is not None:
        elbow_fig = go.Figure(go.Scatter(
            x=list(range(2, 9)), y=inertias, mode="lines+markers",
            marker=dict(size=8, color="steelblue"),
        ))
        elbow_fig.add_vline(x=n_clusters, line_dash="dash", line_color="red",
                            annotation_text=f"k={n_clusters}")
        elbow_fig.update_layout(
            title="Elbow Method -- Inertia vs k",
            xaxis_title="Number of Clusters (k)", yaxis_title="Inertia",
            height=350, margin=dict(t=50, b=40),
        )
        st.plotly_chart(elbow_fig, use_container_width=True)
    else:
        st.info("Elbow method is only available for K-Means.")

# -- Cluster profiles ---------------------------------------------------------
with st.expander("Cluster Profiles"):
    profile = data.groupby("Cluster")[FEATURE_COLS].mean().round(0)
    profile.index = profile.index.astype(str)
    profile["count"] = data.groupby("Cluster").size()
    st.dataframe(
        profile.style.format({
            "income": "${:,.0f}", "annual_spending": "${:,.0f}",
            "credit_score": "{:.0f}", "account_balance": "${:,.0f}",
        }),
        use_container_width=True,
    )
