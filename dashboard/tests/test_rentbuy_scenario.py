"""Tests for the rentbuy scenario runner."""

import pandas as pd
import pytest

from lib.rentbuy.finance import Scenario
from lib.rentbuy.scenario import run_scenario, Result
from tests.test_rentbuy_finance import make_scenario, boe_rates  # reuse fixtures


def test_run_scenario_returns_complete_result(boe_rates):
    scenario = make_scenario()
    result = run_scenario(scenario, boe_rates)
    assert isinstance(result, Result)
    assert result.buy_net_cost > 0
    assert result.rent_net_cost > 0
    assert result.breakeven_monthly_rent > 0
    assert result.verdict in ("buy_wins", "rent_wins")
    assert len(result.yearly_buy_cost) == scenario.plan_to_stay_years
    assert len(result.yearly_rent_cost) == scenario.plan_to_stay_years


def test_run_scenario_verdict_consistent_with_delta(boe_rates):
    scenario = make_scenario()
    result = run_scenario(scenario, boe_rates)
    if result.verdict == "buy_wins":
        assert result.buy_rent_delta <= 0
    else:
        assert result.buy_rent_delta > 0


def test_run_scenario_feasibility_flag(boe_rates):
    lean = make_scenario(starting_cash=10_000)
    rich = make_scenario(starting_cash=500_000)
    assert run_scenario(lean, boe_rates).feasible is False
    assert run_scenario(lean, boe_rates).shortfall > 0
    assert run_scenario(rich, boe_rates).feasible is True
    assert run_scenario(rich, boe_rates).shortfall == 0
