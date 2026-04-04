import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd


@pytest.fixture
async def app():
    from src.scanner.db_models import Base
    from src.scanner.main import create_app

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    app = create_app()
    app.state.session_factory = factory
    yield app
    await engine.dispose()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestHealthEndpoint:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestHealthDb:
    async def test_db_connected(self, client):
        resp = await client.get("/api/health/db")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert resp.json()["database"] == "connected"


class TestCreateScan:
    async def test_returns_pending(self, client):
        resp = await client.post(
            "/api/scan",
            json={"tickers": ["AAPL", "MSFT"], "weights": [0.6, 0.4]},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "pending"
        assert "id" in data


class TestGetScan:
    async def test_returns_scan_by_id(self, client):
        # Create a scan first
        resp = await client.post(
            "/api/scan",
            json={"tickers": ["AAPL"], "weights": [1.0]},
        )
        scan_id = resp.json()["id"]

        resp = await client.get(f"/api/scans/{scan_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == scan_id
        assert resp.json()["status"] == "pending"

    async def test_returns_404_for_missing_id(self, client):
        resp = await client.get("/api/scans/9999")
        assert resp.status_code == 404


class TestListScans:
    async def test_returns_list(self, client):
        resp = await client.get("/api/scans")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
