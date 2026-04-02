import pytest
from datetime import datetime, UTC


class TestScanRequest:
    def test_valid_request(self):
        from src.scanner.models import ScanRequest

        req = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        assert req.tickers == ["AAPL", "MSFT"]
        assert req.weights == [0.6, 0.4]
        assert req.period == "1y"

    def test_tickers_uppercased(self):
        from src.scanner.models import ScanRequest

        req = ScanRequest(tickers=["aapl", "msft"], weights=[0.5, 0.5])
        assert req.tickers == ["AAPL", "MSFT"]

    def test_mismatched_lengths_raises(self):
        from src.scanner.models import ScanRequest

        with pytest.raises(ValueError, match="length"):
            ScanRequest(tickers=["AAPL", "MSFT"], weights=[1.0])

    def test_weights_not_summing_to_one_raises(self):
        from src.scanner.models import ScanRequest

        with pytest.raises(ValueError, match="sum"):
            ScanRequest(tickers=["AAPL"], weights=[0.5])


class TestRiskMetrics:
    def test_risk_metrics_fields(self):
        from src.scanner.models import RiskMetrics

        metrics = RiskMetrics(
            var_pct=-2.15,
            cvar_pct=-3.42,
            max_drawdown_pct=-18.7,
            volatility_pct=22.5,
            sharpe_ratio=1.2,
        )
        assert metrics.var_pct == pytest.approx(-2.15)
        assert metrics.sharpe_ratio == pytest.approx(1.2)


class TestScanResult:
    def test_scan_result_fields(self):
        from src.scanner.models import RiskMetrics, ScanResult

        metrics = RiskMetrics(
            var_pct=-2.0, cvar_pct=-3.0, max_drawdown_pct=-15.0,
            volatility_pct=20.0, sharpe_ratio=0.8,
        )
        result = ScanResult(
            tickers=["AAPL"], weights=[1.0], metrics=metrics,
            narrative="Test", generated_at=datetime.now(UTC),
        )
        assert result.tickers == ["AAPL"]
        assert result.metrics.var_pct == pytest.approx(-2.0)
        assert result.narrative == "Test"
