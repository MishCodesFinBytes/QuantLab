"""Forward rate curve derivation from spot rates (OIDC-deployed).

The forward rate f(t₁, t₂) is the rate the market implies today for
borrowing/lending between future times t₁ and t₂. It falls out of a
no-arbitrage argument: earning s₂ for t₂ years must equal earning s₁ for
t₁ years and then rolling into f from t₁ to t₂.

    (1 + s₂)^t₂ = (1 + s₁)^t₁ · (1 + f)^(t₂ − t₁)

Solving for f:

    f = [(1 + s₂)^t₂ / (1 + s₁)^t₁]^(1/(t₂ − t₁)) − 1

Business uses: FRA pricing, swap valuation, gauging market expectations
of future rate moves. Rates here are in percent (e.g. 4.5) on the
boundary, decimal internally.
"""

MATURITY_YEARS: dict[str, float] = {
    "1M": 1 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "1Y": 1.0,
    "2Y": 2.0,
    "3Y": 3.0,
    "5Y": 5.0,
    "7Y": 7.0,
    "10Y": 10.0,
    "20Y": 20.0,
    "30Y": 30.0,
}

MATURITY_ORDER: list[str] = [
    "1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y",
]


def forward_rate_between(
    spot_short: float,
    years_short: float,
    spot_long: float,
    years_long: float,
) -> float:
    """Forward rate implied between two spot maturities, in percent."""
    s1 = spot_short / 100.0
    s2 = spot_long / 100.0
    dt = years_long - years_short
    forward = ((1 + s2) ** years_long / (1 + s1) ** years_short) ** (1 / dt) - 1
    return round(forward * 100, 4)


def calculate_forward_rates(spot_curve: dict[str, float]) -> dict[str, float]:
    """Forward rates between consecutive maturities in a spot curve.

    Args:
        spot_curve: maturity label → spot rate in percent.

    Returns:
        Dict mapping "{short}-{long}" → forward rate in percent.
    """
    if len(spot_curve) < 2:
        return {}

    ordered = [(m, spot_curve[m]) for m in MATURITY_ORDER if m in spot_curve]
    forwards: dict[str, float] = {}

    for i in range(1, len(ordered)):
        short_label, short_rate = ordered[i - 1]
        long_label, long_rate = ordered[i]
        forwards[f"{short_label}-{long_label}"] = forward_rate_between(
            spot_short=short_rate,
            years_short=MATURITY_YEARS[short_label],
            spot_long=long_rate,
            years_long=MATURITY_YEARS[long_label],
        )

    return forwards
