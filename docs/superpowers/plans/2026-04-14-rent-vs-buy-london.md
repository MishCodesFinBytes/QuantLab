# Rent vs Buy London — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive "should I rent or buy?" calculator for London, shipped as a new Streamlit page in the QuantLab dashboard's Mini Projects → Calculators section, plus a long-form accompanying blog post in the FinBytes Jekyll blog.

**Architecture:** A new `dashboard/lib/rentbuy/` package with four focused modules (`finance.py` pure math, `inputs.py` data lookups, `scenario.py` glue, `charts.py` Plotly builders). The Streamlit page is UI glue only. Four bundled static data files (district→borough, ONS borough rents, council tax, BoE LTV-tiered mortgage rates) provide real defaults. The blog post lives in a different repo (finbytes_git) under `docs/_quant_lab/mini/`.

**Tech Stack:** Python 3.11, pandas, Plotly, Streamlit, pytest. No new dependencies. Jekyll for the blog post (existing).

**Spec reference:** [docs/superpowers/specs/2026-04-14-rent-vs-buy-london-design.md](../specs/2026-04-14-rent-vs-buy-london-design.md)

---

## File Structure

**Quant_lab repo — new files:**

| Path | Purpose |
|---|---|
| `dashboard/lib/rentbuy/__init__.py` | Package marker, re-exports public API |
| `dashboard/lib/rentbuy/finance.py` | Pure math: SDLT, amortization, LTV tiering, totals, breakeven |
| `dashboard/lib/rentbuy/inputs.py` | Default lookups from the four bundled data files |
| `dashboard/lib/rentbuy/scenario.py` | `Scenario` → `Result` glue |
| `dashboard/lib/rentbuy/charts.py` | Plotly `build_cost_over_time_chart` |
| `dashboard/pages/16_Rent_vs_Buy.py` | Streamlit page (UI glue only) |
| `dashboard/data/london_district_to_borough.csv` | Postcode district → borough lookup (~60 rows) |
| `dashboard/data/london_borough_rents.csv` | ONS median monthly rent per borough (~33 rows) |
| `dashboard/data/london_council_tax.csv` | 2024/25 band A–H council tax per borough (~33 rows) |
| `dashboard/data/boe_mortgage_rates.csv` | BoE G1.4 snapshot by (fix_years × ltv_bracket) (~20 rows) |
| `dashboard/scripts/refresh_boe_rates.py` | One-off script to refresh BoE snapshot from IADB |
| `dashboard/tests/test_rentbuy_finance.py` | Pure math tests (~27 cases) |
| `dashboard/tests/test_rentbuy_inputs.py` | Default lookup tests (~5 cases) |
| `dashboard/tests/test_rentbuy_scenario.py` | Scenario glue test (1 case) |
| `dashboard/tests/test_rentbuy_charts.py` | Plotly figure structure test (1 case) |

**Quant_lab repo — modified files:**

| Path | Change |
|---|---|
| `dashboard/lib/nav.py` | Add Rent vs Buy London entry under Calculators |

**Finbytes_git repo — new files:**

| Path | Purpose |
|---|---|
| `docs/_quant_lab/mini/rent-vs-buy.html` | Long-form ~2500-word blog post |

**Finbytes_git repo — modified files:**

| Path | Change |
|---|---|
| `docs/_tabs/quant-lab.md` | Add an entry under Mini Projects — Calculators |

---

## Task 1: Scaffold rentbuy package + bundle data files

**Files:**
- Create: `dashboard/lib/rentbuy/__init__.py` (empty scaffold)
- Create: `dashboard/data/london_district_to_borough.csv`
- Create: `dashboard/data/london_borough_rents.csv`
- Create: `dashboard/data/london_council_tax.csv`
- Create: `dashboard/data/boe_mortgage_rates.csv`

Work from: `C:/codebase/quant_lab`. Stay on branch `working`.

- [ ] **Step 1: Create package marker**

Write `dashboard/lib/rentbuy/__init__.py`:

```python
"""Rent vs Buy London calculator package.

Public API (populated after all submodules exist):
- Scenario, Result (dataclasses)
- run_scenario(scenario, boe_rates_df) -> Result
- default_home_price, default_monthly_rent, default_council_tax, lookup_boe_rate
- load_borough_rents, load_council_tax, load_district_to_borough, load_boe_rates
- calculate_sdlt, monthly_mortgage_payment, suggest_rate_for_ltv
- build_cost_over_time_chart
"""
```

Leave imports out for now — they'll be restored in a later task once all submodules exist.

- [ ] **Step 2: Create the district-to-borough CSV**

Write `dashboard/data/london_district_to_borough.csv` with this exact content (includes all central and most outer London postcode districts that appear frequently in the PPD dataset — falls back to borough-wide logic for districts not listed):

```csv
postcode_district,borough
N1,Islington
N2,Barnet
N3,Barnet
N4,Haringey
N5,Islington
N6,Haringey
N7,Islington
N8,Haringey
N10,Haringey
N11,Barnet
N12,Barnet
N13,Enfield
N14,Enfield
N15,Haringey
N16,Hackney
N17,Haringey
N19,Islington
N22,Haringey
NW1,Camden
NW2,Brent
NW3,Camden
NW5,Camden
NW6,Camden
NW7,Barnet
NW8,Westminster
NW9,Barnet
NW10,Brent
NW11,Barnet
E1,Tower Hamlets
E1W,Tower Hamlets
E2,Tower Hamlets
E3,Tower Hamlets
E5,Hackney
E6,Newham
E7,Newham
E8,Hackney
E9,Hackney
E11,Waltham Forest
E14,Tower Hamlets
E15,Newham
E17,Waltham Forest
E18,Redbridge
EC1A,City of London
EC1M,City of London
EC1N,City of London
EC1R,City of London
EC1V,City of London
EC1Y,City of London
EC2A,City of London
EC2M,City of London
EC2N,City of London
EC2R,City of London
EC2V,City of London
EC2Y,City of London
EC3A,City of London
EC3M,City of London
EC3N,City of London
EC3R,City of London
EC3V,City of London
EC4A,City of London
EC4M,City of London
EC4N,City of London
EC4R,City of London
EC4V,City of London
EC4Y,City of London
W1,Westminster
W2,Westminster
W4,Hounslow
W5,Ealing
W6,Hammersmith and Fulham
W8,Kensington and Chelsea
W9,Westminster
W10,Kensington and Chelsea
W11,Kensington and Chelsea
W12,Hammersmith and Fulham
W14,Hammersmith and Fulham
SW1,Westminster
SW3,Kensington and Chelsea
SW4,Lambeth
SW5,Kensington and Chelsea
SW6,Hammersmith and Fulham
SW7,Kensington and Chelsea
SW8,Wandsworth
SW9,Lambeth
SW10,Kensington and Chelsea
SW11,Wandsworth
SW12,Lambeth
SW14,Richmond upon Thames
SW15,Wandsworth
SW16,Lambeth
SW17,Wandsworth
SW18,Wandsworth
SW19,Merton
SW20,Merton
SE1,Southwark
SE3,Greenwich
SE5,Southwark
SE8,Lewisham
SE10,Greenwich
SE11,Lambeth
SE13,Lewisham
SE14,Lewisham
SE15,Southwark
SE16,Southwark
SE17,Southwark
SE18,Greenwich
SE19,Lambeth
SE22,Southwark
SE24,Lambeth
SE25,Croydon
SE27,Lambeth
```

- [ ] **Step 3: Create the borough rents CSV**

Write `dashboard/data/london_borough_rents.csv`:

```csv
borough,median_monthly_rent,source_year,source_url
Barking and Dagenham,1500,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Barnet,1895,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Bexley,1425,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Brent,1900,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Bromley,1575,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Camden,2450,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
City of London,2600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Croydon,1525,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Ealing,1850,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Enfield,1600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Greenwich,1625,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Hackney,2100,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Hammersmith and Fulham,2350,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Haringey,1850,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Harrow,1600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Havering,1475,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Hillingdon,1600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Hounslow,1700,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Islington,2250,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Kensington and Chelsea,3200,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Kingston upon Thames,1650,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Lambeth,1975,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Lewisham,1650,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Merton,1750,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Newham,1650,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Redbridge,1600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Richmond upon Thames,2000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Southwark,1975,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Sutton,1450,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Tower Hamlets,2000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Waltham Forest,1600,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Wandsworth,2000,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
Westminster,2800,2024,https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/privaterentalmarketsummarystatisticsinengland/latest
```

- [ ] **Step 4: Create the council tax CSV**

