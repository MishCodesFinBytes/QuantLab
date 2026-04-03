import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime

from lib.api_client import check_health, submit_scan, poll_scan, get_recent_scans
from lib.charts import price_history_chart, cumulative_return_chart, drawdown_chart, weight_pie_chart
from lib.risk_colors import var_color, cvar_color, drawdown_color, volatility_color, sharpe_color

st.set_page_config(page_title="Stock Risk Scanner", page_icon="📊", layout="wide")

# --- Backend status in sidebar ---
if check_health():
    st.sidebar.success("Backend: Online")
else:
    st.sidebar.warning("Backend: Warming up...")

# --- Rate limiting ---
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0
    st.session_state.scan_reset_time = datetime.now()


def _check_rate_limit() -> bool:
    elapsed = (datetime.now() - st.session_state.scan_reset_time).total_seconds()
    if elapsed > 3600:
        st.session_state.scan_count = 0
        st.session_state.scan_reset_time = datetime.now()
    return st.session_state.scan_count < 10


# --- Precomputed sample result for instant display on first load ---
SAMPLE_RESULT = {
    "id": 0,
    "tickers": ["AAPL", "MSFT", "GOOG"],
    "weights": [0.333, 0.333, 0.334],
    "period": "1y",
    "status": "complete",
    "var_pct": -2.14,
    "cvar_pct": -3.19,
    "max_drawdown_pct": -19.37,
    "volatility_pct": 23.89,
    "sharpe_ratio": 0.61,
    "narrative": (
        "Portfolio AAPL, MSFT, GOOG: VaR -2.14%, CVaR -3.19%, "
        "Max Drawdown -19.37%, Volatility 23.89%, Sharpe 0.61. "
        "This is a moderately volatile tech-heavy portfolio with "
        "acceptable risk-adjusted returns."
    ),
    "error_message": None,
}

# --- Title ---
st.title("Stock Risk Scanner")
st.markdown(
    "Enter stock tickers and portfolio weights to analyse risk metrics "
    "with AI-powered commentary."
)

# --- Preset buttons ---
PRESETS = {
    "Tech Giants": (["AAPL", "MSFT", "GOOG"], "Tech heavyweights"),
    "Safe Haven": (["JNJ", "PG", "KO"], "Defensive consumer stocks"),
    "Balanced": (["AAPL", "JNJ", "BND"], "Growth + defense + bonds"),
}

st.markdown("#### Quick Presets")
preset_cols = st.columns(len(PRESETS))
for i, (name, (tickers, desc)) in enumerate(PRESETS.items()):
    with preset_cols[i]:
        if st.button(f"{name}", help=desc, use_container_width=True):
            st.session_state.tickers_input = ", ".join(tickers)
            st.session_state.use_equal_weights = True

# --- Custom input ---
st.markdown("#### Custom Portfolio")

tickers_input = st.text_input(
    "Tickers (comma-separated, max 5)",
    value=st.session_state.get("tickers_input", "AAPL, MSFT, GOOG"),
    key="tickers_field",
)

period = st.radio("Period", ["6mo", "1y", "2y"], index=1, horizontal=True)

# Parse tickers
raw_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = raw_tickers[:5]

if len(raw_tickers) > 5:
    st.warning("Maximum 5 tickers allowed. Using first 5.")

# Weight sliders
st.markdown("#### Portfolio Weights")

equal_weight = st.button("Equal Weight")
if equal_weight or st.session_state.get("use_equal_weights"):
    st.session_state.use_equal_weights = False
    for i, t in enumerate(tickers):
        st.session_state[f"weight_{i}"] = 100.0 / len(tickers)

weights = []
weight_cols = st.columns(len(tickers)) if tickers else []
for i, t in enumerate(tickers):
    with weight_cols[i]:
        w = st.slider(
            f"{t}",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.get(f"weight_{i}", 100.0 / max(len(tickers), 1)),
            step=1.0,
            key=f"weight_slider_{i}",
        )
        weights.append(w)

weight_sum = sum(weights)
if tickers and abs(weight_sum - 100.0) > 1.0:
    st.error(f"Weights must sum to 100% (currently {weight_sum:.0f}%)")
    can_scan = False
elif not tickers:
    can_scan = False
else:
    can_scan = True

# Normalize weights to 0-1
norm_weights = [w / 100.0 for w in weights] if weight_sum > 0 else []

