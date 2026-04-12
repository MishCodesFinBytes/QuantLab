"""Data loading, aggregation, and Overpass API helpers for London house prices."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PPD_PATH = DATA_DIR / "london_ppd.parquet"
GEOJSON_PATH = DATA_DIR / "london_postcode_districts.geojson"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
LONDON_BBOX = "51.28,-0.51,51.69,0.33"


def load_ppd() -> pd.DataFrame:
    """Load the pre-processed London PPD parquet file."""
    return pd.read_parquet(PPD_PATH)


def load_geojson() -> dict:
    """Load London postcode district GeoJSON as a dict."""
    import json
    with open(GEOJSON_PATH) as f:
        return json.load(f)


def aggregate_by_district_year(df: pd.DataFrame, district: str) -> pd.DataFrame:
    """Compute average price per year for a single postcode district."""
    subset = df[df["postcode_district"].str.upper() == district.upper()]
    if subset.empty:
        return pd.DataFrame(columns=["year", "avg_price", "median_price", "count"])
    subset = subset.copy()
    subset["year"] = subset["date"].dt.year
    agg = subset.groupby("year").agg(
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        count=("price", "count"),
    ).reset_index()
    return agg


def get_all_districts_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average price per postcode district (latest year)."""
    latest_year = df["date"].dt.year.max()
    recent = df[df["date"].dt.year == latest_year]
    agg = recent.groupby("postcode_district").agg(
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        count=("price", "count"),
    ).reset_index()
    return agg


def compute_growth(df: pd.DataFrame, district: str) -> dict:
    """Compute growth stats for a district."""
    agg = aggregate_by_district_year(df, district)
    if len(agg) < 2:
        return {"growth_pct": 0, "start_price": 0, "end_price": 0, "peak_year": 0}
    first = agg.iloc[0]
    last = agg.iloc[-1]
    peak = agg.loc[agg["avg_price"].idxmax()]
    growth = ((last["avg_price"] - first["avg_price"]) / first["avg_price"]) * 100
    return {
        "growth_pct": round(growth, 1),
        "start_price": round(first["avg_price"]),
        "end_price": round(last["avg_price"]),
        "peak_year": int(peak["year"]),
    }


def query_brand_locations(brand: str) -> list[dict]:
    """Query OpenStreetMap Overpass API for brand locations in London."""
    import time
    query = (
        f'[out:json][timeout:60][bbox:{LONDON_BBOX}];'
        f'(node["brand"~"{brand}",i];way["brand"~"{brand}",i];'
        f'node["name"~"{brand}",i]["shop"];way["name"~"{brand}",i]["shop"];);'
        f'out center;'
    )
    for attempt in range(3):
        try:
            resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=60)
            if resp.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            locations = []
            for el in elements:
                lat = el.get("lat") or el.get("center", {}).get("lat")
                lon = el.get("lon") or el.get("center", {}).get("lon")
                name = el.get("tags", {}).get("name", brand)
                if lat and lon:
                    locations.append({"lat": lat, "lon": lon, "name": name})
            return locations
        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(3)
                continue
            raise
    return []


def assign_brand_districts(locations: list[dict], geojson: dict) -> set:
    """Find which postcode districts contain brand locations using point-in-polygon."""
    import geopandas as gpd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame.from_features(geojson["features"])
    brand_districts = set()
    for loc in locations:
        pt = Point(loc["lon"], loc["lat"])
        match = gdf[gdf.geometry.contains(pt)]
        if not match.empty:
            brand_districts.add(match.iloc[0]["name"])
    return brand_districts
