"""Portfolio Credit VaR via Monte Carlo simulation.

Process
-------
1. Generate correlated spread shocks using Cholesky decomposition.
2. Scale shocks by each position's spread volatility.
3. Compute P&L for each simulation path using spread duration (CS01).
4. VaR = percentile of the P&L distribution.

Cholesky decomposition
----------------------
Given correlation matrix Sigma, find lower-triangular L where LL^T = Sigma.
Then: correlated_shocks = L @ independent_standard_normals.
This transforms independent N(0,1) draws into draws with the target
correlation structure — the standard technique for Monte Carlo with
correlated risk factors.

Spread duration (CS01)
----------------------
Delta_P / P ~ -SD x Delta_spread.
The dollar price change per 1 bp spread move. Analogous to modified
duration for interest rates, but measures sensitivity to credit spreads
specifically.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import cholesky


def generate_correlated_spread_shocks(
    correlation_matrix: np.ndarray,
    num_simulations: int,
    seed: int | None = None,
) -> np.ndarray:
    """Generate correlated standard normal shocks via Cholesky decomposition.

    Args:
        correlation_matrix: n x n correlation matrix (symmetric, PD).
        num_simulations: Number of Monte Carlo paths.
        seed: Random seed for reproducibility.

    Returns:
        (num_simulations, n) array of correlated standard normals.
    """
    rng = np.random.default_rng(seed)
    n = correlation_matrix.shape[0]
    L = cholesky(correlation_matrix, lower=True)
    Z = rng.standard_normal((num_simulations, n))
    return Z @ L.T


def spread_duration(
    price: float,
    coupon: float,
    maturity_years: int,
    spread_bps: float,
    face: float = 100.0,
    bump_bps: float = 1.0,
) -> float:
    """Spread duration (CS01) via central finite difference.

    Returns the absolute dollar price change per 1 bp spread move,
    per unit of face.
    """

    def _price_at_spread(s_bps: float) -> float:
        discount_rate = (coupon / 100.0) + (s_bps / 10000.0)
        if discount_rate <= 0:
            discount_rate = 0.001
        times = np.arange(1, maturity_years + 1, dtype=float)
        cfs = np.full_like(times, coupon / 100.0 * face)
        cfs[-1] += face
        return float(sum(cf / (1 + discount_rate) ** t for cf, t in zip(cfs, times)))

    price_up = _price_at_spread(spread_bps + bump_bps)
    price_down = _price_at_spread(spread_bps - bump_bps)

    return abs((price_up - price_down) / (2 * bump_bps))


def portfolio_credit_var(
    positions: list[dict],
    correlation_matrix: np.ndarray,
    spread_volatilities: np.ndarray,
    confidence: float = 0.95,
    num_simulations: int = 10000,
    seed: int | None = None,
) -> float:
    """Portfolio credit VaR via Monte Carlo.

    Args:
        positions: List of dicts, each with keys:
            price, coupon, maturity_years, spread_bps, face, quantity.
        correlation_matrix: n x n spread correlation matrix.
        spread_volatilities: n-array of spread vols in bps.
        confidence: VaR confidence level (e.g. 0.95 for 95%).
        num_simulations: Number of MC paths.
        seed: Random seed.

    Returns:
        VaR as a negative dollar amount (loss at the given percentile).
    """
    n = len(positions)

    # Correlated standard-normal shocks, scaled by vol to get spread changes
    shocks = generate_correlated_spread_shocks(
        correlation_matrix, num_simulations, seed
    )
    spread_changes = shocks * spread_volatilities  # (sims, n) in bps

    # CS01 per position
    durations = [
        spread_duration(
            pos["price"], pos["coupon"], pos["maturity_years"],
            pos["spread_bps"], pos["face"],
        )
        for pos in positions
    ]

    # P&L: -SD * delta_spread * quantity * face/100
    pnl = np.zeros(num_simulations)
    for i, pos in enumerate(positions):
        position_pnl = (
            -durations[i] * spread_changes[:, i]
            * pos["quantity"] * pos["face"] / 100.0
        )
        pnl += position_pnl

    var_percentile = (1.0 - confidence) * 100
    return round(float(np.percentile(pnl, var_percentile)), 2)
