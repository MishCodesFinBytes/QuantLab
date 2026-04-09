"""Sentiment Analysis -- analyze finance headlines with TextBlob or VADER."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from nav import render_sidebar
from test_tab import render_test_tab
render_sidebar()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("Headline Sentiment Analysis")

with st.expander("How it works"):
    st.markdown("""
    - **VADER:** rule-based sentiment scorer tuned for social media and news; outputs a compound score from -1 (most negative) to +1 (most positive)
    - **TextBlob:** simpler polarity model based on word-level sentiment lookups
    - **Thresholds:** score > 0.05 = Positive, < -0.05 = Negative, otherwise Neutral
    - **Input:** paste your own headlines or use the provided financial news samples
    """)

with st.expander("What the outputs mean"):
    st.markdown("""
    - **Average Sentiment:** the mean score across all headlines -- positive means overall optimistic tone
    - **% Positive / % Negative:** proportion of headlines classified as positive or negative
    - **Bar chart:** each headline's score sorted from most negative to most positive, color-coded
    - **Scores table:** full list with per-headline score and label (Positive / Negative / Neutral)
    """)

# -- Sample headlines ----------------------------------------------------------
DEFAULT_HEADLINES = [
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

DEFAULT_TEXT = "\n".join(DEFAULT_HEADLINES)

# -- Inputs --------------------------------------------------------------------
analyzer = st.radio("Sentiment Analyzer", ["VADER", "TextBlob"], horizontal=True)

if "headline_text" not in st.session_state:
    st.session_state["headline_text"] = DEFAULT_TEXT

headline_text = st.text_area(
    "Headlines (one per line)",
    value=st.session_state["headline_text"],
    height=250,
    key="headline_input",
)

if st.button("Reset to samples"):
    st.session_state["headline_text"] = DEFAULT_TEXT
    st.rerun()
else:
    st.session_state["headline_text"] = headline_text

HEADLINES = [line.strip() for line in headline_text.splitlines() if line.strip()]

if not HEADLINES:
    st.info("Enter at least one headline above.")
    st.stop()

st.divider()


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

# -- Metrics -------------------------------------------------------------------
avg_score = df["Score"].mean()
pct_pos = (df["Label"] == "Positive").mean() * 100
pct_neg = (df["Label"] == "Negative").mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Average Sentiment", f"{avg_score:.3f}")
c2.metric("% Positive", f"{pct_pos:.0f}%")
c3.metric("% Negative", f"{pct_neg:.0f}%")

# -- Bar chart -----------------------------------------------------------------
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

# -- Table ---------------------------------------------------------------------
with st.expander("Headlines and Scores"):
    st.dataframe(
        df.style.applymap(
            lambda v: "color: green" if v == "Positive" else (
                "color: red" if v == "Negative" else "color: gray"),
            subset=["Label"],
        ),
        use_container_width=True, hide_index=True,
    )

# -- Tests ----------------------------------------------------------------
with st.expander("Test Results"):
    render_test_tab("test_sentiment_analysis.py")

# -- Tech stack ---------------------------------------------------------------
st.markdown("---")
st.caption("**Tech:** Python · VADER · TextBlob · Plotly · Streamlit")
