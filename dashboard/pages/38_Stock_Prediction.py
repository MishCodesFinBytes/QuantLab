"""Stock Prediction -- predict next-day returns with ML features."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from page_init import setup_page
from stock_inputs import stock_input_panel
from cached_data import load_stock_data
from test_tab import render_test_tab

tab_app, tab_tests = setup_page("Stock Prediction", "Feature engineering and regression for price forecasting")

with tab_app:
    with st.expander("How it works"):
        st.markdown("""
        - **Feature engineering:** creates lagged returns, SMA ratio, 20-day volatility, RSI, and volume change from historical data
        - **Chronological split:** trains on older data, tests on recent data (no random shuffle -- avoids data leakage)
        - **Linear Regression:** fits a linear relationship between features and next-day return
        - **Random Forest:** ensemble of decision trees that captures non-linear patterns
        - **Target:** next-day return (`close_tomorrow / close_today - 1`)
        """)

    with st.expander("What the outputs mean"):
        st.markdown("""
        - **MAE (Mean Absolute Error):** average size of prediction errors -- lower is better
        - **RMSE (Root Mean Squared Error):** like MAE but penalizes large errors more heavily
        - **R-squared:** fraction of variance explained by the model; 0 = no skill, 1 = perfect (values near 0 are expected here)
        - **Actual vs Predicted chart:** overlay of real and predicted returns over time
        - **Note:** this is educational -- simple ML models cannot reliably predict stock returns
        """)

    st.warning(
        "This tool is for **educational purposes only**. Predicting stock prices with simple "
        "ML models is not reliable for real trading. Past patterns do not guarantee future results."
    )

    # -- Inputs -------------------------------------------------------------------
    ticker, period = stock_input_panel(periods=["1y", "2y", "5y"], default_period="2y")

    col3, col4 = st.columns(2)

    with col3:
        model_choice = st.radio("Model", ["Linear Regression", "Random Forest"])

    with col4:
        test_pct = st.slider("Test Size (%)", 10, 40, 20)

    if not ticker:
        st.info("Enter a ticker symbol above.")
        st.stop()

    st.divider()


    with st.spinner(f"Loading {ticker}..."):
        df = load_stock_data(ticker, period)

    if not df.empty:
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
        df = df.dropna()

    if df.empty or len(df) < 60:
        st.error(f"Insufficient data for **{ticker}**.")
        st.stop()

    FEATURES = ["Ret_Lag1", "Ret_Lag2", "Ret_Lag3", "Ret_Lag4", "Ret_Lag5",
                "SMA_Ratio", "Vol_20", "RSI", "Vol_Change"]


    # -- Train / Test (chronological) --------------------------------------------
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

    # -- Metrics ------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("MAE", f"{results['mae']:.6f}")
    c2.metric("RMSE", f"{results['rmse']:.6f}")
    c3.metric("R-squared", f"{results['r2']:.4f}")

    # -- Charts -------------------------------------------------------------------
    tab1, tab2 = st.tabs(["Actual vs Predicted (Time Series)", "Actual vs Predicted (Scatter)"])

    with tab1:
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
            title=f"{ticker} -- Actual vs Predicted Next-Day Return ({model_choice})",
            xaxis_title="Date", yaxis_title="Daily Return",
            height=500, margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig, width='stretch')

    with tab2:
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
        st.plotly_chart(fig2, width='stretch')

with tab_tests:
    render_test_tab("test_stock_prediction.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "yfinance", "scikit-learn", "Plotly", "Streamlit"])