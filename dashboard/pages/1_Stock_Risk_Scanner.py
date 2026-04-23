import streamlit as st
from tech_footer import render_tech_footer
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from nav import render_sidebar
from page_header import render_page_header
from test_tab import render_test_tab
render_sidebar()
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime

from lib.mermaid import render_mermaid

from lib.api_client import check_health, submit_scan, poll_scan, get_recent_scans
from lib.charts import price_history_chart, cumulative_return_chart, drawdown_chart, weight_pie_chart
from lib.risk_colors import var_color, cvar_color, drawdown_color, volatility_color, sharpe_color
from lib.ci_status import fetch_ci_status


def rag(s):
    if s == "ok": return "#28a745", "#fff"
    if s == "error": return "#dc3545", "#fff"
    return "#ffc107", "#333"

from pathlib import Path

st.set_page_config(page_title="Stock Risk Scanner | FinBytes QuantLabs", page_icon="assets/logo.png", layout="wide")

HERE = Path(__file__).parent.parent

# Custom sidebar (auto-nav is hidden)
st.sidebar.image(str(HERE / "assets" / "logo.png"), width=180)
st.sidebar.title("FinBytes QuantLabs")
st.sidebar.markdown("**Built by** [Manisha](https://mish-codes.github.io/FinBytes/)")
st.sidebar.markdown("---")
st.sidebar.markdown("### Projects")
try:
    st.sidebar.page_link("pages/1_Stock_Risk_Scanner.py", label="Stock Risk Scanner", icon="📊")
except Exception:
    st.sidebar.markdown("- Stock Risk Scanner")
st.sidebar.markdown("*More coming soon...*")
st.sidebar.markdown("---")
try:
    st.sidebar.page_link("app.py", label="System Health", icon="🩺")
except Exception:
    st.sidebar.markdown("- System Health")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "[GitHub](https://github.com/mish-codes/QuantLab) · "
    "[Blog](https://mish-codes.github.io/FinBytes/quant-lab/stock-risk-scanner/)"
)

API_URL = st.secrets.get("API_URL", "http://localhost:8000")
GITHUB_REPO = "mish-codes/QuantLab"

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


# --- Precomputed sample ---
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

# ============================================================
render_page_header("Stock Risk Scanner", "Full-stack portfolio risk analysis with FastAPI, Postgres, and Claude")

tab_app, tab_health, tab_arch, tab_tests = st.tabs(["App", "System Health", "Architecture", "Tests"])

