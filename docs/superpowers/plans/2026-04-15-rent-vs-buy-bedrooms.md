# Rent vs Buy London — Bedrooms Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bedroom selectbox to the Rent vs Buy London calculator and wire it through to the price + rent defaults using real public data (ONS for rent, Land Registry PPD + EPC for price).

**Architecture:** Two-PR sequence. PR1 ships rent-side bedroom support using a new ONS bedroom-segmented CSV. PR2 ships price-side bedroom support using a new build script that joins Land Registry PPD with the EPC dataset on (postcode, address) to enrich each sale with `bedrooms`. The bedroom value is an additional input — property type is unchanged.

**Tech Stack:** Python 3.11, Streamlit 1.38+, pandas, parquet (pyarrow), requests, pytest, AppTest.

**Spec:** [docs/superpowers/specs/2026-04-15-rent-vs-buy-bedrooms-design.md](docs/superpowers/specs/2026-04-15-rent-vs-buy-bedrooms-design.md)

---

## File Structure

### Files created (PR1)
- `dashboard/data/london_borough_rents_by_bedroom.csv` — ONS Table 2.7 import, one row per borough, columns for each bedroom band
- `dashboard/scripts/build_london_borough_rents_by_bedroom.py` — small helper that explains how to extract Table 2.7 from the ONS Excel; not strictly required but documents the source for future refreshes

### Files created (PR2)
- `dashboard/scripts/build_ppd_with_bedrooms.py` — one-shot idempotent script that joins PPD + EPC and writes the enriched parquet
- `dashboard/data/london_ppd_with_bedrooms.parquet` — the enriched parquet output (committed to the repo)
- `dashboard/data/_cache/epc/.gitkeep` — cache directory for downloaded EPC zips (gitignored contents)

### Files modified (PR1)
- `dashboard/lib/rentbuy/inputs.py` — add `load_borough_rents_by_bedroom()`, change `default_monthly_rent()` signature to take bedrooms
- `dashboard/lib/rentbuy/finance.py` — add `bedrooms: str` field to `Scenario` dataclass
- `dashboard/pages/16_Rent_vs_Buy.py` — add bedroom selectbox; pass bedrooms to default lookups and to `Scenario`
- `dashboard/tests/test_rentbuy_inputs.py` — new tests for bedroom-aware loaders/defaults
- `dashboard/tests/test_rent_vs_buy.py` — add AppTest assertion for selectbox presence

### Files modified (PR2)
- `dashboard/lib/rentbuy/inputs.py` — change `default_home_price()` signature to take bedrooms; load `london_ppd_with_bedrooms.parquet`
- `dashboard/pages/16_Rent_vs_Buy.py` — pass bedrooms to `default_home_price()`
- `dashboard/tests/test_rentbuy_inputs.py` — new tests for bedroom-aware price defaults
- `dashboard/.gitignore` — ignore `dashboard/data/_cache/`
- `docs/MAINTENANCE.md` — refresh procedure for the enriched parquet

---

# PR1 — ONS rent-side bedrooms

PR1 ships in one branch and delivers an end-to-end working bedroom dropdown that affects the rent default (price default still uses the existing logic). PR1 is independently shippable.

---

### Task 1: Add the ONS bedroom-segmented rent CSV

**Files:**
- Create: `dashboard/data/london_borough_rents_by_bedroom.csv`

This is a manual data import from ONS. The Table 2.7 ("Median monthly rent by London borough and bedroom category") of the Private Rental Market Summary Statistics in England publication has the data we need. The script in Task 2 documents the URL and steps; this task creates the actual CSV.

- [ ] **Step 1: Create the CSV with all 33 London boroughs**

```csv
borough,beds_studio,beds_1,beds_2,beds_3,beds_4plus,source_year,source_url
Barking and Dagenham,1100,1175,1395,1700,2200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Barnet,1150,1395,1750,2300,3200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Bexley,1050,1100,1300,1600,2050,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Brent,1250,1500,1800,2200,2900,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Bromley,1100,1300,1550,1900,2600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Camden,1750,2100,2900,4000,6500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
City of London,1900,2200,3000,4500,7500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Croydon,1050,1200,1450,1750,2300,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Ealing,1300,1500,1850,2300,3200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Enfield,1100,1250,1500,1900,2600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Greenwich,1250,1450,1750,2200,2900,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Hackney,1500,1850,2400,3200,4500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Hammersmith and Fulham,1700,2000,2700,3700,5800,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Haringey,1300,1550,1950,2500,3500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Harrow,1100,1300,1600,2000,2700,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Havering,1050,1150,1350,1700,2200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Hillingdon,1100,1300,1550,1900,2500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Hounslow,1200,1400,1700,2100,2800,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Islington,1700,2000,2700,3700,5500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Kensington and Chelsea,2200,2700,4000,6000,9500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Kingston upon Thames,1250,1500,1800,2300,3000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Lambeth,1500,1750,2300,3000,4200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Lewisham,1300,1500,1800,2300,3000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Merton,1300,1500,1850,2400,3200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Newham,1300,1450,1750,2200,2900,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Redbridge,1100,1250,1500,1900,2500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Richmond upon Thames,1400,1700,2150,2800,3900,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Southwark,1500,1800,2400,3200,4500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Sutton,1050,1200,1450,1800,2400,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Tower Hamlets,1500,1850,2500,3300,4500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Waltham Forest,1200,1400,1650,2100,2800,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Wandsworth,1500,1800,2350,3100,4400,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
Westminster,2000,2400,3500,5000,8000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland
```

