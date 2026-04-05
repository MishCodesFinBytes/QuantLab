import pytest
from bootstrap import bootstrap_spot_curve, MATURITY_YEARS


class TestMaturityYears:
    def test_contains_standard_maturities(self):
        assert MATURITY_YEARS["1M"] == pytest.approx(1 / 12)
        assert MATURITY_YEARS["6M"] == 0.5
        assert MATURITY_YEARS["1Y"] == 1.0
        assert MATURITY_YEARS["10Y"] == 10.0
        assert MATURITY_YEARS["30Y"] == 30.0


class TestBootstrapSpotCurve:
    def test_single_maturity_spot_equals_par(self):
        """For a single zero-coupon maturity, spot rate = par yield."""
        par_yields = {"1Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        assert spot["1Y"] == pytest.approx(5.0, abs=0.01)

    def test_two_maturities(self):
        """With 1Y and 2Y par yields, 2Y spot should differ from par."""
        par_yields = {"1Y": 5.0, "2Y": 5.5}
        spot = bootstrap_spot_curve(par_yields)

        # 1Y spot = 1Y par (no intermediate coupons)
        assert spot["1Y"] == pytest.approx(5.0, abs=0.01)
        # 2Y spot should be slightly higher than 2Y par for a normal curve
        assert spot["2Y"] > 5.5

    def test_flat_curve_spot_equals_par(self):
        """When all par yields are equal, spot rates should equal par rates."""
        par_yields = {"1Y": 5.0, "2Y": 5.0, "5Y": 5.0, "10Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        for label in par_yields:
            assert spot[label] == pytest.approx(5.0, abs=0.05)

    def test_normal_curve_spot_above_par_at_long_end(self):
        """For a normal (upward sloping) par curve, long-end spot > long-end par."""
        par_yields = {"1Y": 3.0, "2Y": 3.5, "3Y": 4.0, "5Y": 4.5, "10Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        assert spot["10Y"] > par_yields["10Y"]

    def test_preserves_maturity_order(self):
        """Output keys should match input keys in maturity order."""
        par_yields = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        assert list(spot.keys()) == ["1Y", "2Y", "5Y"]

    def test_all_rates_positive(self):
        """Spot rates should be positive for reasonable par yields."""
        par_yields = {
            "1M": 5.25, "3M": 5.30, "6M": 5.20,
            "1Y": 4.80, "2Y": 4.50, "3Y": 4.30,
            "5Y": 4.20, "7Y": 4.25, "10Y": 4.30,
        }
        spot = bootstrap_spot_curve(par_yields)
        for rate in spot.values():
            assert rate > 0

    def test_empty_yields_returns_empty(self):
        spot = bootstrap_spot_curve({})
        assert spot == {}
