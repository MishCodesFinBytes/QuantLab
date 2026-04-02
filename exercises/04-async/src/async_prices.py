import asyncio
import aiohttp


async def fetch_price(ticker: str) -> float:
    """Fetch the current market price for a single ticker.

    Uses Yahoo Finance's chart API endpoint.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])


async def fetch_many_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch prices for multiple tickers concurrently.

    Failed tickers are silently skipped — returns only successful results.
    """
    async def safe_fetch(ticker: str) -> tuple[str, float | None]:
        try:
            price = await fetch_price(ticker)
            return ticker, price
        except Exception:
            return ticker, None

    tasks = [safe_fetch(t) for t in tickers]
    results = await asyncio.gather(*tasks)
    return {ticker: price for ticker, price in results if price is not None}
