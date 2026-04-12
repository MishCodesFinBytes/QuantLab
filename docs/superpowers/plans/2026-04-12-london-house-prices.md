# London House Prices Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit dashboard page for exploring London house prices by postcode district — single postcode growth, compare two postcodes, and "brand effect" correlation analysis — with choropleth maps.

**Architecture:** Pre-processed Land Registry PPD data as parquet, London postcode district GeoJSON boundaries from GitHub, Overpass API for brand shop locations. Single dashboard page with 4 tabs (growth, compare, brand effect, tests). Plotly choropleth_mapbox for maps.

**Tech Stack:** Streamlit, Plotly, pandas, geopandas, requests, pyarrow

---

## File Structure

```
scripts/
└── build_london_ppd.py              # Data prep — download PPD, filter London, save parquet

dashboard/
├── data/
│   ├── london_ppd.parquet            # Generated — 10 years of London transactions
│   └── london_postcode_districts.geojson  # Generated — merged postcode boundaries
├── lib/
│   └── house_prices.py               # Data loading, aggregation, Overpass API helpers
├── pages/
│   └── 42_London_House_Prices.py     # Dashboard page — 4 tabs
├── tests/
│   └── test_london_house_prices.py   # AppTest smoke tests
├── requirements.txt                  # Add geopandas
└── lib/nav.py                        # Add sidebar link
```

---

### Task 1: Add Dependencies

**Files:**
- Modify: `dashboard/requirements.txt`

- [ ] **Step 1: Add geopandas to requirements.txt**

Add after the existing `statsmodels` line:

```
geopandas>=0.14.0
```

- [ ] **Step 2: Install locally**

Run: `cd C:/codebase/quant_lab/dashboard && pip install geopandas`

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/requirements.txt
git commit -m "deps: add geopandas for London house prices choropleth"
```

---

### Task 2: Data Prep Script + GeoJSON

**Files:**
- Create: `scripts/build_london_ppd.py`

- [ ] **Step 1: Create the data prep script**

Create `scripts/build_london_ppd.py`:

```python
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
```

- [ ] **Step 2: Run the script**

Run: `cd C:/codebase/quant_lab && python scripts/build_london_ppd.py`

This takes ~5-10 minutes (downloading ~1.5GB of CSVs). Expected output: `london_ppd.parquet` (~20-30MB) and `london_postcode_districts.geojson` (~1MB) in `dashboard/data/`.

- [ ] **Step 3: Verify the output files**

Run:
```bash
ls -la C:/codebase/quant_lab/dashboard/data/london_ppd.parquet
ls -la C:/codebase/quant_lab/dashboard/data/london_postcode_districts.geojson
python -c "import pandas as pd; df = pd.read_parquet('C:/codebase/quant_lab/dashboard/data/london_ppd.parquet'); print(df.shape); print(df.head())"
```

- [ ] **Step 4: Add data files to .gitignore (parquet is too large for git)**

Add to the repo root `.gitignore`:
```
dashboard/data/london_ppd.parquet
```

The GeoJSON is small enough to commit (~1MB).

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add scripts/build_london_ppd.py dashboard/data/london_postcode_districts.geojson .gitignore
git commit -m "feat: add London PPD data prep script and postcode district GeoJSON"
```

---

### Task 3: House Prices Helper Library

**Files:**
- Create: `dashboard/lib/house_prices.py`
- Create: `dashboard/tests/test_london_house_prices.py`

- [ ] **Step 1: Write failing tests for data loading helpers**

Create `dashboard/tests/test_london_house_prices.py`:

