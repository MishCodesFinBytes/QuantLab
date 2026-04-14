"""Glue layer: takes a Scenario, returns a Result with all numbers needed
for the UI. One function call per page render."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .finance import (
    Scenario,
    total_cost_of_buying,
    total_cost_of_renting,
    compute_breakeven_rent,
)


@dataclass
class Result:
    scenario: Scenario

    # Feasibility
    required_upfront_buy: float
    shortfall: float
    feasible: bool

    # Buying
    buy_upfront_total: float
    buy_monthly_total: float
    buy_total_cost_over_period: float
    buy_equity_at_sale: float
    buy_investment_income: float
    buy_net_cost: float

    # Renting
    rent_total_cost_over_period: float
    rent_opportunity_cost_benefit: float
    rent_net_cost: float

    # Headline
    verdict: str
    breakeven_monthly_rent: float
    buy_rent_delta: float

    # Year-by-year cumulative costs for chart
    yearly_buy_cost: list
    yearly_rent_cost: list

    # Full breakdowns for expander UI
    buy_breakdown: dict = field(default_factory=dict)
    rent_breakdown: dict = field(default_factory=dict)


def _yearly_cumulative_buy(scenario: Scenario, buy: dict, boe_rates_df) -> list:
    """Cumulative net cost of buying at end of each year 1..N."""
    years = scenario.plan_to_stay_years
    yearly = []
    for y in range(1, years + 1):
        subscenario = Scenario(**{**scenario.__dict__, "plan_to_stay_years": y})
        partial = total_cost_of_buying(subscenario, boe_rates_df)
        yearly.append(partial["net_cost"])
    return yearly


def _yearly_cumulative_rent(scenario: Scenario) -> list:
    years = scenario.plan_to_stay_years
    yearly = []
    for y in range(1, years + 1):
        subscenario = Scenario(**{**scenario.__dict__, "plan_to_stay_years": y})
        partial = total_cost_of_renting(subscenario)
        yearly.append(partial["net_cost"])
    return yearly


def run_scenario(scenario: Scenario, boe_rates_df) -> Result:
    """Run one scenario — returns every number the UI needs in a Result."""
    buy = total_cost_of_buying(scenario, boe_rates_df)
    rent = total_cost_of_renting(scenario)
    breakeven = compute_breakeven_rent(scenario, boe_rates_df)

    required_upfront = buy["upfront"]
    shortfall = max(0.0, required_upfront - scenario.starting_cash)
    feasible = shortfall == 0

    verdict = "rent_wins" if scenario.monthly_rent < breakeven else "buy_wins"

    return Result(
        scenario=scenario,
        required_upfront_buy=required_upfront,
        shortfall=shortfall,
        feasible=feasible,
        buy_upfront_total=buy["upfront"],
        buy_monthly_total=buy["monthly_total"],
        buy_total_cost_over_period=buy["upfront"] + buy["total_ongoing"],
        buy_equity_at_sale=buy["equity_at_sale"],
        buy_investment_income=buy["investment_income"],
        buy_net_cost=buy["net_cost"],
        rent_total_cost_over_period=rent["total_cost"],
        rent_opportunity_cost_benefit=rent["investment_income"],
        rent_net_cost=rent["net_cost"],
        verdict=verdict,
        breakeven_monthly_rent=breakeven,
        buy_rent_delta=buy["net_cost"] - rent["net_cost"],
        yearly_buy_cost=_yearly_cumulative_buy(scenario, buy, boe_rates_df),
        yearly_rent_cost=_yearly_cumulative_rent(scenario),
        buy_breakdown=buy["breakdown"],
        rent_breakdown=rent,
    )
