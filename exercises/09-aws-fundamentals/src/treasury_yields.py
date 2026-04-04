from datetime import date, timedelta
from fredapi import Fred


# FRED series IDs → human-readable maturity labels
TREASURY_SERIES = {
    "DGS1MO": "1M",
    "DGS3MO": "3M",
    "DGS6MO": "6M",
    "DGS1": "1Y",
    "DGS2": "2Y",
    "DGS3": "3Y",
    "DGS5": "5Y",
    "DGS7": "7Y",
    "DGS10": "10Y",
    "DGS20": "20Y",
    "DGS30": "30Y",
}

# Ordered list for consistent display and shape classification
MATURITY_ORDER = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]


def fetch_par_yields(api_key: str, as_of: date | None = None) -> dict[str, float]:
    """Fetch US Treasury par yields from FRED.

    Args:
        api_key: FRED API key.
        as_of: Date to fetch yields for. Defaults to most recent available.

    Returns:
        Dict mapping maturity label (e.g. "10Y") to yield in percent (e.g. 4.30).
        Maturities with no data are omitted.
    """
    fred = Fred(api_key=api_key)
    target = as_of or date.today()
    start = target - timedelta(days=7)  # look back a week to handle weekends/holidays

    yields = {}
    for series_id, label in TREASURY_SERIES.items():
        data = fred.get_series(series_id, observation_start=start, observation_end=target)
        data = data.dropna()
        if len(data) > 0:
            yields[label] = round(float(data.iloc[-1]), 2)

    return yields


def format_yield_table(yields: dict[str, float]) -> str:
    """Format yields as a readable ASCII table.

    Args:
        yields: Dict mapping maturity label to yield percent.

    Returns:
        Formatted string table.
    """
    if not yields:
        return "No yield data available."

    lines = []
    lines.append(f"{'Maturity':<10} {'Yield (%)':<10}")
    lines.append("-" * 20)
    for label in MATURITY_ORDER:
        if label in yields:
            lines.append(f"{label:<10} {yields[label]:<10.2f}")
    return "\n".join(lines)


def classify_curve_shape(yields: dict[str, float]) -> str:
    """Classify the yield curve shape.

    Uses short-end (1M or shortest available) and long-end (30Y or longest available)
    to determine overall shape, with mid-point check for humped curves.

    Args:
        yields: Dict mapping maturity label to yield percent.

    Returns:
        One of: "normal", "inverted", "flat", "humped".
    """
    ordered = [(label, yields[label]) for label in MATURITY_ORDER if label in yields]
    if len(ordered) < 3:
        return "flat"  # not enough data to classify

    short_rate = ordered[0][1]
    long_rate = ordered[-1][1]
    mid_rate = ordered[len(ordered) // 2][1]

    spread = long_rate - short_rate

    # Humped: mid-term rate is higher than both short and long ends
    if mid_rate > short_rate + 0.2 and mid_rate > long_rate + 0.2:
        return "humped"

    if abs(spread) <= 0.2:
        return "flat"
    elif spread > 0:
        return "normal"
    else:
        return "inverted"