```python
"""Tests for London House Prices page."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock


@pytest.fixture
def sample_ppd():
    """Small London PPD DataFrame for testing."""
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=100, freq="W")
    districts = np.random.choice(["SW11", "E14", "N1", "SE1", "W1"], 100)
    prices = np.random.randint(200000, 800000, 100)
    types = np.random.choice(["F", "T", "S", "D"], 100)
    return pd.DataFrame({
        "price": prices,
        "date": dates,
        "postcode": [f"{d} {np.random.randint(1,9)}AA" for d in districts],
        "postcode_district": districts,
        "property_type": types,
        "new_build": np.random.choice(["Y", "N"], 100),
    })


class TestHousePriceHelpers:
    def test_load_ppd_returns_dataframe(self, sample_ppd):
        with patch("pandas.read_parquet", return_value=sample_ppd):
            from lib.house_prices import load_ppd
            df = load_ppd()
            assert isinstance(df, pd.DataFrame)
            assert "postcode_district" in df.columns

    def test_aggregate_by_district_year(self, sample_ppd):
        from lib.house_prices import aggregate_by_district_year
        result = aggregate_by_district_year(sample_ppd, "SW11")
        assert "year" in result.columns
        assert "avg_price" in result.columns

    def test_aggregate_empty_district(self, sample_ppd):
        from lib.house_prices import aggregate_by_district_year
        result = aggregate_by_district_year(sample_ppd, "ZZ99")
        assert len(result) == 0

    def test_get_all_districts_summary(self, sample_ppd):
        from lib.house_prices import get_all_districts_summary
        result = get_all_districts_summary(sample_ppd)
        assert "postcode_district" in result.columns
        assert "avg_price" in result.columns

    def test_query_overpass_returns_list(self):
        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.json.return_value = {
            "elements": [
                {"lat": 51.5, "lon": -0.1, "tags": {"name": "Waitrose"}},
                {"type": "way", "center": {"lat": 51.51, "lon": -0.12}, "tags": {"name": "Waitrose"}},
            ]
        }
        with patch("requests.get", return_value=fake_resp):
            from lib.house_prices import query_brand_locations
            locs = query_brand_locations("Waitrose")
            assert len(locs) == 2
            assert "lat" in locs[0]
            assert "lon" in locs[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_london_house_prices.py::TestHousePriceHelpers -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Create the helper library**

Create `dashboard/lib/house_prices.py`:

```python
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
    query = (
        f'[out:json][timeout:25][bbox:{LONDON_BBOX}];'
        f'(node["brand"~"{brand}",i];way["brand"~"{brand}",i];);'
        f'out center;'
    )
    resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=30)
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
```

- [ ] **Step 4: Run tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_london_house_prices.py::TestHousePriceHelpers -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/house_prices.py dashboard/tests/test_london_house_prices.py
git commit -m "feat: add house prices helper library with tests"
```

---

### Task 4: Dashboard Page — Tab 1 (Postcode Growth)

**Files:**
- Create: `dashboard/pages/42_London_House_Prices.py`

- [ ] **Step 1: Create the dashboard page with Tab 1**

Create `dashboard/pages/42_London_House_Prices.py`:

```python
"""London House Prices — postcode growth, comparison, and brand effect analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from house_prices import (
    load_ppd,
    load_geojson,
    aggregate_by_district_year,
    get_all_districts_summary,
    compute_growth,
    query_brand_locations,
    assign_brand_districts,
)
from nav import render_sidebar
from test_tab import render_test_tab

st.set_page_config(page_title="London House Prices", page_icon="assets/logo.png", layout="wide")
render_sidebar()
st.title("London House Prices")

tab_growth, tab_compare, tab_brand, tab_tests = st.tabs(
    ["Postcode Growth", "Compare Postcodes", "Brand Effect", "Tests"]
)


@st.cache_data(show_spinner="Loading London house price data...")
def get_ppd():
    return load_ppd()


@st.cache_data(show_spinner="Loading map boundaries...")
def get_geojson():
    return load_geojson()


ppd = get_ppd()
geojson = get_geojson()
all_districts = sorted(ppd["postcode_district"].unique())

with tab_growth:
    with st.expander("How it works"):
        st.markdown("""
        - **Data source:** HM Land Registry Price Paid Data (2015-2024) — every residential property sale in London
        - **Postcode district:** the first part of a UK postcode (e.g., SW11, E14, N1)
        - **Map:** choropleth coloured by average price in the latest year
        - **Chart:** average price per year for the selected district
        """)

    col1, col2 = st.columns([1, 2])
    with col1:
        district = st.selectbox("Postcode District", all_districts, index=all_districts.index("SW11") if "SW11" in all_districts else 0, key="growth_district")
        year_range = st.slider("Year Range", 2015, 2024, (2015, 2024), key="growth_years")

    filtered = ppd[(ppd["date"].dt.year >= year_range[0]) & (ppd["date"].dt.year <= year_range[1])]
    agg = aggregate_by_district_year(filtered, district)
    summary = get_all_districts_summary(filtered)
    growth = compute_growth(filtered, district)

    with col2:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Avg Price", f"\u00a3{growth['end_price']:,}")
        c2.metric("Growth", f"{growth['growth_pct']}%")
        c3.metric("Peak Year", str(growth["peak_year"]))
        c4.metric("Transactions", f"{agg['count'].sum():,}" if len(agg) > 0 else "0")

    map_col, chart_col = st.columns([1, 1])

    with map_col:
        merged = summary.copy()
        fig_map = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations="postcode_district",
            featureidkey="properties.name",
            color="avg_price",
            color_continuous_scale="YlOrRd",
            mapbox_style="carto-positron",
            center={"lat": 51.5, "lon": -0.1},
            zoom=9,
            opacity=0.7,
            labels={"avg_price": "Avg Price"},
            title="Average Price by District",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=450)
        st.plotly_chart(fig_map, use_container_width=True)

    with chart_col:
        if not agg.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=agg["year"], y=agg["avg_price"],
                mode="lines+markers", name=district,
                line=dict(color="#2a7ae2", width=3),
            ))
            fig_line.update_layout(
                title=f"{district} — Average House Price",
                xaxis_title="Year", yaxis_title="Price (\u00a3)",
                height=450,
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info(f"No data found for {district}.")
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/pages/42_London_House_Prices.py
git commit -m "feat: add London House Prices page — Tab 1 postcode growth"
```