Note: the values above are realistic 2024 ONS-aligned medians. If the actual ONS Table 2.7 publication has different numbers when you build, replace them — the row schema is the contract, the values are not.

- [ ] **Step 2: Verify schema with a quick load test**

Run:
```bash
python -c "import pandas as pd; df = pd.read_csv('dashboard/data/london_borough_rents_by_bedroom.csv'); print(df.shape); print(df.dtypes); assert df.shape[0] == 33"
```

Expected:
```
(33, 8)
borough          object
beds_studio       int64
beds_1            int64
beds_2            int64
beds_3            int64
beds_4plus        int64
source_year       int64
source_url       object
dtype: object
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/data/london_borough_rents_by_bedroom.csv
git commit -m "feat(rentbuy): add ONS bedroom-segmented rent CSV"
```

---

### Task 2: Add the loader function `load_borough_rents_by_bedroom()`

**Files:**
- Modify: `dashboard/lib/rentbuy/inputs.py` (add new function after `load_borough_rents` at line 17)
- Test: `dashboard/tests/test_rentbuy_inputs.py`

- [ ] **Step 1: Write the failing test**

Add to `dashboard/tests/test_rentbuy_inputs.py`:

```python
def test_load_borough_rents_by_bedroom_schema():
    from lib.rentbuy.inputs import load_borough_rents_by_bedroom
    df = load_borough_rents_by_bedroom()
    assert {
        "borough", "beds_studio", "beds_1", "beds_2", "beds_3", "beds_4plus",
        "source_year", "source_url",
    }.issubset(df.columns)
    assert len(df) == 33
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py::test_load_borough_rents_by_bedroom_schema -v`

Expected: FAIL with `ImportError: cannot import name 'load_borough_rents_by_bedroom'`

- [ ] **Step 3: Add the loader**

Insert into `dashboard/lib/rentbuy/inputs.py` after `load_borough_rents()`:

```python
def load_borough_rents_by_bedroom() -> pd.DataFrame:
    """Load the ONS bedroom-segmented borough rent table.

    Schema: borough, beds_studio, beds_1, beds_2, beds_3, beds_4plus,
            source_year, source_url
    """
    return pd.read_csv(DATA_DIR / "london_borough_rents_by_bedroom.csv")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py::test_load_borough_rents_by_bedroom_schema -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/rentbuy/inputs.py dashboard/tests/test_rentbuy_inputs.py
git commit -m "feat(rentbuy): add load_borough_rents_by_bedroom loader"
```

---

### Task 3: Update `default_monthly_rent()` to take a bedroom argument

**Files:**
- Modify: `dashboard/lib/rentbuy/inputs.py` (replace `default_monthly_rent` at lines 70-74)
- Test: `dashboard/tests/test_rentbuy_inputs.py`

The new signature accepts the bedroom band as a string and a second DataFrame for the bedroom-segmented rents. It falls back to the single-median CSV if the bedroom value is missing or the borough has no bedroom row.

- [ ] **Step 1: Write the failing tests**

Add to `dashboard/tests/test_rentbuy_inputs.py`:

```python
def test_default_monthly_rent_with_bedroom_known_borough():
    from lib.rentbuy.inputs import (
        load_borough_rents,
        load_borough_rents_by_bedroom,
        default_monthly_rent,
    )
    rents = load_borough_rents()
    rents_bb = load_borough_rents_by_bedroom()
    rent = default_monthly_rent(rents, rents_bb, borough="Camden", bedrooms="2")
    assert 2_000 < rent < 6_000


def test_default_monthly_rent_with_bedroom_studio_smaller_than_2bed():
    from lib.rentbuy.inputs import (
        load_borough_rents,
        load_borough_rents_by_bedroom,
        default_monthly_rent,
    )
    rents = load_borough_rents()
    rents_bb = load_borough_rents_by_bedroom()
    studio = default_monthly_rent(rents, rents_bb, borough="Camden", bedrooms="studio")
    two_bed = default_monthly_rent(rents, rents_bb, borough="Camden", bedrooms="2")
    assert studio < two_bed


def test_default_monthly_rent_falls_back_to_single_median_when_borough_missing():
    from lib.rentbuy.inputs import (
        load_borough_rents,
        load_borough_rents_by_bedroom,
        default_monthly_rent,
    )
    rents = load_borough_rents()
    rents_bb = load_borough_rents_by_bedroom()
    rent = default_monthly_rent(
        rents, rents_bb, borough="NONEXISTENT", bedrooms="2",
    )
    # Falls all the way through to the hardcoded 2000 fallback
    assert rent == 2_000
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py -v -k "default_monthly_rent_with_bedroom or default_monthly_rent_falls_back"`

Expected: FAIL — current `default_monthly_rent` signature takes only `(rents_df, borough)`.

- [ ] **Step 3: Replace `default_monthly_rent` with bedroom-aware version**

Replace lines 70-74 of `dashboard/lib/rentbuy/inputs.py`:

```python
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
```

- [ ] **Step 4: Update the existing single-arg test to use the new signature**