# --- Scan button ---
if st.button("Scan", type="primary", disabled=not can_scan, use_container_width=True):
    if not _check_rate_limit():
        st.error("Rate limit reached — max 10 scans per hour. Try again later.")
    else:
        st.session_state.scan_count += 1

        # Validate tickers
        with st.spinner("Validating tickers..."):
            invalid = []
            for t in tickers:
                try:
                    info = yf.Ticker(t).info
                    if not info or info.get("regularMarketPrice") is None:
                        invalid.append(t)
                except Exception:
                    invalid.append(t)

            if invalid:
                st.error(
                    f"Ticker(s) not found: {', '.join(invalid)} "
                    "— check the symbols and try again."
                )
                st.stop()

        # Submit scan
        try:
            with st.status("Running scan...", expanded=True) as status:
                st.write("Submitting scan request...")
                result = submit_scan(tickers, norm_weights, period)
                scan_id = result["id"]

                st.write("Fetching market data & calculating risk...")
                scan_data = poll_scan(scan_id)

                if scan_data["status"] == "failed":
                    status.update(label="Scan failed", state="error")
                    st.error(
                        f"Scan failed: {scan_data.get('error_message', 'Unknown error')}"
                    )
                    st.stop()

                st.write("Fetching chart data...")
                prices = yf.download(
                    tickers, period=period, auto_adjust=True, progress=False
                )
                if isinstance(prices.columns, pd.MultiIndex):
                    prices = prices["Close"]
                else:
                    prices = prices[["Close"]].rename(columns={"Close": tickers[0]})
                prices = prices.dropna(how="all").ffill()

                status.update(label="Scan complete!", state="complete")

            # Store results in session state for display
            st.session_state.scan_result = scan_data
            st.session_state.scan_prices = prices
            st.session_state.scan_tickers = tickers
            st.session_state.scan_weights = norm_weights

        except requests.exceptions.ConnectionError:
            st.error("Backend is offline — please try again later.")
        except TimeoutError:
            st.error(
                "The scan is taking longer than expected — "
                "the backend may be waking up. Try again in a minute."
            )
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# --- Load sample data on first visit ---
if "scan_result" not in st.session_state:
    st.info(
        "Here's a sample scan of Tech Giants (AAPL, MSFT, GOOG). "
        "Try your own portfolio above!"
    )
    st.session_state.scan_result = SAMPLE_RESULT
    st.session_state.scan_tickers = SAMPLE_RESULT["tickers"]
    st.session_state.scan_weights = SAMPLE_RESULT["weights"]
    try:
        sample_prices = yf.download(
            SAMPLE_RESULT["tickers"], period="1y", auto_adjust=True, progress=False
        )
        if isinstance(sample_prices.columns, pd.MultiIndex):
            sample_prices = sample_prices["Close"]
        sample_prices = sample_prices.dropna(how="all").ffill()
        st.session_state.scan_prices = sample_prices
    except Exception:
        pass

# --- Display results if available ---
if "scan_result" in st.session_state:
    data = st.session_state.scan_result
    scan_tickers = st.session_state.scan_tickers
    scan_weights = st.session_state.scan_weights

    st.markdown("---")
    st.markdown("## Results")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(
            f"{var_color(data['var_pct'])} VaR (95%)",
            f"{data['var_pct']:.2f}%",
        )
    with m2:
        st.metric(
            f"{cvar_color(data['cvar_pct'])} CVaR",
            f"{data['cvar_pct']:.2f}%",
        )
    with m3:
        st.metric(
            f"{drawdown_color(data['max_drawdown_pct'])} Max Drawdown",
            f"{data['max_drawdown_pct']:.2f}%",
        )
    with m4:
        st.metric(
            f"{volatility_color(data['volatility_pct'])} Volatility",
            f"{data['volatility_pct']:.2f}%",
        )
    with m5:
        st.metric(
            f"{sharpe_color(data['sharpe_ratio'])} Sharpe",
            f"{data['sharpe_ratio']:.2f}",
        )

    # Narrative
    st.markdown("### AI Risk Narrative")
    st.info(data.get("narrative", "No narrative available."))

    # Charts
    if "scan_prices" in st.session_state:
        prices = st.session_state.scan_prices

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(
                price_history_chart(prices), use_container_width=True
            )
        with chart_col2:
            st.plotly_chart(
                cumulative_return_chart(prices, scan_weights),
                use_container_width=True,
            )

        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.plotly_chart(
                drawdown_chart(prices, scan_weights),
                use_container_width=True,
            )
        with chart_col4:
            st.plotly_chart(
                weight_pie_chart(scan_tickers, scan_weights),
                use_container_width=True,
            )

# --- Scan History ---
st.markdown("---")
with st.expander("Recent Scans"):
    history = get_recent_scans(limit=5)
    if history:
        for scan in history:
            tks = (
                ", ".join(scan["tickers"])
                if isinstance(scan["tickers"], list)
                else scan["tickers"]
            )
            st.markdown(
                f"**{tks}** — VaR: {scan.get('var_pct', 'N/A')}%, "
                f"Sharpe: {scan.get('sharpe_ratio', 'N/A')} — "
                f"_{scan.get('created_at', '')[:10]}_"
            )
    else:
        st.markdown("No recent scans available.")
