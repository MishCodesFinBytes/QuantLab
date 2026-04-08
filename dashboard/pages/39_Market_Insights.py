"""Market Insights -- correlate headline sentiment with stock price movements."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from data import fetch_stock_history

st.set_page_config(page_title="Market Insights", layout="wide")
st.title("Market Insights -- Sentiment vs Price")

# -- Inputs -------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

with col2:
    period = st.selectbox("Period", ["3mo", "6mo", "1y"], index=1)

if not ticker:
    st.info("Enter a ticker symbol above.")
    st.stop()

st.divider()

# -- Sample headlines with dates ----------------------------------------------
SAMPLE_HEADLINES = [
    ("2025-11-01", "Apple reports record quarterly revenue beating analyst expectations"),
    ("2025-11-08", "Tech stocks rally on strong earnings season across the board"),
    ("2025-11-15", "Federal Reserve signals potential rate cuts boosting market optimism"),
    ("2025-11-22", "Supply chain disruptions threaten holiday season sales forecasts"),
    ("2025-12-01", "NASDAQ hits all-time high as AI stocks continue to surge"),
    ("2025-12-08", "Inflation data comes in hotter than expected sparking concerns"),
    ("2025-12-15", "Major banks warn of credit market deterioration ahead"),
    ("2025-12-22", "Holiday retail spending exceeds expectations lifting consumer stocks"),
    ("2026-01-05", "New year sell-off as investors rotate out of growth stocks"),
    ("2026-01-12", "Strong jobs report eases recession fears across markets"),
    ("2026-01-19", "Semiconductor shortage worsens impacting global production"),
    ("2026-01-26", "Earnings season kicks off with mixed results from mega caps"),
    ("2026-02-02", "Oil prices surge on geopolitical tensions in the Middle East"),
    ("2026-02-09", "Tech layoffs accelerate as companies focus on profitability"),
    ("2026-02-16", "Consumer confidence index falls to lowest level in six months"),
    ("2026-02-23", "Bond yields spike causing sharp equity market pullback"),
    ("2026-03-02", "AI investment boom drives venture capital to record levels"),
    ("2026-03-09", "Housing market shows surprising resilience with rising prices"),
    ("2026-03-16", "Global trade tensions escalate with new tariff announcements"),
    ("2026-03-23", "Pharmaceutical stocks surge on breakthrough drug approvals"),
]


@st.cache_data(show_spinner=False)
def score_headlines(headlines: list[tuple]) -> pd.DataFrame:
    sia = SentimentIntensityAnalyzer()
    rows = []
    for date_str, headline in headlines:
        score = sia.polarity_scores(headline)["compound"]
        rows.append({"Date": pd.Timestamp(date_str), "Headline": headline, "Sentiment": score})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_prices(tkr: str, per: str) -> pd.DataFrame:
    return fetch_stock_history(tkr, per)


sent_df = score_headlines(SAMPLE_HEADLINES)

with st.spinner(f"Loading {ticker}..."):
    price_df = load_prices(ticker, period)

if price_df.empty:
    st.error(f"No data found for **{ticker}**.")
    st.stop()

price_df["Return"] = price_df["Close"].pct_change()
price_df["Next_Return"] = price_df["Return"].shift(-1)

# -- Merge sentiment with nearest trading date --------------------------------
price_daily = price_df[["Close", "Return", "Next_Return"]].copy()
price_daily.index = price_daily.index.normalize()

merged = pd.merge_asof(
    sent_df.sort_values("Date"),
    price_daily.reset_index().rename(columns={"Date": "Trade_Date"}).sort_values("Trade_Date"),
    left_on="Date", right_on="Trade_Date", direction="nearest",
)

# -- Metrics ------------------------------------------------------------------
valid = merged.dropna(subset=["Sentiment", "Next_Return"])
if len(valid) > 2:
    corr = valid["Sentiment"].corr(valid["Next_Return"])
else:
    corr = 0.0

avg_sent = sent_df["Sentiment"].mean()
c1, c2, c3 = st.columns(3)
c1.metric("Average Sentiment", f"{avg_sent:.3f}")
c2.metric("Sentiment-Return Correlation", f"{corr:.3f}")
c3.metric("Headlines Analyzed", len(sent_df))

# -- Dual-axis chart ----------------------------------------------------------
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=price_df.index, y=price_df["Close"], name="Price",
    line=dict(color="steelblue"),
), secondary_y=False)

colors = ["#2ca02c" if s > 0 else "#d62728" for s in sent_df["Sentiment"]]
fig.add_trace(go.Bar(
    x=sent_df["Date"], y=sent_df["Sentiment"], name="Sentiment",
    marker_color=colors, opacity=0.6, width=3 * 86400000,
), secondary_y=True)

fig.update_layout(
    title=f"{ticker} Price vs Headline Sentiment",
    height=500, margin=dict(t=60, b=40),
)
fig.update_yaxes(title_text="Price ($)", secondary_y=False)
fig.update_yaxes(title_text="Sentiment Score", secondary_y=True, range=[-1, 1])
st.plotly_chart(fig, use_container_width=True)

# -- Top positive / negative headlines ----------------------------------------
tab1, tab2 = st.tabs(["Top 5 Most Positive", "Top 5 Most Negative"])

with tab1:
    top_pos = sent_df.nlargest(5, "Sentiment")[["Date", "Headline", "Sentiment"]]
    top_pos["Date"] = top_pos["Date"].dt.strftime("%Y-%m-%d")
    top_pos["Sentiment"] = top_pos["Sentiment"].map("{:.3f}".format)
    st.dataframe(top_pos, use_container_width=True, hide_index=True)

with tab2:
    top_neg = sent_df.nsmallest(5, "Sentiment")[["Date", "Headline", "Sentiment"]]
    top_neg["Date"] = top_neg["Date"].dt.strftime("%Y-%m-%d")
    top_neg["Sentiment"] = top_neg["Sentiment"].map("{:.3f}".format)
    st.dataframe(top_neg, use_container_width=True, hide_index=True)

st.caption(
    "Sentiment scores are computed using VADER on sample headlines. "
    "Correlation measures the relationship between headline sentiment and next-day stock return."
)
