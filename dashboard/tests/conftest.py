"""Shared pytest fixtures for the QuantLab Streamlit dashboard test suite.

Every autouse fixture patches an external dependency so that no test
hits the network or requires real credentials.  Non-autouse fixtures
(mock_vader, mock_textblob, mock_empty_data) are opt-in per test.
"""

import pytest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np


# ── Sample data ──────────────────────────────────────────


@pytest.fixture
def sample_ohlcv_df():
    """~252-row OHLCV DataFrame mimicking AAPL."""
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=252, name="Date")
    n = len(dates)
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(n) * 2)
    return pd.DataFrame(
        {
            "Open": close - np.random.rand(n),
            "High": close + np.random.rand(n) * 2,
            "Low": close - np.random.rand(n) * 2,
            "Close": close,
            "Volume": np.random.randint(1_000_000, 10_000_000, n),
        },
        index=dates,
    )


@pytest.fixture
def sample_multi_stock_df(sample_ohlcv_df):
    """Close prices for 4 tickers."""
    n = len(sample_ohlcv_df)
    df = pd.DataFrame(index=sample_ohlcv_df.index)
    np.random.seed(42)
    for ticker in ["AAPL", "MSFT", "GOOG", "AMZN"]:
        df[ticker] = 150 + np.cumsum(np.random.randn(n) * 2)
    return df


# ── Auto-applied mocks (autouse) ────────────────────────


@pytest.fixture(autouse=True)
def mock_set_page_config():
    """Make st.set_page_config a no-op so pages don't crash in AppTest."""
    with patch("streamlit.set_page_config"):
        yield


@pytest.fixture(autouse=True)
def mock_yfinance(sample_ohlcv_df, sample_multi_stock_df):
    """Patch yfinance.download globally so no test hits the network."""

    def fake_download(tickers, **kwargs):
        if isinstance(tickers, list) and len(tickers) > 1:
            return sample_multi_stock_df
        return sample_ohlcv_df

    with patch("yfinance.download", side_effect=fake_download):
        # Also patch yf.Ticker for pages that use it directly
        mock_ticker = MagicMock()
        mock_ticker.return_value.info = {
            "sector": "Technology",
            "shortName": "Apple Inc.",
        }
        mock_ticker.return_value.sustainability = pd.DataFrame(
            {"Value": [50, 60, 70]},
            index=["totalEsg", "environmentScore", "socialScore"],
        )
        with patch("yfinance.Ticker", mock_ticker):
            yield


@pytest.fixture(autouse=True)
def mock_requests():
    """Patch requests.get and requests.post for all external HTTP calls."""

    def fake_get(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.text = ""

        if "coingecko" in url:
            resp.json.return_value = {
                "bitcoin": {
                    "usd": 65000,
                    "usd_24h_change": 2.5,
                    "usd_market_cap": 1_200_000_000_000,
                },
                "ethereum": {
                    "usd": 3500,
                    "usd_24h_change": -1.2,
                    "usd_market_cap": 400_000_000_000,
                },
            }
        elif "er-api" in url or "exchange" in url.lower():
            resp.json.return_value = {
                "result": "success",
                "rates": {
                    "EUR": 0.92,
                    "GBP": 0.79,
                    "JPY": 149.50,
                    "CHF": 0.88,
                    "CAD": 1.36,
                    "AUD": 1.53,
                    "USD": 1.0,
                },
            }
        elif "github.com" in url:
            resp.json.return_value = {
                "workflow_runs": [
                    {
                        "conclusion": "success",
                        "run_number": 42,
                        "html_url": "https://github.com/test/runs/42",
                        "created_at": "2026-04-09T00:00:00Z",
                    }
                ]
            }
        elif "bankofengland" in url:
            resp.text = "DATE,IUDSNPY\n02/Jan/2025,4.70\n03/Jan/2025,4.70\n06/Jan/2025,4.695\n07/Jan/2025,4.695\n08/Jan/2025,4.695\n"
        elif "ecb.europa" in url:
            resp.text = "KEY,FREQ,REF_AREA,INSTRUMENT_TYPE,MATURITY,DATA_TYPE_FM,TIME_PERIOD,OBS_VALUE\nEST.B.EU000A2X2A25.WT,,,,,,2025-01-02,2.90\nEST.B.EU000A2X2A25.WT,,,,,,2025-01-03,2.90\nEST.B.EU000A2X2A25.WT,,,,,,2025-01-06,2.65\n"
        elif "newyorkfed" in url:
            resp.text = "effectiveDate,percentRate\n2025-01-02,4.33\n2025-01-03,4.33\n2025-01-06,4.33\n"
        elif "render" in url or "localhost" in url:
            resp.json.return_value = {"status": "ok"}
        else:
            resp.json.return_value = {}
        return resp

    fake_post_resp = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"status": "ok"}),
    )

    with patch("requests.get", side_effect=fake_get):
        with patch("requests.post", return_value=fake_post_resp):
            yield


@pytest.fixture(autouse=True)
def mock_boto3():
    """Patch boto3 for Admin page."""
    mock_client = MagicMock()
    mock_client.describe_db_instances.return_value = {
        "DBInstances": [
            {
                "DBInstanceStatus": "available",
                "Endpoint": {"Address": "test.rds.amazonaws.com"},
            }
        ]
    }
    mock_client.get_function.return_value = {
        "Configuration": {"FunctionName": "test", "State": "Active"}
    }
    mock_client.get_rest_apis.return_value = {"items": []}
    mock_client.list_objects_v2.return_value = {"Contents": [], "KeyCount": 0}
    with patch("boto3.client", return_value=mock_client):
        yield


@pytest.fixture(autouse=True)
def mock_streamlit_secrets():
    """Provide fake Streamlit secrets for pages that need them."""
    secrets = {
        "API_URL": "http://localhost:8000",
        "ADMIN_PASSWORD": "test123",
        "AWS_ACCESS_KEY_ID": "fake",
        "AWS_SECRET_ACCESS_KEY": "fake",
        "AWS_DEFAULT_REGION": "us-east-1",
        "RDS_INSTANCE_ID": "test-instance",
    }
    with patch("streamlit.secrets", secrets):
        yield


# ── Opt-in mocks (not autouse) ──────────────────────────


@pytest.fixture
def mock_vader():
    """Deterministic VADER sentiment scores."""
    mock_analyzer = MagicMock()
    mock_analyzer.polarity_scores.return_value = {
        "compound": 0.5,
        "pos": 0.6,
        "neg": 0.1,
        "neu": 0.3,
    }
    with patch(
        "vaderSentiment.vaderSentiment.SentimentIntensityAnalyzer",
        return_value=mock_analyzer,
    ):
        yield mock_analyzer


@pytest.fixture
def mock_textblob():
    """Deterministic TextBlob sentiment."""
    mock_blob = MagicMock()
    mock_blob.sentiment.polarity = 0.5
    with patch("textblob.TextBlob", return_value=mock_blob):
        yield mock_blob


@pytest.fixture
def mock_empty_data():
    """Return empty DataFrames for testing error states."""
    empty_df = pd.DataFrame()
    with patch("yfinance.download", return_value=empty_df):
        yield


# ── Benchmark Lab fixtures ──────────────────────────────────────────

from pathlib import Path


@pytest.fixture
def tiny_ppd_path():
    """Path to the 100-row Price Paid parquet fixture."""
    return Path(__file__).parent / "fixtures" / "tiny_ppd.parquet"


@pytest.fixture
def tiny_ppd_df(tiny_ppd_path):
    """The 100-row Price Paid DataFrame, loaded fresh per test."""
    return pd.read_parquet(tiny_ppd_path)
