"""OAS (Option-Adjusted Spread) and Z-spread calculation.

Binomial interest rate tree
---------------------------
At each node, the rate can move up or down:
    r_up   = r * exp(+sigma * sqrt(dt))
    r_down = r * exp(-sigma * sqrt(dt))
Probability of each move is 0.5 under the risk-neutral measure.

Bond pricing on the tree (backward induction)
----------------------------------------------
At maturity: value = face + coupon.
At earlier nodes:
    continuation = (0.5 * V_up + 0.5 * V_down) / (1 + r * dt) + coupon

Callable bond
-------------
At each node the issuer calls if call_price < continuation value.
    value = min(continuation, call_price + coupon)

Z-spread
--------
Constant spread z over the spot curve such that:
    sum(CF_i / (1 + s_i + z)^t_i) = market_price
Solved via Brent's method.

OAS
---
Spread z added to every rate on the binomial tree such that
the model price equals the market price.
- For non-callable bonds: OAS ~ Z-spread.
- For callable bonds: OAS < Z-spread (the embedded option has value).
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

MATURITY_YEARS = {
    "1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0,
    "7Y": 7.0, "10Y": 10.0, "20Y": 20.0, "30Y": 30.0,
}


def build_rate_tree(
    short_rate: float, volatility: float, steps: int, dt: float = 1.0
) -> list[list[float]]:
    """Build a recombining binomial interest rate tree.

    Args:
        short_rate: Initial short rate in percent.
        volatility: Rate volatility (annualised decimal, e.g. 0.15).
        steps: Number of time steps.
        dt: Time step size in years.

    Returns:
        tree[i][j] = rate at step i, node j (in percent).
    """
    u = np.exp(volatility * np.sqrt(dt))
    d = 1.0 / u

    tree: list[list[float]] = []
    for i in range(steps + 1):
        level = []
        for j in range(i + 1):
            rate = short_rate * (u ** (i - 2 * j))
            level.append(round(rate, 6))
        tree.append(level)

    return tree


def price_bond_on_tree(
    tree: list[list[float]],
    coupon: float,
    face: float,
    dt: float = 1.0,
) -> float:
    """Price a non-callable bond via backward induction on the rate tree.

    Args:
        tree: Interest rate tree (percent values).
        coupon: Annual coupon rate in percent.
        face: Face value.
        dt: Time step in years.

    Returns:
        Bond price (present value at root node).
    """
    steps = len(tree) - 1
    coupon_payment = coupon / 100.0 * face * dt

    # Terminal values
    values = [face + coupon_payment for _ in tree[steps]]

    # Backward induction
    for i in range(steps - 1, -1, -1):
        new_values = []
        for j in range(len(tree[i])):
            r = tree[i][j] / 100.0
            discount = 1.0 / (1.0 + r * dt)
            expected = 0.5 * values[j] + 0.5 * values[j + 1]
            pv = expected * discount
            # Add coupon at intermediate nodes (not at root — no coupon at t=0)
            if i > 0:
                pv += coupon_payment
            new_values.append(pv)
        values = new_values

    return round(values[0], 4)


def price_callable_bond_on_tree(
    tree: list[list[float]],
    coupon: float,
    face: float,
    call_price: float,
    dt: float = 1.0,
    oas_bps: float = 0.0,
) -> float:
    """Price a callable bond via backward induction.

    At each node (except the root), the issuer calls if it's cheaper.
    """
    steps = len(tree) - 1
    coupon_payment = coupon / 100.0 * face * dt
    oas_dec = oas_bps / 10000.0

    values = [face + coupon_payment for _ in tree[steps]]

    for i in range(steps - 1, -1, -1):
        new_values = []
        for j in range(len(tree[i])):
            r = tree[i][j] / 100.0 + oas_dec
            discount = 1.0 / (1.0 + r * dt)
            expected = 0.5 * values[j] + 0.5 * values[j + 1]
            continuation = expected * discount
            if i > 0:
                continuation += coupon_payment
                # Issuer calls if cheaper than continuing
                value = min(continuation, call_price + coupon_payment)
            else:
                value = continuation
            new_values.append(value)
        values = new_values

    return round(values[0], 4)


def calculate_z_spread(
    spot_curve: dict[str, float],
    coupon: float,
    maturity_years: int,
    face: float,
    market_price: float,
) -> float:
    """Calculate Z-spread in basis points.

    The Z-spread is the constant spread over the spot curve that equates
    the present value of a bond's cash flows to its market price.
    """
    mats_known = sorted([(MATURITY_YEARS[m], spot_curve[m]) for m in spot_curve])
    x = np.array([m[0] for m in mats_known])
    y = np.array([m[1] for m in mats_known])
    cs = CubicSpline(x, y, extrapolate=True)

    times = np.arange(1, maturity_years + 1, dtype=float)
    spots = cs(times) / 100.0
    cfs = np.full_like(times, coupon / 100.0 * face)
    cfs[-1] += face

    def objective(z_bps):
        z = z_bps / 10000.0
        price = sum(cf / (1 + s + z) ** t for cf, s, t in zip(cfs, spots, times))
        return price - market_price

    return round(brentq(objective, -500, 3000), 2)


def calculate_oas(
    spot_curve: dict[str, float],
    coupon: float,
    maturity_years: int,
    face: float,
    call_price: float | None,
    market_price: float,
    volatility: float = 0.15,
) -> float:
    """Calculate OAS in basis points.

    For non-callable bonds (call_price=None), OAS ~ Z-spread.
    For callable bonds, OAS < Z-spread because the embedded option
    value is stripped out.
    """
    mats_known = sorted([(MATURITY_YEARS[m], spot_curve[m]) for m in spot_curve])
    short_rate = mats_known[0][1]

    tree = build_rate_tree(short_rate, volatility, maturity_years, dt=1.0)

    def objective(oas_bps):
        if call_price is not None:
            price = price_callable_bond_on_tree(
                tree, coupon, face, call_price, dt=1.0, oas_bps=oas_bps
            )
        else:
            # Non-callable: shift all tree rates by OAS (in percent) and price
            oas_pct = oas_bps / 100.0  # bps -> percentage points
            shifted_tree = [
                [r + oas_pct for r in level] for level in tree
            ]
            price = price_bond_on_tree(shifted_tree, coupon, face, dt=1.0)
        return price - market_price

    return round(brentq(objective, -500, 3000), 2)
