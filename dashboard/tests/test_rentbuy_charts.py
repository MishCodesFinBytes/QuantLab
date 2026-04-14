"""Tests for the rentbuy chart builders."""

import plotly.graph_objects as go
import pytest

from lib.rentbuy.scenario import run_scenario
from lib.rentbuy.charts import build_cost_over_time_chart
from tests.test_rentbuy_finance import make_scenario, boe_rates


def test_build_cost_over_time_chart_returns_figure(boe_rates):
    result = run_scenario(make_scenario(), boe_rates)
    fig = build_cost_over_time_chart(result)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2
    trace_names = [t.name.lower() for t in fig.data if t.name]
    assert any("buy" in n for n in trace_names)
    assert any("rent" in n for n in trace_names)
