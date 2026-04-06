import numpy as np
import pytest

from credit_var import (
    generate_correlated_spread_shocks,
    portfolio_credit_var,
    spread_duration,
)


class TestCorrelatedShocks:
    def test_output_shape(self):
        corr = np.array([[1.0, 0.5], [0.5, 1.0]])
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr, num_simulations=1000, seed=42
        )
        assert shocks.shape == (1000, 2)

    def test_correlation_preserved(self):
        corr = np.array([[1.0, 0.8], [0.8, 1.0]])
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr, num_simulations=10000, seed=42
        )
        realized_corr = np.corrcoef(shocks.T)
        assert realized_corr[0, 1] == pytest.approx(0.8, abs=0.05)

    def test_uncorrelated(self):
        corr = np.eye(3)
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr, num_simulations=10000, seed=42
        )
        realized_corr = np.corrcoef(shocks.T)
        assert abs(realized_corr[0, 1]) < 0.05


class TestSpreadDuration:
    def test_positive_duration(self):
        sd = spread_duration(
            price=98.0, coupon=5.0, maturity_years=5, spread_bps=100, face=100.0
        )
        assert sd > 0

    def test_longer_maturity_higher_duration(self):
        sd5 = spread_duration(price=98.0, coupon=5.0, maturity_years=5, spread_bps=100, face=100.0)
        sd10 = spread_duration(price=95.0, coupon=5.0, maturity_years=10, spread_bps=100, face=100.0)
        assert sd10 > sd5


class TestPortfolioCreditVaR:
    def test_var_is_negative(self):
        """VaR should represent a loss (negative P&L)."""
        positions = [
            {"price": 98.0, "coupon": 5.0, "maturity_years": 5, "spread_bps": 100, "face": 100.0, "quantity": 1000},
            {"price": 95.0, "coupon": 4.5, "maturity_years": 10, "spread_bps": 150, "face": 100.0, "quantity": 500},
        ]
        corr = np.array([[1.0, 0.6], [0.6, 1.0]])
        spread_vols = np.array([50, 80])

        var = portfolio_credit_var(
            positions=positions, correlation_matrix=corr,
            spread_volatilities=spread_vols, confidence=0.95,
            num_simulations=10000, seed=42,
        )
        assert var < 0

    def test_higher_correlation_higher_var(self):
        """More correlation -> worse tail loss."""
        positions = [
            {"price": 98.0, "coupon": 5.0, "maturity_years": 5, "spread_bps": 100, "face": 100.0, "quantity": 1000},
            {"price": 95.0, "coupon": 4.5, "maturity_years": 10, "spread_bps": 150, "face": 100.0, "quantity": 500},
        ]
        spread_vols = np.array([50, 80])

        low_corr = np.array([[1.0, 0.2], [0.2, 1.0]])
        high_corr = np.array([[1.0, 0.9], [0.9, 1.0]])

        var_low = portfolio_credit_var(positions, low_corr, spread_vols, 0.95, 10000, seed=42)
        var_high = portfolio_credit_var(positions, high_corr, spread_vols, 0.95, 10000, seed=42)

        assert var_high < var_low  # more negative = worse
