"""Data loaders and default-value lookups for the rent-vs-buy calculator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_district_to_borough() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_district_to_borough.csv")


def load_borough_rents() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_borough_rents.csv")


def load_borough_rents_by_bedroom() -> pd.DataFrame:
    """Load the ONS bedroom-segmented borough rent table.

    Schema: borough, beds_studio, beds_1, beds_2, beds_3, beds_4plus,
            source_year, source_url
    """
    return pd.read_csv(DATA_DIR / "london_borough_rents_by_bedroom.csv")


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
    bedrooms: str | None = None,
) -> int:
    """Return median sale price from the tightest available filter.

    Falls back in order:
      1. district × type × new_build × bedrooms, last 3y, >=10 sales
      2. district × type × new_build, last 3y, >=10 sales
      3. borough × type × bedrooms, last 3y, > 0 sales
      4. borough × type, last 3y, > 0 sales
      5. £500,000 hardcoded fallback
    """
    three_years_ago = pd.Timestamp.now() - pd.DateOffset(years=3)
    recent = ppd_df[ppd_df["date"] >= three_years_ago]
    new_build_flag = "Y" if new_build else "N"
    has_bedrooms_col = "bedrooms" in recent.columns

    # 1. district x type x new_build x bedrooms
    if postcode_district and bedrooms and has_bedrooms_col:
        subset = recent[
            (recent["postcode_district"] == postcode_district)
            & (recent["property_type"] == property_type)
            & (recent["new_build"] == new_build_flag)
            & (recent["bedrooms"] == bedrooms)
        ]
        if len(subset) >= 10:
            return int(subset["price"].median())

    # 2. district x type x new_build (existing)
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

    # 3. borough x type x bedrooms
    if borough_districts and bedrooms and has_bedrooms_col:
        subset = recent[
            (recent["postcode_district"].isin(borough_districts))
            & (recent["property_type"] == property_type)
            & (recent["bedrooms"] == bedrooms)
        ]
        if len(subset) > 0:
            return int(subset["price"].median())

    # 4. borough x type (existing)
    if borough_districts:
        subset = recent[
            (recent["postcode_district"].isin(borough_districts))
            & (recent["property_type"] == property_type)
        ]
        if len(subset) > 0:
            return int(subset["price"].median())

    # 5. hardcoded fallback
    return 500_000


_BEDROOM_COLUMN_MAP = {
    "studio": "beds_studio",
    "1": "beds_1",
    "2": "beds_2",
    "3": "beds_3",
    "4+": "beds_4plus",
}


def default_monthly_rent(
    rents_df: pd.DataFrame,
    rents_by_bedroom_df: pd.DataFrame,
    borough: str,
    bedrooms: str,
) -> int:
    """Return median monthly rent for the chosen borough + bedroom band.

    Falls back to the single-median rents_df row when the bedroom band
    is missing for the borough, and to a hardcoded £2000 when the borough
    is unknown to both files.
    """
    bedroom_col = _BEDROOM_COLUMN_MAP.get(bedrooms)
    if bedroom_col is not None:
        row = rents_by_bedroom_df[rents_by_bedroom_df["borough"] == borough]
        if len(row) > 0 and bedroom_col in row.columns:
            value = row[bedroom_col].iloc[0]
            if pd.notna(value):
                return int(value)

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
