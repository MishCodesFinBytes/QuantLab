"""Stock Prediction — predict next-day returns with ML features."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from data import fetch_stock_history

st.set_page_config(page_title="Stock Prediction", page_icon="🔮", layout="wide")
st.title("Stock Return Prediction (ML)")

st.warning(
    "This tool is for **educational purposes only**. Predicting stock prices with simple "
    "ML models is not reliable for real trading. Past patterns do not guarantee future results."
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper().strip()
period = st.sidebar.selectbox("Period", ["1y", "2y", "5y"], index=1)
model_choice = st.sidebar.radio("Model", ["Linear Regression", "Random Forest"])
test_pct = st.sidebar.slider("Test Size (%)", 10, 40, 20)

if not ticker:
    st.info("Enter a ticker symbol in the sidebar.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_and_engineer(tkr: str, per: str) -> pd.DataFrame:
    df = fetch_stock_history(tkr, per)
    if df.empty:
        return pd.DataFrame()

    df["Return"] = df["Close"].pct_change()
    # Lagged returns
    for lag in range(1, 6):
        df[f"Ret_Lag{lag}"] = df["Return"].shift(lag)
    # SMA 20
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_Ratio"] = df["Close"] / df["SMA_20"]
    # 20-day volatility
    df["Vol_20"] = df["Return"].rolling(20).std()
    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    # Volume change
    df["Vol_Change"] = df["Volume"].pct_change()
    # Target: next-day return
    df["Target"] = df["Return"].shift(-1)

    return df.dropna()


with st.spinner(f"Loading {ticker}..."):
    df = load_and_engineer(ticker, period)

if df.empty or len(df) < 60:
    st.error(f"Insufficient data for **{ticker}**.")
    st.stop()

FEATURES = ["Ret_Lag1", "Ret_Lag2", "Ret_Lag3", "Ret_Lag4", "Ret_Lag5",
            "SMA_Ratio", "Vol_20", "RSI", "Vol_Change"]


# ── Train / Test (chronological) ────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def train_and_evaluate(data: pd.DataFrame, features: list, model_name: str, test_frac: float):
    split = int(len(data) * (1 - test_frac / 100))
    train, test = data.iloc[:split], data.iloc[split:]

    X_train, y_train = train[features], train["Target"]
    X_test, y_test = test[features], test["Target"]

    if model_name == "Linear Regression":
        model = LinearRegression()
    else:
        model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    return {
        "mae": mae, "rmse": rmse, "r2": r2,
        "test_index": test.index, "y_test": y_test.values,
        "preds": preds,
    }


with st.spinner("Training model..."):
    results = train_and_evaluate(df, FEATURES, model_choice, test_pct)

# ── Metrics ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("MAE", f"{results['mae']:.6f}")
c2.metric("RMSE", f"{results['rmse']:.6f}")
c3.metric("R-squared", f"{results['r2']:.4f}")

# ── Actual vs Predicted ─────────────────────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=results["test_index"], y=results["y_test"],
    name="Actual", line=dict(color="steelblue"),
))
fig.add_trace(go.Scatter(
    x=results["test_index"], y=results["preds"],
    name="Predicted", line=dict(color="orange", dash="dash"),
))
fig.update_layout(
    title=f"{ticker} — Actual vs Predicted Next-Day Return ({model_choice})",
    xaxis_title="Date", yaxis_title="Daily Return",
    height=500, margin=dict(t=60, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# ── Scatter: actual vs predicted ─────────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=results["y_test"], y=results["preds"], mode="markers",
    marker=dict(size=4, color="steelblue", opacity=0.5), name="Predictions",
))
min_val = min(results["y_test"].min(), results["preds"].min())
max_val = max(results["y_test"].max(), results["preds"].max())
fig2.add_trace(go.Scatter(
    x=[min_val, max_val], y=[min_val, max_val],
    mode="lines", line=dict(dash="dash", color="gray"), name="Perfect",
))
fig2.update_layout(
    title="Predicted vs Actual Scatter",
    xaxis_title="Actual Return", yaxis_title="Predicted Return",
    height=400, margin=dict(t=50, b=40),
)
st.plotly_chart(fig2, use_container_width=True)
