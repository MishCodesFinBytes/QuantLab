"""Spot curve bootstrapping from par yields.

A par bond prices at 100 (face value). For an annual-coupon bond with
coupon c and maturity n years:

    100 = c/(1+s₁) + c/(1+s₂)² + ... + (c+100)/(1+sₙ)ⁿ

where sᵢ are the zero-coupon (spot) rates. A 1Y bond has no intermediate
coupons so its spot equals its par yield. Once shorter spots are pinned
down, each longer spot can be solved from the equation above given the
already-known spots at every earlier *integer year*. That sequential
back-out is "bootstrapping".

Treasury par-yield grids are gappy (1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y,
20Y, 30Y). The standard bootstrap needs a coupon and a spot at *every*
year from 1 to n — so we linearly interpolate par yields onto the dense
integer-year grid first, bootstrap year-by-year, and report spots only
at the originally-requested tenors.

Sub-year tenors (1M, 3M, 6M) are single-cashflow zeros: s = par.
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


def _interpolate_par_to_annual_grid(
    years: list[int], rates: list[float]
) -> dict[int, float]:
    """Linearly interpolate par yields to every integer year from 1..max."""
    max_year = years[-1]
    dense: dict[int, float] = {}
    for y in range(1, max_year + 1):
        if y <= years[0]:
            dense[y] = rates[0]
            continue
        if y >= years[-1]:
            dense[y] = rates[-1]
            continue
        for i in range(len(years) - 1):
            if years[i] <= y <= years[i + 1]:
                x0, x1 = years[i], years[i + 1]
                y0, y1 = rates[i], rates[i + 1]
                dense[y] = y0 + (y1 - y0) * (y - x0) / (x1 - x0)
                break
    return dense


def bootstrap_spot_curve(par_yields: dict[str, float]) -> dict[str, float]:
    """Bootstrap zero-coupon spot rates from a par-yield curve.

    Args:
        par_yields: maturity label → par yield in percent (e.g. 4.30).

    Returns:
        maturity label → spot rate in percent, in maturity order.
    """
    if not par_yields:
        return {}

    ordered_labels = [m for m in MATURITY_ORDER if m in par_yields]
    par_decimal = {m: par_yields[m] / 100.0 for m in ordered_labels}
    spots: dict[str, float] = {}

    # Sub-year tenors are single-cashflow zeros — spot = par, no bootstrap.
    short_labels = [m for m in ordered_labels if MATURITY_YEARS[m] < 1.0]
    for m in short_labels:
        spots[m] = par_decimal[m]

    # Annual tenors: densify par curve, then bootstrap year-by-year.
    annual_labels = [m for m in ordered_labels if MATURITY_YEARS[m] >= 1.0]
    if annual_labels:
        known_years = [int(MATURITY_YEARS[m]) for m in annual_labels]
        known_rates = [par_decimal[m] for m in annual_labels]
        dense_par = _interpolate_par_to_annual_grid(known_years, known_rates)

        dense_spots: dict[int, float] = {}
        for y in range(1, known_years[-1] + 1):
            c = dense_par[y]
            if y == 1:
                dense_spots[1] = c
                continue
            pv_coupons = sum(
                c / ((1 + dense_spots[k]) ** k) for k in range(1, y)
            )
            denominator = 1.0 - pv_coupons
            if denominator <= 0:
                # Degenerate — coupons already exceed face. Fall back to par.
                dense_spots[y] = c
            else:
                dense_spots[y] = ((c + 1.0) / denominator) ** (1.0 / y) - 1.0

        for m in annual_labels:
            y = int(MATURITY_YEARS[m])
            spots[m] = dense_spots[y]

    return {m: round(spots[m] * 100, 4) for m in ordered_labels}