# ============================================================
# TAB 1: APP
# ============================================================
with tab_app:
    st.markdown(
        "Enter stock tickers and portfolio weights to analyse risk metrics "
        "with AI-powered commentary."
    )

    # Preset buttons
    PRESETS = {
        "Tech Giants": (["AAPL", "MSFT", "GOOG"], "Tech heavyweights"),
        "Safe Haven": (["JNJ", "PG", "KO"], "Defensive consumer stocks"),
        "Balanced": (["AAPL", "JNJ", "BND"], "Growth + defense + bonds"),
    }

    st.markdown("#### Quick Presets")
    preset_cols = st.columns(len(PRESETS))
    for i, (name, (preset_tickers, desc)) in enumerate(PRESETS.items()):
        with preset_cols[i]:
            if st.button(f"{name}", help=desc, use_container_width=True):
                st.session_state["tickers_field"] = ", ".join(preset_tickers)

    # Custom input
    st.markdown("#### Custom Portfolio")

    tickers_input = st.text_input(
        "Tickers (comma-separated, max 5)",
        value=st.session_state.get("tickers_input", "AAPL, MSFT, GOOG"),
        key="tickers_field",
    )

    period = st.radio("Period", ["6mo", "1y", "2y"], index=1, horizontal=True)

    raw_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    tickers = raw_tickers[:5]
    if len(raw_tickers) > 5:
        st.warning("Maximum 5 tickers allowed. Using first 5.")

    # Weight sliders
    st.markdown("#### Portfolio Weights")

    current_ticker_key = ",".join(tickers)
    tickers_changed = current_ticker_key != st.session_state.get("_prev_tickers", "")
    if tickers_changed:
        st.session_state._prev_tickers = current_ticker_key

    equal_weight = st.button("Equal Weight")
    need_equal = equal_weight or tickers_changed
    eq_val = 100.0 / max(len(tickers), 1)

    weights = []
    weight_cols = st.columns(len(tickers)) if tickers else []
    for i, t in enumerate(tickers):
        with weight_cols[i]:
            default = eq_val if need_equal else st.session_state.get(f"weight_slider_{i}", eq_val)
            if need_equal:
                st.session_state[f"weight_slider_{i}"] = eq_val
            w = st.slider(
                f"{t}", min_value=0.0, max_value=100.0, value=default,
                step=1.0, key=f"weight_slider_{i}",
            )
            weights.append(w)

    weight_sum = sum(weights)
    can_scan = bool(tickers) and abs(weight_sum - 100.0) <= 1.0
    if tickers and not can_scan:
        st.error(f"Weights must sum to 100% (currently {weight_sum:.0f}%)")

    norm_weights = [w / 100.0 for w in weights] if weight_sum > 0 else []

    # Scan button
    if st.button("Scan", type="primary", disabled=not can_scan, use_container_width=True):
        if not _check_rate_limit():
            st.error("Rate limit reached — max 10 scans per hour. Try again later.")
        else:
            st.session_state.scan_count += 1
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
                    st.error(f"Ticker(s) not found: {', '.join(invalid)} — check the symbols and try again.")
                    st.stop()

            try:
                with st.status("Running scan...", expanded=True) as status:
                    st.write("Submitting scan request...")
                    result = submit_scan(tickers, norm_weights, period)
                    scan_id = result["id"]
                    st.write("Fetching market data & calculating risk...")
                    scan_data = poll_scan(scan_id)
                    if scan_data["status"] == "failed":
                        status.update(label="Scan failed", state="error")
                        st.error(f"Scan failed: {scan_data.get('error_message', 'Unknown error')}")
                        st.stop()
                    st.write("Fetching chart data...")
                    prices = yf.download(tickers, period=period, auto_adjust=True, progress=False)
                    if isinstance(prices.columns, pd.MultiIndex):
                        prices = prices["Close"]
                    else:
                        prices = prices[["Close"]].rename(columns={"Close": tickers[0]})
                    prices = prices.dropna(how="all").ffill()
                    status.update(label="Scan complete!", state="complete")
                st.session_state.scan_result = scan_data
                st.session_state.scan_prices = prices
                st.session_state.scan_tickers = tickers
                st.session_state.scan_weights = norm_weights
            except requests.exceptions.ConnectionError:
                st.error("Backend is offline — please try again later.")
            except TimeoutError:
                st.error("The scan is taking longer than expected — the backend may be waking up. Try again in a minute.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

    # Load sample on first visit
    if "scan_result" not in st.session_state:
        st.info("Here's a sample scan of Tech Giants (AAPL, MSFT, GOOG). Try your own portfolio above!")
        st.session_state.scan_result = SAMPLE_RESULT
        st.session_state.scan_tickers = SAMPLE_RESULT["tickers"]
        st.session_state.scan_weights = SAMPLE_RESULT["weights"]
        try:
            sample_prices = yf.download(SAMPLE_RESULT["tickers"], period="1y", auto_adjust=True, progress=False)
            if isinstance(sample_prices.columns, pd.MultiIndex):
                sample_prices = sample_prices["Close"]
            sample_prices = sample_prices.dropna(how="all").ffill()
            st.session_state.scan_prices = sample_prices
        except Exception:
            pass

    # Display results
    if "scan_result" in st.session_state:
        data = st.session_state.scan_result
        scan_tickers = st.session_state.scan_tickers
        scan_weights = st.session_state.scan_weights

        st.markdown("---")
        st.markdown("## Results")

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric(f"{var_color(data['var_pct'])} VaR (95%)", f"{data['var_pct']:.2f}%")
        with m2:
            st.metric(f"{cvar_color(data['cvar_pct'])} CVaR", f"{data['cvar_pct']:.2f}%")
        with m3:
            st.metric(f"{drawdown_color(data['max_drawdown_pct'])} Max Drawdown", f"{data['max_drawdown_pct']:.2f}%")
        with m4:
            st.metric(f"{volatility_color(data['volatility_pct'])} Volatility", f"{data['volatility_pct']:.2f}%")
        with m5:
            st.metric(f"{sharpe_color(data['sharpe_ratio'])} Sharpe", f"{data['sharpe_ratio']:.2f}")

        # Business insights — expandable
        with st.expander("What do these numbers mean?"):
            st.markdown("""
**VaR (95%) — "How much could I lose on a bad day?"**
On 19 out of 20 trading days, your portfolio won't drop more than this percentage. For a $100,000 portfolio with VaR of -2.14%, that's a max expected daily loss of $2,140 under normal conditions.

**CVaR — "When things go really wrong, how bad?"**
Averages the worst 5% of days. More useful than VaR for tail risk — it tells you what to actually expect when things go south, not just the threshold.

**Max Drawdown — "What's the worst drop I'd have sat through?"**
The largest peak-to-trough decline during the period. This is the *emotional* risk metric — even if long-term returns are positive, can you stomach a 20% drop? Clients often panic-sell at the bottom.

**Volatility — "How bumpy is the ride?"**
Annualised standard deviation. Higher = more uncertainty. A pension fund targets 8-12%. Tech-heavy at 24% is moderately aggressive. Not inherently bad — it's the price of higher expected returns.

**Sharpe Ratio — "Am I being paid for the risk?"**
Return per unit of risk. Above 1.0 = good (adequately compensated). Below 0.5 = you could get similar returns with less risk. Think of it as bang-for-your-buck.
            """)

        with st.expander("How to read the charts"):
            st.markdown("""
**Price History** — Each coloured line is one stock. Look for: *divergence* (one drops while others rise = diversification working), *correlation* (all move together = not truly diversified), *trends* (slope direction).

**Cumulative Return** — Your blended portfolio value over time. Above 1.0 = gained value. Below 1.0 = down. The slope tells you momentum. This is the chart to show a client.

**Drawdown** — The red area shows how far the portfolio dropped from its peak at every point. Look for: *depth* (how far down), *duration* (how long the red lasts), *frequency* (many dips or one big one).

**Allocation Pie** — Your weight split. If one slice dominates, a single stock's bad day becomes the portfolio's bad day.

**Reading a scan result:** Start with Sharpe (is risk worth it?) → check drawdown (can you tolerate the worst dip?) → look at the price chart (are stocks correlated?) → read the AI narrative.
            """)

        st.markdown("### AI Risk Narrative")
        st.info(data.get("narrative", "No narrative available."))
        st.caption(
            "Currently showing a **formatted summary** of the metrics. "
            "When the Claude API is enabled, this section provides a rich, "
            "plain-English risk assessment — for example:"
        )
        st.markdown(
            "> *\"This tech-heavy portfolio carries moderate risk. The 95% VaR of "
            "-2.14% means you could lose up to 2.14% on a typical bad day. The max "
            "drawdown of -19.37% is notable — during the worst stretch, the portfolio "
            "fell nearly a fifth from its peak. With a Sharpe ratio of 0.61, the "
            "risk-adjusted returns are below the 1.0 threshold, suggesting the "
            "volatility isn't being adequately compensated. Consider diversifying "
            "beyond tech to reduce concentration risk.\"*"
        )

        if "scan_prices" in st.session_state:
            prices = st.session_state.scan_prices
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(price_history_chart(prices), use_container_width=True)
            with c2:
                st.plotly_chart(cumulative_return_chart(prices, scan_weights), use_container_width=True)
            c3, c4 = st.columns(2)
            with c3:
                st.plotly_chart(drawdown_chart(prices, scan_weights), use_container_width=True)
            with c4:
                st.plotly_chart(weight_pie_chart(scan_tickers, scan_weights), use_container_width=True)

    # Scan History
    st.markdown("---")
    with st.expander("Recent Scans"):
        history = get_recent_scans(limit=5)
        if history:
            for s in history:
                tks = ", ".join(s["tickers"]) if isinstance(s["tickers"], list) else s["tickers"]
                st.markdown(f"**{tks}** — VaR: {s.get('var_pct', 'N/A')}%, Sharpe: {s.get('sharpe_ratio', 'N/A')} — _{s.get('created_at', '')[:10]}_")
        else:
            st.markdown("No recent scans available.")


# ============================================================
# TAB 2: SYSTEM HEALTH
# ============================================================
with tab_health:
    st.markdown("Live status of all services. Click **Run Checks** to test connectivity.")

    if st.button("Run Checks", type="primary", key="run_checks"):
        st.session_state.health_checked = True

    if st.session_state.get("health_checked"):
        # API check
        api_status = {"status": "unknown", "detail": ""}
        try:
            r = requests.get(f"{API_URL}/health", timeout=15)
            api_status = {"status": "ok", "detail": "API is responding"} if r.ok else {"status": "error", "detail": f"HTTP {r.status_code}"}
        except requests.exceptions.ConnectionError:
            api_status = {"status": "error", "detail": "Cannot connect — backend may be sleeping (Render free tier)"}
        except Exception as e:
            api_status = {"status": "error", "detail": str(e)}

        # DB check
        db_status = {"status": "unknown", "database": ""}
        try:
            r = requests.get(f"{API_URL}/api/health/db", timeout=15)
            db_status = r.json()
        except Exception as e:
            db_status = {"status": "error", "database": str(e)}

        # CI check
        ci_status = fetch_ci_status()

        # Status cards
        st.markdown("### Service Status")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("**API**")
            if api_status["status"] == "ok":
                st.success("Online")
            else:
                st.error("Offline")
            st.caption(api_status.get("detail", ""))
        with c2:
            st.markdown("**Database**")
            if db_status.get("status") == "ok":
                st.success("Connected")
            else:
                st.error("Disconnected")
            st.caption(db_status.get("database", db_status.get("detail", "")))
        with c3:
            st.markdown("**CI Pipeline**")
            if ci_status["status"] == "ok":
                st.success(f"Passing (#{ci_status.get('run_number', '?')})")
            elif ci_status["status"] == "error":
                st.error(f"Failing (#{ci_status.get('run_number', '?')})")
            else:
                st.warning("Unknown")
            if ci_status.get("url"):
                st.caption(f"[View run]({ci_status['url']}) — {ci_status.get('created_at', '')}")
        with c4:
            st.markdown("**Dashboard**")
            st.success("Running")
            st.caption("You're seeing this page")

        # RAG Mermaid pipeline
        api_bg, api_fg = rag(api_status["status"])
        db_bg, db_fg = rag(db_status.get("status", "unknown"))
        ci_bg, ci_fg = rag(ci_status["status"])

        # Store health results for Architecture tab pipeline
        st.session_state._health_api = api_status["status"]
        st.session_state._health_db = db_status.get("status", "unknown")
        st.session_state._health_ci = ci_status["status"]

        # Test runner
        st.markdown("### Test Suite — 35 tests (27 backend + 8 dashboard)")

        ci_passing = ci_status.get("conclusion") == "success" if ci_status.get("status") != "unknown" else None

        if ci_passing is True:
            st.success("All 35 tests passing")
        elif ci_passing is False:
            st.error("Some tests failing — check CI for details")
        else:
            st.info("CI status unavailable — showing test inventory")

        st.markdown("#### Backend Tests (27)")
        TEST_MODULES = {
            "🌐 API Endpoints (test_api.py)": [
                ("test_health", "GET /health returns 200"),
                ("test_db_connected", "GET /api/health/db returns connected"),
                ("test_returns_pending", "POST /api/scan returns 202 + pending"),
                ("test_returns_scan_by_id", "GET /api/scans/{id} returns scan"),
                ("test_returns_404_for_missing_id", "GET /api/scans/9999 returns 404"),
                ("test_returns_list", "GET /api/scans returns list"),
            ],
            "🗄️ Database Layer (test_db_layer.py)": [
                ("test_creates_pending_record", "Insert pending scan record"),
                ("test_updates_to_complete", "Update scan to complete with metrics"),
                ("test_updates_to_failed", "Update scan to failed with error"),
                ("test_returns_record_by_id", "Fetch scan by ID"),
                ("test_returns_none_for_missing_id", "Returns None for missing ID"),
                ("test_returns_completed_scans_newest_first", "Recent scans ordered newest first"),
            ],
            "📋 Pydantic Models (test_models.py)": [
                ("test_valid_request", "Valid request accepted"),
                ("test_tickers_uppercased", "Tickers auto-uppercased"),
                ("test_mismatched_lengths_raises", "Mismatched tickers/weights raises ValueError"),
                ("test_weights_not_summing_to_one_raises", "Bad weight sum raises ValueError"),
                ("test_risk_metrics_fields", "RiskMetrics stores all 5 fields"),
                ("test_scan_result_fields", "ScanResult stores all fields"),
            ],
            "📊 Risk Calculations (test_risk.py)": [
                ("test_var_and_cvar", "VaR is negative, CVaR worse than VaR"),
                ("test_max_drawdown", "Max drawdown calculation correct"),
                ("test_sharpe_ratio_sign", "Sharpe positive for uptrend, negative for downtrend"),
            ],
            "📈 Market Data (test_market_data.py)": [
                ("test_successful_fetch", "yfinance download returns correct DataFrame"),
                ("test_empty_data_raises", "Empty data raises ValueError"),
            ],
            "🤖 AI Narrative (test_narrative.py)": [
                ("test_generate_with_api", "Claude API returns narrative"),
                ("test_generate_api_error_returns_fallback", "API error returns fallback string"),
                ("test_generate_no_api_key_returns_fallback", "No API key returns fallback string"),
            ],
            "🔄 Scanner Pipeline (test_scanner.py)": [
                ("test_full_pipeline", "Full pipeline: fetch → risk → narrative → result"),
            ],
        }

        for module_name, tests in TEST_MODULES.items():
            tc = len(tests)
            if ci_passing is True:
                header = f"{module_name} — ✅ {tc}/{tc} passed"
            elif ci_passing is False:
                header = f"{module_name} — ⚠️ {tc} tests (check CI)"
            else:
                header = f"{module_name} — {tc} tests"

            with st.expander(header):
                for test_name, test_desc in tests:
                    icon = "✅" if ci_passing is True else "⚠️" if ci_passing is False else "⬜"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{test_name}` — {test_desc}")

        st.markdown("#### Dashboard Tests (8)")
        DASHBOARD_TESTS = {
            "🖥️ Landing Page (test_app.py)": [
                ("test_loads_without_error", "Landing page renders without crash"),
                ("test_shows_title", "Shows FinBytes QuantLabs title"),
            ],
            "📊 Scanner Page (test_app.py)": [
                ("test_loads_without_error", "Scanner page renders without crash"),
                ("test_shows_title", "Shows Stock Risk Scanner title"),
                ("test_has_three_tabs", "Page has App, System Health, Architecture tabs"),
                ("test_has_scan_button", "Scan button is present"),
                ("test_has_preset_buttons", "Tech Giants, Safe Haven, Balanced presets"),
                ("test_has_equal_weight_button", "Equal Weight button is present"),
            ],
        }

        for module_name, tests in DASHBOARD_TESTS.items():
            tc = len(tests)
            if ci_passing is True:
                header = f"{module_name} — ✅ {tc}/{tc} passed"
            elif ci_passing is False:
                header = f"{module_name} — ⚠️ {tc} tests (check CI)"
            else:
                header = f"{module_name} — {tc} tests"

            with st.expander(header):
                for test_name, test_desc in tests:
                    icon = "✅" if ci_passing is True else "⚠️" if ci_passing is False else "⬜"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{test_name}` — {test_desc}")

    else:
        st.info("Click **Run Checks** above to test all services.")


# ============================================================
# TAB 3: ARCHITECTURE
# ============================================================
with tab_arch:
    api_bg, api_fg = rag(st.session_state.get("_health_api", "unknown"))
    db_bg, db_fg = rag(st.session_state.get("_health_db", "unknown"))
    ci_bg, ci_fg = rag(st.session_state.get("_health_ci", "unknown"))

    st.markdown("### Deployment Pipeline")
    if st.session_state.get("health_checked"):
        render_mermaid(f"""
        graph LR
            DEV["Code Push"]:::neutral --> WK["working"]:::neutral
            WK --> PR["Pull Request"]:::neutral
            PR --> MASTER["master"]:::neutral
            MASTER --> CI["CI Tests"]:::ci_s
            MASTER --> API["Scanner API"]:::api_s
            MASTER --> DASH["Dashboard"]:::dash_s
            API --> DB[("PostgreSQL")]:::db_s
            API --> YF["yfinance"]:::neutral
            API --> CLAUDE["Claude API"]:::neutral

            classDef neutral fill:#f0f2f6,stroke:#ccc,color:#333
            classDef api_s fill:{api_bg},stroke:{api_bg},color:{api_fg}
            classDef db_s fill:{db_bg},stroke:{db_bg},color:{db_fg}
            classDef ci_s fill:{ci_bg},stroke:{ci_bg},color:{ci_fg}
            classDef dash_s fill:#28a745,stroke:#28a745,color:#fff
        """, height=350)
        st.caption("🟢 Online · 🟡 Unknown · 🔴 Offline · ⬜ External")
    else:
        render_mermaid("""
        graph LR
            DEV["Code Push"]:::neutral --> WK["working"]:::neutral
            WK --> PR["Pull Request"]:::neutral
            PR --> MASTER["master"]:::neutral
            MASTER --> CI["CI Tests"]:::neutral
            MASTER --> API["Scanner API"]:::neutral
            MASTER --> DASH["Dashboard"]:::neutral
            API --> DB[("PostgreSQL")]:::neutral
            API --> YF["yfinance"]:::neutral
            API --> CLAUDE["Claude API"]:::neutral

            classDef neutral fill:#f0f2f6,stroke:#ccc,color:#333
        """, height=350)
        st.caption("Run health checks in the System Health tab to see live RAG status")

    st.markdown("---")

    st.markdown("### System Overview")
    render_mermaid("""
    graph LR
        User([User Browser]) --> SC[Streamlit Cloud]
        SC -->|scan requests| RA[Render API]
        SC -->|chart data| YF[yfinance]
        RA -->|persist| PG[(PostgreSQL)]
        RA -->|narrative| CL[Claude API]
        RA -->|fallback| FB[Summary]
        GH[GitHub Repo] -->|deploy| SC
        GH -->|deploy| RA
        GH -->|CI| CI[GitHub Actions]
    """, height=300)

    st.markdown("### Request Flow")
    render_mermaid("""
    sequenceDiagram
        participant U as User
        participant S as Streamlit
        participant A as API
        participant DB as PostgreSQL
        participant YF as yfinance
        participant C as Claude

        U->>S: Enter tickers, click Scan
        S->>A: POST scan request
        A->>DB: Insert pending record
        A-->>S: Return scan ID
        Note over A: Background task
        A->>YF: Fetch prices
        YF-->>A: Price data
        Note over A: Calculate risk
        A->>C: Generate narrative
        C-->>A: Narrative text
        A->>DB: Update to complete
        loop Polling
            S->>A: Check status
            A-->>S: Still pending
        end
        S->>A: Check status
        A-->>S: Complete with metrics
        S->>YF: Fetch chart data
        Note over S: Render charts
        S-->>U: Show results
    """, height=550)

    st.markdown("### Code Module Map")
    render_mermaid("""
    graph TD
        REQ[ScanRequest] --> SCANNER[scanner.py]
        SCANNER --> MD[market_data.py]
        SCANNER --> RISK[risk.py]
        SCANNER --> NARR[narrative.py]
        MD --> YF[yfinance]
        RISK --> METRICS[RiskMetrics]
        NARR --> CLAUDE[Claude API]
        NARR --> FB[Fallback]
        SCANNER --> RESULT[ScanResult]
        MAIN[main.py FastAPI] --> SCANNER
        MAIN --> DB[db.py]
        DB --> DBMOD[db_models.py]
        DBMOD --> PG[(PostgreSQL)]
    """, height=450)

    st.markdown("---")
    st.markdown(
        "For the full architecture deep dive including tech decisions Q&A, "
        "read the [Architecture blog post]"
        "(https://mish-codes.github.io/FinBytes/2026/04/03/stock-risk-scanner-architecture/)."
    )

# ============================================================
# TAB 4: TESTS
# ============================================================
with tab_tests:
    render_test_tab("test_stock_risk_scanner.py")

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Docker", "Claude API", "yfinance", "NumPy", "Streamlit", "GitHub Actions"])
