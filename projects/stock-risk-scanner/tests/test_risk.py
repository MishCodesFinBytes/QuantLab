import pytest
import numpy as np
import pandas as pd


class TestCalculateRiskMetrics:
    def test_var_and_cvar(self):
        from src.scanner.risk import calculate_risk_metrics

        # Create a predictable declining asset
        prices = pd.DataFrame({"A": np.linspace(100, 80, 252)})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        # Steadily declining: VaR should be negative
        assert metrics.var_pct < 0
        # CVaR should be worse (more negative) than VaR
        assert metrics.cvar_pct <= metrics.var_pct

    def test_max_drawdown(self):
        from src.scanner.risk import calculate_risk_metrics

        # Price goes 100 -> 120 -> 90 -> 110
        prices = pd.DataFrame({"A": [100.0, 110.0, 120.0, 90.0, 100.0, 110.0]})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        # Max drawdown: peak 120 to trough 90 = -25%
        assert metrics.max_drawdown_pct == pytest.approx(-25.0, abs=1.0)

    def test_sharpe_ratio_sign(self):
        from src.scanner.risk import calculate_risk_metrics

        # Upward trending asset should have positive Sharpe
        prices = pd.DataFrame({"A": np.linspace(100, 130, 252)})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        assert metrics.sharpe_ratio > 0

        # Downward trending asset should have negative Sharpe
        prices_down = pd.DataFrame({"A": np.linspace(100, 70, 252)})
        metrics_down = calculate_risk_metrics(prices_down, weights=[1.0])
        assert metrics_down.sharpe_ratio < 0
