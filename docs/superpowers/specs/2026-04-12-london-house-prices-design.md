# London House Prices Dashboard — Design Spec

## Goal
Add a Streamlit dashboard page for exploring London house prices by postcode district, comparing growth across areas, and analysing the "brand effect" (correlation between nearby shops/franchises and house price growth).

## Deliverables
1. **Data prep script:** `scripts/build_london_ppd.py` — downloads Land Registry PPD CSVs, filters to London, saves as parquet
2. **GeoJSON file:** `dashboard/data/london_postcode_districts.geojson` — postcode district boundaries from ONS
3. **Dashboard page:** `dashboard/pages/42_London_House_Prices.py` — 4-tab page
4. **Test file:** `dashboard/tests/test_london_house_prices.py`
5. **Dependencies:** add `geopandas>=0.14.0` to `dashboard/requirements.txt`
6. **Sidebar nav:** add page link to `dashboard/lib/nav.py`

---

## 1. Data

### Pre-processed parquet (built by script)

**Script:** `scripts/build_london_ppd.py`

Downloads Land Registry Price Paid Data yearly CSVs (2015–2024) from:
`https://price-paid-data.publicdata.landregistry.gov.uk/pp-{year}.csv`

Processing:
- Filter to London postcodes (starting with E, EC, N, NW, SE, SW, W, WC)
- Extract postcode district (first part of postcode, e.g., "SW11" from "SW11 1AA")
- Keep columns: price, date, postcode, postcode_district, property_type, new_build
- Save to `dashboard/data/london_ppd.parquet` (pyarrow compression)

Expected size: ~20-30MB for 10 years of London transactions.

PPD CSV columns (no header, positional):
0: id, 1: price, 2: date, 3: postcode, 4: property_type (D/S/T/F), 5: new_build (Y/N), 6: tenure, 7: paon, 8: saon, 9: street, 10: locality, 11: town, 12: district, 13: county, 14: ppd_type, 15: record_status

### GeoJSON boundaries

**Source:** ONS Open Geography Portal — postcode district boundaries for London
**File:** `dashboard/data/london_postcode_districts.geojson`
**Licence:** Open Government Licence v3.0

This is downloaded once and committed to the repo. Contains polygon geometries for each London postcode district (SW1, SW11, E14, N1, etc.).

### OpenStreetMap Overpass API (runtime, Tab 3 only)

Query for a brand name's shops within the London bounding box:
```
[out:json][timeout:25];
area["name"="London"]["admin_level"="6"]->.london;
(
  node["brand"~"{brand_name}",i](area.london);
  way["brand"~"{brand_name}",i](area.london);
);
out center;
```

Returns lat/lng of each shop location. Free, no auth. Cached with `@st.cache_data(ttl=86400)`.

---

## 2. Dashboard Page

**File:** `dashboard/pages/42_London_House_Prices.py`

### Tab 1: Postcode Growth

**Inputs (sidebar):**
- Postcode district text input (default: "SW11")
- Year range slider (2015–2025, default: full range)

**Outputs:**
- Choropleth map of London: all postcode districts coloured by current average price, selected district highlighted with a border
- Line chart: average price per year for the selected district
- Metrics row: current avg price, total growth %, peak year, number of transactions

**Data flow:**
- Load parquet → filter to selected district + year range → group by year → compute avg price per year
- Load GeoJSON → merge with avg price data → render Plotly choropleth_mapbox

### Tab 2: Compare Postcodes

**Inputs (sidebar):**
- Two postcode district text inputs (defaults: "SW11", "E14")
- Year range slider

**Outputs:**
- Choropleth map with both districts highlighted in contrasting colours
- Overlaid line chart: both districts on same y-axis
- Side-by-side comparison table: avg price, growth %, transaction count for each

### Tab 3: Brand Effect

**Input (sidebar):**
- Brand name text input (default: "Waitrose")

**Processing:**
1. Query Overpass API for brand locations in London → list of lat/lng
2. For each brand location, find the nearest postcode district (spatial join with GeoJSON)
3. Split districts into "has brand" vs "no brand"
4. Compute avg price growth (2015→latest) for each group

**Outputs:**
- Choropleth map: districts coloured green (has brand) / grey (no brand)
- Brand locations plotted as markers on the map
- Bar chart or line chart: average growth in "near brand" vs "no brand" districts
- Stat: "Postcodes near {brand} grew X% vs Y% for the rest of London"

### Tab 4: Tests

Standard `render_test_tab("test_london_house_prices.py")` pattern.

---

## 3. Dependencies

Add to `dashboard/requirements.txt`:
```
geopandas>=0.14.0
```

Plotly, pandas, numpy, requests already present.

---

## 4. Tests

**File:** `dashboard/tests/test_london_house_prices.py`

Follows existing conftest.py pattern (autouse mocks for requests, yfinance).

Additional mocks needed:
- Mock `pd.read_parquet` to return a small fake London PPD dataframe
- Mock `requests.get` for Overpass API to return fake shop locations
- Mock `geopandas.read_file` to return a simple fake GeoDataFrame

Tests:
- Page loads without error (AppTest)
- Title check
- Has postcode text input
- Has year range slider
- Has tabs (at least 3)

---

## 5. Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `scripts/build_london_ppd.py` | Create | Data prep — download PPD, filter London, save parquet |
| `dashboard/data/london_ppd.parquet` | Generated | Pre-processed London transaction data |
| `dashboard/data/london_postcode_districts.geojson` | Download + commit | Postcode district polygon boundaries |
| `dashboard/pages/42_London_House_Prices.py` | Create | Dashboard page with 4 tabs |
| `dashboard/tests/test_london_house_prices.py` | Create | AppTest smoke tests |
| `dashboard/lib/nav.py` | Modify | Add sidebar link |
| `dashboard/requirements.txt` | Modify | Add geopandas |
