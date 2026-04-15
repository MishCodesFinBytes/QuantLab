# Rent vs Buy London — Bedrooms Feature Design

**Date:** 2026-04-15
**Status:** Approved (architecture)
**Author:** brainstorming session, mish-codes/QuantLab

---

## Goal

Add a "number of bedrooms" dropdown to the Rent vs Buy London calculator and wire it into the price + rent defaults so the calculation reflects the chosen bedroom count using real public data.

## Background

Today the calculator defaults home price from Land Registry Price Paid Data filtered by borough + postcode district + property type + new build, and defaults monthly rent from a single ONS borough median. Neither side has any awareness of bedroom count. Users want to compare a 1-bed flat in Camden against a 3-bed terrace in Camden — currently they get the same default whichever they pick.

Land Registry PPD does not record bedroom counts, only property type (Detached / Semi / Terraced / Flat). ONS Private Rental Market Statistics does publish median rents segmented by bedroom (Room / Studio / 1 / 2 / 3 / 4+) per London borough, but we don't currently load it.

## Scope

**In scope:**
- A bedroom selectbox on the Rent vs Buy page, in addition to the existing property-type radio
- Bedroom-segmented rent defaults driven by real ONS data
- Bedroom-segmented price defaults driven by joining Land Registry PPD with the EPC dataset (Energy Performance Certificates) which records `number-habitable-rooms` per address
- A reusable build script that regenerates the enriched parquet on demand (so future PPD refreshes are one command)
- Documentation in `docs/MAINTENANCE.md` for how to refresh the data

**Out of scope:**
- Bedroom support on other pages (London House Prices, Stock Risk Scanner, etc.)
- Real-time scraping of Rightmove / Zoopla
- Any change to property type, new build, or postcode district inputs
- Changing the calculation logic itself — only the defaults that feed it

## Decisions

| Question | Decision | Rationale |
|---|---|---|
| Bedroom options | Studio / 1 / 2 / 3 / 4+ (5 options) | Granular enough to be useful, common Rightmove convention |
| Relationship to property type | Additional input alongside property type | Bedrooms and property type are independent attributes; users can pick "2-bed Flat" or "2-bed Terraced" |
| Rent data source | ONS Private Rental Market Statistics, Table 2.7 (London borough × bedroom category) | Real public data, free, no scraping, updates annually |
| Price data source | Land Registry PPD joined to EPC on (postcode, address) | Real public data from gov.uk, OGL licensed, derives bedroom count from EPC's `number-habitable-rooms − 1` |
| PR sequencing | Two PRs: PR1 (ONS rent only, ships fast), PR2 (EPC join + price) | PR1 delivers rent-side value in hours; PR2 takes 1–2 days for the join engineering and ships independently |

## Architecture

```
                         ┌────────────────────────────────┐
ONS Excel (manual)   →   │ london_borough_rents_          │
(Table 2.7)              │   by_bedroom.csv               │
                         └──────────────┬─────────────────┘
                                        │
PPD CSV (gov.uk)     →   ┌──────────────▼─────────────────┐
EPC zips (gov.uk)    →   │ build_ppd_with_bedrooms.py     │
                         │   (one-shot script, PR2)       │
                         └──────────────┬─────────────────┘
                                        │
                         ┌──────────────▼─────────────────┐
                         │ london_ppd_with_bedrooms.      │
                         │   parquet                      │
                         └──────────────┬─────────────────┘
                                        │
                         ┌──────────────▼─────────────────┐
                         │ rentbuy.inputs.default_*       │
                         │   take `bedrooms` parameter    │
                         └──────────────┬─────────────────┘
                                        │
                         ┌──────────────▼─────────────────┐
                         │ pages/16_Rent_vs_Buy.py        │
                         │   bedroom selectbox            │
                         └────────────────────────────────┘
```

## Components

### 1. New data file: `dashboard/data/london_borough_rents_by_bedroom.csv`

Manual import from ONS Private Rental Market Statistics Excel (Table 2.7). One row per borough, one column per bedroom category.

```
borough,beds_studio,beds_1,beds_2,beds_3,beds_4plus,source_year,source_url
Barking and Dagenham,995,1100,1395,1700,2200,2024,https://...
Barnet,1150,1395,1750,2300,3200,2024,https://...
...
```

The existing `london_borough_rents.csv` (single median per borough) stays as a fallback for any borough that's missing or has gaps in the bedroom breakdown.

### 2. New build script: `dashboard/scripts/build_ppd_with_bedrooms.py`

A standalone idempotent script. Run with:

```bash
python dashboard/scripts/build_ppd_with_bedrooms.py
```