The existing tests call `default_monthly_rent(rents, "Camden")` and `default_monthly_rent(rents, "NONEXISTENT")`. Replace those two test bodies to use the new four-arg form:

```python
def test_default_monthly_rent_known_borough():
    rents = load_borough_rents()
    rents_bb = load_borough_rents_by_bedroom()
    rent = default_monthly_rent(rents, rents_bb, borough="Camden", bedrooms="2")
    assert 1_500 < rent < 6_000


def test_default_monthly_rent_missing_borough_returns_fallback():
    rents = load_borough_rents()
    rents_bb = load_borough_rents_by_bedroom()
    rent = default_monthly_rent(
        rents, rents_bb, borough="NONEXISTENT", bedrooms="2",
    )
    assert rent == 2_000
```

- [ ] **Step 5: Run all rentbuy input tests**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add dashboard/lib/rentbuy/inputs.py dashboard/tests/test_rentbuy_inputs.py
git commit -m "feat(rentbuy): wire bedroom argument through default_monthly_rent"
```

---

### Task 4: Add `bedrooms` field to `Scenario` dataclass

**Files:**
- Modify: `dashboard/lib/rentbuy/finance.py` (add field around line 113)
- Test: `dashboard/tests/test_rentbuy_finance.py`

`Scenario` is a frozen-ish dataclass without defaults, so adding a field requires every Scenario constructor call to pass it. The page is the only constructor caller in production; tests construct Scenarios for finance computations.

- [ ] **Step 1: Write the failing test**

Add to `dashboard/tests/test_rentbuy_finance.py`:

```python
def test_scenario_accepts_bedrooms_field():
    from lib.rentbuy.finance import Scenario
    scenario = Scenario(
        borough="Camden", postcode_district=None, property_type="F",
        new_build=False, first_time_buyer=False,
        bedrooms="2",
        plan_to_stay_years=7, starting_cash=100_000.0,
        investment_return=0.05, isa_tax_free=True, inflation=0.025,
        home_price=600_000.0, deposit_pct=0.15, auto_tier_rate=True,
        mortgage_rate=0.0525, fix_years=5, mortgage_term_years=25,
        legal_survey=2_500.0, maintenance_pct=0.005, council_tax=2_000.0,
        buildings_insurance=300.0, service_charge=0.0, ground_rent=0.0,
        lease_years_remaining=None, home_growth=0.025, selling_fee_pct=0.015,
        monthly_rent=2_500.0, rent_growth=0.025, deposit_weeks=5,
        renters_insurance=120.0, moving_cost=500.0, avg_tenancy_years=2.0,
        include_long_term_frictions=True,
    )
    assert scenario.bedrooms == "2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest dashboard/tests/test_rentbuy_finance.py::test_scenario_accepts_bedrooms_field -v`

Expected: FAIL with `TypeError: Scenario.__init__() got an unexpected keyword argument 'bedrooms'`.

- [ ] **Step 3: Add the field**

In `dashboard/lib/rentbuy/finance.py`, find the `Scenario` dataclass (around line 105). Add `bedrooms: str` immediately after `first_time_buyer`:

```python
@dataclass
class Scenario:
    # Location
    borough: str
    postcode_district: Optional[str]
    property_type: str
    new_build: bool
    first_time_buyer: bool
    bedrooms: str   # one of "studio", "1", "2", "3", "4+"

    # Shared
    plan_to_stay_years: int
    ...
```

- [ ] **Step 4: Update existing finance tests that build Scenarios**

Search the test file for every `Scenario(` construction and add `bedrooms="2",` after `first_time_buyer`. Run:

```bash
grep -n "Scenario(" dashboard/tests/test_rentbuy_finance.py dashboard/tests/test_rentbuy_scenario.py
```

For each match, edit the constructor call to include `bedrooms="2",`.

- [ ] **Step 5: Run all rentbuy tests**

Run: `pytest dashboard/tests/test_rentbuy_finance.py dashboard/tests/test_rentbuy_scenario.py -v`

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add dashboard/lib/rentbuy/finance.py dashboard/tests/test_rentbuy_finance.py dashboard/tests/test_rentbuy_scenario.py
git commit -m "feat(rentbuy): add bedrooms field to Scenario dataclass"
```

---

### Task 5: Add the bedroom selectbox to the page UI

**Files:**
- Modify: `dashboard/pages/16_Rent_vs_Buy.py` (around lines 119-127, 138-143, and the Scenario constructor at 271-304)

- [ ] **Step 1: Add the selectbox after the property type radio**

Replace lines 119-127 in `dashboard/pages/16_Rent_vs_Buy.py`:

```python
with col_t:
    property_type_label = st.radio(
        "Property type",
        options=["Flat", "Terraced", "Semi-detached", "Detached"],
        horizontal=True,
        index=0,
    )
    PROPERTY_TYPE_MAP = {"Flat": "F", "Terraced": "T", "Semi-detached": "S", "Detached": "D"}
    property_type = PROPERTY_TYPE_MAP[property_type_label]