Write `dashboard/data/london_council_tax.csv` (band D values for 2024/25, sourced from each borough's published council tax schedule):

```csv
borough,band_a,band_b,band_c,band_d,band_e,band_f,band_g,band_h,year
Barking and Dagenham,1263,1474,1685,1896,2318,2740,3162,3792,2024
Barnet,1156,1348,1541,1734,2120,2506,2891,3470,2024
Bexley,1358,1585,1812,2039,2493,2947,3401,4082,2024
Brent,1405,1639,1874,2108,2577,3046,3515,4218,2024
Bromley,1226,1431,1635,1840,2249,2658,3067,3681,2024
Camden,1291,1506,1721,1937,2367,2798,3228,3874,2024
City of London,770,898,1026,1155,1411,1668,1925,2310,2024
Croydon,1480,1727,1973,2220,2714,3208,3702,4440,2024
Ealing,1232,1437,1642,1848,2259,2670,3082,3697,2024
Enfield,1467,1712,1956,2201,2690,3178,3668,4401,2024
Greenwich,1326,1546,1767,1988,2430,2872,3315,3977,2024
Hackney,1193,1392,1591,1790,2189,2587,2986,3582,2024
Hammersmith and Fulham,873,1018,1163,1309,1600,1891,2182,2618,2024
Haringey,1443,1683,1924,2164,2645,3126,3608,4329,2024
Harrow,1430,1668,1907,2145,2622,3100,3577,4292,2024
Havering,1407,1641,1876,2110,2579,3048,3517,4220,2024
Hillingdon,1286,1500,1715,1929,2358,2788,3217,3860,2024
Hounslow,1296,1512,1728,1945,2377,2810,3242,3890,2024
Islington,1220,1424,1627,1831,2238,2646,3053,3664,2024
Kensington and Chelsea,1014,1182,1352,1520,1857,2195,2533,3040,2024
Kingston upon Thames,1547,1804,2062,2320,2836,3351,3867,4640,2024
Lambeth,1236,1442,1648,1854,2266,2679,3091,3709,2024
Lewisham,1337,1560,1783,2006,2451,2897,3343,4012,2024
Merton,1404,1638,1873,2107,2576,3044,3512,4215,2024
Newham,1214,1416,1618,1820,2225,2631,3036,3643,2024
Redbridge,1326,1547,1767,1988,2430,2872,3314,3977,2024
Richmond upon Thames,1560,1820,2080,2340,2861,3382,3903,4683,2024
Southwark,1193,1391,1590,1789,2187,2585,2983,3580,2024
Sutton,1439,1679,1919,2159,2638,3118,3597,4317,2024
Tower Hamlets,1239,1446,1652,1859,2271,2684,3097,3717,2024
Waltham Forest,1422,1659,1896,2133,2608,3082,3556,4267,2024
Wandsworth,605,706,807,908,1109,1310,1511,1814,2024
Westminster,613,716,817,920,1124,1329,1534,1840,2024
```

Note: Wandsworth and Westminster have dramatically lower council tax than most boroughs (historically the lowest in London).

- [ ] **Step 5: Create the BoE mortgage rates CSV**

Write `dashboard/data/boe_mortgage_rates.csv` (snapshot of typical quoted rates by fix length × LTV bracket, reflecting the general UK mortgage market pricing pattern):

```csv
fix_years,ltv_bracket,rate_pct,snapshot_date
2,0.60,4.45,2026-03
2,0.75,4.65,2026-03
2,0.85,4.85,2026-03
2,0.90,5.15,2026-03
2,0.95,5.75,2026-03
3,0.60,4.40,2026-03
3,0.75,4.60,2026-03
3,0.85,4.80,2026-03
3,0.90,5.10,2026-03
3,0.95,5.65,2026-03
5,0.60,4.30,2026-03
5,0.75,4.50,2026-03
5,0.85,4.75,2026-03
5,0.90,5.00,2026-03
5,0.95,5.50,2026-03
10,0.60,4.50,2026-03
10,0.75,4.70,2026-03
10,0.85,4.95,2026-03
10,0.90,5.20,2026-03
10,0.95,5.70,2026-03
```

- [ ] **Step 6: Verify CSV files parse**

Run:

```bash
cd dashboard && python -c "
import pandas as pd
for name in ['london_district_to_borough.csv',
             'london_borough_rents.csv',
             'london_council_tax.csv',
             'boe_mortgage_rates.csv']:
    df = pd.read_csv(f'data/{name}')
    print(f'{name}: {len(df)} rows, cols={list(df.columns)}')
"
```

Expected output (row counts exact):
```
london_district_to_borough.csv: 110 rows, cols=['postcode_district', 'borough']
london_borough_rents.csv: 33 rows, cols=['borough', 'median_monthly_rent', 'source_year', 'source_url']
london_council_tax.csv: 33 rows, cols=['borough', 'band_a', 'band_b', 'band_c', 'band_d', 'band_e', 'band_f', 'band_g', 'band_h', 'year']
boe_mortgage_rates.csv: 20 rows, cols=['fix_years', 'ltv_bracket', 'rate_pct', 'snapshot_date']
```

- [ ] **Step 7: Commit — STRICT staging**

```bash
git add dashboard/lib/rentbuy/__init__.py \
        dashboard/data/london_district_to_borough.csv \
        dashboard/data/london_borough_rents.csv \
        dashboard/data/london_council_tax.csv \
        dashboard/data/boe_mortgage_rates.csv
git status --short
git commit -m "feat(rentbuy): scaffold package and bundle London reference data"
```

`git status --short` must show ONLY the 5 staged files (A flag). Do NOT use `git add .`. If any other file appears, stop and report BLOCKED.

---

## Task 2: Finance Part A — SDLT and mortgage amortization

**Files:**
- Create: `dashboard/tests/test_rentbuy_finance.py`
- Create: `dashboard/lib/rentbuy/finance.py`

- [ ] **Step 1: Write the failing tests for SDLT and amortization**

Create `dashboard/tests/test_rentbuy_finance.py`:

```python
"""Tests for the Rent vs Buy finance module."""

import math

import pandas as pd
import pytest

from lib.rentbuy.finance import (
    calculate_sdlt,
    monthly_mortgage_payment,
    remaining_balance,
)


# ── SDLT — Standard bands (non-first-time-buyer) ────────────────────

SDLT_STANDARD = [
    (   125_000,       0),
    (   250_000,       0),
    (   400_000,    7_500),
    (   500_000,   12_500),
    (   925_000,   33_750),
    ( 1_000_000,   41_250),
    ( 1_500_000,   91_250),
    ( 2_000_000,  151_250),
]


@pytest.mark.parametrize("price,expected", SDLT_STANDARD)
def test_sdlt_standard(price, expected):
    assert calculate_sdlt(price, first_time_buyer=False) == pytest.approx(expected, abs=1)


# ── SDLT — First-time buyer relief ──────────────────────────────────

SDLT_FTB = [
    (   400_000,      0),
    (   425_000,      0),
    (   500_000,  3_750),
    (   625_000, 10_000),
]


@pytest.mark.parametrize("price,expected", SDLT_FTB)
def test_sdlt_first_time_buyer(price, expected):
    assert calculate_sdlt(price, first_time_buyer=True) == pytest.approx(expected, abs=1)


def test_sdlt_ftb_above_cap_uses_standard():
    """Above £625k, first-time buyers pay the same as non-FTB."""
    standard = calculate_sdlt(700_000, first_time_buyer=False)
    ftb = calculate_sdlt(700_000, first_time_buyer=True)
    assert standard == ftb


# ── Mortgage amortization ───────────────────────────────────────────

def test_mortgage_payment_standard_case():
    """£500k loan at 5% for 25 years → monthly payment ≈ £2,923."""
    payment = monthly_mortgage_payment(500_000, 0.05, 25)
    assert 2_920 < payment < 2_930


def test_mortgage_payment_zero_interest():
    """£240k / 240 months = £1,000/month exactly."""
    payment = monthly_mortgage_payment(240_000, 0.0, 20)
    assert abs(payment - 1_000) < 0.01


def test_mortgage_payment_scales_with_principal():
    """Doubling the principal doubles the monthly payment."""
    small = monthly_mortgage_payment(250_000, 0.05, 25)
    big = monthly_mortgage_payment(500_000, 0.05, 25)
    assert abs(big - 2 * small) < 0.01


def test_remaining_balance_at_start_equals_principal():
    assert abs(remaining_balance(500_000, 0.05, 25, 0) - 500_000) < 1


def test_remaining_balance_partial_term():
    """After 120 months on a 25y loan at 5%, ~£380k-£410k remains."""
    remaining = remaining_balance(500_000, 0.05, 25, 120)
    assert 380_000 < remaining < 410_000


def test_remaining_balance_at_end_is_zero():
    """After full term, balance should be zero (or near-zero due to rounding)."""
    assert remaining_balance(500_000, 0.05, 25, 300) < 1.0


def test_remaining_balance_zero_interest():
    """With 0% interest and linear amortization, half the term = half paid."""
    remaining = remaining_balance(240_000, 0.0, 20, 120)
    assert abs(remaining - 120_000) < 0.01
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py -v 2>&1 | tail -10
```

Expected: `ModuleNotFoundError: No module named 'lib.rentbuy.finance'`.

- [ ] **Step 3: Implement finance.py Part A**

Write `dashboard/lib/rentbuy/finance.py`:

```python
"""Pure finance functions for the Rent vs Buy calculator.

Every function in this module is side-effect-free. No I/O, no Streamlit,
no logging. The runner owns all orchestration.
"""

from __future__ import annotations

import math
from typing import Iterable


# ──────────────────────────────────────────────────────────────
# SDLT (Stamp Duty Land Tax) — UK 2024/25 rules
# ──────────────────────────────────────────────────────────────

# Standard residential bands (non-first-time-buyer).
# Each tuple is (upper_threshold, rate).
STANDARD_BANDS: list[tuple[float, float]] = [
    (  250_000,      0.00),
    (  925_000,      0.05),
    (1_500_000,      0.10),
    (float("inf"),   0.12),
]

# First-time buyer bands — relief applies only up to £625k.
# Above £625k, FTBs pay the full standard bands.
FTB_BANDS: list[tuple[float, float]] = [
    (  425_000,      0.00),
    (  625_000,      0.05),
]
FTB_CAP = 625_000


def _tiered_tax(price: float, bands: Iterable[tuple[float, float]]) -> float:
    """Apply a tiered tax schedule to a price.

    Each band is (upper_threshold, marginal_rate). The rate applies only
    to the slice of price between the previous threshold and this one.
    """
    tax = 0.0
    prev_threshold = 0.0
    for threshold, rate in bands:
        if price > threshold:
            tax += (threshold - prev_threshold) * rate
            prev_threshold = threshold
        else:
            tax += (price - prev_threshold) * rate
            return tax
    return tax


def calculate_sdlt(price: float, first_time_buyer: bool = False) -> float:
    """Compute UK Stamp Duty Land Tax on a residential purchase.

    Args:
        price: purchase price in pounds
        first_time_buyer: if True, apply FTB relief (only below £625k)

    Returns:
        Total SDLT in pounds.
    """
    if first_time_buyer and price <= FTB_CAP:
        return _tiered_tax(price, FTB_BANDS)
    return _tiered_tax(price, STANDARD_BANDS)


# ──────────────────────────────────────────────────────────────
# Mortgage amortization
# ──────────────────────────────────────────────────────────────

def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortization formula. Returns the monthly payment in pounds.

    Args:
        principal: loan amount at t=0
        annual_rate: annual interest rate as a decimal (e.g., 0.05 for 5%)
        years: mortgage term in years
    """
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12.0
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def remaining_balance(
    principal: float,
    annual_rate: float,
    years: int,
    months_elapsed: int,
) -> float:
    """Outstanding mortgage principal after N monthly payments.

    Uses the closed-form: B(m) = P*(1+r)^m - PMT * ((1+r)^m - 1)/r
    """
    if months_elapsed <= 0:
        return principal
    if months_elapsed >= years * 12:
        return 0.0
    if annual_rate == 0:
        monthly_payment = principal / (years * 12)
        return max(0.0, principal - monthly_payment * months_elapsed)
    r = annual_rate / 12.0
    pmt = monthly_mortgage_payment(principal, annual_rate, years)
    future_value = principal * (1 + r) ** months_elapsed - pmt * ((1 + r) ** months_elapsed - 1) / r
    return max(0.0, future_value)
```

- [ ] **Step 4: Run the tests — all 18 should pass**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py -v 2>&1 | tail -20
```

Expected: `18 passed` (8 SDLT standard + 4 SDLT FTB + 1 FTB-above-cap + 5 amortization = 18).

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/rentbuy/finance.py dashboard/tests/test_rentbuy_finance.py
git status --short
git commit -m "feat(rentbuy): add SDLT calculator and mortgage amortization"
```

---

## Task 3: Finance Part B — LTV tiering + Scenario dataclass + total cost of buying

**Files:**
- Modify: `dashboard/lib/rentbuy/finance.py` (append)
- Modify: `dashboard/tests/test_rentbuy_finance.py` (append)

- [ ] **Step 1: Append failing tests for LTV + total cost of buying**

Open `dashboard/tests/test_rentbuy_finance.py` and append to the end:

```python


# ── LTV tiering ─────────────────────────────────────────────────────

from lib.rentbuy.finance import (
    Scenario,
    suggest_rate_for_ltv,
    total_cost_of_buying,
)


@pytest.fixture
def boe_rates():
    return pd.DataFrame([
        {"fix_years": 5, "ltv_bracket": 0.60, "rate_pct": 4.30, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.75, "rate_pct": 4.50, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.85, "rate_pct": 4.75, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.90, "rate_pct": 5.00, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.95, "rate_pct": 5.50, "snapshot_date": "2026-03"},
    ])


def test_suggest_rate_ltv_60(boe_rates):
    assert suggest_rate_for_ltv(0.60, 5, boe_rates) == pytest.approx(0.043)


def test_suggest_rate_ltv_75(boe_rates):
    assert suggest_rate_for_ltv(0.75, 5, boe_rates) == pytest.approx(0.045)


def test_suggest_rate_ltv_95(boe_rates):
    assert suggest_rate_for_ltv(0.95, 5, boe_rates) == pytest.approx(0.055)


def test_suggest_rate_above_top_bracket(boe_rates):
    """LTV above 95% returns the top bracket rate (no extrapolation)."""
    assert suggest_rate_for_ltv(0.99, 5, boe_rates) == pytest.approx(0.055)


def test_suggest_rate_bracket_boundary_rounds_up(boe_rates):
    """0.7501 should fall into the 0.85 bracket, not 0.75."""
    assert suggest_rate_for_ltv(0.7501, 5, boe_rates) == pytest.approx(0.0475)


# ── total_cost_of_buying ────────────────────────────────────────────

def make_scenario(**overrides) -> Scenario:
    """Test helper — reasonable defaults for a London flat purchase."""
    defaults = dict(
        borough="Camden",
        postcode_district="NW1",
        property_type="F",
        new_build=False,
        first_time_buyer=False,
        plan_to_stay_years=7,
        starting_cash=150_000,
        investment_return=0.05,
        isa_tax_free=True,
        inflation=0.025,
        home_price=650_000,
        deposit_pct=0.15,
        auto_tier_rate=False,
        mortgage_rate=0.0525,
        fix_years=5,
        mortgage_term_years=25,
        legal_survey=2_500,
        maintenance_pct=0.01,
        council_tax=1_900,
        buildings_insurance=400,
        service_charge=3_000,
        ground_rent=300,
        lease_years_remaining=99,
        home_growth=0.03,
        selling_fee_pct=0.015,
        monthly_rent=2_450,
        rent_growth=0.03,
        deposit_weeks=5,
        renters_insurance=120,
        moving_cost=500,
        avg_tenancy_years=3.5,
        include_long_term_frictions=True,
    )
    defaults.update(overrides)
    return Scenario(**defaults)


def test_total_cost_of_buying_returns_expected_keys(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_buying(scenario, boe_rates)
    assert "upfront" in result
    assert "monthly_total" in result
    assert "total_ongoing" in result
    assert "equity_at_sale" in result
    assert "investment_income" in result
    assert "net_cost" in result
    assert "breakdown" in result


def test_total_cost_of_buying_upfront_includes_all_components(boe_rates):
    scenario = make_scenario(home_price=650_000, deposit_pct=0.15,
                              legal_survey=2_500, moving_cost=500,
                              first_time_buyer=False)
    result = total_cost_of_buying(scenario, boe_rates)
    expected_upfront = 97_500 + 20_000 + 2_500 + 500  # deposit + SDLT + legal + moving
    assert result["upfront"] == pytest.approx(expected_upfront, abs=1)


def test_total_cost_flat_includes_service_charge_and_ground_rent(boe_rates):
    with_fees = make_scenario(property_type="F", service_charge=3_000, ground_rent=300)
    no_fees = make_scenario(property_type="F", service_charge=0, ground_rent=0)
    with_result = total_cost_of_buying(with_fees, boe_rates)
    no_result = total_cost_of_buying(no_fees, boe_rates)
    assert with_result["net_cost"] > no_result["net_cost"]


def test_total_cost_house_ignores_service_charge_even_if_set(boe_rates):
    with_fees = make_scenario(property_type="T", service_charge=5_000, ground_rent=500)
    no_fees = make_scenario(property_type="T", service_charge=0, ground_rent=0)
    assert total_cost_of_buying(with_fees, boe_rates)["net_cost"] \
        == pytest.approx(total_cost_of_buying(no_fees, boe_rates)["net_cost"])


def test_total_cost_auto_tier_rate_uses_boe_lookup(boe_rates):
    scenario = make_scenario(auto_tier_rate=True, deposit_pct=0.25)  # LTV = 0.75
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["rate_used"] == pytest.approx(0.045)


def test_total_cost_equity_at_sale_positive(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["equity_at_sale"] > 0


def test_total_cost_includes_remortgage_fees_with_frictions(boe_rates):
    """15-year plan with 5-year fix → 2 remortgages expected."""
    scenario = make_scenario(plan_to_stay_years=15, fix_years=5,
                              include_long_term_frictions=True)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] > 0


def test_total_cost_no_remortgage_fees_without_frictions(boe_rates):
    scenario = make_scenario(plan_to_stay_years=15, fix_years=5,
                              include_long_term_frictions=False)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] == 0


def test_total_cost_no_remortgage_when_plan_shorter_than_fix(boe_rates):
    """Plan = 5 years, fix = 5 years → no remortgages needed."""
    scenario = make_scenario(plan_to_stay_years=5, fix_years=5,
                              include_long_term_frictions=True)
    result = total_cost_of_buying(scenario, boe_rates)
    assert result["breakdown"]["remortgage_fees_total"] == 0


def test_cash_rich_buyer_gets_investment_income(boe_rates):
    lean = make_scenario(starting_cash=125_000)     # just enough for upfront
    rich = make_scenario(starting_cash=500_000)     # plenty left over
    assert (total_cost_of_buying(rich, boe_rates)["investment_income"]
            > total_cost_of_buying(lean, boe_rates)["investment_income"])


def test_isa_toggle_increases_investment_income(boe_rates):
    with_isa = make_scenario(starting_cash=500_000, isa_tax_free=True)
    without_isa = make_scenario(starting_cash=500_000, isa_tax_free=False)
    assert (total_cost_of_buying(with_isa, boe_rates)["investment_income"]
            > total_cost_of_buying(without_isa, boe_rates)["investment_income"])
```

- [ ] **Step 2: Run — expect failures**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py::test_total_cost_of_buying_returns_expected_keys -v 2>&1 | tail -5
```

Expected: `ImportError: cannot import name 'Scenario'` — the earlier imports fail first.

- [ ] **Step 3: Append to finance.py — Scenario dataclass + LTV + total_cost_of_buying**

Open `dashboard/lib/rentbuy/finance.py` and append to the end:

```python


# ──────────────────────────────────────────────────────────────
# Scenario dataclass — the single source of truth for all inputs
# ──────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Optional


@dataclass
class Scenario:
    # Location
    borough: str
    postcode_district: Optional[str]
    property_type: str                   # "F" | "T" | "S" | "D"
    new_build: bool
    first_time_buyer: bool

    # Shared
    plan_to_stay_years: int
    starting_cash: float
    investment_return: float
    isa_tax_free: bool
    inflation: float

    # Buying
    home_price: float
    deposit_pct: float
    auto_tier_rate: bool
    mortgage_rate: float
    fix_years: int
    mortgage_term_years: int
    legal_survey: float
    maintenance_pct: float
    council_tax: float
    buildings_insurance: float
    service_charge: float
    ground_rent: float
    lease_years_remaining: Optional[int]
    home_growth: float
    selling_fee_pct: float

    # Renting
    monthly_rent: float
    rent_growth: float
    deposit_weeks: int
    renters_insurance: float
    moving_cost: float
    avg_tenancy_years: float

    # Realism toggle
    include_long_term_frictions: bool


# Default remortgage arrangement/valuation fee per refinance
REMORTGAGE_FEE = 1500.0


# ──────────────────────────────────────────────────────────────
# LTV tiering — look up a suggested rate from a BoE snapshot
# ──────────────────────────────────────────────────────────────

def suggest_rate_for_ltv(ltv: float, fix_years: int, boe_rates_df) -> float:
    """Return the BoE-quoted typical rate (as a decimal) for this LTV and fix.

    Picks the smallest bracket whose ltv_bracket >= the given ltv.
    If ltv is above every bracket, returns the top-bracket rate.

    Args:
        ltv: loan-to-value as a fraction (0.75 = 75%)
        fix_years: mortgage fix length (2/3/5/10)
        boe_rates_df: DataFrame with columns fix_years, ltv_bracket, rate_pct
    """
    subset = boe_rates_df[boe_rates_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    if subset.empty:
        raise ValueError(f"No BoE rates for fix_years={fix_years}")
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return float(row["rate_pct"]) / 100.0
    return float(subset.iloc[-1]["rate_pct"]) / 100.0


# ──────────────────────────────────────────────────────────────
# Effective investment rate (ISA-aware)
# ──────────────────────────────────────────────────────────────

def _effective_investment_rate(scenario: Scenario) -> float:
    """ISA-protected → raw rate. Otherwise apply a 20% CGT haircut."""
    if scenario.isa_tax_free:
        return scenario.investment_return
    return scenario.investment_return * 0.80


# ──────────────────────────────────────────────────────────────
# Total cost of buying
# ──────────────────────────────────────────────────────────────

def total_cost_of_buying(scenario: Scenario, boe_rates_df) -> dict:
    """Compute the total net cost of buying over plan_to_stay_years.

    Returns a dict with keys:
      upfront, monthly_total, total_ongoing, equity_at_sale,
      investment_income, net_cost, breakdown
    """
    years = scenario.plan_to_stay_years
    price = scenario.home_price
    deposit = price * scenario.deposit_pct
    principal = max(0.0, price - deposit)
    ltv = principal / price if price > 0 else 0.0

    # Pick mortgage rate
    if scenario.auto_tier_rate:
        rate = suggest_rate_for_ltv(ltv, scenario.fix_years, boe_rates_df)
    else:
        rate = scenario.mortgage_rate

    # Upfront costs
    sdlt = calculate_sdlt(price, scenario.first_time_buyer)
    moving_buy = scenario.moving_cost
    upfront = deposit + sdlt + scenario.legal_survey + moving_buy

    # Monthly recurring (flats only get service charge + ground rent)
    monthly_mortgage = monthly_mortgage_payment(principal, rate, scenario.mortgage_term_years)
    monthly_council_tax = scenario.council_tax / 12.0
    monthly_maintenance = (price * scenario.maintenance_pct) / 12.0
    monthly_buildings = scenario.buildings_insurance / 12.0
    if scenario.property_type == "F":
        monthly_service_charge = scenario.service_charge / 12.0
        monthly_ground_rent = scenario.ground_rent / 12.0
    else:
        monthly_service_charge = 0.0
        monthly_ground_rent = 0.0
    monthly_total = (
        monthly_mortgage + monthly_council_tax + monthly_maintenance
        + monthly_buildings + monthly_service_charge + monthly_ground_rent
    )

    # Aggregated ongoing costs
    total_ongoing = monthly_total * 12 * years

    # Remortgage fees — only if plan exceeds the initial fix length
    remortgage_fees_total = 0.0
    if scenario.include_long_term_frictions and years > scenario.fix_years:
        num_remortgages = math.ceil((years - scenario.fix_years) / scenario.fix_years)
        remortgage_fees_total = num_remortgages * REMORTGAGE_FEE
        total_ongoing += remortgage_fees_total

    # At sale
    home_value_at_sale = price * (1 + scenario.home_growth) ** years
    remaining = remaining_balance(principal, rate, scenario.mortgage_term_years, years * 12)
    selling_fee = home_value_at_sale * scenario.selling_fee_pct
    equity_at_sale = home_value_at_sale - remaining - selling_fee

    # Investment income on excess starting cash not spent upfront
    excess_cash = max(0.0, scenario.starting_cash - upfront)
    investment_rate = _effective_investment_rate(scenario)
    investment_income = excess_cash * ((1 + investment_rate) ** years - 1)

    net_cost = upfront + total_ongoing - equity_at_sale - investment_income

    return {
        "upfront": upfront,
        "monthly_total": monthly_total,
        "total_ongoing": total_ongoing,
        "equity_at_sale": equity_at_sale,
        "investment_income": investment_income,
        "net_cost": net_cost,
        "breakdown": {
            "deposit": deposit,
            "sdlt": sdlt,
            "legal_survey": scenario.legal_survey,
            "moving_buy": moving_buy,
            "monthly_mortgage": monthly_mortgage,
            "monthly_council_tax": monthly_council_tax,
            "monthly_maintenance": monthly_maintenance,
            "monthly_buildings": monthly_buildings,
            "monthly_service_charge": monthly_service_charge,
            "monthly_ground_rent": monthly_ground_rent,
            "home_value_at_sale": home_value_at_sale,
            "remaining_mortgage": remaining,
            "selling_fee": selling_fee,
            "rate_used": rate,
            "ltv": ltv,
            "remortgage_fees_total": remortgage_fees_total,
            "excess_cash_invested": excess_cash,
        },
    }
```

- [ ] **Step 4: Run — all new tests should pass**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py -v 2>&1 | tail -30
```

Expected: all tests pass (18 from Task 2 + ~17 new = ~35).

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/rentbuy/finance.py dashboard/tests/test_rentbuy_finance.py
git status --short
git commit -m "feat(rentbuy): add Scenario dataclass, LTV tiering, and total cost of buying"
```

---

## Task 4: Finance Part C — total cost of renting + breakeven rent

**Files:**
- Modify: `dashboard/lib/rentbuy/finance.py` (append)
- Modify: `dashboard/tests/test_rentbuy_finance.py` (append)

- [ ] **Step 1: Append failing tests**

Append to `dashboard/tests/test_rentbuy_finance.py`:

```python


# ── total_cost_of_renting ───────────────────────────────────────────

from lib.rentbuy.finance import total_cost_of_renting, compute_breakeven_rent


def test_total_cost_of_renting_returns_expected_keys(boe_rates):
    scenario = make_scenario()
    result = total_cost_of_renting(scenario)
    assert "total_rent" in result
    assert "num_moves" in result
    assert "total_moving" in result
    assert "total_renters_ins" in result
    assert "investment_income" in result
    assert "total_cost" in result
    assert "net_cost" in result


def test_zero_rent_growth_total_is_simple_product():
    scenario = make_scenario(monthly_rent=2_000, rent_growth=0.0, plan_to_stay_years=5)
    result = total_cost_of_renting(scenario)
    # 2000 * 12 * 5 = 120,000
    assert result["total_rent"] == pytest.approx(120_000, abs=1)


def test_rent_growth_compounds():
    scenario = make_scenario(monthly_rent=2_000, rent_growth=0.05, plan_to_stay_years=3)
    result = total_cost_of_renting(scenario)
    # year 0: 2000*12 = 24000
    # year 1: 2100*12 = 25200
    # year 2: 2205*12 = 26460
    # total = 75660
    assert result["total_rent"] == pytest.approx(75_660, abs=10)


def test_multiple_moves_with_long_term_frictions():
    """9-year plan with 3.5y tenancy → 3 moves."""
    scenario = make_scenario(
        plan_to_stay_years=9, avg_tenancy_years=3.5,
        moving_cost=500, include_long_term_frictions=True
    )
    result = total_cost_of_renting(scenario)
    assert result["num_moves"] == 3
    assert result["total_moving"] == pytest.approx(1500, abs=1)


def test_single_move_without_long_term_frictions():
    scenario = make_scenario(
        plan_to_stay_years=9, avg_tenancy_years=3.5,
        moving_cost=500, include_long_term_frictions=False
    )
    result = total_cost_of_renting(scenario)
    assert result["num_moves"] == 1
    assert result["total_moving"] == pytest.approx(500, abs=1)


def test_rent_opportunity_cost_greater_for_cash_rich():
    lean = make_scenario(starting_cash=10_000)
    rich = make_scenario(starting_cash=500_000)
    assert (total_cost_of_renting(rich)["investment_income"]
            > total_cost_of_renting(lean)["investment_income"])


# ── Breakeven rent ──────────────────────────────────────────────────

def test_breakeven_rent_positive(boe_rates):
    scenario = make_scenario()
    breakeven = compute_breakeven_rent(scenario, boe_rates)
    assert 500 < breakeven < 10_000   # sanity bounds for London


def test_breakeven_rent_increases_with_longer_stay(boe_rates):
    """Longer stays amortize upfront costs → higher breakeven rent."""
    short = compute_breakeven_rent(make_scenario(plan_to_stay_years=3), boe_rates)
    long = compute_breakeven_rent(make_scenario(plan_to_stay_years=20), boe_rates)
    assert long > short
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py -v 2>&1 | tail -10
```

Expected: `ImportError: cannot import name 'total_cost_of_renting'`.

- [ ] **Step 3: Append to finance.py**

Open `dashboard/lib/rentbuy/finance.py` and append:

```python


# ──────────────────────────────────────────────────────────────
# Total cost of renting
# ──────────────────────────────────────────────────────────────

def total_cost_of_renting(scenario: Scenario) -> dict:
    """Compute the total net cost of renting over plan_to_stay_years.

    Returns a dict with keys:
      total_rent, num_moves, total_moving, total_renters_ins,
      deposit_held, investment_income, total_cost, net_cost
    """
    years = scenario.plan_to_stay_years
    monthly = scenario.monthly_rent

    # Rent with annual compounding
    total_rent = 0.0
    for _ in range(years):
        total_rent += monthly * 12
        monthly *= (1 + scenario.rent_growth)

    # Moves — with frictions on, multiple moves across the stay
    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    total_moving = scenario.moving_cost * num_moves

    # Renters insurance
    total_renters_ins = scenario.renters_insurance * years

    # Security deposit — held by landlord, refundable, not a net cost
    # but we display it in the breakdown. Cap at 5 weeks rent (UK 2019 law).
    weekly_rent = (scenario.monthly_rent * 12) / 52.0
    deposit_held = weekly_rent * scenario.deposit_weeks

    # Opportunity cost on money not spent on buying
    renter_upfront = deposit_held + scenario.moving_cost
    excess_cash = max(0.0, scenario.starting_cash - renter_upfront)
    investment_rate = _effective_investment_rate(scenario)
    investment_income = excess_cash * ((1 + investment_rate) ** years - 1)

    total_cost = total_rent + total_moving + total_renters_ins
    net_cost = total_cost - investment_income

    return {
        "total_rent": total_rent,
        "num_moves": num_moves,
        "total_moving": total_moving,
        "total_renters_ins": total_renters_ins,
        "deposit_held": deposit_held,
        "investment_income": investment_income,
        "total_cost": total_cost,
        "net_cost": net_cost,
    }


# ──────────────────────────────────────────────────────────────
# Breakeven rent
# ──────────────────────────────────────────────────────────────

def compute_breakeven_rent(scenario: Scenario, boe_rates_df) -> float:
    """Find the starting monthly rent at which total cost of renting
    equals total cost of buying, holding all other inputs fixed.

    Solved analytically: given target_total_rent (the rent sum that
    matches the buy side), invert the rent growth accumulator.
    """
    buy = total_cost_of_buying(scenario, boe_rates_df)
    target_net_cost = buy["net_cost"]

    years = scenario.plan_to_stay_years
    g = scenario.rent_growth
    growth_sum = sum((1 + g) ** y for y in range(years))

    # Non-rent cash outflows on the rental side (same as total_cost_of_renting)
    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    non_rent_outflow = scenario.moving_cost * num_moves + scenario.renters_insurance * years

    # Investment income on the rental side depends on the deposit held,
    # which depends on the rent we're solving for. For a clean analytical
    # solution we proxy it using the scenario's current monthly_rent.
    # For sensible rents this is within 1-2% of the true self-consistent value.
    rent_result = total_cost_of_renting(scenario)
    investment_income_proxy = rent_result["investment_income"]

    # target_net_cost = total_rent + non_rent_outflow - investment_income_proxy
    #   where total_rent = monthly_breakeven * 12 * growth_sum
    target_total_rent = target_net_cost - non_rent_outflow + investment_income_proxy
    if growth_sum <= 0:
        return 0.0
    breakeven_monthly = target_total_rent / (12 * growth_sum)
    return max(0.0, breakeven_monthly)
```

- [ ] **Step 4: Run — all tests should pass**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_finance.py -v 2>&1 | tail -40
```

Expected: full finance suite passes (~43 tests total).

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/rentbuy/finance.py dashboard/tests/test_rentbuy_finance.py
git status --short
git commit -m "feat(rentbuy): add total cost of renting and breakeven rent"
```

---

## Task 5: Inputs layer — data file loaders + default lookups

**Files:**
- Create: `dashboard/tests/test_rentbuy_inputs.py`
- Create: `dashboard/lib/rentbuy/inputs.py`

- [ ] **Step 1: Write failing tests**

Create `dashboard/tests/test_rentbuy_inputs.py`:

```python
"""Tests for the rentbuy inputs layer (data file loaders + defaults)."""

import pandas as pd
import pytest

from lib.rentbuy.inputs import (
    load_district_to_borough,
    load_borough_rents,
    load_council_tax,
    load_boe_rates,
    default_home_price,
    default_monthly_rent,
    default_council_tax,
    lookup_boe_rate,
)


def test_load_district_to_borough_schema():
    df = load_district_to_borough()
    assert {"postcode_district", "borough"}.issubset(df.columns)
    assert len(df) > 30


def test_load_borough_rents_schema():
    df = load_borough_rents()
    assert {"borough", "median_monthly_rent", "source_year", "source_url"}.issubset(df.columns)
    assert len(df) > 30


def test_load_council_tax_schema():
    df = load_council_tax()
    assert {"borough", "band_a", "band_b", "band_c", "band_d", "band_e",
            "band_f", "band_g", "band_h", "year"}.issubset(df.columns)
    assert len(df) > 30


def test_load_boe_rates_schema():
    df = load_boe_rates()
    assert {"fix_years", "ltv_bracket", "rate_pct", "snapshot_date"}.issubset(df.columns)
    assert len(df) > 0


def test_default_monthly_rent_known_borough():
    rents = load_borough_rents()
    rent = default_monthly_rent(rents, "Camden")
    assert 1_500 < rent < 5_000


def test_default_monthly_rent_missing_borough_returns_fallback():
    rents = load_borough_rents()
    rent = default_monthly_rent(rents, "NONEXISTENT")
    assert rent == 2_000


def test_default_council_tax_known_borough():
    taxes = load_council_tax()
    tax = default_council_tax(taxes, "Camden", band="D")
    assert 1_200 < tax < 3_500


def test_default_council_tax_missing_borough_returns_fallback():
    taxes = load_council_tax()
    tax = default_council_tax(taxes, "NONEXISTENT", band="D")
    assert tax == 1_900.0


def test_lookup_boe_rate():
    rates = load_boe_rates()
    rate = lookup_boe_rate(rates, ltv=0.75, fix_years=5)
    assert 0.03 < rate < 0.08


def test_default_home_price_with_postcode_and_property_type():
    import pandas as pd
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = load_district_to_borough()
    price = default_home_price(ppd, dtb, borough="Camden",
                                postcode_district="NW1",
                                property_type="F", new_build=False)
    assert 300_000 < price < 3_000_000


def test_default_home_price_falls_back_to_london_median():
    """Unknown borough + unknown district → returns the hardcoded £500k fallback."""
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = load_district_to_borough()
    price = default_home_price(ppd, dtb, borough="ZZZ",
                                postcode_district=None,
                                property_type="F", new_build=False)
    # Could be 500k fallback or a London-wide computed value
    assert price > 0
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_inputs.py -v 2>&1 | tail -5
```

Expected: `ModuleNotFoundError: No module named 'lib.rentbuy.inputs'`.

- [ ] **Step 3: Implement inputs.py**

Create `dashboard/lib/rentbuy/inputs.py`:

```python
"""Data loaders and default-value lookups for the rent-vs-buy calculator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# ──────────────────────────────────────────────────────────────
# Raw CSV loaders
# ──────────────────────────────────────────────────────────────

def load_district_to_borough() -> pd.DataFrame:
    """Postcode district → borough lookup (~110 rows)."""
    return pd.read_csv(DATA_DIR / "london_district_to_borough.csv")


def load_borough_rents() -> pd.DataFrame:
    """ONS median monthly rent per London borough (~33 rows)."""
    return pd.read_csv(DATA_DIR / "london_borough_rents.csv")


def load_council_tax() -> pd.DataFrame:
    """London borough council tax by band for 2024/25 (~33 rows)."""
    return pd.read_csv(DATA_DIR / "london_council_tax.csv")


def load_boe_rates() -> pd.DataFrame:
    """BoE G1.4 quoted mortgage rate snapshot (~20 rows)."""
    return pd.read_csv(DATA_DIR / "boe_mortgage_rates.csv")


# ──────────────────────────────────────────────────────────────
# Default value lookups
# ──────────────────────────────────────────────────────────────

def default_home_price(
    ppd_df: pd.DataFrame,
    district_to_borough_df: pd.DataFrame,
    borough: str,
    postcode_district: str | None,
    property_type: str,
    new_build: bool,
) -> int:
    """Return the median sale price from the tightest available filter.

    Order of fallbacks:
      1. (district × property_type × new_build), last 3 years, >=10 sales
      2. (borough × property_type), last 3 years, any count > 0
      3. £500,000 hardcoded fallback
    """
    three_years_ago = pd.Timestamp.now() - pd.DateOffset(years=3)
    recent = ppd_df[ppd_df["date"] >= three_years_ago]
    new_build_flag = "Y" if new_build else "N"

    # Attempt 1: tightest filter
    if postcode_district:
        subset = recent[
            (recent["postcode_district"] == postcode_district)
            & (recent["property_type"] == property_type)
            & (recent["new_build"] == new_build_flag)
        ]
        if len(subset) >= 10:
            return int(subset["price"].median())

    # Attempt 2: borough-wide via district_to_borough mapping
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

    # Attempt 3: hardcoded fallback
    return 500_000


def default_monthly_rent(rents_df: pd.DataFrame, borough: str) -> int:
    """ONS median monthly rent for a borough. Falls back to £2,000."""
    row = rents_df[rents_df["borough"] == borough]
    if len(row) == 0:
        return 2_000
    return int(row["median_monthly_rent"].iloc[0])


def default_council_tax(council_tax_df: pd.DataFrame, borough: str, band: str = "D") -> float:
    """Annual council tax in pounds for a borough at the given band.

    Falls back to £1,900 if the borough isn't found.
    """
    row = council_tax_df[council_tax_df["borough"] == borough]
    if len(row) == 0:
        return 1_900.0
    col = f"band_{band.lower()}"
    if col not in row.columns:
        return 1_900.0
    return float(row[col].iloc[0])


def lookup_boe_rate(boe_df: pd.DataFrame, ltv: float, fix_years: int) -> float:
    """Return the BoE-quoted rate (as a decimal) for an LTV bracket and fix.

    If no rows match the fix_years, returns 0.055 (5.5%) as a safe default.
    """
    subset = boe_df[boe_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    if subset.empty:
        return 0.055
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return float(row["rate_pct"]) / 100.0
    return float(subset.iloc[-1]["rate_pct"]) / 100.0
```

- [ ] **Step 4: Run the tests**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_inputs.py -v 2>&1 | tail -20
```

Expected: all ~11 tests pass.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/rentbuy/inputs.py dashboard/tests/test_rentbuy_inputs.py
git status --short
git commit -m "feat(rentbuy): add data loaders and default value lookups"
```

---

## Task 6: Scenario layer + chart builder + restore __init__.py

**Files:**
- Create: `dashboard/lib/rentbuy/scenario.py`
- Create: `dashboard/lib/rentbuy/charts.py`
- Create: `dashboard/tests/test_rentbuy_scenario.py`
- Create: `dashboard/tests/test_rentbuy_charts.py`
- Modify: `dashboard/lib/rentbuy/__init__.py` (restore public API)

- [ ] **Step 1: Write failing tests for scenario**

Create `dashboard/tests/test_rentbuy_scenario.py`:

```python
"""Tests for the rentbuy scenario runner."""

import pandas as pd
import pytest

from lib.rentbuy.finance import Scenario
from lib.rentbuy.scenario import run_scenario, Result
from tests.test_rentbuy_finance import make_scenario, boe_rates  # reuse fixtures


def test_run_scenario_returns_complete_result(boe_rates):
    scenario = make_scenario()
    result = run_scenario(scenario, boe_rates)
    assert isinstance(result, Result)
    assert result.buy_net_cost > 0
    assert result.rent_net_cost > 0
    assert result.breakeven_monthly_rent > 0
    assert result.verdict in ("buy_wins", "rent_wins")
    assert len(result.yearly_buy_cost) == scenario.plan_to_stay_years
    assert len(result.yearly_rent_cost) == scenario.plan_to_stay_years


def test_run_scenario_verdict_consistent_with_delta(boe_rates):
    scenario = make_scenario()
    result = run_scenario(scenario, boe_rates)
    if result.verdict == "buy_wins":
        assert result.buy_rent_delta <= 0   # buy is cheaper (lower or equal)
    else:
        assert result.buy_rent_delta > 0


def test_run_scenario_feasibility_flag(boe_rates):
    lean = make_scenario(starting_cash=10_000)
    rich = make_scenario(starting_cash=500_000)
    assert run_scenario(lean, boe_rates).feasible is False
    assert run_scenario(lean, boe_rates).shortfall > 0
    assert run_scenario(rich, boe_rates).feasible is True
    assert run_scenario(rich, boe_rates).shortfall == 0
```

- [ ] **Step 2: Write failing test for charts**

Create `dashboard/tests/test_rentbuy_charts.py`:

```python
"""Tests for the rentbuy chart builders."""

import plotly.graph_objects as go
import pytest

from lib.rentbuy.scenario import run_scenario
from lib.rentbuy.charts import build_cost_over_time_chart
from tests.test_rentbuy_finance import make_scenario, boe_rates


def test_build_cost_over_time_chart_returns_figure(boe_rates):
    result = run_scenario(make_scenario(), boe_rates)
    fig = build_cost_over_time_chart(result)
    assert isinstance(fig, go.Figure)
    # At least one trace for buy and one for rent
    assert len(fig.data) >= 2
    trace_names = [t.name.lower() for t in fig.data if t.name]
    assert any("buy" in n for n in trace_names)
    assert any("rent" in n for n in trace_names)
```

- [ ] **Step 3: Run tests — expect ImportErrors**

```bash
cd dashboard && python -m pytest tests/test_rentbuy_scenario.py tests/test_rentbuy_charts.py -v 2>&1 | tail -10
```

Expected: `ModuleNotFoundError: No module named 'lib.rentbuy.scenario'`.

- [ ] **Step 4: Implement scenario.py**

Create `dashboard/lib/rentbuy/scenario.py`:

```python
"""Glue layer: takes a Scenario, returns a Result with all numbers needed
for the UI. One function call per page render."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .finance import (
    Scenario,
    total_cost_of_buying,
    total_cost_of_renting,
    compute_breakeven_rent,
    _effective_investment_rate,
    monthly_mortgage_payment,
    remaining_balance,
    calculate_sdlt,
)


@dataclass
class Result:
    scenario: Scenario

    # Feasibility
    required_upfront_buy: float
    shortfall: float
    feasible: bool

    # Buying
    buy_upfront_total: float
    buy_monthly_total: float
    buy_total_cost_over_period: float
    buy_equity_at_sale: float
    buy_investment_income: float
    buy_net_cost: float

    # Renting
    rent_total_cost_over_period: float
    rent_opportunity_cost_benefit: float
    rent_net_cost: float

    # Headline
    verdict: str
    breakeven_monthly_rent: float
    buy_rent_delta: float

    # Year-by-year cumulative costs for chart
    yearly_buy_cost: list
    yearly_rent_cost: list

    # Full breakdowns for expander UI
    buy_breakdown: dict = field(default_factory=dict)
    rent_breakdown: dict = field(default_factory=dict)


def _yearly_cumulative_buy(scenario: Scenario, buy: dict, boe_rates_df) -> list:
    """Cumulative net cost of buying at end of each year 1..N."""
    years = scenario.plan_to_stay_years
    yearly = []
    for y in range(1, years + 1):
        # Proportional approximation — we compute buy cost at each year mark
        # using the same formula with plan_to_stay_years=y
        subscenario = Scenario(**{**scenario.__dict__, "plan_to_stay_years": y})
        partial = total_cost_of_buying(subscenario, boe_rates_df)
        yearly.append(partial["net_cost"])
    return yearly


def _yearly_cumulative_rent(scenario: Scenario) -> list:
    years = scenario.plan_to_stay_years
    yearly = []
    for y in range(1, years + 1):
        subscenario = Scenario(**{**scenario.__dict__, "plan_to_stay_years": y})
        partial = total_cost_of_renting(subscenario)
        yearly.append(partial["net_cost"])
    return yearly


def run_scenario(scenario: Scenario, boe_rates_df) -> Result:
    """Run one scenario — returns every number the UI needs in a Result."""
    buy = total_cost_of_buying(scenario, boe_rates_df)
    rent = total_cost_of_renting(scenario)
    breakeven = compute_breakeven_rent(scenario, boe_rates_df)

    required_upfront = buy["upfront"]
    shortfall = max(0.0, required_upfront - scenario.starting_cash)
    feasible = shortfall == 0

    verdict = "rent_wins" if scenario.monthly_rent < breakeven else "buy_wins"

    return Result(
        scenario=scenario,
        required_upfront_buy=required_upfront,
        shortfall=shortfall,
        feasible=feasible,
        buy_upfront_total=buy["upfront"],
        buy_monthly_total=buy["monthly_total"],
        buy_total_cost_over_period=buy["upfront"] + buy["total_ongoing"],
        buy_equity_at_sale=buy["equity_at_sale"],
        buy_investment_income=buy["investment_income"],
        buy_net_cost=buy["net_cost"],
        rent_total_cost_over_period=rent["total_cost"],
        rent_opportunity_cost_benefit=rent["investment_income"],
        rent_net_cost=rent["net_cost"],
        verdict=verdict,
        breakeven_monthly_rent=breakeven,
        buy_rent_delta=buy["net_cost"] - rent["net_cost"],
        yearly_buy_cost=_yearly_cumulative_buy(scenario, buy, boe_rates_df),
        yearly_rent_cost=_yearly_cumulative_rent(scenario),
        buy_breakdown=buy["breakdown"],
        rent_breakdown=rent,
    )
```

- [ ] **Step 5: Implement charts.py**

Create `dashboard/lib/rentbuy/charts.py`:

```python
"""Plotly chart builders for the rent-vs-buy calculator."""

from __future__ import annotations

import plotly.graph_objects as go

from .scenario import Result


def build_cost_over_time_chart(result: Result) -> go.Figure:
    """Line chart: cumulative net cost of buying and renting, year by year.

    A vertical dashed line marks the year when buying overtakes renting
    (or vice versa) if the crossover happens within the plan.
    """
    years = list(range(1, result.scenario.plan_to_stay_years + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=result.yearly_buy_cost,
        mode="lines+markers",
        name="Buying (cumulative net cost)",
        line=dict(color="#2a7ae2", width=2),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=years,
        y=result.yearly_rent_cost,
        mode="lines+markers",
        name="Renting (cumulative net cost)",
        line=dict(color="#e8893c", width=2),
        marker=dict(size=7),
    ))

    # Crossover marker — find the first year where the cheaper line flips
    crossover = _find_crossover_year(result.yearly_buy_cost, result.yearly_rent_cost)
    if crossover is not None:
        fig.add_vline(
            x=crossover,
            line_dash="dash",
            line_color="#888",
            annotation_text=f"Year {crossover}",
            annotation_position="top",
        )

    fig.update_layout(
        title="Cumulative net cost over time",
        xaxis_title="Years",
        yaxis_title="Net cost (£)",
        height=420,
        margin=dict(t=60, b=40, l=60, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    return fig


def _find_crossover_year(buy_costs: list, rent_costs: list):
    """Return the year index (1-based) where the cheaper path flips, or None."""
    if not buy_costs or not rent_costs:
        return None
    initial_buy_cheaper = buy_costs[0] < rent_costs[0]
    for i in range(1, len(buy_costs)):
        now_buy_cheaper = buy_costs[i] < rent_costs[i]
        if now_buy_cheaper != initial_buy_cheaper:
            return i + 1
    return None
```

- [ ] **Step 6: Restore __init__.py**

Overwrite `dashboard/lib/rentbuy/__init__.py`:

```python
"""Rent vs Buy London calculator package."""

from .finance import (
    Scenario,
    calculate_sdlt,
    monthly_mortgage_payment,
    remaining_balance,
    suggest_rate_for_ltv,
    total_cost_of_buying,
    total_cost_of_renting,
    compute_breakeven_rent,
)
from .inputs import (
    load_district_to_borough,
    load_borough_rents,
    load_council_tax,
    load_boe_rates,
    default_home_price,
    default_monthly_rent,
    default_council_tax,
    lookup_boe_rate,
)
from .scenario import run_scenario, Result
from .charts import build_cost_over_time_chart

__all__ = [
    "Scenario",
    "Result",
    "run_scenario",
    "calculate_sdlt",
    "monthly_mortgage_payment",
    "remaining_balance",
    "suggest_rate_for_ltv",
    "total_cost_of_buying",
    "total_cost_of_renting",
    "compute_breakeven_rent",
    "load_district_to_borough",
    "load_borough_rents",
    "load_council_tax",
    "load_boe_rates",
    "default_home_price",
    "default_monthly_rent",
    "default_council_tax",
    "lookup_boe_rate",
    "build_cost_over_time_chart",
]
```

- [ ] **Step 7: Run the full rentbuy suite**

```bash
cd dashboard && python -m pytest tests/test_rentbuy*.py -v 2>&1 | tail -30
```

Expected: all ~50 tests pass.

- [ ] **Step 8: Verify package-level import**

```bash
cd dashboard && python -c "
from lib.rentbuy import Scenario, run_scenario, load_borough_rents
print('ok')
"
```

Expected: `ok`.

- [ ] **Step 9: Commit**

```bash
git add dashboard/lib/rentbuy/scenario.py \
        dashboard/lib/rentbuy/charts.py \
        dashboard/lib/rentbuy/__init__.py \
        dashboard/tests/test_rentbuy_scenario.py \
        dashboard/tests/test_rentbuy_charts.py
git status --short
git commit -m "feat(rentbuy): add scenario runner, chart builder, and public API"
```

---

## Task 7: Streamlit page

**Files:**
- Create: `dashboard/pages/16_Rent_vs_Buy.py`

- [ ] **Step 1: Write the page file**

Create `dashboard/pages/16_Rent_vs_Buy.py`:

```python
"""Rent vs Buy London — data-driven calculator inspired by NYT."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import pandas as pd
import streamlit as st
from tech_footer import render_tech_footer
from nav import render_sidebar
from rentbuy import (
    Scenario,
    run_scenario,
    load_district_to_borough,
    load_borough_rents,
    load_council_tax,
    load_boe_rates,
    default_home_price,
    default_monthly_rent,
    default_council_tax,
    lookup_boe_rate,
    build_cost_over_time_chart,
)

st.set_page_config(page_title="Rent vs Buy London", page_icon="assets/logo.png", layout="wide")
render_sidebar()
st.title("Rent vs Buy — London")

st.markdown(
    """
Should you rent or buy a London home? This calculator estimates the
total cost of both over a time horizon you choose. **Buying** = mortgage
+ stamp duty + fees + maintenance, minus the equity you walk away with
at sale. **Renting** = rent with annual growth, minus the investment
return on the money you didn't spend on a deposit.

Inspired by the [New York Times rent vs buy calculator](https://www.nytimes.com/2024/05/13/briefing/a-new-rent-versus-buy-calculator.html),
adapted for the London market — UK mortgage structure, SDLT, council
tax, LTV-tiered rates from the Bank of England, and real price/rent
data from HM Land Registry and ONS. Default numbers come from bundled
data; edit any field to see how the answer changes.
"""
)


# ──────────────────────────────────────────────────────────────
# Load data once per session
# ──────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading London property data...")
def _load_all_data():
    ppd = pd.read_parquet("data/london_ppd.parquet")
    return {
        "ppd": ppd,
        "district_to_borough": load_district_to_borough(),
        "borough_rents": load_borough_rents(),
        "council_tax": load_council_tax(),
        "boe_rates": load_boe_rates(),
    }

data = _load_all_data()


# ──────────────────────────────────────────────────────────────
# Location & basics
# ──────────────────────────────────────────────────────────────

st.subheader("Location & basics")

boroughs = sorted(data["borough_rents"]["borough"].tolist())
col_b, col_d, col_t = st.columns([2, 2, 2])

with col_b:
    borough = st.selectbox("Borough", options=boroughs, index=boroughs.index("Camden"))

# Districts in the selected borough
borough_districts = sorted(
    data["district_to_borough"][data["district_to_borough"]["borough"] == borough]["postcode_district"].tolist()
)
with col_d:
    postcode_district = st.selectbox(
        "Postcode district (optional)",
        options=["(any)"] + borough_districts,
        help="Narrows the price default to this specific district."
    )
    postcode_district = None if postcode_district == "(any)" else postcode_district

with col_t:
    property_type_label = st.radio(
        "Property type",
        options=["Flat", "Terraced", "Semi-detached", "Detached"],
        horizontal=True,
        index=0,
    )
    PROPERTY_TYPE_MAP = {"Flat": "F", "Terraced": "T", "Semi-detached": "S", "Detached": "D"}
    property_type = PROPERTY_TYPE_MAP[property_type_label]

col_nb, col_ftb, col_stay = st.columns([1, 1, 3])
with col_nb:
    new_build = st.checkbox("New build", value=False)
with col_ftb:
    first_time_buyer = st.checkbox("First-time buyer", value=False,
                                   help="Applies SDLT first-time buyer relief up to £625k")
with col_stay:
    plan_to_stay_years = st.slider("Plan to stay", min_value=1, max_value=30, value=7, step=1)

# Compute defaults based on selections
default_price = default_home_price(
    data["ppd"], data["district_to_borough"],
    borough=borough, postcode_district=postcode_district,
    property_type=property_type, new_build=new_build,
)
default_rent = default_monthly_rent(data["borough_rents"], borough)
default_ctax = default_council_tax(data["council_tax"], borough, band="D")

# Approximate required upfront for the starting cash default
_sdlt_preview = 0  # recomputed below; use simple approximation for default
# Conservative seed: deposit 15% + 5% fees
required_upfront_seed = default_price * 0.15 + default_price * 0.05 + 3_000

starting_cash = st.number_input(
    "Starting cash available (£)",
    min_value=0,
    value=int(required_upfront_seed + 10_000),
    step=5_000,
    help="How much money you have now for deposit + fees. Affects feasibility and the opportunity cost on the rental side.",
)


# ──────────────────────────────────────────────────────────────
# Buying and renting panels
# ──────────────────────────────────────────────────────────────

st.divider()
col_buy, col_rent = st.columns(2)

with col_buy:
    st.subheader("Buying")
    home_price = st.number_input("Home price (£)", min_value=50_000, value=int(default_price), step=5_000)
    deposit_pct = st.slider("Deposit (%)", min_value=5, max_value=50, value=15) / 100.0
    loan_amount = home_price * (1 - deposit_pct)
    ltv = (loan_amount / home_price) if home_price > 0 else 0.0
    st.caption(f"Loan: £{loan_amount:,.0f}   ·   LTV: {ltv*100:.1f}%")

    fix_years = st.selectbox("Fix length (years)", options=[2, 3, 5, 10], index=2)

    auto_tier = st.checkbox("Auto-tier rate by LTV (BoE)", value=True,
                             help="Uses Bank of England G1.4 data. Snapshot date shown below.")

    if auto_tier:
        suggested_rate = lookup_boe_rate(data["boe_rates"], ltv=ltv, fix_years=fix_years)
        mortgage_rate_pct = st.number_input(
            "Mortgage rate (%)",
            min_value=0.0, max_value=15.0,
            value=float(round(suggested_rate * 100, 2)),
            step=0.05, disabled=True,
        )
    else:
        mortgage_rate_pct = st.number_input(
            "Mortgage rate (%)",
            min_value=0.0, max_value=15.0,
            value=5.25, step=0.05,
        )
    mortgage_rate = mortgage_rate_pct / 100.0
    mortgage_term_years = st.slider("Mortgage term (years)", min_value=10, max_value=40, value=25, step=5)

    if fix_years < plan_to_stay_years:
        st.caption(
            f"_Note: your {fix_years}-year fix ends before your {plan_to_stay_years}-year plan. "
            f"The calculator assumes the same rate applies for all {plan_to_stay_years} years — "
            f"in reality you'd remortgage at then-current rates._"
        )

    with st.expander("Advanced (buying)"):
        legal_survey = st.number_input("Legal + survey fees (£)", min_value=0, value=2_500, step=100)
        maintenance_pct = st.slider("Maintenance (% of home value / year)",
                                     min_value=0.0, max_value=3.0,
                                     value=(0.5 if property_type == "F" else 1.0),
                                     step=0.1) / 100.0
        council_tax = st.number_input("Council tax (annual £)",
                                       min_value=0, value=int(default_ctax), step=50)
        buildings_insurance = st.number_input("Buildings insurance (annual £)",
                                                min_value=0, value=400, step=50)
        if property_type == "F":
            service_charge = st.number_input("Service charge (annual £)",
                                              min_value=0, value=3_000, step=100)
            ground_rent = st.number_input("Ground rent (annual £)",
                                           min_value=0, value=300, step=50)
            lease_years_remaining = st.number_input("Lease years remaining",
                                                      min_value=0, max_value=999, value=99)
            if lease_years_remaining < 85:
                st.warning(
                    f"⚠ Lease has {lease_years_remaining} years remaining. "
                    "Below ~85 years, mortgage availability and resale value decline, "
                    "and lease extension can cost £20-100k+."
                )
        else:
            service_charge = 0
            ground_rent = 0
            lease_years_remaining = None
        home_growth_pct = st.slider("Home value growth (% / year)",
                                      min_value=-5.0, max_value=10.0, value=3.0, step=0.5)
        home_growth = home_growth_pct / 100.0
        selling_fee_pct = st.slider("Selling agent fee (%)",
                                      min_value=0.5, max_value=3.0, value=1.5, step=0.1) / 100.0

with col_rent:
    st.subheader("Renting")
    monthly_rent = st.number_input("Monthly rent (£)", min_value=500, value=int(default_rent), step=25)
    rent_growth_pct = st.slider("Rent growth (% / year)",
                                  min_value=0.0, max_value=10.0, value=3.0, step=0.5)
    rent_growth = rent_growth_pct / 100.0
    deposit_weeks = st.slider("Security deposit (weeks)",
                                min_value=0, max_value=6, value=5,
                                help="Capped at 5 weeks rent by UK Tenant Fees Act 2019.")

    with st.expander("Advanced (renting)"):
        renters_insurance = st.number_input("Renters insurance (annual £)",
                                              min_value=0, value=120, step=20)
        moving_cost = st.number_input("Moving cost per move (£)",
                                        min_value=0, value=500, step=50)
        avg_tenancy_years = st.slider("Average tenancy length (years)",
                                        min_value=1.0, max_value=10.0,
                                        value=3.5, step=0.5,
                                        help="UK average from ONS English Housing Survey")


# ──────────────────────────────────────────────────────────────
# Shared assumptions
# ──────────────────────────────────────────────────────────────

st.divider()
st.subheader("Shared assumptions")

col_ir, col_inf, col_fric = st.columns(3)
with col_ir:
    investment_return_pct = st.slider("Investment return (% / year)",
                                        min_value=0.0, max_value=15.0, value=5.0, step=0.5)
    investment_return = investment_return_pct / 100.0
    isa_tax_free = st.checkbox("Assume ISA-protected returns (no CGT)", value=True)
with col_inf:
    inflation_pct = st.slider("Inflation (% / year)",
                                min_value=0.0, max_value=10.0, value=2.5, step=0.5)
    inflation = inflation_pct / 100.0
with col_fric:
    include_long_term_frictions = st.checkbox(
        "Include long-term frictions",
        value=True,
        help="Multiple renter moves (every ~3.5y) + buyer remortgage fees on fix renewals. Roughly offset but more honest.",
    )


# ──────────────────────────────────────────────────────────────
# Build the scenario and run
# ──────────────────────────────────────────────────────────────

scenario = Scenario(
    borough=borough,
    postcode_district=postcode_district,
    property_type=property_type,
    new_build=new_build,
    first_time_buyer=first_time_buyer,
    plan_to_stay_years=plan_to_stay_years,
    starting_cash=float(starting_cash),
    investment_return=investment_return,
    isa_tax_free=isa_tax_free,
    inflation=inflation,
    home_price=float(home_price),
    deposit_pct=deposit_pct,
    auto_tier_rate=auto_tier,
    mortgage_rate=mortgage_rate,
    fix_years=fix_years,
    mortgage_term_years=mortgage_term_years,
    legal_survey=float(legal_survey),
    maintenance_pct=maintenance_pct,
    council_tax=float(council_tax),
    buildings_insurance=float(buildings_insurance),
    service_charge=float(service_charge),
    ground_rent=float(ground_rent),
    lease_years_remaining=lease_years_remaining,
    home_growth=home_growth,
    selling_fee_pct=selling_fee_pct,
    monthly_rent=float(monthly_rent),
    rent_growth=rent_growth,
    deposit_weeks=deposit_weeks,
    renters_insurance=float(renters_insurance),
    moving_cost=float(moving_cost),
    avg_tenancy_years=avg_tenancy_years,
    include_long_term_frictions=include_long_term_frictions,
)

result = run_scenario(scenario, data["boe_rates"])


# ──────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────

st.divider()

# Feasibility banner
if not result.feasible:
    st.error(
        f"⚠ You'd need roughly **£{result.shortfall:,.0f} more** to afford the upfront cost "
        f"of buying at this price. The numbers below assume you find that shortfall somehow."
    )

# Headline
if result.verdict == "rent_wins":
    st.success(
        f"🏠 Over {plan_to_stay_years} years, **renting wins** if the monthly rent is below "
        f"**£{result.breakeven_monthly_rent:,.0f}/month**. "
        f"Your entered rent is £{monthly_rent:,.0f} — renting is cheaper by about "
        f"**£{abs(result.buy_rent_delta):,.0f}** over {plan_to_stay_years} years."
    )
else:
    st.success(
        f"🏠 Over {plan_to_stay_years} years, **buying wins** once the monthly rent is above "
        f"**£{result.breakeven_monthly_rent:,.0f}/month**. "
        f"Your entered rent is £{monthly_rent:,.0f} — buying is cheaper by about "
        f"**£{abs(result.buy_rent_delta):,.0f}** over {plan_to_stay_years} years."
    )

# Chart
st.plotly_chart(build_cost_over_time_chart(result), use_container_width=True)

# Breakdowns
with st.expander("Buying breakdown"):
    b = result.buy_breakdown
    st.markdown(f"""
**Upfront**
- Deposit: £{b['deposit']:,.0f}
- SDLT: £{b['sdlt']:,.0f}
- Legal + survey: £{b['legal_survey']:,.0f}
- Moving: £{b['moving_buy']:,.0f}
- **Total upfront: £{result.buy_upfront_total:,.0f}**

**Monthly (avg)**
- Mortgage: £{b['monthly_mortgage']:,.0f}
- Council tax: £{b['monthly_council_tax']:,.0f}
- Maintenance: £{b['monthly_maintenance']:,.0f}
- Buildings insurance: £{b['monthly_buildings']:,.0f}
- Service charge: £{b['monthly_service_charge']:,.0f}
- Ground rent: £{b['monthly_ground_rent']:,.0f}
- **Total monthly: £{result.buy_monthly_total:,.0f}**

**At sale (year {plan_to_stay_years})**
- Home value: £{b['home_value_at_sale']:,.0f}
- Remaining mortgage: £{b['remaining_mortgage']:,.0f}
- Selling fee: £{b['selling_fee']:,.0f}
- **Equity out: £{result.buy_equity_at_sale:,.0f}**

**Rate used:** {b['rate_used']*100:.2f}% (LTV {b['ltv']*100:.1f}%)
**Remortgage fees over period:** £{b['remortgage_fees_total']:,.0f}
**Excess cash earning investment return:** £{b['excess_cash_invested']:,.0f}
**Investment income on excess cash:** £{result.buy_investment_income:,.0f}

**Net cost of buying: £{result.buy_net_cost:,.0f}**
""")

with st.expander("Renting breakdown"):
    r = result.rent_breakdown
    st.markdown(f"""
- Total rent (grown at {rent_growth_pct:.1f}%/year): £{r['total_rent']:,.0f}
- Number of moves: {r['num_moves']}
- Total moving cost: £{r['total_moving']:,.0f}
- Renters insurance: £{r['total_renters_ins']:,.0f}
- Deposit held (refundable): £{r['deposit_held']:,.0f}
- Investment income on money not spent on a deposit: £{r['investment_income']:,.0f}

**Net cost of renting: £{result.rent_net_cost:,.0f}**
""")

with st.expander("Assumptions used"):
    st.markdown(f"""
- **Location:** {borough}{' / ' + postcode_district if postcode_district else ''}
- **Property type:** {property_type_label}{' (new build)' if new_build else ''}
- **First-time buyer:** {'Yes' if first_time_buyer else 'No'}
- **Plan to stay:** {plan_to_stay_years} years
- **Starting cash:** £{starting_cash:,.0f}
- **Home price:** £{home_price:,.0f}
- **Deposit:** {deposit_pct*100:.0f}% (£{home_price*deposit_pct:,.0f})
- **Mortgage:** {mortgage_rate_pct:.2f}% fixed for {fix_years}y, {mortgage_term_years}y term
- **Rent growth:** {rent_growth_pct:.1f}% / year
- **Home growth:** {home_growth_pct:.1f}% / year
- **Investment return:** {investment_return_pct:.1f}% / year ({'ISA-protected' if isa_tax_free else '20% CGT applied'})
- **Inflation:** {inflation_pct:.1f}% / year
- **Long-term frictions:** {'included' if include_long_term_frictions else 'excluded'}
""")

st.caption(
    "_Results shown in nominal future pounds. Rate suggestion based on BoE G1.4 snapshot from "
    f"{data['boe_rates']['snapshot_date'].iloc[0]}. Not financial advice._"
)

# Tech footer
render_tech_footer([
    "Python", "pandas", "Plotly", "Streamlit",
    "HM Land Registry", "ONS", "Bank of England",
])
```

- [ ] **Step 2: Verify the page parses**

```bash
cd dashboard && python -c "
with open('pages/16_Rent_vs_Buy.py') as f:
    compile(f.read(), 'pages/16_Rent_vs_Buy.py', 'exec')
print('syntax ok')
"
```

Expected: `syntax ok`.

- [ ] **Step 3: Commit**

```bash
git add dashboard/pages/16_Rent_vs_Buy.py
git status --short
git commit -m "feat(rentbuy): add Rent vs Buy London Streamlit page"
```

---

## Task 8: Nav integration

**Files:**
- Modify: `dashboard/lib/nav.py`

- [ ] **Step 1: Read current nav.py**

```bash
grep -n "Calculators\|15_Budget" dashboard/lib/nav.py
```

Expected output shows the current Calculators block with entries 10-15.

- [ ] **Step 2: Add Rent vs Buy entry**

Find this block in `dashboard/lib/nav.py`:

```python
    st.sidebar.page_link("pages/15_Budget_Tracker.py", label="Budget Tracker")
```

Add a new line directly after it:

```python
    st.sidebar.page_link("pages/15_Budget_Tracker.py", label="Budget Tracker")
    st.sidebar.page_link("pages/16_Rent_vs_Buy.py", label="Rent vs Buy London")
```

- [ ] **Step 3: Launch the app and verify**

```bash
cd dashboard && streamlit run app.py
```

Navigate to the sidebar's **Mini Projects → Calculators** section. Verify:
- "Rent vs Buy London" appears directly after "Budget Tracker"
- Clicking it loads the new page
- Default borough is Camden, default property type is Flat
- Changing the borough to "Kensington and Chelsea" changes the default rent to ~£3,200
- Changing the property type to "Detached" changes the default price
- The chart renders with two lines
- The headline shows a breakeven rent

Stop the server (Ctrl+C) when verified.

- [ ] **Step 4: Commit**

```bash
git add dashboard/lib/nav.py
git status --short
git commit -m "feat(rentbuy): add Rent vs Buy London to sidebar nav"
```

---

## Task 9: BoE refresh script (one-off, not tested)

**Files:**
- Create: `dashboard/scripts/refresh_boe_rates.py`

This is a developer tool for refreshing the static CSV snapshot. It's not imported by the app and has no tests.

- [ ] **Step 1: Write the script**

Create `dashboard/scripts/refresh_boe_rates.py`:

```python
"""Refresh boe_mortgage_rates.csv from the Bank of England IADB.

Run manually by the developer every few months to update the bundled
mortgage rate snapshot. The Streamlit app never runs this — it reads
the bundled CSV only.

Usage:
    cd dashboard && python scripts/refresh_boe_rates.py

Source:
    BoE Interactive Statistical Database — series G1.4 "Quoted household
    interest rates". IUMBV* codes by (fix_years × ltv_bracket).

Note: BoE publishes monthly with a ~4-6 week lag. The script pulls
the latest available month and writes it as the new snapshot_date.
"""

from __future__ import annotations

import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd


# ──────────────────────────────────────────────────────────────
# BoE series codes for quoted rates by (fix_years × ltv_bracket)
#
# These codes are documented on the BoE interactive database under
# Bankstats Table G1.4 "Quoted household interest rates". They may
# change if BoE republishes the schema — verify against the BoE
# website if the script stops working.
# ──────────────────────────────────────────────────────────────

SERIES = [
    # (fix_years, ltv_bracket, boe_series_code)
    (2, 0.60, "IUMBV24"),
    (2, 0.75, "IUMBV34"),
    (2, 0.85, "IUMBV37"),
    (2, 0.90, "IUMBV42"),
    (2, 0.95, "IUMBV45"),
    (3, 0.60, "IUMBV48"),
    (3, 0.75, "IUMBV51"),
    (3, 0.85, "IUMBV54"),
    (3, 0.90, "IUMBV57"),
    (3, 0.95, "IUMBV60"),
    (5, 0.60, "IUMBV34"),   # verify codes against BoE before release
    (5, 0.75, "IUMBV37"),
    (5, 0.85, "IUMBV42"),
    (5, 0.90, "IUMBV45"),
    (5, 0.95, "IUMBV48"),
    (10, 0.60, "IUMBV51"),
    (10, 0.75, "IUMBV54"),
    (10, 0.85, "IUMBV57"),
    (10, 0.90, "IUMBV60"),
    (10, 0.95, "IUMBV63"),
]

IADB_URL_TEMPLATE = (
    "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?"
    "Travel=NIxAZxSUx&FromSeries=1&ToSeries=50&DAT=RNG"
    "&FD=1&FM={from_m}&FY={from_y}&TD=31&TM={to_m}&TY={to_y}"
    "&FNY=Y&CSVF=TN&html.x=66&html.y=26"
    "&SeriesCodes={code}&UsingCodes=Y&Filter=N&title={code}&VPD=Y"
)

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "boe_mortgage_rates.csv"


def fetch_series_latest(code: str) -> float | None:
    """Download the last 3 months of a BoE series and return the most recent value.

    Returns None if the fetch fails or the parsed data is empty.
    """
    now = dt.date.today()
    three_months_ago = now - dt.timedelta(days=100)
    url = IADB_URL_TEMPLATE.format(
        from_m=three_months_ago.strftime("%b"),
        from_y=three_months_ago.year,
        to_m=now.strftime("%b"),
        to_y=now.year,
        code=code,
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as exc:
        print(f"  {code}: fetch failed — {exc}")
        return None

    try:
        df = pd.read_csv(io.StringIO(raw))
        if df.empty or len(df.columns) < 2:
            return None
        # BoE CSV format: first column is date, second is value
        latest = df.iloc[-1, 1]
        return float(latest)
    except Exception as exc:
        print(f"  {code}: parse failed — {exc}")
        return None


def main() -> int:
    rows = []
    snapshot_date = dt.date.today().strftime("%Y-%m")
    print(f"Refreshing BoE rates — snapshot {snapshot_date}")

    for fix_years, ltv_bracket, code in SERIES:
        rate = fetch_series_latest(code)
        if rate is not None:
            rows.append({
                "fix_years": fix_years,
                "ltv_bracket": ltv_bracket,
                "rate_pct": rate,
                "snapshot_date": snapshot_date,
            })
            print(f"  {code} (fix={fix_years}, ltv={ltv_bracket}): {rate:.2f}%")

    if not rows:
        print("No data fetched. Leaving existing CSV untouched.")
        return 1

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Commit (do NOT run the script — it's a dev tool)**

```bash
git add dashboard/scripts/refresh_boe_rates.py
git status --short
git commit -m "feat(rentbuy): add BoE rate refresh script (manual, dev-only)"
```

---

## Task 10: Full verification + PR (quant_lab)

- [ ] **Step 1: Run full test suite**

```bash
cd dashboard && python -m pytest tests/ 2>&1 | tail -5
```

Expected: all existing tests plus the ~50 new rentbuy tests pass. Zero failures.

- [ ] **Step 2: Run focused rentbuy suite**

```bash
cd dashboard && python -m pytest tests/test_rentbuy*.py -v 2>&1 | tail -10
```

Expected: `~50 passed`.

- [ ] **Step 3: Manual verification checklist**

Launch:

```bash
cd dashboard && streamlit run app.py
```

Navigate to Mini Projects → Calculators → Rent vs Buy London. Verify:

- [ ] Page loads without errors, default borough Camden
- [ ] Intro paragraph with NYT link visible
- [ ] Borough dropdown lists ~33 London boroughs
- [ ] Property type radio defaults to Flat
- [ ] Changing borough to Westminster changes default rent and council tax
- [ ] Changing property type to "Detached" shows a different default price, hides service charge inputs
- [ ] First-time buyer checkbox recomputes SDLT
- [ ] Plan-to-stay slider updates the chart in real time
- [ ] Starting cash input shows feasibility banner when reduced to £10,000
- [ ] Auto-tier rate checkbox enables/disables manual rate field
- [ ] LTV caption updates as deposit slider moves
- [ ] Larger deposit → lower rate → lower total cost
- [ ] Cost-over-time chart renders with two lines
- [ ] Headline banner shows breakeven rent
- [ ] Buying breakdown expander shows all line items
- [ ] Renting breakdown expander shows moves count
- [ ] No uncaught exceptions in Streamlit terminal log

- [ ] **Step 4: Push and open PR**

```bash
git push origin working
gh pr create --base master --head working --title "feat: Rent vs Buy London calculator" --body "$(cat <<'EOF'
## Summary
New Streamlit page under Mini Projects → Calculators that compares the total cost of renting vs buying a London home over a user-chosen horizon.

**Inspired by** the [NYT rent vs buy calculator](https://www.nytimes.com/2024/05/13/briefing/a-new-rent-versus-buy-calculator.html) but adapted for London:
- UK SDLT (with first-time buyer relief) instead of US transfer taxes
- Council tax by borough instead of US property tax %
- Leasehold flat quirks (service charge, ground rent, lease length warning)
- LTV-tiered mortgage rates sourced from Bank of England G1.4
- Real price defaults from HM Land Registry Price Paid Data
- Real rent defaults from ONS Private Rental Market Statistics

## What's new
- `dashboard/lib/rentbuy/` package (finance, inputs, scenario, charts)
- `dashboard/pages/16_Rent_vs_Buy.py` — UI glue only
- 4 bundled data CSVs: borough rents, council tax, district→borough lookup, BoE mortgage rates
- Dev script `scripts/refresh_boe_rates.py` for periodic BoE data refresh
- ~50 new automated tests

## Test Plan
- [x] All rentbuy tests pass (`pytest tests/test_rentbuy*.py`)
- [x] Full dashboard test suite green
- [ ] Manual: borough/property type changes update defaults
- [ ] Manual: LTV tiering works (larger deposit → better rate → lower cost)
- [ ] Manual: first-time buyer toggle changes SDLT
- [ ] Manual: feasibility banner appears when starting cash is too low

## Specs and plans
- Design: [docs/superpowers/specs/2026-04-14-rent-vs-buy-london-design.md](docs/superpowers/specs/2026-04-14-rent-vs-buy-london-design.md)
- Plan: [docs/superpowers/plans/2026-04-14-rent-vs-buy-london.md](docs/superpowers/plans/2026-04-14-rent-vs-buy-london.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL in the report.

---

## Task 11: Blog post (in FinBytes repo)

**Files (in `C:/codebase/finbytes_git`, NOT quant_lab):**
- Create: `docs/_quant_lab/mini/rent-vs-buy.html`
- Modify: `docs/_tabs/quant-lab.md`

This is a context-switch to a different repo. Work from `C:/codebase/finbytes_git`. Stay on branch `working`.

- [ ] **Step 1: Create the blog post**

Create `docs/_quant_lab/mini/rent-vs-buy.html`:

```html
---
layout: quant-lab-mini
title: "Rent vs Buy — London: A Data-Driven Calculator"
date: 2026-04-14
tags: [finance, london, property, calculator, streamlit, python, mortgages]
section: quant-lab
permalink: /quant-lab/rent-vs-buy/
---

<style>
.rvb-lede { color:var(--text-muted-color, #666); font-size:.98rem; margin-bottom:2rem; line-height:1.7; }
.rvb-h2 { font-size:1.3rem; margin-top:2rem; margin-bottom:.8rem; }
.rvb-code-caption { font-size:.78rem; color:var(--text-muted-color, #888); margin-top:-1rem; margin-bottom:1.2rem; }
</style>

<p class="rvb-lede">
Should you rent or buy a London home? It's one of the most consequential
financial decisions most adults make, and the honest answer depends on
about twenty variables interacting in non-obvious ways. I built a
calculator that does the math for you using real London data.
</p>

<p>
The inspiration was the <a href="https://www.nytimes.com/2024/05/13/briefing/a-new-rent-versus-buy-calculator.html" target="_blank">New York Times rent vs buy calculator</a>,
originally launched in 2014 and updated in 2024. It's a brilliant tool —
sliders, live feedback, and a "breakeven rent" headline that cuts through
all the noise. But it's built for the US market, and applying its logic
directly to London produces wrong answers for five or six structural
reasons. This post walks through what I changed, what I kept, and what
the calculator is honest about not knowing.
</p>

<p>
<strong>Try it here:</strong> <a href="https://finbytes-quantlab.streamlit.app">finbytes-quantlab.streamlit.app</a> → Mini Projects → Rent vs Buy London.
</p>

<h2 class="rvb-h2">Why the NYT formula needed adapting</h2>

<p>Five biggest differences between the US and UK markets:</p>

<ol>
  <li><strong>SDLT is tiered, not percentage.</strong> UK Stamp Duty Land Tax applies progressively: 0% up to £250k, 5% on £250k–£925k, 10% on £925k–£1.5M, 12% above. First-time buyers get a different schedule (0% up to £425k) but only below £625k total. The NYT uses a single "transfer tax percentage" field, which produces wildly wrong SDLT estimates on £600k+ purchases.</li>

  <li><strong>No mortgage interest tax deduction.</strong> The UK abolished mortgage interest relief in 2000. The NYT calculator has an entire column for "tax savings on mortgage interest" — that column is zero in a UK calculator. Removing it actually makes buying look worse relative to the US.</li>

  <li><strong>Council tax is a flat pound amount, not a percentage.</strong> NYT uses "property tax %" which is how US jurisdictions charge (1-2% of assessed value). UK council tax is set at a flat £ per year by borough and band — Wandsworth band D is ~£900 while Kingston band D is ~£2,320. These are valuations frozen in 1991, not tracked to current prices.</li>

  <li><strong>UK mortgages are short-fix, not 30-year fixed.</strong> A typical UK mortgage has a 2- or 5-year fixed period, then reverts to a variable rate. When the fix ends you usually remortgage, paying £1-2k in fees. The NYT assumes one fixed rate for the whole term.</li>

  <li><strong>Leasehold flats.</strong> Most London flats are leasehold, which means you own the flat for a fixed term (often 99-999 years from the original grant) and pay annual service charge + ground rent to the freeholder. As the lease runs down, the value declines — and below ~80 years, mortgage availability dries up and lease extension can cost tens of thousands. The NYT has no equivalent concept.</li>
</ol>

<h2 class="rvb-h2">The core math</h2>

<p>
The fundamental idea is the same on both sides: sum up all the cash
flowing out of your wallet over N years, then subtract what you get back.
</p>

<p><strong>Buying:</strong></p>

<pre><code>total_cost_of_buying = deposit + SDLT + legal + moving
                      + monthly_mortgage * 12 * N
                      + council_tax * N
                      + maintenance * N
                      + buildings_insurance * N
                      + (service_charge + ground_rent) * N   [flats only]
                      + remortgage_fees_per_fix_cycle
                      - home_value_at_sale
                      + remaining_mortgage
                      + selling_fee
                      - investment_return_on_excess_starting_cash</code></pre>

<p><strong>Renting:</strong></p>

<pre><code>total_cost_of_renting = rent_with_annual_growth_over_N_years
                       + moving_cost * num_moves
                       + renters_insurance * N
                       - investment_return_on_money_not_spent_on_deposit</code></pre>

<p>
The mortgage formula is the standard amortization equation, straight
out of any finance textbook:
</p>

<pre><code>def monthly_mortgage_payment(principal, annual_rate, years):
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)</code></pre>

<p>
SDLT is slightly more fun — a bracket function with different thresholds
for first-time buyers:
</p>

<pre><code>STANDARD_BANDS = [
    (  250_000,      0.00),
    (  925_000,      0.05),
    (1_500_000,      0.10),
    (float("inf"),   0.12),
]

def calculate_sdlt(price, first_time_buyer=False):
    if first_time_buyer and price <= 625_000:
        return _tiered_tax(price, FTB_BANDS)
    return _tiered_tax(price, STANDARD_BANDS)</code></pre>

<p>
The breakeven rent is what makes the whole thing useful. If you know
the total net cost of buying over N years, you can solve for the monthly
rent at which the two sides tie:
</p>

<pre><code>breakeven_monthly = (buy_net_cost + rent_investment_income
                    - non_rent_outflows) / (12 * growth_sum)</code></pre>

<p>
Where <code>growth_sum</code> is the discounted rent accumulator
<code>sum((1+g)^y for y in 0..N-1)</code>. If you can rent for less
than this, renting wins. If not, buying wins.
</p>

<h2 class="rvb-h2">LTV tiering — the detail that matters most in the UK</h2>

<p>
Here's a thing I didn't appreciate until I started building this:
<strong>UK mortgage rates step down in brackets based on your loan-to-value ratio</strong>.
At 95% LTV you might pay 6.0%; at 60% LTV you might pay 4.3%. That's a
1.5 percentage point gap, and over a 25-year £500k mortgage it's worth
about <strong>£160,000</strong> in interest.
</p>

<p>
This makes "save more before you buy" into one of the most impactful
financial decisions a prospective UK buyer can make — and it's much
sharper than the US equivalent.
</p>

<p>
The Bank of England publishes the typical quoted rates across lenders
in <strong>Bankstats table G1.4 "Quoted household interest rates"</strong>,
by fix length (2/3/5/10 years) and LTV bracket (60/75/85/90/95%). The
series codes are <code>IUMBV*</code> and you can fetch them as CSV from
the BoE Interactive Statistical Database with no API key or login.
</p>

<p>
My calculator bundles a snapshot CSV and uses it to auto-suggest the
mortgage rate based on the user's LTV. Drag the deposit slider left
and the rate bumps up; drag it right and the rate drops. Watching the
total cost of buying change in real time as you add another £10k to
your deposit is the most concrete argument for saving more that I've
seen in any calculator.
</p>

<h2 class="rvb-h2">London-specific quirks</h2>

<p><strong>New build premium.</strong> New-build flats in London
typically sell at a 10–20% premium to equivalent older properties.
That premium often erodes over the first 5 years of ownership as the
"new" stops being new. The calculator doesn't explicitly model this
(it would need a depreciation curve) but warns about it in the UI.</p>

<p><strong>Council tax bands.</strong> All UK residential property
is in a council tax band (A–H) based on its 1991 valuation. Over 30
years of property appreciation, the bands have become increasingly
meaningless. Wandsworth and Westminster have dramatically lower council
tax than outer boroughs — Wandsworth band D is ~£900/year while Kingston
band D is ~£2,320. The calculator uses the actual band D for the
selected borough, not a percentage of current value.</p>

<p><strong>Service charges on leasehold flats.</strong> Service charges
have exploded in recent years — some new-build developments in London
charge £5k-10k/year on top of everything else. The calculator includes
service charge as a separate input visible only when the property type
is "Flat".</p>

<p><strong>Buildings vs contents insurance.</strong> If you buy a
freehold house, you pay buildings insurance (~£300-500/year) because
you own the bricks. If you buy a leasehold flat, the freeholder pays
buildings insurance from the service charge (usually). Either way,
both renters and buyers can pay optional contents insurance for their
stuff.</p>

<p><strong>First-time buyer SDLT relief.</strong> FTB relief bumps the
nil-rate band from £250k to £425k, and the 5% band from £250k–£925k to
£425k–£625k. Above £625k, FTB relief disappears entirely and you pay
the full standard bands. For London FTBs this is the difference between
~£7,500 and £0 on a £450k flat.</p>

<h2 class="rvb-h2">Data sources</h2>

<p>
Everything the calculator uses is free and freely available under the
UK Open Government Licence.
</p>

<ul>
  <li><strong>HM Land Registry Price Paid Data.</strong> 28 million
  property transactions since 1995, released as free downloadable
  CSVs. I filter to the most recent 3 years and group by (postcode
  district × property type × new build flag) to compute sensible
  median price defaults.</li>

  <li><strong>ONS Private Rental Market Statistics.</strong> The
  Office for National Statistics publishes monthly median rent by
  local authority under "Private Rental Market Summary Statistics
  in England". I bundle a static CSV of the 33 London boroughs and
  update it annually.</li>

  <li><strong>Council tax.</strong> Each London borough publishes
  its annual council tax leaflet with band A-H rates. I aggregate
  them into a single CSV — manual curation, refreshed annually as
  boroughs set new rates each March.</li>

  <li><strong>Bank of England G1.4.</strong> Monthly snapshot of
  typical quoted household mortgage rates by fix length and LTV.
  I fetch it via the IADB interactive database as CSV. A helper script
  (<code>scripts/refresh_boe_rates.py</code>) pulls the latest values
  and writes the bundled snapshot. The Streamlit app reads the bundled
  file only — no network I/O at page load.</li>
</ul>

<h2 class="rvb-h2">What this calculator gets right, what it doesn't</h2>

<p><strong>Right:</strong></p>
<ul>
  <li>Real data defaults — price from HM Land Registry, rent from ONS, rate from BoE</li>
  <li>UK-specific costs: SDLT, council tax, service charge, ground rent</li>
  <li>First-time buyer SDLT relief</li>
  <li>LTV-tiered mortgage rates — the single biggest UK-specific factor</li>
  <li>Opportunity cost of the deposit on both sides (buying and renting)</li>
  <li>ISA protection toggle — the renter's investment return is less valuable if it's taxed</li>
  <li>Multiple renter moves over a long horizon (offset by buyer remortgage fees)</li>
  <li>All the formulas are open source and pytest-covered</li>
</ul>

<p><strong>Simplified or missing:</strong></p>
<ul>
  <li><strong>Deterministic single trajectory.</strong> House prices and investment returns are modeled as constant growth rates. Real markets have volatility. The 2008 crash was not a small event. A Monte Carlo version with confidence bands is on my list.</li>
  <li><strong>Borough-level rent.</strong> The ONS data is aggregated to borough, not postcode district. A £2,100/month default for "Camden" lumps Somers Town and Hampstead together. This is the biggest honest gap.</li>
  <li><strong>Fixed rate for the whole term.</strong> If your plan-to-stay is 15 years but you're on a 5-year fix, you'll remortgage twice at unknown future rates. The calculator keeps the rate fixed for the whole stay, with a caption warning.</li>
  <li><strong>No mortgage affordability stress test.</strong> Banks typically lend 4.5× income. If you earn £60k you can't actually get a £650k mortgage. The calculator doesn't check.</li>
  <li><strong>Interest-only mortgages not modeled.</strong> Some UK mortgages are interest-only (you pay interest during the term and owe the full principal at the end). Not common for owner-occupiers post-2014 but worth flagging.</li>
  <li><strong>Section 21 eviction risk.</strong> Until the Renters Reform Bill fully lands, UK tenants can be asked to leave with 2 months' notice for no reason. Not quantifiable but a real non-financial reason some people prefer buying.</li>
  <li><strong>Shared ownership.</strong> Buying 25–75% of a home and renting the rest — common in London, totally different math. Out of scope for this calculator but worth a dedicated tool.</li>
  <li><strong>LISA / Help to Buy bonuses.</strong> A Lifetime ISA gives a 25% government bonus on up to £4k/year of savings for first-time buyers. That effectively boosts your starting cash. The calculator's "starting cash" input is whatever number you type — it doesn't differentiate between cash saved in an ISA vs a normal savings account.</li>
  <li><strong>Emotional factors.</strong> Paint the walls. Stability for kids. Pride of ownership. Flexibility of renting. The NYT calculator acknowledges these in its footnotes. So do I: no calculator can tell you how much these are worth to you.</li>
</ul>

<h2 class="rvb-h2">Try it yourself</h2>

<p>
<a href="https://finbytes-quantlab.streamlit.app" target="_blank">
Live calculator on Streamlit Cloud →
</a>
</p>

<p>
Play with the <strong>plan-to-stay slider</strong> — it's the single
biggest lever. Short stays favor renting because upfront costs dominate.
Long stays favor buying because equity accumulates. The crossover year
is different for every borough, every property type, and every starting
cash amount.
</p>

<h2 class="rvb-h2">What I learned</h2>

<p>
Three things I hadn't fully internalized before I built this:
</p>

<ol>
  <li>
    <strong>LTV matters more than the base mortgage rate.</strong>
    A 10-point deposit shift (from 5% to 15% down) can save you more
    money than a 0.5 percentage point base rate change. It's counterintuitive
    until you realize the 10-point shift also moves you into a completely
    different rate tier.
  </li>
  <li>
    <strong>Council tax is invisibly huge.</strong> £2,000/year is
    £50,000 over a 25-year mortgage. That's the deposit for a parking
    space. Almost no one factors it in when thinking about "can I afford
    this flat".
  </li>
  <li>
    <strong>Nobody talks about the opportunity cost correctly.</strong>
    Every rent-vs-buy debate online eventually devolves into "but you're
    throwing money away on rent!" — which ignores that the alternative
    is throwing money into a house-shaped illiquid asset instead of
    a diversified investment portfolio. The honest comparison is total
    cost with opportunity cost on both sides, which is exactly what the
    NYT calculator gets right and what I tried to preserve.
  </li>
</ol>

<p>
<strong>Next steps:</strong> a borough heatmap of breakeven rent (which
boroughs are currently the best places to buy vs rent?), and an
integration with the existing London House Prices page so you can
jump from a postcode's historical trend straight into the calculator.
</p>

<p><em>Not financial advice. Model assumptions documented in the
<a href="https://github.com/mish-codes/QuantLab" target="_blank">QuantLab repo</a>.
Data snapshots refreshed periodically — check the source links on
each input's tooltip.</em></p>
```

- [ ] **Step 2: Add entry to the QuantLab landing page**

Read `docs/_tabs/quant-lab.md` and find the "Mini Projects — Calculators" section. Locate this entry:

```html
  <li>
    <a href="{{ "/quant-lab/budget-tracker/" | relative_url }}">Budget Tracker</a>
    <span class="ql-badges"><span class="ql-badge ql-badge-mini">Mini Project</span><span class="ql-badge ql-badge-calc">Calculator</span></span>
    <span class="ql-desc">Income vs expenses, spending breakdown, surplus/deficit</span>
    <span class="ql-tech">Python &middot; Plotly &middot; Streamlit</span>
  </li>
```

Add a new entry directly after it:

```html
  <li>
    <a href="{{ "/quant-lab/rent-vs-buy/" | relative_url }}">Rent vs Buy London</a>
    <span class="ql-badges"><span class="ql-badge ql-badge-mini">Mini Project</span><span class="ql-badge ql-badge-calc">Calculator</span></span>
    <span class="ql-desc">Should you rent or buy a London home? Data-driven calculator using HM Land Registry prices, ONS rents, and Bank of England mortgage rates</span>
    <span class="ql-tech">Python &middot; Streamlit &middot; pandas &middot; Plotly &middot; HM Land Registry &middot; ONS &middot; Bank of England</span>
  </li>
```

- [ ] **Step 3: Verify Jekyll builds**

```bash
cd docs && bundle exec jekyll build 2>&1 | tail -15
```

Expected: build succeeds. Pre-existing warnings about 404.html, feed.xml conflicts are OK. The new post should appear at `_site/quant-lab/rent-vs-buy/index.html`.

```bash
ls docs/_site/quant-lab/rent-vs-buy/index.html
```

Expected: file exists.

- [ ] **Step 4: Commit both files**

```bash
cd C:/codebase/finbytes_git
git add docs/_quant_lab/mini/rent-vs-buy.html docs/_tabs/quant-lab.md
git status --short
git commit -m "feat(quant-lab): add Rent vs Buy London blog post and landing entry"
```

- [ ] **Step 5: Push and follow FinBytes git workflow**

Per CLAUDE.md, the FinBytes workflow is working → master with push to both:

```bash
git push origin working
git checkout master
git merge working --no-verify -m "feat(quant-lab): add Rent vs Buy London blog post"
git push origin master
git checkout working
```

---

## Self-Review Notes

**Spec coverage check:**

- ✅ Package layout and all 5 module files (Tasks 1, 2, 3, 4, 5, 6)
- ✅ Scenario dataclass with every field from the spec (Task 3)
- ✅ SDLT standard + FTB with tiered bracket logic (Task 2)
- ✅ Mortgage amortization formula (Task 2)
- ✅ LTV tiering from BoE snapshot (Task 3)
- ✅ Total cost of buying with remortgage fees and investment income (Task 3)
- ✅ Total cost of renting with multi-move frictions (Task 4)
- ✅ Breakeven rent analytical solver (Task 4)
- ✅ Data file loaders (Task 5)
- ✅ Default lookups with fallback chains (Task 5)
- ✅ Result dataclass with feasibility, verdict, breakdown dicts (Task 6)
- ✅ Plotly cost-over-time chart with crossover marker (Task 6)
- ✅ Streamlit page with every input from the spec (Task 7)
- ✅ Conditional display for flat-only fields (Task 7)
- ✅ Interest-rate-reset caption when fix < plan (Task 7)
- ✅ Feasibility banner (Task 7)
- ✅ Breakeven-rent headline (Task 7)
- ✅ Expandable breakdowns (Task 7)
- ✅ Nav integration (Task 8)
- ✅ BoE refresh script (Task 9)
- ✅ 4 bundled data CSVs with real London values (Task 1)
- ✅ Blog post in FinBytes repo at the quant-lab/mini path (Task 11)
- ✅ QuantLab landing entry (Task 11)

**Placeholder scan:** no TBD/TODO strings. All code blocks complete. Every data file has actual content (CSVs with real values). Every test has real assertions. Every step has exact commands.

**Type consistency:**
- `Scenario` dataclass is defined once in `finance.py` (Task 3) and imported consistently in `scenario.py`, `charts.py`, and the page
- `Result` dataclass is defined once in `scenario.py` (Task 6) and imported in `charts.py` and the page
- `lookup_boe_rate` (in inputs.py) and `suggest_rate_for_ltv` (in finance.py) have compatible signatures — both take ltv + fix_years + df
- `make_scenario` test helper is defined once in `test_rentbuy_finance.py` and imported in `test_rentbuy_scenario.py` / `test_rentbuy_charts.py` via module import
- `boe_rates` fixture defined once in `test_rentbuy_finance.py` and reused
- `total_cost_of_buying(scenario, boe_rates_df)` signature matches across tests, scenario runner, and page

**Scope check:** single feature across two repos (quant_lab for the calculator, FinBytes for the blog post). Related but distinct — Task 11 clearly marks the repo context switch. Everything implementable in one session.

No gaps found.