Steps:
1. Read raw London PPD CSV (or download fresh if `--download` flag is passed)
2. Read cached EPC dataset for all 32 London local authorities (download fresh on first run, cache afterwards under `dashboard/data/_cache/epc/`)
3. Normalise addresses on both sides: lowercase, strip whitespace, collapse multiple spaces, take first line of the address only
4. Join on `(postcode, normalised_first_line)`
5. Derive `bedrooms` from EPC's `number-habitable-rooms − 1` (assumes one living room) and bucket into the same 5 categories used in the UI
6. Write `dashboard/data/london_ppd_with_bedrooms.parquet` atomically (write to `.tmp` then rename)
7. Print a summary: rows in, rows joined, match rate, distribution by bedroom

The script is dev-only — it never runs on Streamlit Cloud. The output parquet is checked into the repo (same as today's `london_ppd.parquet`).

### 3. Updated loader: `dashboard/lib/rentbuy/inputs.py`

New / changed functions:

```python
def load_borough_rents_by_bedroom() -> pd.DataFrame: ...

def default_monthly_rent(
    rents_df: pd.DataFrame,
    rents_by_bedroom_df: pd.DataFrame,
    borough: str,
    bedrooms: str,  # "studio", "1", "2", "3", "4+"
) -> int:
    """Return median monthly rent for the chosen borough + bedroom band.
    Falls back to the single-median CSV if the bedroom band is missing."""

def default_home_price(
    ppd_df: pd.DataFrame,
    district_to_borough_df: pd.DataFrame,
    borough: str,
    postcode_district: str | None,
    property_type: str,
    new_build: bool,
    bedrooms: str | None,  # new optional parameter
) -> int:
    """Existing fallback chain plus a tighter bedroom filter when set."""
```

The fallback chain for `default_home_price` becomes:

1. district × property_type × new_build × **bedrooms**, last 3y, ≥10 sales
2. district × property_type × new_build, last 3y, ≥10 sales (existing)
3. borough × property_type × bedrooms, last 3y, > 0 sales
4. borough × property_type, last 3y, > 0 sales (existing)
5. £500,000 hardcoded fallback (existing)

So when bedroom data is sparse for a particular slice, we fall through to the existing logic. No regression for existing flows.

### 4. Updated Scenario: `dashboard/lib/rentbuy/finance.py`

`Scenario` gains a `bedrooms: str` field. It's only used for telemetry / the breakdown display; the price + rent inputs are already passed in by the page so the calculation logic doesn't change.

### 5. Updated page: `dashboard/pages/16_Rent_vs_Buy.py`

New `st.selectbox` between property type and new build:

```python
bedrooms = st.selectbox(
    "Bedrooms",
    options=["Studio", "1", "2", "3", "4+"],
    index=2,  # 2 bed default
)
```

Default lookups now pass the bedroom value:

```python
default_price = default_home_price(
    data["ppd"], data["district_to_borough"],
    borough=borough, postcode_district=postcode_district,
    property_type=property_type, new_build=new_build,
    bedrooms=bedrooms,  # new
)
default_rent = default_monthly_rent(
    data["borough_rents"], data["borough_rents_by_bedroom"],
    borough=borough, bedrooms=bedrooms,  # new
)
```

## Data freshness display

A small "Data correct as of YYYY" caption next to each input that's data-driven, sourced from the CSV's `source_year` column. Reuses the `data_freshness_caption()` helper if it exists by then; otherwise inline.

## Failure modes and fallbacks

| Failure | Fallback |
|---|---|
| EPC join match rate < 30% | Print a warning in the build script and exit non-zero. The PR cannot ship the parquet. |
| Bedroom column missing in the parquet at runtime | `default_home_price` ignores the `bedrooms` parameter and uses the existing logic |
| Bedroom band missing in the ONS CSV for a borough | Fall back to the single-median `london_borough_rents.csv` |
| EPC dataset URL changes | Build script logs a clear error message pointing at https://epc.opendatacommunities.org/; fix in script and re-run |

## Testing approach

- **Unit tests** for `default_home_price` and `default_monthly_rent` covering: bedroom present + match, bedroom present + fall-through, bedroom missing
- **Integration test** that runs the build script on a fixture PPD slice and a fixture EPC slice, asserts match rate ≥ 50%
- **AppTest** for the rent-vs-buy page asserting the selectbox is present and changing it re-runs the calculation
- **Existing 58 rentbuy tests** must still pass

## Maintenance

Update `docs/MAINTENANCE.md` with:

```
### Refreshing London PPD with bedroom data

1. Download the latest London PPD CSV from gov.uk
2. Run: python dashboard/scripts/build_ppd_with_bedrooms.py
3. Verify the printed match rate is ≥ 50%
4. Commit dashboard/data/london_ppd_with_bedrooms.parquet
```

## Open questions

None remaining — all decisions captured above.
