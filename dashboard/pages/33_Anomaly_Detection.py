"""Anomaly Detection -- flag unusual returns with Z-score or Isolation Forest."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data import fetch_stock_history
from nav import render_sidebar
from test_tab import render_test_tab
render_sidebar()

st.set_page_config(page_title="Anomaly Detection", layout="wide")
st.title("Return Anomaly Detection")

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
col1, col2, col3, col4 = st.columns(4)

with col1:
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

with col2:
    period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

with col3:
    method = st.radio("Detection Method", ["Z-Score", "Isolation Forest"])

with col4:
    threshold = st.slider("Z-Score Threshold", 1.5, 4.0, 2.5, 0.1,
                           disabled=(method != "Z-Score"))

if not ticker:
    st.info("Enter a ticker symbol above.")
    st.stop()

st.divider()


@st.cache_data(show_spinner=False)
def load_returns(tkr: str, per: str) -> pd.DataFrame:
    df = fetch_stock_history(tkr, per)
    df["Return"] = df["Close"].pct_change()
    return df.dropna(subset=["Return"])


with st.spinner(f"Loading {ticker}..."):
    df = load_returns(ticker, period)

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
st.plotly_chart(fig, use_container_width=True)

# -- Anomaly dates table ------------------------------------------------------
if n_anomalies > 0:
    with st.expander("Anomaly Dates"):
        anomaly_df = outliers[["Close", "Return"]].copy()
        anomaly_df["Return"] = anomaly_df["Return"].map("{:.4%}".format)
        anomaly_df.index = anomaly_df.index.strftime("%Y-%m-%d")
        anomaly_df.index.name = "Date"
        st.dataframe(anomaly_df, use_container_width=True)
else:
    st.info("No anomalies detected with current settings.")

# -- Tests ----------------------------------------------------------------
with st.expander("Test Results"):
    render_test_tab("test_anomaly_detection.py")

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · yfinance · scikit-learn · Plotly · Streamlit")
