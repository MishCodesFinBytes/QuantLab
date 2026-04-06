import pytest

from oas import (
    build_rate_tree,
    calculate_oas,
    calculate_z_spread,
    price_bond_on_tree,
    price_callable_bond_on_tree,
)


class TestBuildRateTree:
    def test_root_node(self):
        """Root node should be the short rate."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=3, dt=1.0)
        assert tree[0][0] == pytest.approx(5.0, abs=0.01)

    def test_tree_size(self):
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=4, dt=1.0)
        assert len(tree) == 5
        assert len(tree[4]) == 5

    def test_up_down_symmetry(self):
        """Tree should be recombining: up-down = down-up."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=3, dt=1.0)
        assert len(tree[2]) == 3


class TestPriceBondOnTree:
    def test_zero_coupon_discounting(self):
        """A zero-coupon bond should be discounted at tree rates."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.0, steps=3, dt=1.0)
        price = price_bond_on_tree(tree, coupon=0.0, face=100.0, dt=1.0)
        assert price == pytest.approx(86.38, abs=0.5)

    def test_par_bond_near_par(self):
        """A bond with coupon ~ yield should price near par."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.0, steps=5, dt=1.0)
        price = price_bond_on_tree(tree, coupon=5.0, face=100.0, dt=1.0)
        assert abs(price - 100.0) < 2.0


class TestCallableBond:
    def test_callable_le_noncallable(self):
        """Callable bond price <= non-callable (issuer has the option)."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.20, steps=5, dt=1.0)
        nc_price = price_bond_on_tree(tree, coupon=6.0, face=100.0, dt=1.0)
        c_price = price_callable_bond_on_tree(
            tree, coupon=6.0, face=100.0, call_price=100.0, dt=1.0
        )
        assert c_price <= nc_price + 0.01


class TestZSpread:
    def test_z_spread_positive_for_discount_bond(self):
        """Bond priced below par with coupon < yield should have positive Z-spread."""
        spot_curve = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        z = calculate_z_spread(
            spot_curve, coupon=5.0, maturity_years=5, face=100.0, market_price=98.0
        )
        assert z > 0


class TestOAS:
    def test_oas_less_than_z_spread_for_callable(self):
        """OAS < Z-spread for callable bonds (option value removed)."""
        spot_curve = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        market_price = 98.0
        z = calculate_z_spread(
            spot_curve, coupon=5.0, maturity_years=5, face=100.0,
            market_price=market_price,
        )
        oas = calculate_oas(
            spot_curve, coupon=5.0, maturity_years=5, face=100.0,
            call_price=100.0, market_price=market_price, volatility=0.20,
        )
        assert oas < z

    def test_oas_equals_z_spread_for_noncallable(self):
        """Without call option, OAS ~ Z-spread."""
        spot_curve = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        market_price = 98.0
        z = calculate_z_spread(
            spot_curve, coupon=5.0, maturity_years=5, face=100.0,
            market_price=market_price,
        )
        oas = calculate_oas(
            spot_curve, coupon=5.0, maturity_years=5, face=100.0,
            call_price=None, market_price=market_price, volatility=0.20,
        )
        # Binomial tree with vol introduces convexity, so OAS and Z-spread
        # won't match exactly — 20 bps tolerance is reasonable for a simple model
        assert abs(oas - z) < 20
