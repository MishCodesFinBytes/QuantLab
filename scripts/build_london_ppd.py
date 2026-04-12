"""Download Land Registry PPD data, filter to London, save as parquet.

Usage:
    python scripts/build_london_ppd.py

Downloads yearly CSVs (2015-2024) from Land Registry, filters to London
postcodes, extracts postcode district, and saves to dashboard/data/london_ppd.parquet.
Also downloads and merges London postcode district GeoJSON boundaries.
"""

import re
import json
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "dashboard" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PPD_URL = "https://price-paid-data.publicdata.landregistry.gov.uk/pp-{year}.csv"
PPD_COLS = [
    "id", "price", "date", "postcode", "property_type", "new_build",
    "tenure", "paon", "saon", "street", "locality", "town",
    "district", "county", "ppd_type", "record_status",
]
KEEP_COLS = ["price", "date", "postcode", "postcode_district", "property_type", "new_build"]
LONDON_RE = re.compile(r"^(E|EC|N|NW|SE|SW|W|WC)\d", re.IGNORECASE)
YEARS = range(2015, 2025)

GEOJSON_BASE = "https://raw.githubusercontent.com/missinglink/uk-postcode-polygons/master/geojson/{}.geojson"
LONDON_AREAS = ["E", "EC", "N", "NW", "SE", "SW", "W", "WC"]


def extract_district(postcode):
    """Extract postcode district from full postcode, e.g. 'SW11 1AA' -> 'SW11'."""
    if pd.isna(postcode):
        return None
    parts = str(postcode).strip().split()
    return parts[0] if parts else None


def download_ppd():
    """Download PPD CSVs, filter to London, return combined DataFrame."""
    frames = []
    for year in YEARS:
        url = PPD_URL.format(year=year)
        print(f"Downloading {url}...")
        df = pd.read_csv(url, header=None, names=PPD_COLS, low_memory=False)
        df = df[df["postcode"].str.match(LONDON_RE, na=False)]
        df["postcode_district"] = df["postcode"].apply(extract_district)
        df["date"] = pd.to_datetime(df["date"])
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df[KEEP_COLS].dropna(subset=["price", "postcode_district"])
        frames.append(df)
        print(f"  {year}: {len(df):,} London transactions")

    combined = pd.concat(frames, ignore_index=True)
    out = DATA_DIR / "london_ppd.parquet"
    combined.to_parquet(out, index=False)
    print(f"\nSaved {len(combined):,} rows to {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return combined


def download_geojson():
    """Download and merge London postcode district GeoJSON files."""
    features = []
    for area in LONDON_AREAS:
        url = GEOJSON_BASE.format(area)
        print(f"Downloading {url}...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        features.extend(data.get("features", []))
        print(f"  {area}: {len(data.get('features', []))} districts")

    geojson = {"type": "FeatureCollection", "features": features}
    out = DATA_DIR / "london_postcode_districts.geojson"
    with open(out, "w") as f:
        json.dump(geojson, f)
    print(f"\nSaved {len(features)} district boundaries to {out}")
    return geojson


if __name__ == "__main__":
    download_ppd()
    download_geojson()