---

### Task 5: Dashboard Page — Tab 2 (Compare Postcodes)

**Files:**
- Modify: `dashboard/pages/42_London_House_Prices.py`

- [ ] **Step 1: Add Tab 2 content**

Append inside the `with tab_compare:` block (after the `tab_growth` block, before `tab_brand`):

```python
with tab_compare:
    with st.expander("How it works"):
        st.markdown("""
        - Pick two postcode districts and a year range
        - Side-by-side line chart shows price trends for both
        - Map highlights both districts in contrasting colours
        """)

    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        dist_a = st.selectbox("District A", all_districts, index=all_districts.index("SW11") if "SW11" in all_districts else 0, key="cmp_a")
    with cc2:
        dist_b = st.selectbox("District B", all_districts, index=all_districts.index("E14") if "E14" in all_districts else 1, key="cmp_b")
    with cc3:
        cmp_years = st.slider("Year Range", 2015, 2024, (2015, 2024), key="cmp_years")

    cmp_filtered = ppd[(ppd["date"].dt.year >= cmp_years[0]) & (ppd["date"].dt.year <= cmp_years[1])]
    agg_a = aggregate_by_district_year(cmp_filtered, dist_a)
    agg_b = aggregate_by_district_year(cmp_filtered, dist_b)
    growth_a = compute_growth(cmp_filtered, dist_a)
    growth_b = compute_growth(cmp_filtered, dist_b)

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"**{dist_a}**")
        st.metric("Avg Price", f"\u00a3{growth_a['end_price']:,}")
        st.metric("Growth", f"{growth_a['growth_pct']}%")
    with mc2:
        st.markdown(f"**{dist_b}**")
        st.metric("Avg Price", f"\u00a3{growth_b['end_price']:,}")
        st.metric("Growth", f"{growth_b['growth_pct']}%")

    fig_cmp = go.Figure()
    if not agg_a.empty:
        fig_cmp.add_trace(go.Scatter(x=agg_a["year"], y=agg_a["avg_price"], mode="lines+markers", name=dist_a, line=dict(color="#2a7ae2", width=3)))
    if not agg_b.empty:
        fig_cmp.add_trace(go.Scatter(x=agg_b["year"], y=agg_b["avg_price"], mode="lines+markers", name=dist_b, line=dict(color="#e24a4a", width=3)))
    fig_cmp.update_layout(title=f"{dist_a} vs {dist_b} — Average House Price", xaxis_title="Year", yaxis_title="Price (\u00a3)", height=450)
    st.plotly_chart(fig_cmp, use_container_width=True)
```