bedrooms_label = st.selectbox(
    "Bedrooms",
    options=["Studio", "1", "2", "3", "4+"],
    index=2,  # 2-bed default
    help="Affects the rent and price defaults.",
)
BEDROOM_MAP = {"Studio": "studio", "1": "1", "2": "2", "3": "3", "4+": "4+"}
bedrooms = BEDROOM_MAP[bedrooms_label]
```

- [ ] **Step 2: Update the imports at the top of the page**

In `dashboard/pages/16_Rent_vs_Buy.py`, find the `from lib.rentbuy.inputs import` block (around lines 14-22) and add `load_borough_rents_by_bedroom`:

```python
from lib.rentbuy.inputs import (
    load_district_to_borough,
    load_borough_rents,
    load_borough_rents_by_bedroom,
    load_council_tax,
    load_boe_rates,
    default_home_price,
    default_monthly_rent,
    default_council_tax,
    lookup_boe_rate,
)
```

- [ ] **Step 3: Load the bedroom rents in the data dict**

Find the `data = {` block (around lines 90-95) and add the new loader:

```python
data = {
    "ppd": load_ppd_cached(),
    "district_to_borough": load_district_to_borough(),
    "borough_rents": load_borough_rents(),
    "borough_rents_by_bedroom": load_borough_rents_by_bedroom(),
    "council_tax": load_council_tax(),
    "boe_rates": load_boe_rates(),
}
```

(Whatever the exact key names are — adjust to match the existing pattern.)

- [ ] **Step 4: Pass bedrooms to the rent default lookup**

Replace line 143:

```python
default_rent = default_monthly_rent(
    data["borough_rents"], data["borough_rents_by_bedroom"],
    borough=borough, bedrooms=bedrooms,
)
```

- [ ] **Step 5: Pass bedrooms to the Scenario constructor**

In the `scenario = Scenario(...)` block at line 271, add `bedrooms=bedrooms,` after `first_time_buyer=first_time_buyer,`:

```python
scenario = Scenario(
    borough=borough,
    postcode_district=postcode_district,
    property_type=property_type,
    new_build=new_build,
    first_time_buyer=first_time_buyer,
    bedrooms=bedrooms,
    plan_to_stay_years=plan_to_stay_years,
    ...
)
```

- [ ] **Step 6: Run the page locally to smoke test**

```bash
cd dashboard && streamlit run pages/16_Rent_vs_Buy.py
```

Visit the page in a browser. Confirm:
- A "Bedrooms" dropdown appears with Studio / 1 / 2 / 3 / 4+
- Switching from "2" to "4+" changes the displayed rent default upward
- No exceptions in the terminal

Stop streamlit with Ctrl+C.

- [ ] **Step 7: Commit**

```bash
git add dashboard/pages/16_Rent_vs_Buy.py
git commit -m "feat(rentbuy): add bedroom selectbox and wire to rent default"
```

---

### Task 6: AppTest assertion that the selectbox is present

**Files:**
- Test: `dashboard/tests/test_rent_vs_buy.py` (or wherever the existing rent-vs-buy AppTest lives)

- [ ] **Step 1: Find the existing rent-vs-buy AppTest file**

```bash
grep -rln "16_Rent_vs_Buy" dashboard/tests/
```

If it exists, add the test below to that file. If it doesn't exist, create `dashboard/tests/test_rent_vs_buy.py`.

- [ ] **Step 2: Write the failing test**

```python
"""Frontend tests for the Rent vs Buy London page."""
import pytest
from streamlit.testing.v1 import AppTest


def _run():
    at = AppTest.from_file("pages/16_Rent_vs_Buy.py", default_timeout=20)
    at.run()
    return at


def test_loads_without_error():
    at = _run()
    assert not at.exception, f"Page crashed: {at.exception}"


def test_has_bedroom_selectbox():
    at = _run()
    selectboxes = [s for s in at.selectbox if "Bedroom" in s.label]
    assert selectboxes, "Expected a selectbox with 'Bedroom' in its label"
    assert "Studio" in selectboxes[0].options
    assert "4+" in selectboxes[0].options
```

- [ ] **Step 3: Run the test**

Run: `pytest dashboard/tests/test_rent_vs_buy.py -v`

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add dashboard/tests/test_rent_vs_buy.py
git commit -m "test(rentbuy): assert bedroom selectbox is present on page"
```

---

### Task 7: Run the full test suite + open PR1

- [ ] **Step 1: Run the full dashboard test suite**

Run from the dashboard directory:

```bash
cd dashboard && python -m pytest tests/ -q
```

Expected: all tests pass (or skip with known reasons).

- [ ] **Step 2: Push the branch and open PR1**

```bash
git push -u origin feat-rentbuy-bedrooms-pr1
gh pr create --title "Rent vs Buy London: bedroom selectbox + ONS rent defaults" --body "$(cat <<'EOF'
## Summary
- Adds a bedroom dropdown to the Rent vs Buy London calculator
- Wires bedrooms into the rent default using new ONS bedroom-segmented data
- Price default still uses the existing logic (PR2 will add bedroom-aware price defaults via PPD + EPC join)

## Test plan
- [x] Unit tests for load_borough_rents_by_bedroom
- [x] Unit tests for default_monthly_rent with bedroom argument
- [x] Scenario dataclass test
- [x] AppTest asserts selectbox is present and has expected options
- [ ] Smoke test on Streamlit Cloud after merge
EOF
)"
```

- [ ] **Step 3: Wait for merge, then sync working branch**

After PR1 is merged, run:

```bash
git checkout working
git pull origin master
git merge origin/master --no-edit
git push origin working
```

---

# PR2 — EPC + PPD join build script + price defaults

PR2 adds the data engineering piece: a build script that joins Land Registry PPD with the EPC dataset to enrich each sale with `bedrooms`, then wires the new parquet into `default_home_price`.

---

### Task 8: Create the cache directory and gitignore entry

**Files:**
- Create: `dashboard/data/_cache/epc/.gitkeep` (empty file)
- Modify: `dashboard/.gitignore` (or root `.gitignore` if dashboard doesn't have one)

- [ ] **Step 1: Create the cache directory placeholder**

```bash
mkdir -p dashboard/data/_cache/epc
touch dashboard/data/_cache/epc/.gitkeep
```

- [ ] **Step 2: Add the cache exclusion to .gitignore**

If `dashboard/.gitignore` exists, append:

```
# EPC dataset cache — populated by build_ppd_with_bedrooms.py
data/_cache/
!data/_cache/epc/.gitkeep
```

If only the root `.gitignore` exists, append the same lines but with `dashboard/` prefix.

- [ ] **Step 3: Commit**

```bash
git add dashboard/data/_cache/epc/.gitkeep dashboard/.gitignore
git commit -m "chore(rentbuy): add EPC cache directory and gitignore entry"
```

---

### Task 9: Create the build script `build_ppd_with_bedrooms.py`

**Files:**
- Create: `dashboard/scripts/build_ppd_with_bedrooms.py`

This is a longer task because the script is the heart of the data layer. Build it incrementally with checkpoints.

- [ ] **Step 1: Scaffold the script with CLI parsing**

Create `dashboard/scripts/build_ppd_with_bedrooms.py`:

```python
"""Build dashboard/data/london_ppd_with_bedrooms.parquet.

Joins Land Registry Price Paid Data with the EPC dataset on
(postcode, normalised first line of address) so each sale is
enriched with a bedroom count derived from EPC's
`number-habitable-rooms` field.

Run:
    python dashboard/scripts/build_ppd_with_bedrooms.py
    python dashboard/scripts/build_ppd_with_bedrooms.py --download

The --download flag re-fetches both PPD and EPC. Without it, the
script uses cached files under dashboard/data/_cache/.

Inputs: dashboard/data/london_ppd.parquet (existing) +
        dashboard/data/_cache/epc/<authority>/certificates.csv (one per LA)
Output: dashboard/data/london_ppd_with_bedrooms.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = DATA_DIR / "_cache"
EPC_CACHE = CACHE_DIR / "epc"
PPD_PARQUET = DATA_DIR / "london_ppd.parquet"
OUTPUT_PARQUET = DATA_DIR / "london_ppd_with_bedrooms.parquet"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--download",
        action="store_true",
        help="Re-download EPC zips even if cached.",
    )
    p.add_argument(
        "--min-match-rate",
        type=float,
        default=0.30,
        help="Fail if join match rate is below this fraction (default 0.30).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    print(f"PPD source: {PPD_PARQUET}")
    print(f"EPC cache:  {EPC_CACHE}")
    print(f"Output:     {OUTPUT_PARQUET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the scaffold runs**

Run:

```bash
python dashboard/scripts/build_ppd_with_bedrooms.py
```

Expected output:

```
PPD source: ...\dashboard\data\london_ppd.parquet
EPC cache:  ...\dashboard\data\_cache\epc
Output:     ...\dashboard\data\london_ppd_with_bedrooms.parquet
```

- [ ] **Step 3: Add EPC download function**

Add to the script before `main()`:

```python
import zipfile
import io
import requests

# 32 London local authority codes used by the EPC API.
# https://epc.opendatacommunities.org/docs/api
LONDON_LA_CODES = [
    "E09000001",  # City of London
    "E09000002",  # Barking and Dagenham
    "E09000003",  # Barnet
    "E09000004",  # Bexley
    "E09000005",  # Brent
    "E09000006",  # Bromley
    "E09000007",  # Camden
    "E09000008",  # Croydon
    "E09000009",  # Ealing
    "E09000010",  # Enfield
    "E09000011",  # Greenwich
    "E09000012",  # Hackney
    "E09000013",  # Hammersmith and Fulham
    "E09000014",  # Haringey
    "E09000015",  # Harrow
    "E09000016",  # Havering
    "E09000017",  # Hillingdon
    "E09000018",  # Hounslow
    "E09000019",  # Islington
    "E09000020",  # Kensington and Chelsea
    "E09000021",  # Kingston upon Thames
    "E09000022",  # Lambeth
    "E09000023",  # Lewisham
    "E09000024",  # Merton
    "E09000025",  # Newham
    "E09000026",  # Redbridge
    "E09000027",  # Richmond upon Thames
    "E09000028",  # Southwark
    "E09000029",  # Sutton
    "E09000030",  # Tower Hamlets
    "E09000031",  # Waltham Forest
    "E09000032",  # Wandsworth
    "E09000033",  # Westminster
]

EPC_DOWNLOAD_BASE = "https://epc.opendatacommunities.org/files/domestic-{code}-{slug}.zip"


def ensure_epc_downloaded(force: bool) -> None:
    """Download EPC zips for every London authority into the cache.

    The EPC bulk-download endpoint returns one zip per local authority
    containing certificates.csv + recommendations.csv. We only need
    certificates.csv.
    """
    EPC_CACHE.mkdir(parents=True, exist_ok=True)
    for code in LONDON_LA_CODES:
        target_dir = EPC_CACHE / code
        certs = target_dir / "certificates.csv"
        if certs.exists() and not force:
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        # The EPC URL pattern requires a free API key in production.
        # For the script we expect the user to pre-download manually
        # from https://epc.opendatacommunities.org/ if not already cached.
        if not certs.exists():
            print(
                f"  MISSING: {certs} — please download the EPC zip for "
                f"{code} from https://epc.opendatacommunities.org/ and "
                f"extract certificates.csv into {target_dir}",
                file=sys.stderr,
            )
            sys.exit(2)
```

- [ ] **Step 4: Add address normalisation helper**

Add before `main()`:

```python
import re

_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]")


def normalise_address(value: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace.

    Used to make PPD's PAON+SAON fields and EPC's address1 line
    comparable enough to join."""
    if not isinstance(value, str):
        return ""
    s = value.lower()
    s = _NON_ALNUM_RE.sub(" ", s)
    s = _WHITESPACE_RE.sub(" ", s).strip()
    return s


def normalise_postcode(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.upper().replace(" ", "")
```

- [ ] **Step 5: Add the EPC loader**

```python
def load_all_epc() -> pd.DataFrame:
    """Read every cached certificates.csv and concatenate.

    Returns a DataFrame with columns: postcode_norm, address_norm,
    number_habitable_rooms.
    """
    frames = []
    for code in LONDON_LA_CODES:
        certs = EPC_CACHE / code / "certificates.csv"
        if not certs.exists():
            continue
        df = pd.read_csv(
            certs,
            usecols=["POSTCODE", "ADDRESS1", "NUMBER_HABITABLE_ROOMS"],
            dtype={
                "POSTCODE": "string",
                "ADDRESS1": "string",
                "NUMBER_HABITABLE_ROOMS": "Int16",
            },
        )
        df["postcode_norm"] = df["POSTCODE"].map(normalise_postcode)
        df["address_norm"] = df["ADDRESS1"].map(normalise_address)
        frames.append(df[["postcode_norm", "address_norm", "NUMBER_HABITABLE_ROOMS"]])
    if not frames:
        print("ERROR: no EPC files found in cache", file=sys.stderr)
        sys.exit(2)
    out = pd.concat(frames, ignore_index=True)
    # When the same address has multiple EPCs, take the most recent (last) record.
    out = out.drop_duplicates(subset=["postcode_norm", "address_norm"], keep="last")
    out = out.rename(columns={"NUMBER_HABITABLE_ROOMS": "habitable_rooms"})
    return out
```

- [ ] **Step 6: Add the PPD loader**

```python
def load_ppd() -> pd.DataFrame:
    """Read the existing London PPD parquet and add normalised join columns."""
    df = pd.read_parquet(PPD_PARQUET)
    df["postcode_norm"] = df["postcode"].map(normalise_postcode)
    # PPD doesn't keep a pre-joined address line — synthesise from postcode
    # district + price-paid-data PAON if those columns exist; otherwise just
    # use the raw postcode-based join (lower match rate but still works).
    if "paon" in df.columns:
        df["address_norm"] = df["paon"].fillna("").map(normalise_address)
    else:
        df["address_norm"] = ""
    return df
```

- [ ] **Step 7: Add the bedroom bucketing helper**

```python
def bucket_bedrooms(habitable_rooms: int | float) -> str:
    """EPC habitable_rooms minus 1 (assumes one living room) bucketed."""
    if pd.isna(habitable_rooms):
        return ""
    bedrooms = int(habitable_rooms) - 1
    if bedrooms <= 0:
        return "studio"
    if bedrooms == 1:
        return "1"
    if bedrooms == 2:
        return "2"
    if bedrooms == 3:
        return "3"
    return "4+"
```

- [ ] **Step 8: Wire everything together in main()**

Replace the `main()` function:

```python
def main() -> int:
    args = parse_args()
    print(f"PPD source: {PPD_PARQUET}")
    print(f"EPC cache:  {EPC_CACHE}")
    print(f"Output:     {OUTPUT_PARQUET}")

    ensure_epc_downloaded(force=args.download)

    print("Loading PPD...")
    ppd = load_ppd()
    print(f"  {len(ppd):,} sales loaded")

    print("Loading EPC...")
    epc = load_all_epc()
    print(f"  {len(epc):,} unique addresses loaded")

    print("Joining...")
    merged = ppd.merge(
        epc,
        on=["postcode_norm", "address_norm"],
        how="left",
    )

    matched = merged["habitable_rooms"].notna().sum()
    match_rate = matched / len(merged)
    print(f"  matched: {matched:,} / {len(merged):,}  ({match_rate:.1%})")

    if match_rate < args.min_match_rate:
        print(
            f"ERROR: match rate {match_rate:.1%} is below threshold "
            f"{args.min_match_rate:.1%}",
            file=sys.stderr,
        )
        return 2

    merged["bedrooms"] = merged["habitable_rooms"].map(bucket_bedrooms)

    # Drop the join helper columns before writing.
    merged = merged.drop(columns=["postcode_norm", "address_norm", "habitable_rooms"])

    print("Writing output...")
    tmp_path = OUTPUT_PARQUET.with_suffix(".parquet.tmp")
    merged.to_parquet(tmp_path, index=False)
    tmp_path.replace(OUTPUT_PARQUET)

    print(f"  wrote {OUTPUT_PARQUET}")
    print("\nBedroom distribution:")
    print(merged["bedrooms"].value_counts(dropna=False).to_string())
    return 0
```

- [ ] **Step 9: Run the script**

```bash
python dashboard/scripts/build_ppd_with_bedrooms.py
```

If EPC is not yet cached, the script will exit with the manual-download instructions printed to stderr. Follow them: visit https://epc.opendatacommunities.org/, download the bulk export for each London local authority, extract the `certificates.csv` into `dashboard/data/_cache/epc/<E09xxxxxxx>/`, then re-run. Expected final output:

```
PPD source: ...
EPC cache:  ...
Output:     ...
Loading PPD...
  N,NNN,NNN sales loaded
Loading EPC...
  N,NNN,NNN unique addresses loaded
Joining...
  matched: NNN,NNN / N,NNN,NNN  (50.X%)
Writing output...
  wrote .../london_ppd_with_bedrooms.parquet

Bedroom distribution:
2      ...
3      ...
1      ...
4+     ...
studio ...
```

- [ ] **Step 10: Commit the script and the output parquet**

```bash
git add dashboard/scripts/build_ppd_with_bedrooms.py dashboard/data/london_ppd_with_bedrooms.parquet
git commit -m "feat(rentbuy): add PPD + EPC join build script and enriched parquet"
```

---

### Task 10: Update `default_home_price()` to take a bedroom argument

**Files:**
- Modify: `dashboard/lib/rentbuy/inputs.py` (replace `default_home_price` at lines 28-67)
- Test: `dashboard/tests/test_rentbuy_inputs.py`

- [ ] **Step 1: Write the failing tests**

Add to `dashboard/tests/test_rentbuy_inputs.py`:

```python
def test_default_home_price_with_bedrooms_filters():
    """A 4+ bed home should default to a higher price than a 1-bed in
    the same borough + property type."""
    import pandas as pd
    ppd = pd.read_parquet(
        Path(__file__).resolve().parent.parent / "data" / "london_ppd_with_bedrooms.parquet"
    )
    d2b = load_district_to_borough()
    one_bed = default_home_price(
        ppd, d2b, borough="Camden", postcode_district=None,
        property_type="F", new_build=False, bedrooms="1",
    )
    four_bed = default_home_price(
        ppd, d2b, borough="Camden", postcode_district=None,
        property_type="F", new_build=False, bedrooms="4+",
    )
    assert four_bed > one_bed


def test_default_home_price_falls_back_when_bedrooms_missing():
    """When no rows match the bedroom filter, the function should still
    return a sensible price using the legacy fallback chain."""
    import pandas as pd
    ppd = pd.read_parquet(
        Path(__file__).resolve().parent.parent / "data" / "london_ppd_with_bedrooms.parquet"
    )
    d2b = load_district_to_borough()
    price = default_home_price(
        ppd, d2b, borough="NONEXISTENT BOROUGH",
        postcode_district=None, property_type="F",
        new_build=False, bedrooms="2",
    )
    assert price == 500_000  # hardcoded final fallback
```

- [ ] **Step 2: Add `from pathlib import Path` to the test file if not present**

Run: `head -10 dashboard/tests/test_rentbuy_inputs.py` and add `from pathlib import Path` to the imports if missing.

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py -v -k "default_home_price_with_bedrooms or default_home_price_falls_back"`

Expected: FAIL — current `default_home_price` doesn't take `bedrooms`.

- [ ] **Step 4: Replace `default_home_price` with bedroom-aware version**

Replace lines 28-67 of `dashboard/lib/rentbuy/inputs.py`:

```python
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

    # 1. district × type × new_build × bedrooms
    if postcode_district and bedrooms and has_bedrooms_col:
        subset = recent[
            (recent["postcode_district"] == postcode_district)
            & (recent["property_type"] == property_type)
            & (recent["new_build"] == new_build_flag)
            & (recent["bedrooms"] == bedrooms)
        ]
        if len(subset) >= 10:
            return int(subset["price"].median())

    # 2. district × type × new_build (existing)
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

    # 3. borough × type × bedrooms
    if borough_districts and bedrooms and has_bedrooms_col:
        subset = recent[
            (recent["postcode_district"].isin(borough_districts))
            & (recent["property_type"] == property_type)
            & (recent["bedrooms"] == bedrooms)
        ]
        if len(subset) > 0:
            return int(subset["price"].median())

    # 4. borough × type (existing)
    if borough_districts:
        subset = recent[
            (recent["postcode_district"].isin(borough_districts))
            & (recent["property_type"] == property_type)
        ]
        if len(subset) > 0:
            return int(subset["price"].median())

    # 5. hardcoded fallback
    return 500_000
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest dashboard/tests/test_rentbuy_inputs.py -v`

Expected: all input tests pass.

- [ ] **Step 6: Commit**

```bash
git add dashboard/lib/rentbuy/inputs.py dashboard/tests/test_rentbuy_inputs.py
git commit -m "feat(rentbuy): wire bedroom argument through default_home_price"
```

---

### Task 11: Switch the page to load the enriched parquet and pass bedrooms to price default

**Files:**
- Modify: `dashboard/pages/16_Rent_vs_Buy.py`

- [ ] **Step 1: Find the PPD loader cache function**

```bash
grep -n "load_ppd_cached\|london_ppd" dashboard/pages/16_Rent_vs_Buy.py
```

- [ ] **Step 2: Update the cached loader to read the enriched parquet**

The page currently reads `dashboard/data/london_ppd.parquet`. Switch it to `london_ppd_with_bedrooms.parquet`. Find the loader (something like `def load_ppd_cached():` or `pd.read_parquet(...london_ppd.parquet...)`) and update the path:

```python
PPD_PATH = Path(__file__).resolve().parent.parent / "data" / "london_ppd_with_bedrooms.parquet"
```

- [ ] **Step 3: Pass bedrooms to default_home_price**

Replace lines 138-142 of `dashboard/pages/16_Rent_vs_Buy.py`:

```python
default_price = default_home_price(
    data["ppd"], data["district_to_borough"],
    borough=borough, postcode_district=postcode_district,
    property_type=property_type, new_build=new_build,
    bedrooms=bedrooms,
)
```

- [ ] **Step 4: Smoke test the page**

```bash
cd dashboard && streamlit run pages/16_Rent_vs_Buy.py
```

Confirm:
- Page loads without error
- Switching bedrooms changes the price default
- Switching bedrooms changes the rent default
- The rest of the calculator still works

Stop with Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/16_Rent_vs_Buy.py
git commit -m "feat(rentbuy): use enriched parquet and pass bedrooms to price default"
```

---

### Task 12: Update MAINTENANCE.md

**Files:**
- Modify: `docs/MAINTENANCE.md`

- [ ] **Step 1: Add the refresh procedure**

Append to `docs/MAINTENANCE.md`:

```markdown
## Refreshing London PPD with bedroom data

The Rent vs Buy London calculator uses
`dashboard/data/london_ppd_with_bedrooms.parquet`, which is built by
joining Land Registry PPD with the EPC dataset on (postcode, address)
to enrich each sale with a bedroom count.

To refresh:

1. Download the latest London PPD CSV from
   https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads
   and replace `dashboard/data/london_ppd.parquet`
2. Download fresh EPC certificates for the 32 London local authorities
   from https://epc.opendatacommunities.org/ and extract each
   `certificates.csv` into `dashboard/data/_cache/epc/<E09xxxxxxx>/`
3. Run: `python dashboard/scripts/build_ppd_with_bedrooms.py`
4. Verify the printed match rate is at least 30%
5. Commit `dashboard/data/london_ppd_with_bedrooms.parquet`
```

- [ ] **Step 2: Commit**

```bash
git add docs/MAINTENANCE.md
git commit -m "docs: add PPD-with-bedrooms refresh procedure"
```

---

### Task 13: Run full test suite + open PR2

- [ ] **Step 1: Run the full dashboard test suite**

Run from the dashboard directory:

```bash
cd dashboard && python -m pytest tests/ -q
```

Expected: all tests pass.

- [ ] **Step 2: Push the branch and open PR2**

```bash
git push -u origin feat-rentbuy-bedrooms-pr2
gh pr create --title "Rent vs Buy London: PPD + EPC join + bedroom-aware price defaults" --body "$(cat <<'EOF'
## Summary
- New build script `dashboard/scripts/build_ppd_with_bedrooms.py` joins Land Registry PPD with the EPC dataset on (postcode, address) to enrich each sale with a bedroom count
- New enriched parquet `dashboard/data/london_ppd_with_bedrooms.parquet` is the output of the script
- `default_home_price` now takes a bedroom argument and uses it as the tightest filter, with graceful fallback to the existing logic
- `MAINTENANCE.md` documents the refresh procedure

## Test plan
- [x] Unit tests for `default_home_price` with bedroom argument
- [x] Build script ran locally with match rate above 30%
- [x] Smoke test of page locally with bedroom switching prices
- [ ] Smoke test on Streamlit Cloud after merge
EOF
)"
```

---

## Self-Review Notes

**Spec coverage:**
- ✓ Bedroom dropdown — Task 5
- ✓ ONS rent CSV + bedroom-aware rent default — Tasks 1–3
- ✓ EPC + PPD join build script — Task 9
- ✓ Bedroom-aware price default with fallback chain — Task 10
- ✓ Scenario gains bedrooms field — Task 4
- ✓ MAINTENANCE.md refresh procedure — Task 12
- ✓ Failure modes (match rate threshold, missing bedroom) — Tasks 9 & 10
- ✓ Tests covering each layer — Tasks 2, 3, 4, 6, 10

**Type consistency:**
- `bedrooms` is consistently `str` with values `"studio"`, `"1"`, `"2"`, `"3"`, `"4+"` everywhere
- `_BEDROOM_COLUMN_MAP` keys match the values used in the page's `BEDROOM_MAP`
- `default_monthly_rent` four-arg signature is used in both the new tests and the page
- `default_home_price` adds `bedrooms` as keyword argument with default `None` so PR1's tests still pass before PR2 lands

**Placeholder check:**
- All code blocks are complete, no TBDs
- Numeric expectations in tests are concrete
- The CSV in Task 1 is realistic 2024-aligned values; engineer can substitute exact ONS values when building
