"""Loan Default Prediction -- classify defaults with Logistic Regression or Random Forest."""
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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

st.set_page_config(page_title="Loan Default", layout="wide")
st.title("Loan Default Prediction")

with st.expander("How it works"):
    st.markdown("""
    - **Training data:** 1,000 synthetic loan applications with features like income, credit score, debt ratio
    - **Logistic Regression:** linear model that estimates default probability from a weighted sum of features
    - **Random Forest:** ensemble of decision trees that captures non-linear relationships between features
    - **Feature importance:** shows which input variables have the most influence on the prediction
    - **Train/test split:** model is trained on one portion and evaluated on a held-out test set
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Accuracy:** percentage of correct predictions overall (default + no-default)
    - **Precision:** of those predicted as default, how many actually defaulted
    - **Recall:** of actual defaults, how many the model correctly caught
    - **Feature Importance chart:** taller bars = stronger predictors of default
    - **Confusion Matrix:** 2x2 grid showing true positives, false positives, true negatives, false negatives
    - **Prediction panel:** enter your own applicant details and get a real-time default probability
    """)

# -- Model parameters ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    model_choice = st.radio("Model", ["Logistic Regression", "Random Forest"],
                            horizontal=True)

with col2:
    test_size = st.slider("Test Size (%)", 10, 40, 20) / 100

st.divider()

FEATURES = ["income", "credit_score", "debt_ratio", "loan_amount", "employment_years"]


# -- Generate synthetic data --------------------------------------------------
@st.cache_data(show_spinner=False)
def generate_data(n: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    income = rng.normal(60000, 20000, n).clip(15000, 200000)
    credit = rng.normal(680, 80, n).clip(300, 850)
    debt = rng.beta(2, 5, n)
    amount = rng.normal(30000, 15000, n).clip(1000, 500000)
    years = rng.poisson(5, n).clip(0, 40)

    logit = (-3 + 0.00002 * (80000 - income) + 0.01 * (650 - credit)
             + 4 * debt + 0.00001 * amount - 0.08 * years)
    prob = 1 / (1 + np.exp(-logit + rng.normal(0, 0.5, n)))
    default = (prob > 0.5).astype(int)

    return pd.DataFrame({
        "income": income, "credit_score": credit, "debt_ratio": debt,
        "loan_amount": amount, "employment_years": years, "default": default,
    })


data = generate_data()


# -- Train model --------------------------------------------------------------
@st.cache_data(show_spinner=False)
def train_model(df: pd.DataFrame, model_name: str, ts: float):
    X = df[FEATURES]
    y = df["default"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ts, random_state=42)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    if model_name == "Logistic Regression":
        model = LogisticRegression(random_state=42, max_iter=1000)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)

    model.fit(X_train_s, y_train)
    preds = model.predict(X_test_s)

    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    else:
        importance = np.abs(model.coef_[0])

    return {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "cm": confusion_matrix(y_test, preds),
        "importance": importance,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "model": model,
        "scaler": scaler,
    }


with st.spinner("Training model..."):
    results = train_model(data, model_choice, test_size)

# -- Metrics ------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Accuracy", f"{results['accuracy']:.2%}")
c2.metric("Precision", f"{results['precision']:.2%}")
c3.metric("Recall", f"{results['recall']:.2%}")

# -- Feature importance & confusion matrix ------------------------------------
tab1, tab2, tab_tests = st.tabs(["Feature Importance", "Confusion Matrix", "Tests"])

with tab1:
    imp_df = pd.DataFrame({"Feature": FEATURES, "Importance": results["importance"]})
    imp_df = imp_df.sort_values("Importance")
    fig_imp = go.Figure(go.Bar(x=imp_df["Importance"], y=imp_df["Feature"],
                               orientation="h", marker_color="steelblue"))
    fig_imp.update_layout(title="Feature Importance", height=350, margin=dict(t=40, b=30))
    st.plotly_chart(fig_imp, use_container_width=True)

with tab2:
    cm = results["cm"]
    labels = ["No Default", "Default"]
    fig_cm = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels, colorscale="Blues",
        text=cm, texttemplate="%{text}", showscale=False,
    ))
    fig_cm.update_layout(title="Confusion Matrix", height=350,
                         xaxis_title="Predicted", yaxis_title="Actual",
                         margin=dict(t=40, b=30))
    st.plotly_chart(fig_cm, use_container_width=True)

with tab_tests:
    render_test_tab("test_loan_default.py")

# -- User prediction ----------------------------------------------------------
st.divider()
st.subheader("Predict for New Applicant")

inp_col1, inp_col2, inp_col3, inp_col4, inp_col5 = st.columns(5)

with inp_col1:
    inp_income = st.number_input("Income ($)", 20000, 200000, 55000, 5000)

with inp_col2:
    inp_credit = st.number_input("Credit Score", 300, 850, 680, 10)

with inp_col3:
    inp_debt = st.number_input("Debt Ratio", 0.0, 1.0, 0.35, 0.05)

with inp_col4:
    inp_amount = st.number_input("Loan Amount ($)", 1000, 500000, 25000, 1000)

with inp_col5:
    inp_years = st.number_input("Employment Years", 0, 40, 5, 1)

user_input = np.array([[inp_income, inp_credit, inp_debt, inp_amount, inp_years]])
user_scaled = results["scaler"].transform(user_input)
pred = results["model"].predict(user_scaled)[0]
prob = results["model"].predict_proba(user_scaled)[0][1]

if pred == 1:
    st.error(f"Prediction: **DEFAULT** (probability: {prob:.1%})")
else:
    st.success(f"Prediction: **NO DEFAULT** (probability of default: {prob:.1%})")

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · scikit-learn · NumPy · Plotly · Streamlit")
