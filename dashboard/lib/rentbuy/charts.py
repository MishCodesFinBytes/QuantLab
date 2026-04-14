"""Plotly chart builders for the rent-vs-buy calculator."""

from __future__ import annotations

import plotly.graph_objects as go

from .scenario import Result


def build_cost_over_time_chart(result: Result) -> go.Figure:
    """Line chart: cumulative net cost of buying and renting, year by year."""
    years = list(range(1, result.scenario.plan_to_stay_years + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=result.yearly_buy_cost,
        mode="lines+markers",
        name="Buying (cumulative net cost)",
        line=dict(color="#2a7ae2", width=2),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=years,
        y=result.yearly_rent_cost,
        mode="lines+markers",
        name="Renting (cumulative net cost)",
        line=dict(color="#e8893c", width=2),
        marker=dict(size=7),
    ))

    crossover = _find_crossover_year(result.yearly_buy_cost, result.yearly_rent_cost)
    if crossover is not None:
        fig.add_vline(
            x=crossover,
            line_dash="dash",
            line_color="#888",
            annotation_text=f"Year {crossover}",
            annotation_position="top",
        )

    fig.update_layout(
        title="Cumulative net cost over time",
        xaxis_title="Years",
        yaxis_title="Net cost (£)",
        height=420,
        margin=dict(t=60, b=40, l=60, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    return fig


def _find_crossover_year(buy_costs: list, rent_costs: list):
    """Return the year index (1-based) where the cheaper path flips, or None."""
    if not buy_costs or not rent_costs:
        return None
    initial_buy_cheaper = buy_costs[0] < rent_costs[0]
    for i in range(1, len(buy_costs)):
        now_buy_cheaper = buy_costs[i] < rent_costs[i]
        if now_buy_cheaper != initial_buy_cheaper:
            return i + 1
    return None
