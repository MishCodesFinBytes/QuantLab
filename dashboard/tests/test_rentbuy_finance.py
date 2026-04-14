"""Tests for the Rent vs Buy finance module."""

import math

import pandas as pd
import pytest

from lib.rentbuy.finance import (
    calculate_sdlt,
    monthly_mortgage_payment,
    remaining_balance,
)


# ── SDLT — Standard bands (non-first-time-buyer) ────────────────────
# Rules effective from 1 April 2025 (post-temporary-threshold reversion).
# Expected values computed by hand against the published HMRC schedule:
#   0% up to £125k, 2% £125k-£250k, 5% £250k-£925k,
#   10% £925k-£1.5M, 12% above £1.5M.

SDLT_STANDARD = [
    (   125_000,       0),
    (   250_000,    2_500),   # 125k * 2%
    (   400_000,   10_000),   # 2_500 + 150k * 5%
    (   500_000,   15_000),   # 2_500 + 250k * 5%
    (   925_000,   36_250),   # 2_500 + 675k * 5%
    ( 1_000_000,   43_750),   # 36_250 + 75k * 10%
    ( 1_500_000,   93_750),   # 36_250 + 575k * 10%
    ( 2_000_000,  153_750),   # 93_750 + 500k * 12%
]


@pytest.mark.parametrize("price,expected", SDLT_STANDARD)
def test_sdlt_standard(price, expected):
    assert calculate_sdlt(price, first_time_buyer=False) == pytest.approx(expected, abs=1)


# ── SDLT — First-time buyer relief (post-1-April-2025) ──────────────
# FTB: 0% up to £300k, 5% £300k-£500k. Above £500k → full standard bands.

SDLT_FTB = [
    (   300_000,      0),
    (   400_000,  5_000),    # 100k * 5%
    (   500_000, 10_000),    # 200k * 5%
]


@pytest.mark.parametrize("price,expected", SDLT_FTB)
def test_sdlt_first_time_buyer(price, expected):
    assert calculate_sdlt(price, first_time_buyer=True) == pytest.approx(expected, abs=1)


def test_sdlt_ftb_above_cap_uses_standard():
    """Above £500k, first-time buyers pay the same as non-FTB."""
    standard = calculate_sdlt(700_000, first_time_buyer=False)
    ftb = calculate_sdlt(700_000, first_time_buyer=True)
    assert standard == ftb


# ── Mortgage amortization ───────────────────────────────────────────

def test_mortgage_payment_standard_case():
    """£500k loan at 5% for 25 years → monthly payment ≈ £2,923."""
    payment = monthly_mortgage_payment(500_000, 0.05, 25)
    assert 2_920 < payment < 2_930


def test_mortgage_payment_zero_interest():
    """£240k / 240 months = £1,000/month exactly."""
    payment = monthly_mortgage_payment(240_000, 0.0, 20)
    assert abs(payment - 1_000) < 0.01


def test_mortgage_payment_scales_with_principal():
    """Doubling the principal doubles the monthly payment."""
    small = monthly_mortgage_payment(250_000, 0.05, 25)
    big = monthly_mortgage_payment(500_000, 0.05, 25)
    assert abs(big - 2 * small) < 0.01


def test_remaining_balance_at_start_equals_principal():
    assert abs(remaining_balance(500_000, 0.05, 25, 0) - 500_000) < 1


def test_remaining_balance_partial_term():
    """After 120 months on a 25y loan at 5%, ~£360k-£390k remains."""
    remaining = remaining_balance(500_000, 0.05, 25, 120)
    assert 360_000 < remaining < 390_000


def test_remaining_balance_at_end_is_zero():
    """After full term, balance should be zero (or near-zero due to rounding)."""
    assert remaining_balance(500_000, 0.05, 25, 300) < 1.0


def test_remaining_balance_zero_interest():
    """With 0% interest and linear amortization, half the term = half paid."""
    remaining = remaining_balance(240_000, 0.0, 20, 120)
    assert abs(remaining - 120_000) < 0.01


# ── LTV tiering ─────────────────────────────────────────────────────

from lib.rentbuy.finance import (
    Scenario,
    suggest_rate_for_ltv,
    total_cost_of_buying,
)


