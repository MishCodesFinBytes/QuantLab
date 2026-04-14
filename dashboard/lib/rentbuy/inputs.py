"""Data loaders and default-value lookups for the rent-vs-buy calculator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_district_to_borough() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_district_to_borough.csv")


def load_borough_rents() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_borough_rents.csv")


def load_council_tax() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_council_tax.csv")


def load_boe_rates() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "boe_mortgage_rates.csv")


def default_home_price(
    ppd_df: pd.DataFrame,
    district_to_borough_df: pd.DataFrame,
    borough: str,
    postcode_district: str | None,
    property_type: str,
    new_build: bool,
) -> int:
    """Return median sale price from the tightest available filter.

    Falls back in order:
      1. (district × property_type × new_build), last 3y, >=10 sales
      2. (borough × property_type), last 3y, any count > 0
      3. £500,000 hardcoded fallback
    """
    three_years_ago = pd.Timestamp.now() - pd.DateOffset(years=3)
    recent = ppd_df[ppd_df["date"] >= three_years_ago]
    new_build_flag = "Y" if new_build else "N"

    if postcode_district:
        subset = recent[
            (recent["postcode_district"] == postcode_district)
            & (recent["property_type"] == property_type)
            & (recent["new_build"] == new_build_flag)
        ]
        if len(subset) >= 10:
            return int(subset["price"].median())

    borough_districts = district_to_borough_df[
        district_to_borough_df["borough"] == borough
    ]["postcode_district"].tolist()
    if borough_districts:
        subset = recent[
            (recent["postcode_district"].isin(borough_districts))
            & (recent["property_type"] == property_type)
        ]
        if len(subset) > 0:
            return int(subset["price"].median())

    return 500_000


def default_monthly_rent(rents_df: pd.DataFrame, borough: str) -> int:
    row = rents_df[rents_df["borough"] == borough]
    if len(row) == 0:
        return 2_000
    return int(row["median_monthly_rent"].iloc[0])


def default_council_tax(council_tax_df: pd.DataFrame, borough: str, band: str = "D") -> float:
    row = council_tax_df[council_tax_df["borough"] == borough]
    if len(row) == 0:
        return 1_900.0
    col = f"band_{band.lower()}"
    if col not in row.columns:
        return 1_900.0
    return float(row[col].iloc[0])


def lookup_boe_rate(boe_df: pd.DataFrame, ltv: float, fix_years: int) -> float:
    subset = boe_df[boe_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    if subset.empty:
        return 0.055
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return float(row["rate_pct"]) / 100.0
    return float(subset.iloc[-1]["rate_pct"]) / 100.0
