from datetime import datetime, UTC
from src.scanner.models import ScanRequest, ScanResult
from src.scanner.risk import calculate_risk_metrics
from src.scanner.market_data import fetch_prices
from src.scanner.narrative import RiskNarrator


def scan(request: ScanRequest) -> ScanResult:
    prices = fetch_prices(request.tickers, request.period)
    metrics = calculate_risk_metrics(prices, request.weights)
    narrator = RiskNarrator()
    narrative = narrator.generate(request.tickers, metrics)

    return ScanResult(
        tickers=request.tickers,
        weights=request.weights,
        metrics=metrics,
        narrative=narrative,
        generated_at=datetime.now(UTC),
    )
