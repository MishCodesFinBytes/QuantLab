"""Sentiment Analysis — analyze finance headlines with TextBlob or VADER."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Sentiment Analysis", page_icon="💬", layout="wide")
st.title("Headline Sentiment Analysis")

# ── Sample headlines ─────────────────────────────────────────────────────────
HEADLINES = [
    "Apple reports record quarterly revenue beating analyst expectations",
    "Federal Reserve raises interest rates by 25 basis points",
    "Tesla shares plunge 12% after disappointing delivery numbers",
    "Amazon announces massive layoffs affecting 18,000 employees",
    "NVIDIA stock surges on strong AI chip demand forecast",
    "Bank of America warns of potential recession in 2026",
    "Microsoft acquires gaming company in landmark $69B deal",
    "Oil prices crash as OPEC fails to reach production agreement",
    "Google parent Alphabet posts strong cloud revenue growth",
    "Crypto market loses $200 billion in overnight sell-off",
    "JPMorgan reports highest annual profit in banking history",
    "Housing market shows signs of recovery with rising sales",
    "Meta platforms face regulatory challenges in European Union",
    "Goldman Sachs downgrades consumer discretionary sector outlook",
    "Semiconductor stocks rally on improving supply chain conditions",
    "Inflation data comes in hotter than expected sparking sell-off",
    "Netflix subscriber growth exceeds Wall Street expectations",
    "Boeing receives largest order in company history from airlines",
]

# ── Sidebar ──────────────────────────────────────────────────────────────────
analyzer = st.sidebar.radio("Sentiment Analyzer", ["VADER", "TextBlob"])


@st.cache_data(show_spinner=False)
def compute_sentiment(headlines: list[str], method: str) -> pd.DataFrame:
    scores = []
    if method == "VADER":
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        for h in headlines:
            scores.append(sia.polarity_scores(h)["compound"])
    else:
        from textblob import TextBlob
        for h in headlines:
            scores.append(TextBlob(h).sentiment.polarity)
    df = pd.DataFrame({"Headline": headlines, "Score": scores})
    df["Label"] = df["Score"].apply(
        lambda x: "Positive" if x > 0.05 else ("Negative" if x < -0.05 else "Neutral")
    )
    return df


with st.spinner("Analyzing sentiment..."):
    df = compute_sentiment(HEADLINES, analyzer)

# ── Metrics ──────────────────────────────────────────────────────────────────
avg_score = df["Score"].mean()
pct_pos = (df["Label"] == "Positive").mean() * 100
pct_neg = (df["Label"] == "Negative").mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Average Sentiment", f"{avg_score:.3f}")
c2.metric("% Positive", f"{pct_pos:.0f}%")
c3.metric("% Negative", f"{pct_neg:.0f}%")

# ── Table ────────────────────────────────────────────────────────────────────
st.subheader("Headlines & Scores")
st.dataframe(
    df.style.applymap(
        lambda v: "color: green" if v == "Positive" else (
            "color: red" if v == "Negative" else "color: gray"),
        subset=["Label"],
    ),
    use_container_width=True, hide_index=True,
)

# ── Bar chart ────────────────────────────────────────────────────────────────
sorted_df = df.sort_values("Score")
colors = ["#2ca02c" if s > 0.05 else "#d62728" if s < -0.05 else "#999999"
          for s in sorted_df["Score"]]
short_labels = [h[:55] + "..." if len(h) > 55 else h for h in sorted_df["Headline"]]

fig = go.Figure(go.Bar(
    x=sorted_df["Score"], y=short_labels, orientation="h",
    marker_color=colors,
))
fig.update_layout(
    title=f"Headline Sentiment ({analyzer})",
    xaxis_title="Sentiment Score", height=max(400, len(HEADLINES) * 28),
    margin=dict(l=350, t=60, b=40),
)
st.plotly_chart(fig, use_container_width=True)
