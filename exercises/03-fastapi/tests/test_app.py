import pytest
from fastapi.testclient import TestClient
from app import app, _watchlist


@pytest.fixture(autouse=True)
def clear_watchlist():
    _watchlist.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestWatchlist:
    def test_get_empty_watchlist(self, client):
        resp = client.get("/watchlist")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_ticker(self, client):
        resp = client.post("/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 201
        assert resp.json()["ticker"] == "AAPL"

    def test_add_and_list(self, client):
        client.post("/watchlist", json={"ticker": "AAPL"})
        client.post("/watchlist", json={"ticker": "MSFT"})
        resp = client.get("/watchlist")
        tickers = [item["ticker"] for item in resp.json()]
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_duplicate_ticker_rejected(self, client):
        client.post("/watchlist", json={"ticker": "AAPL"})
        resp = client.post("/watchlist", json={"ticker": "AAPL"})
        assert resp.status_code == 409

    def test_delete_ticker(self, client):
        client.post("/watchlist", json={"ticker": "GOOG"})
        resp = client.delete("/watchlist/GOOG")
        assert resp.status_code == 204

    def test_delete_missing_returns_404(self, client):
        resp = client.delete("/watchlist/ZZZZ")
        assert resp.status_code == 404


class TestPortfolioAnalysis:
    def test_analyze_validates_weights(self, client):
        resp = client.post("/analyze", json={
            "tickers": ["AAPL", "MSFT"],
            "weights": [0.5],
        })
        assert resp.status_code == 422

    def test_analyze_returns_summary(self, client):
        resp = client.post("/analyze", json={
            "tickers": ["AAPL"],
            "weights": [1.0],
            "period": "1y",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "tickers" in data
        assert "message" in data
