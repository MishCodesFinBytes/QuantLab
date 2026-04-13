"""Build the ~50 MB england_ppd_benchmark.parquet file.

One-time tool. Downloads the current UK Land Registry Price Paid Data
yearly releases, keeps the most recent 2 years of transactions,
and writes a compressed parquet at dashboard/data/england_ppd_benchmark.parquet.

Run:
    cd dashboard && python scripts/build_benchmark_parquet.py

Source:
    https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads

The data is published under the Open Government Licence v3.0.
"""

from __future__ import annotations

import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd

YEAR_CSV_URL = (
    "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-{year}.csv"
)

# Schema for the raw gov.uk CSV (headerless, 16 cols)
RAW_COLUMNS = [
    "transaction_id", "price", "date", "postcode", "property_type",
    "new_build", "duration", "paon", "saon", "street", "locality",
    "town_city", "district", "county", "ppd_category", "record_status",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_PATH = DATA_DIR / "england_ppd_benchmark.parquet"


def download_year(year: int) -> pd.DataFrame:
    url = YEAR_CSV_URL.format(year=year)
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url) as resp:
        raw = resp.read()
    print(f"  got {len(raw) / (1024*1024):.1f} MB")
    df = pd.read_csv(
        io.BytesIO(raw),
        names=RAW_COLUMNS,
        header=None,
        parse_dates=["date"],
        low_memory=False,
    )
    return df


def main() -> int:
    this_year = dt.date.today().year
    years = [this_year - 1, this_year - 2]
    frames = [download_year(y) for y in years]
    df = pd.concat(frames, ignore_index=True)
    print(f"Combined rows: {len(df):,}")

    df = df.dropna(subset=["postcode", "price", "date"])
    df["postcode_district"] = df["postcode"].str.split(" ").str[0]
    df = df[["transaction_id", "price", "date", "postcode",
             "postcode_district", "property_type", "town_city", "district"]]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, compression="snappy", index=False)
    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT_PATH} ({size_mb:.1f} MB, {len(df):,} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