@pytest.fixture
def boe_rates():
    return pd.DataFrame([
        {"fix_years": 5, "ltv_bracket": 0.60, "rate_pct": 4.30, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.75, "rate_pct": 4.50, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.85, "rate_pct": 4.75, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.90, "rate_pct": 5.00, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.95, "rate_pct": 5.50, "snapshot_date": "2026-03"},
    ])


def test_suggest_rate_ltv_60(boe_rates):
    assert suggest_rate_for_ltv(0.60, 5, boe_rates) == pytest.approx(0.043)


def test_suggest_rate_ltv_75(boe_rates):
    assert suggest_rate_for_ltv(0.75, 5, boe_rates) == pytest.approx(0.045)


def test_suggest_rate_ltv_95(boe_rates):
    assert suggest_rate_for_ltv(0.95, 5, boe_rates) == pytest.approx(0.055)


def test_suggest_rate_above_top_bracket(boe_rates):
    """LTV above 95% returns the top bracket rate (no extrapolation)."""
    assert suggest_rate_for_ltv(0.99, 5, boe_rates) == pytest.approx(0.055)


def test_suggest_rate_bracket_boundary_rounds_up(boe_rates):
    """0.7501 should fall into the 0.85 bracket, not 0.75."""
    assert suggest_rate_for_ltv(0.7501, 5, boe_rates) == pytest.approx(0.0475)


# ── total_cost_of_buying ────────────────────────────────────────────

def make_scenario(**overrides) -> Scenario:
    """Test helper — reasonable defaults for a London flat purchase."""
    defaults = dict(
        borough="Camden",
        postcode_district="NW1",
        property_type="F",
        new_build=False,
        first_time_buyer=False,
        plan_to_stay_years=7,
        starting_cash=150_000,
        investment_return=0.05,
        isa_tax_free=True,
        inflation=0.025,
        home_price=650_000,
        deposit_pct=0.15,
        auto_tier_rate=False,
        mortgage_rate=0.0525,
        fix_years=5,
        mortgage_term_years=25,
        legal_survey=2_500,
        maintenance_pct=0.01,
        council_tax=1_900,
        buildings_insurance=400,
        service_charge=3_000,
        ground_rent=300,
        lease_years_remaining=99,
        home_growth=0.03,
        selling_fee_pct=0.015,
        monthly_rent=2_450,
        rent_growth=0.03,
        deposit_weeks=5,
        renters_insurance=120,
        moving_cost=500,
        avg_tenancy_years=3.5,
        include_long_term_frictions=True,
    )
    defaults.update(overrides)
    return Scenario(**defaults)


def test_total_cost_of_buying_returns_expected_keys(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_buying(scenario, boe_rates)
    assert "upfront" in result
    assert "monthly_total" in result
    assert "total_ongoing" in result
    assert "equity_at_sale" in result
    assert "investment_income" in result
    assert "net_cost" in result
    assert "breakdown" in result


def test_total_cost_of_buying_upfront_includes_all_components(boe_rates):
    scenario = make_scenario(home_price=650_000, deposit_pct=0.15,
                              legal_survey=2_500, moving_cost=500,
                              first_time_buyer=False)
    result = total_cost_of_buying(scenario, boe_rates)
    # SDLT on £650k (post-1-April-2025 standard): 2_500 + 400_000 * 5% = 22_500
    expected_upfront = 97_500 + 22_500 + 2_500 + 500  # deposit + SDLT + legal + moving
    assert result["upfront"] == pytest.approx(expected_upfront, abs=1)


def test_total_cost_flat_includes_service_charge_and_ground_rent(boe_rates):
    with_fees = make_scenario(property_type="F", service_charge=3_000, ground_rent=300)
    no_fees = make_scenario(property_type="F", service_charge=0, ground_rent=0)
    with_result = total_cost_of_buying(with_fees, boe_rates)
    no_result = total_cost_of_buying(no_fees, boe_rates)
    assert with_result["net_cost"] > no_result["net_cost"]


def test_total_cost_house_ignores_service_charge_even_if_set(boe_rates):
    with_fees = make_scenario(property_type="T", service_charge=5_000, ground_rent=500)
    no_fees = make_scenario(property_type="T", service_charge=0, ground_rent=0)
    assert total_cost_of_buying(with_fees, boe_rates)["net_cost"] \
        == pytest.approx(total_cost_of_buying(no_fees, boe_rates)["net_cost"])


def test_total_cost_auto_tier_rate_uses_boe_lookup(boe_rates):
    scenario = make_scenario(auto_tier_rate=True, deposit_pct=0.25)  # LTV = 0.75
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["rate_used"] == pytest.approx(0.045)


def test_total_cost_equity_at_sale_positive(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["equity_at_sale"] > 0


def test_total_cost_includes_remortgage_fees_with_frictions(boe_rates):
    """15-year plan with 5-year fix → 2 remortgages expected."""
    scenario = make_scenario(plan_to_stay_years=15, fix_years=5,
                              include_long_term_frictions=True)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] > 0


def test_total_cost_no_remortgage_fees_without_frictions(boe_rates):
    scenario = make_scenario(plan_to_stay_years=15, fix_years=5,
                              include_long_term_frictions=False)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] == 0


