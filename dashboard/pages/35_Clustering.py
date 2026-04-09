"""Clustering -- segment customers with K-Means or DBSCAN."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from nav import render_sidebar
from test_tab import render_test_tab
render_sidebar()

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN

st.set_page_config(page_title="Clustering", layout="wide")
st.title("Customer Segmentation via Clustering")

with st.expander("How it works"):
    st.markdown("""
    - **K-Means:** groups data points by minimizing distance to the nearest cluster center; you choose K (number of clusters)
    - **DBSCAN:** density-based clustering that finds arbitrarily shaped clusters and marks sparse points as noise (-1)
    - **Feature scaling:** all features are standardized (zero mean, unit variance) before clustering
    - **Elbow method:** plots inertia vs K to help pick the optimal number of clusters (look for the "bend")
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Clusters Found:** number of distinct groups identified (DBSCAN may find fewer than expected)
    - **Scatter Plot:** data points colored by cluster assignment on the first two features
    - **Elbow Chart:** inertia drops sharply then flattens -- the bend suggests the best K
    - **Cluster Profiles table:** average feature values per cluster, showing what makes each segment distinct
    """)

# -- Data source --------------------------------------------------------------
data_source = st.radio(
    "Data source",
    ["Use sample data", "Enter my own data"],
    horizontal=True,
)

if data_source == "Enter my own data":
    st.caption("Edit the table below — add, remove, or modify rows. Then choose your clustering parameters.")
    default_data = pd.DataFrame({
        "income": [45000, 85000, 32000, 120000, 55000, 92000, 28000, 150000, 67000, 43000],
        "annual_spending": [18000, 42000, 12000, 65000, 25000, 38000, 15000, 80000, 30000, 20000],
        "credit_score": [620, 750, 580, 800, 680, 720, 550, 810, 700, 640],
        "account_balance": [3000, 25000, 1500, 50000, 8000, 20000, 800, 60000, 12000, 4500],
    })
    data = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
    )
    if len(data) < 3:
        st.warning("Need at least 3 rows to cluster.")
        st.stop()
    feature_cols = list(data.columns)
else:
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
    feature_cols = ["income", "annual_spending", "credit_score", "account_balance"]

st.divider()

# -- Model parameters ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    algorithm = st.radio("Algorithm", ["K-Means", "DBSCAN"], horizontal=True)

with col2:
    n_clusters = st.slider("Number of Clusters (K-Means)", 2, 8, 4,
                            disabled=(algorithm != "K-Means"))

st.caption(f"Clustering {len(data)} rows on {len(feature_cols)} features")

# -- Clustering ---------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_clustering(_hash, values, cols, algo, k):
    df = pd.DataFrame(values, columns=cols)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    if algo == "K-Means":
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        inertias = []
        for ki in range(2, 9):
            km = KMeans(n_clusters=ki, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)
        return labels.tolist(), inertias
    else:
        model = DBSCAN(eps=1.2, min_samples=max(3, len(df) // 50))
        labels = model.fit_predict(X_scaled)
        return labels.tolist(), None

with st.spinner("Clustering..."):
    df_hash = hash(data[feature_cols].values.tobytes())
    labels, inertias = run_clustering(
        df_hash, data[feature_cols].values, feature_cols, algorithm, n_clusters
    )

data["Cluster"] = labels
actual_k = len(set(labels) - {-1})

c1, c2, c3 = st.columns(3)
c1.metric("Algorithm", algorithm)
c2.metric("Clusters Found", actual_k)
c3.metric("Data Points", len(data))

# -- Charts -------------------------------------------------------------------
x_col, y_col = feature_cols[0], feature_cols[1] if len(feature_cols) > 1 else feature_cols[0]

tab1, tab2, tab_tests = st.tabs(["Scatter Plot", "Elbow Method (K-Means)", "Tests"])

with tab1:
    plot_df = data.copy()
    plot_df["Cluster"] = plot_df["Cluster"].astype(str)
    fig = px.scatter(
        plot_df, x=x_col, y=y_col, color="Cluster",
        title=f"{x_col} vs {y_col} by Cluster",
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

with tab_tests:
    render_test_tab("test_clustering.py")

# -- Cluster profiles ---------------------------------------------------------
with st.expander("Cluster Profiles"):
    profile = data.groupby("Cluster")[feature_cols].mean().round(2)
    profile.index = profile.index.astype(str)
    profile["count"] = data.groupby("Cluster").size()
    st.dataframe(profile, use_container_width=True)

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · scikit-learn · NumPy · Plotly · Streamlit")
