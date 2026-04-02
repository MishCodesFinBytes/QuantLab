import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from async_prices import fetch_price, fetch_many_prices


class TestFetchPrice:
    async def test_returns_float(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "chart": {"result": [{"meta": {"regularMarketPrice": 150.25}}]}
        })
        mock_response.raise_for_status = MagicMock()

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("async_prices.aiohttp.ClientSession", return_value=mock_session):
            price = await fetch_price("AAPL")
            assert price == 150.25
            assert isinstance(price, float)


class TestFetchManyPrices:
    async def test_fetches_concurrently(self):
        call_times = []

        async def mock_fetch(ticker):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.05)  # simulate network delay
            return {"AAPL": 150.0, "MSFT": 300.0, "GOOG": 140.0}[ticker]

        with patch("async_prices.fetch_price", side_effect=mock_fetch):
            results = await fetch_many_prices(["AAPL", "MSFT", "GOOG"])

        assert len(results) == 3
        assert results["AAPL"] == 150.0
        assert results["MSFT"] == 300.0
        # All started at roughly the same time (concurrent)
        assert max(call_times) - min(call_times) < 0.03

    async def test_partial_failure_returns_available(self):
        async def mock_fetch(ticker):
            if ticker == "BAD":
                raise ValueError("Unknown ticker")
            return 100.0

        with patch("async_prices.fetch_price", side_effect=mock_fetch):
            results = await fetch_many_prices(["AAPL", "BAD", "MSFT"])

        assert "AAPL" in results
        assert "MSFT" in results
        assert "BAD" not in results
