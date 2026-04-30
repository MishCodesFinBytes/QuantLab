"""Anomaly Detection -- flag unusual returns with Z-score or Isolation Forest."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from page_init import setup_page
from stock_inputs import stock_input_panel
from cached_data import load_stock_data
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Anomaly Detection", "Z-score and Isolation Forest on stock returns")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Z-Score method:** flags returns more than N standard deviations from the mean (`|z| > threshold`)
        - **Isolation Forest:** ML algorithm that isolates outliers by randomly partitioning data; points that are easy to isolate are anomalies
        - **Contamination (IF):** set to 5% -- expects roughly 5% of observations to be anomalies
        - **Threshold slider:** controls Z-Score sensitivity; lower = more anomalies detected
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **Total Observations:** number of trading days analyzed
        - **Anomalies Detected:** count of days flagged as unusual
        - **Anomaly Rate:** percentage of days that are anomalies
        - **Returns chart:** blue line shows normal daily returns; red dots highlight anomalous days
        - **Anomaly Dates table:** lists the flagged dates with closing price and return magnitude
        """)

    # -- Inputs -------------------------------------------------------------------
    ticker, period = stock_input_panel(periods=["3mo", "6mo", "1y", "2y", "5y"], default_period="1y")

    col3, col4 = st.columns(2)

    with col3:
        method = st.radio("Detection Method", ["Z-Score", "Isolation Forest"])

    with col4:
        threshold = st.slider("Z-Score Threshold", 1.5, 4.0, 2.5, 0.1,
                               disabled=(method != "Z-Score"))

    if not ticker:
        st.info("Enter a ticker symbol above.")
        st.stop()

    st.divider()


    with st.spinner(f"Loading {ticker}..."):
        df = load_stock_data(ticker, period)
        df["Return"] = df["Close"].pct_change()
        df = df.dropna(subset=["Return"])

    if df.empty:
        st.error(f"No data found for **{ticker}**.")
        st.stop()


    # -- Detect anomalies ---------------------------------------------------------
    @st.cache_data(show_spinner=False)
    def detect_anomalies(returns: pd.Series, meth: str, thresh: float) -> pd.Series:
        if meth == "Z-Score":
            z = (returns - returns.mean()) / returns.std()
            return z.abs() > thresh
        else:
            from sklearn.ensemble import IsolationForest
            iso = IsolationForest(contamination=0.05, random_state=42)
            preds = iso.fit_predict(returns.values.reshape(-1, 1))
            return pd.Series(preds == -1, index=returns.index)


    anomaly_mask = detect_anomalies(df["Return"], method, threshold)
    df["Anomaly"] = anomaly_mask.values

    # -- Metrics ------------------------------------------------------------------
    n_anomalies = df["Anomaly"].sum()
    pct = n_anomalies / len(df) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Observations", len(df))
    c2.metric("Anomalies Detected", int(n_anomalies))
    c3.metric("Anomaly Rate", f"{pct:.1f}%")

    # -- Chart --------------------------------------------------------------------
    normal = df[~df["Anomaly"]]
    outliers = df[df["Anomaly"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal.index, y=normal["Return"], mode="lines",
        name="Normal", line=dict(color="steelblue", width=1),
    ))
    fig.add_trace(go.Scatter(
        x=outliers.index, y=outliers["Return"], mode="markers",
        name="Anomaly", marker=dict(color="red", size=8, symbol="circle"),
    ))
    fig.update_layout(
        title=f"{ticker} Daily Returns -- Anomalies ({method})",
        xaxis_title="Date", yaxis_title="Daily Return",
        height=500, margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig, width='stretch')

    # -- Anomaly dates table ------------------------------------------------------
    if n_anomalies > 0:
        with st.expander("Anomaly Dates"):
            anomaly_df = outliers[["Close", "Return"]].copy()
            anomaly_df["Return"] = anomaly_df["Return"].map("{:.4%}".format)
            anomaly_df.index = anomaly_df.index.strftime("%Y-%m-%d")
            anomaly_df.index.name = "Date"
            st.dataframe(anomaly_df, width='stretch')
    else:
        st.info("No anomalies detected with current settings.")

with tab_tests:
    render_test_tab("test_anomaly_detection.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "scikit-learn", "Plotly", "Streamlit"])