"""Pure finance functions for the Rent vs Buy calculator.

Every function in this module is side-effect-free. No I/O, no Streamlit,
no logging. The runner owns all orchestration.
"""

from __future__ import annotations

import math
from typing import Iterable


# ──────────────────────────────────────────────────────────────
# SDLT (Stamp Duty Land Tax) — UK rules effective from 1 April 2025
#
# On 1 April 2025 the UK reverted to the pre-September-2022 schedule
# after the temporary higher thresholds expired. The 0% band for
# standard buyers dropped from £250k to £125k (with a new 2% band
# £125k-£250k), and the first-time buyer relief cap dropped from
# £625k to £500k with the FTB nil-rate band cut from £425k to £300k.
#
# Source: https://www.gov.uk/stamp-duty-land-tax/residential-property-rates
# ──────────────────────────────────────────────────────────────

SDLT_RULES_AS_OF = "2025-04-01"
SDLT_SOURCE_URL = "https://www.gov.uk/stamp-duty-land-tax/residential-property-rates"

STANDARD_BANDS: list[tuple[float, float]] = [
    (  125_000,      0.00),
    (  250_000,      0.02),
    (  925_000,      0.05),
    (1_500_000,      0.10),
    (float("inf"),   0.12),
]

FTB_BANDS: list[tuple[float, float]] = [
    (  300_000,      0.00),
    (  500_000,      0.05),
]
FTB_CAP = 500_000


def _tiered_tax(price: float, bands: Iterable[tuple[float, float]]) -> float:
    """Apply a tiered tax schedule to a price."""
    tax = 0.0
    prev_threshold = 0.0
    for threshold, rate in bands:
        if price > threshold:
            tax += (threshold - prev_threshold) * rate
            prev_threshold = threshold
        else:
            tax += (price - prev_threshold) * rate
            return tax
    return tax


def calculate_sdlt(price: float, first_time_buyer: bool = False) -> float:
    """Compute UK Stamp Duty Land Tax on a residential purchase."""
    if first_time_buyer and price <= FTB_CAP:
        return _tiered_tax(price, FTB_BANDS)
    return _tiered_tax(price, STANDARD_BANDS)


# ──────────────────────────────────────────────────────────────
# Mortgage amortization
# ──────────────────────────────────────────────────────────────