- [ ] **Step 2: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/pages/42_London_House_Prices.py
git commit -m "feat: add Tab 2 — compare two postcode districts"
```

---

### Task 6: Dashboard Page — Tab 3 (Brand Effect)

**Files:**
- Modify: `dashboard/pages/42_London_House_Prices.py`

- [ ] **Step 1: Add Tab 3 content**

Append inside the `with tab_brand:` block:

```python
with tab_brand:
    with st.expander("How it works"):
        st.markdown("""
        - Enter a brand name (e.g., Waitrose, Pret, Costa, Greggs)
        - Queries OpenStreetMap for that brand's locations in London
        - Finds which postcode districts have that brand nearby
        - Compares average house price growth in districts **with** vs **without** the brand
        - The classic "Waitrose effect" analysis
        """)

    brand = st.text_input("Brand Name", value="Waitrose", key="brand_input")

    if brand:
        @st.cache_data(show_spinner=f"Finding {brand} locations in London...")
        def get_brand_locs(b):
            return query_brand_locations(b)

        @st.cache_data(show_spinner="Matching to postcode districts...")
        def get_brand_districts(b, _geojson):
            locs = get_brand_locs(b)
            districts = assign_brand_districts(locs, _geojson)
            return locs, districts

        try:
            locs, brand_districts = get_brand_districts(brand, geojson)
        except Exception as e:
            st.error(f"Could not fetch {brand} locations: {e}")
            locs, brand_districts = [], set()

        if not locs:
            st.warning(f"No '{brand}' locations found in London on OpenStreetMap.")
        else:
            st.success(f"Found {len(locs)} {brand} locations across {len(brand_districts)} postcode districts.")

            summary_all = get_all_districts_summary(ppd)
            summary_all["has_brand"] = summary_all["postcode_district"].isin(brand_districts)

            near = summary_all[summary_all["has_brand"]]
            far = summary_all[~summary_all["has_brand"]]
            avg_near = near["avg_price"].mean() if len(near) > 0 else 0
            avg_far = far["avg_price"].mean() if len(far) > 0 else 0

            bc1, bc2, bc3 = st.columns(3)
            bc1.metric(f"Near {brand}", f"\u00a3{avg_near:,.0f}")
            bc2.metric(f"Away from {brand}", f"\u00a3{avg_far:,.0f}")
            diff_pct = ((avg_near - avg_far) / avg_far * 100) if avg_far > 0 else 0
            bc3.metric("Premium", f"{diff_pct:+.1f}%")

            fig_brand = px.choropleth_mapbox(
                summary_all,
                geojson=geojson,
                locations="postcode_district",
                featureidkey="properties.name",
                color="has_brand",
                color_discrete_map={True: "#2ea043", False: "#ddd"},
                mapbox_style="carto-positron",
                center={"lat": 51.5, "lon": -0.1},
                zoom=9,
                opacity=0.7,
                labels={"has_brand": f"Has {brand}"},
                title=f"Postcode Districts with {brand}",
            )

            if locs:
                loc_df = pd.DataFrame(locs)
                fig_brand.add_trace(go.Scattermapbox(
                    lat=loc_df["lat"], lon=loc_df["lon"],
                    mode="markers",
                    marker=dict(size=8, color="#e24a4a"),
                    name=f"{brand} locations",
                    text=loc_df["name"],
                ))

            fig_brand.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=500)
            st.plotly_chart(fig_brand, use_container_width=True)

            fig_bar = go.Figure(data=[
                go.Bar(name=f"Near {brand}", x=["Average Price"], y=[avg_near], marker_color="#2ea043"),
                go.Bar(name=f"Away from {brand}", x=["Average Price"], y=[avg_far], marker_color="#aaa"),
            ])
            fig_bar.update_layout(title=f"The {brand} Effect", yaxis_title="Average Price (\u00a3)", barmode="group", height=350)
            st.plotly_chart(fig_bar, use_container_width=True)
```

- [ ] **Step 2: Add the Tests tab**

Append:

```python
with tab_tests:
    render_test_tab("test_london_house_prices.py")
```

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/pages/42_London_House_Prices.py
git commit -m "feat: add Tab 3 — brand effect analysis with Overpass API"
```

---

### Task 7: AppTest Smoke Tests

**Files:**
- Modify: `dashboard/tests/test_london_house_prices.py`

- [ ] **Step 1: Add AppTest smoke tests**

Add to the top of `test_london_house_prices.py` (after imports, before `TestHousePriceHelpers`):

```python
from streamlit.testing.v1 import AppTest


@pytest.fixture(autouse=True)
def mock_ppd_data(sample_ppd):
    """Mock parquet loading for AppTest."""
    with patch("pandas.read_parquet", return_value=sample_ppd):
        with patch("builtins.open", create=True):
            import json
            fake_geojson = {"type": "FeatureCollection", "features": []}
            with patch("json.load", return_value=fake_geojson):
                yield


class TestLondonHousePricesPage:
    def _run(self):
        at = AppTest.from_file("pages/42_London_House_Prices.py", default_timeout=30)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("London House Prices" in t.value for t in at.title)
```

- [ ] **Step 2: Run all tests**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/test_london_house_prices.py -v`
Expected: All PASSED

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/tests/test_london_house_prices.py
git commit -m "test: add AppTest smoke tests for London House Prices page"
```

---

### Task 8: Sidebar Nav + Final Verification

**Files:**
- Modify: `dashboard/lib/nav.py`

- [ ] **Step 1: Add London House Prices to sidebar**

In `nav.py`, after the Plotting Libraries line, add:

```python
    st.sidebar.page_link("pages/42_London_House_Prices.py", label="London House Prices")
```

- [ ] **Step 2: Run full test suite**

Run: `cd C:/codebase/quant_lab/dashboard && python -m pytest tests/ -v --tb=short`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
cd C:/codebase/quant_lab
git add dashboard/lib/nav.py
git commit -m "feat: add London House Prices to sidebar navigation"
```