def test_total_cost_no_remortgage_when_plan_shorter_than_fix(boe_rates):
    """Plan = 5 years, fix = 5 years → no remortgages needed."""
    scenario = make_scenario(plan_to_stay_years=5, fix_years=5,
                              include_long_term_frictions=True)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] == 0


def test_cash_rich_buyer_gets_investment_income(boe_rates):
    lean = make_scenario(starting_cash=125_000)
    rich = make_scenario(starting_cash=500_000)
    assert (total_cost_of_buying(rich, boe_rates)["investment_income"]
            > total_cost_of_buying(lean, boe_rates)["investment_income"])


def test_isa_toggle_increases_investment_income(boe_rates):
    with_isa = make_scenario(starting_cash=500_000, isa_tax_free=True)
    without_isa = make_scenario(starting_cash=500_000, isa_tax_free=False)
    assert (total_cost_of_buying(with_isa, boe_rates)["investment_income"]
            > total_cost_of_buying(without_isa, boe_rates)["investment_income"])


# ── total_cost_of_renting ───────────────────────────────────────────

from lib.rentbuy.finance import total_cost_of_renting, compute_breakeven_rent


def test_total_cost_of_renting_returns_expected_keys(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_renting(scenario)
    assert "total_rent" in result
    assert "num_moves" in result
    assert "total_moving" in result
    assert "total_renters_ins" in result
    assert "investment_income" in result
    assert "total_cost" in result
    assert "net_cost" in result


def test_zero_rent_growth_total_is_simple_product():
    scenario = make_scenario(monthly_rent=2_000, rent_growth=0.0, plan_to_stay_years=5)
    result = total_cost_of_renting(scenario)
    assert result["total_rent"] == pytest.approx(120_000, abs=1)


def test_rent_growth_compounds():
    scenario = make_scenario(monthly_rent=2_000, rent_growth=0.05, plan_to_stay_years=3)
    result = total_cost_of_renting(scenario)
    assert result["total_rent"] == pytest.approx(75_660, abs=10)


def test_multiple_moves_with_long_term_frictions():
    """9-year plan with 3.5y tenancy → 3 moves."""
    scenario = make_scenario(
        plan_to_stay_years=9, avg_tenancy_years=3.5,
        moving_cost=500, include_long_term_frictions=True
    )
    result = total_cost_of_renting(scenario)
    assert result["num_moves"] == 3
    assert result["total_moving"] == pytest.approx(1500, abs=1)


def test_single_move_without_long_term_frictions():
    scenario = make_scenario(
        plan_to_stay_years=9, avg_tenancy_years=3.5,
        moving_cost=500, include_long_term_frictions=False
    )
    result = total_cost_of_renting(scenario)
    assert result["num_moves"] == 1
    assert result["total_moving"] == pytest.approx(500, abs=1)


def test_rent_opportunity_cost_greater_for_cash_rich():
    lean = make_scenario(starting_cash=10_000)
    rich = make_scenario(starting_cash=500_000)
    assert (total_cost_of_renting(rich)["investment_income"]
            > total_cost_of_renting(lean)["investment_income"])


def test_breakeven_rent_positive(boe_rates):
    scenario = make_scenario()
    breakeven = compute_breakeven_rent(scenario, boe_rates)
    assert 500 < breakeven < 10_000


def test_breakeven_rent_decreases_with_longer_stay(boe_rates):
    """Longer stays let equity build → buying looks better → breakeven rent falls."""
    short = compute_breakeven_rent(make_scenario(plan_to_stay_years=3), boe_rates)
    long = compute_breakeven_rent(make_scenario(plan_to_stay_years=20), boe_rates)
    assert short > long