def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortization formula. Returns the monthly payment in pounds."""
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12.0
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def remaining_balance(
    principal: float,
    annual_rate: float,
    years: int,
    months_elapsed: int,
) -> float:
    """Outstanding mortgage principal after N monthly payments."""
    if months_elapsed <= 0:
        return principal
    if months_elapsed >= years * 12:
        return 0.0
    if annual_rate == 0:
        monthly_payment = principal / (years * 12)
        return max(0.0, principal - monthly_payment * months_elapsed)
    r = annual_rate / 12.0
    pmt = monthly_mortgage_payment(principal, annual_rate, years)
    future_value = principal * (1 + r) ** months_elapsed - pmt * ((1 + r) ** months_elapsed - 1) / r
    return max(0.0, future_value)


# ──────────────────────────────────────────────────────────────
# Scenario dataclass
# ──────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Optional


@dataclass
class Scenario:
    # Location
    borough: str
    postcode_district: Optional[str]
    property_type: str
    new_build: bool
    first_time_buyer: bool
    bedrooms: str   # one of "studio", "1", "2", "3", "4+"

    # Shared
    plan_to_stay_years: int
    starting_cash: float
    investment_return: float
    isa_tax_free: bool
    inflation: float

    # Buying
    home_price: float
    deposit_pct: float
    auto_tier_rate: bool
    mortgage_rate: float
    fix_years: int
    mortgage_term_years: int
    legal_survey: float
    maintenance_pct: float
    council_tax: float
    buildings_insurance: float
    service_charge: float
    ground_rent: float
    lease_years_remaining: Optional[int]
    home_growth: float
    selling_fee_pct: float

    # Renting
    monthly_rent: float
    rent_growth: float
    deposit_weeks: int
    renters_insurance: float
    moving_cost: float
    avg_tenancy_years: float

    # Realism toggle
    include_long_term_frictions: bool


REMORTGAGE_FEE = 1500.0


# ──────────────────────────────────────────────────────────────
# LTV tiering
# ──────────────────────────────────────────────────────────────

def suggest_rate_for_ltv(ltv: float, fix_years: int, boe_rates_df) -> float:
    """Return BoE-quoted rate (decimal) for an LTV bracket and fix length."""
    subset = boe_rates_df[boe_rates_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    if subset.empty:
        raise ValueError(f"No BoE rates for fix_years={fix_years}")
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return float(row["rate_pct"]) / 100.0
    return float(subset.iloc[-1]["rate_pct"]) / 100.0


def _effective_investment_rate(scenario: Scenario) -> float:
    """ISA-protected → raw rate. Otherwise apply 20% CGT haircut."""
    if scenario.isa_tax_free:
        return scenario.investment_return
    return scenario.investment_return * 0.80


# ──────────────────────────────────────────────────────────────
# Total cost of buying
# ──────────────────────────────────────────────────────────────

def total_cost_of_buying(scenario: Scenario, boe_rates_df) -> dict:
    """Compute total net cost of buying over plan_to_stay_years."""
    years = scenario.plan_to_stay_years
    price = scenario.home_price
    deposit = price * scenario.deposit_pct
    principal = max(0.0, price - deposit)
    ltv = principal / price if price > 0 else 0.0

    if scenario.auto_tier_rate:
        rate = suggest_rate_for_ltv(ltv, scenario.fix_years, boe_rates_df)
    else:
        rate = scenario.mortgage_rate

    # Upfront
    sdlt = calculate_sdlt(price, scenario.first_time_buyer)
    moving_buy = scenario.moving_cost
    upfront = deposit + sdlt + scenario.legal_survey + moving_buy

    # Monthly recurring (flats only get service charge + ground rent)
    monthly_mortgage = monthly_mortgage_payment(principal, rate, scenario.mortgage_term_years)
    monthly_council_tax = scenario.council_tax / 12.0
    monthly_maintenance = (price * scenario.maintenance_pct) / 12.0
    monthly_buildings = scenario.buildings_insurance / 12.0
    if scenario.property_type == "F":
        monthly_service_charge = scenario.service_charge / 12.0
        monthly_ground_rent = scenario.ground_rent / 12.0
    else:
        monthly_service_charge = 0.0
        monthly_ground_rent = 0.0
    monthly_total = (
        monthly_mortgage + monthly_council_tax + monthly_maintenance
        + monthly_buildings + monthly_service_charge + monthly_ground_rent
    )

    total_ongoing = monthly_total * 12 * years

    # Remortgage fees
    remortgage_fees_total = 0.0
    if scenario.include_long_term_frictions and years > scenario.fix_years:
        num_remortgages = math.ceil((years - scenario.fix_years) / scenario.fix_years)
        remortgage_fees_total = num_remortgages * REMORTGAGE_FEE
        total_ongoing += remortgage_fees_total

    # At sale
    home_value_at_sale = price * (1 + scenario.home_growth) ** years
    remaining = remaining_balance(principal, rate, scenario.mortgage_term_years, years * 12)
    selling_fee = home_value_at_sale * scenario.selling_fee_pct
    equity_at_sale = home_value_at_sale - remaining - selling_fee

    # Investment income on excess cash
    excess_cash = max(0.0, scenario.starting_cash - upfront)
    investment_rate = _effective_investment_rate(scenario)
    investment_income = excess_cash * ((1 + investment_rate) ** years - 1)

    net_cost = upfront + total_ongoing - equity_at_sale - investment_income

    return {
        "upfront": upfront,
        "monthly_total": monthly_total,
        "total_ongoing": total_ongoing,
        "equity_at_sale": equity_at_sale,
        "investment_income": investment_income,
        "net_cost": net_cost,
        "breakdown": {
            "deposit": deposit,
            "sdlt": sdlt,
            "legal_survey": scenario.legal_survey,
            "moving_buy": moving_buy,
            "monthly_mortgage": monthly_mortgage,
            "monthly_council_tax": monthly_council_tax,
            "monthly_maintenance": monthly_maintenance,
            "monthly_buildings": monthly_buildings,
            "monthly_service_charge": monthly_service_charge,
            "monthly_ground_rent": monthly_ground_rent,
            "home_value_at_sale": home_value_at_sale,
            "remaining_mortgage": remaining,
            "selling_fee": selling_fee,
            "rate_used": rate,
            "ltv": ltv,
            "remortgage_fees_total": remortgage_fees_total,
            "excess_cash_invested": excess_cash,
        },
    }


# ──────────────────────────────────────────────────────────────
# Total cost of renting
# ──────────────────────────────────────────────────────────────

def total_cost_of_renting(scenario: Scenario) -> dict:
    """Compute total net cost of renting over plan_to_stay_years."""
    years = scenario.plan_to_stay_years
    monthly = scenario.monthly_rent

    # Rent with annual compounding
    total_rent = 0.0
    for _ in range(years):
        total_rent += monthly * 12
        monthly *= (1 + scenario.rent_growth)

    # Moves
    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    total_moving = scenario.moving_cost * num_moves

    # Renters insurance
    total_renters_ins = scenario.renters_insurance * years

    # Security deposit (refundable)
    weekly_rent = (scenario.monthly_rent * 12) / 52.0
    deposit_held = weekly_rent * scenario.deposit_weeks

    # Opportunity cost
    renter_upfront = deposit_held + scenario.moving_cost
    excess_cash = max(0.0, scenario.starting_cash - renter_upfront)
    investment_rate = _effective_investment_rate(scenario)
    investment_income = excess_cash * ((1 + investment_rate) ** years - 1)

    total_cost = total_rent + total_moving + total_renters_ins
    net_cost = total_cost - investment_income

    return {
        "total_rent": total_rent,
        "num_moves": num_moves,
        "total_moving": total_moving,
        "total_renters_ins": total_renters_ins,
        "deposit_held": deposit_held,
        "investment_income": investment_income,
        "total_cost": total_cost,
        "net_cost": net_cost,
    }


# ──────────────────────────────────────────────────────────────
# Breakeven rent
# ──────────────────────────────────────────────────────────────

def compute_breakeven_rent(scenario: Scenario, boe_rates_df) -> float:
    """Find starting monthly rent at which renting total equals buying total."""
    buy = total_cost_of_buying(scenario, boe_rates_df)
    target_net_cost = buy["net_cost"]

    years = scenario.plan_to_stay_years
    g = scenario.rent_growth
    growth_sum = sum((1 + g) ** y for y in range(years))

    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    non_rent_outflow = scenario.moving_cost * num_moves + scenario.renters_insurance * years

    rent_result = total_cost_of_renting(scenario)
    investment_income_proxy = rent_result["investment_income"]

    target_total_rent = target_net_cost - non_rent_outflow + investment_income_proxy
    if growth_sum <= 0:
        return 0.0
    breakeven_monthly = target_total_rent / (12 * growth_sum)
    return max(0.0, breakeven_monthly)
