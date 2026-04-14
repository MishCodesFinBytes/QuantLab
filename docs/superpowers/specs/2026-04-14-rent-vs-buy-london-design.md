# Rent vs Buy — London Calculator

**Date:** 2026-04-14
**Status:** Final — ready for implementation plan

## Goal

Build an interactive "should I rent or buy?" calculator for London, inspired by the [NYT 2024 rent vs buy calculator](https://www.nytimes.com/2024/05/13/briefing/a-new-rent-versus-buy-calculator.html) but adapted for the UK market. Ships as a new Streamlit page in the QuantLab dashboard's **Mini Projects → Calculators** section, plus an accompanying long-form blog post in the FinBytes Jekyll blog's **QuantLab mini projects** section.

The calculator uses bundled data so defaults are real (not guesses):
- **Home prices** from HM Land Registry Price Paid Data — filtered by postcode district, property type, and new-build flag
- **Monthly rents** from ONS Private Rental Market Statistics — borough-level medians
- **Council tax** from aggregated London borough 2024/25 rates
- **Mortgage rates** from Bank of England G1.4 "Quoted household interest rates" — tiered by LTV bracket and fix length

Users override any default with live recalculation on input change.

## Non-goals

- No real-time listings / Rightmove / Zoopla scraping
- No user accounts or saved scenarios
- No Monte Carlo / probability bands (single-trajectory model)
- No mortgage affordability stress test vs income (out of scope)
- No shared ownership or Help to Buy calculations (flagged in blog post)
- No interest-only mortgage option (repayment only, flagged)
- No Streamlit page unit tests — pure finance layer gets full tests, UI is manual only
- No automatic BoE data refresh at page load (refresh is a manual script the developer runs)

## Architecture

### Files

| Path | Status | Purpose |
|---|---|---|
| `dashboard/lib/rentbuy/__init__.py` | New | Package marker, re-exports public API |
| `dashboard/lib/rentbuy/finance.py` | New | Pure math: SDLT, LTV tiering, amortization, total-cost functions |
| `dashboard/lib/rentbuy/inputs.py` | New | Default lookups: price by (district × type × new_build), rent by borough, council tax, BoE rate |
| `dashboard/lib/rentbuy/scenario.py` | New | `Scenario` → `Result` glue between UI and finance layer |
| `dashboard/lib/rentbuy/charts.py` | New | Plotly figures for cost-over-time and breakeven visualization |
| `dashboard/pages/16_Rent_vs_Buy.py` | New | Streamlit page (UI glue only) |
| `dashboard/lib/nav.py` | Modified | Add Rent vs Buy entry under Calculators |
| `dashboard/data/london_borough_rents.csv` | New (~1 KB) | ONS median monthly rent per London borough |
| `dashboard/data/london_council_tax.csv` | New (~2 KB) | Band A–H council tax per London borough 2024/25 |
| `dashboard/data/london_district_to_borough.csv` | New (~5 KB) | Postcode district → borough lookup |
| `dashboard/data/boe_mortgage_rates.csv` | New (~1 KB) | BoE G1.4 quoted rates by (fix_years × ltv_bracket), snapshot with date |
| `dashboard/scripts/refresh_boe_rates.py` | New | One-time script to refresh boe_mortgage_rates.csv from BoE IADB |
| `dashboard/tests/test_rentbuy_finance.py` | New | Pure math tests (SDLT, LTV tiering, amortization, totals, breakeven) |
| `dashboard/tests/test_rentbuy_scenario.py` | New | Glue tests (scenario → result shape) |
| `dashboard/tests/test_rentbuy_inputs.py` | New | Default-lookup tests |
| `dashboard/tests/test_rentbuy_charts.py` | New | Plotly figure shape test |

### Blog post (in the FinBytes repo, not QuantLab)

| Path | Status | Purpose |
|---|---|---|
| `docs/_quant_lab/mini/rent-vs-buy.html` | New | Long-form ~2500-word deep-dive post |
| `docs/_tabs/quant-lab.md` | Modified | Add an entry under "Mini Projects — Calculators" |

### Why the split

- `finance.py` is pure number crunching — every formula (SDLT, mortgage amortization, LTV rate lookup, total cost of buying, total cost of renting, breakeven) is a standalone function with no external state. Easy to unit-test.
- `inputs.py` wraps every data-file lookup behind simple functions (`default_home_price`, `default_monthly_rent`, `default_council_tax`, `lookup_boe_rate`). The page never reads CSVs directly.
- `scenario.py` is the seam between UI state and the finance layer. Takes a `Scenario` dataclass, returns a `Result` dataclass. One function call per page render.
- `charts.py` returns Plotly figures. The page drops them into `st.plotly_chart` and forgets them.
- The page is UI glue only — no computation, no data loading, no chart assembly.

No new Python dependencies. Uses existing pandas, Plotly, Streamlit.

## Data model

```python
from dataclasses import dataclass

@dataclass
class Scenario:
    # Location
    borough: str
    postcode_district: str | None       # optional; narrows price default
    property_type: str                   # "F" | "T" | "S" | "D"
    new_build: bool
    first_time_buyer: bool

    # Shared
    plan_to_stay_years: int              # 1-30
    starting_cash: float
    investment_return: float             # annual %
    isa_tax_free: bool                   # if True, no CGT on opportunity cost
    inflation: float                     # annual %

    # Buying
    home_price: float
    deposit_pct: float                   # 0-1
    auto_tier_rate: bool                 # if True, mortgage_rate = BoE rate for current LTV
    mortgage_rate: float                 # annual %, manual or auto-tiered
    fix_years: int                       # 2 | 3 | 5 | 10
    mortgage_term_years: int             # usually 25 or 30
    legal_survey: float                  # default £2,500 inc VAT
    maintenance_pct: float               # of home value per year
    council_tax: float                   # annual £
    buildings_insurance: float           # annual £
    service_charge: float                # annual £, only if property_type == "F"
    ground_rent: float                   # annual £, only if property_type == "F"
    lease_years_remaining: int | None    # only if property_type == "F"
    home_growth: float                   # annual %
    selling_fee_pct: float               # fraction, default 0.015

    # Renting
    monthly_rent: float
    rent_growth: float                   # annual %
    deposit_weeks: int                   # UK standard 5 weeks
    renters_insurance: float             # annual £
    moving_cost: float                   # per move
    avg_tenancy_years: float             # default 3.5 from ONS

    # Realism toggle
    include_long_term_frictions: bool    # default True


@dataclass
class Result:
    scenario: Scenario

    # Feasibility
    required_upfront_buy: float
    shortfall: float                     # max(0, required_upfront_buy - starting_cash)
    feasible: bool                       # starting_cash >= required_upfront_buy

    # Buying side
    buy_upfront_total: float             # deposit + SDLT + legal + survey + moving
    buy_monthly_total: float             # avg monthly outflow while owning
    buy_total_cost_over_period: float    # sum of all buying cash outflows
    buy_equity_at_sale: float            # home value at sale - remaining mortgage - selling fee
    buy_investment_income: float         # returns on excess cash not spent up front
    buy_net_cost: float                  # total cost - equity - investment income

    # Renting side
    rent_total_cost_over_period: float   # sum of rents over the period
    rent_opportunity_cost_benefit: float # investment returns on money not spent on deposit
    rent_net_cost: float                 # total cost - opportunity cost benefit

    # The headline answer
    verdict: str                         # "buy_wins" | "rent_wins"
    breakeven_monthly_rent: float        # the rent at which the two sides cost the same
    buy_rent_delta: float                # buy_net_cost - rent_net_cost (negative = buying wins)

    # Year-by-year arrays for the chart
    yearly_buy_cost: list[float]         # cumulative net cost of buying at end of year y
    yearly_rent_cost: list[float]        # cumulative net cost of renting at end of year y

    # Diagnostic breakdowns for expanders
    buy_breakdown: dict                  # line items for the UI
    rent_breakdown: dict
```

## Finance layer (`finance.py`)

### Mortgage amortization (standard)

```python
def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortization. Returns monthly payment."""
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def remaining_balance(principal: float, annual_rate: float, years: int, months_elapsed: int) -> float:
    """Outstanding mortgage principal after N months of payments."""
    if annual_rate == 0:
        return principal - (principal / (years * 12)) * months_elapsed
    r = annual_rate / 12
    n = years * 12
    pmt = monthly_mortgage_payment(principal, annual_rate, years)
    future_value = principal * (1 + r) ** months_elapsed - pmt * ((1 + r) ** months_elapsed - 1) / r
    return max(0.0, future_value)
```

### SDLT (UK Stamp Duty Land Tax)

**Current rules (2024/25):**
- Standard bands: 0% up to £250k, 5% on £250k–£925k, 10% on £925k–£1.5M, 12% above £1.5M
- First-time buyer relief: 0% up to £425k, 5% on £425k–£625k, **no relief** above £625k

```python
STANDARD_BANDS = [
    (250_000,       0.00),
    (925_000,       0.05),
    (1_500_000,     0.10),
    (float("inf"),  0.12),
]

FTB_BANDS = [
    (425_000,       0.00),
    (625_000,       0.05),
    # above 625k → no relief, fall back to standard bands
]

def calculate_sdlt(price: float, first_time_buyer: bool = False) -> float:
    """Compute SDLT on a purchase price. Returns total tax in pounds."""
    if first_time_buyer and price <= 625_000:
        return _tiered_tax(price, FTB_BANDS)
    return _tiered_tax(price, STANDARD_BANDS)


def _tiered_tax(price: float, bands: list) -> float:
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
```

### LTV tiering (BoE-sourced)

```python
def suggest_rate_for_ltv(ltv: float, fix_years: int, boe_rates_df) -> float:
    """Look up the typical quoted rate for this LTV and fix length.

    boe_rates_df has columns: fix_years, ltv_bracket, rate_pct, snapshot_date
    ltv_bracket is the *ceiling* (e.g., 0.75 means "≤75% LTV").
    We pick the smallest bracket that's >= the caller's ltv.
    """
    subset = boe_rates_df[boe_rates_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return row["rate_pct"] / 100.0
    # Above the highest bracket — use the last one
    return subset.iloc[-1]["rate_pct"] / 100.0
```

### Total cost of buying

```python
def total_cost_of_buying(scenario: Scenario, boe_rates_df) -> dict:
    years = scenario.plan_to_stay_years
    price = scenario.home_price
    deposit = price * scenario.deposit_pct
    principal = price - deposit
    ltv = principal / price

    if scenario.auto_tier_rate:
        rate = suggest_rate_for_ltv(ltv, scenario.fix_years, boe_rates_df)
    else:
        rate = scenario.mortgage_rate

    # Upfront
    sdlt = calculate_sdlt(price, scenario.first_time_buyer)
    moving_buy = scenario.moving_cost                     # one move when buying
    upfront = deposit + sdlt + scenario.legal_survey + moving_buy

    # Monthly recurring
    monthly_mortgage = monthly_mortgage_payment(principal, rate, scenario.mortgage_term_years)
    monthly_council_tax = scenario.council_tax / 12
    monthly_maintenance = (price * scenario.maintenance_pct) / 12
    monthly_buildings = scenario.buildings_insurance / 12
    monthly_service_charge = (scenario.service_charge / 12) if scenario.property_type == "F" else 0
    monthly_ground_rent = (scenario.ground_rent / 12) if scenario.property_type == "F" else 0
    monthly_total = (monthly_mortgage + monthly_council_tax + monthly_maintenance
                     + monthly_buildings + monthly_service_charge + monthly_ground_rent)

    # Total outflows over stay period
    total_ongoing = monthly_total * 12 * years

    # Long-term friction: remortgage fees (if plan > fix period)
    remortgage_fee = 1500.0  # typical UK arrangement + legal + valuation
    if scenario.include_long_term_frictions and years > scenario.fix_years:
        num_remortgages = (years - 1) // scenario.fix_years  # how many times you resign
        total_ongoing += num_remortgages * remortgage_fee

    # At sale
    home_value_at_sale = price * (1 + scenario.home_growth) ** years
    remaining = remaining_balance(principal, rate, scenario.mortgage_term_years, years * 12)
    selling_fee = home_value_at_sale * scenario.selling_fee_pct
    equity_at_sale = home_value_at_sale - remaining - selling_fee

    # Investment income on excess starting cash
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
            "moving": moving_buy,
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
            "remortgage_fees_total": num_remortgages * remortgage_fee if scenario.include_long_term_frictions and years > scenario.fix_years else 0,
        },
    }
```

### Total cost of renting

```python
def total_cost_of_renting(scenario: Scenario) -> dict:
    years = scenario.plan_to_stay_years

    # Rent with annual growth
    monthly = scenario.monthly_rent
    total_rent = 0.0
    for year in range(years):
        total_rent += monthly * 12
        monthly *= (1 + scenario.rent_growth)

    # Moves — 1 initial move plus possible re-moves if friction toggle is on
    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    total_moving = scenario.moving_cost * num_moves

    # Renters insurance
    total_renters_ins = scenario.renters_insurance * years

    # Deposit — refundable, so not a net cost (but we display it for transparency)
    deposit_held = (scenario.monthly_rent * 12 / 52) * scenario.deposit_weeks

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
```

### Effective investment rate (ISA-aware)

```python
def _effective_investment_rate(scenario: Scenario) -> float:
    """If ISA-protected, use the raw rate. If not, apply a simple
    20% tax haircut on returns (rough UK basic-rate CGT assumption)."""
    if scenario.isa_tax_free:
        return scenario.investment_return
    return scenario.investment_return * 0.80
```

### Breakeven monthly rent

```python
def compute_breakeven_rent(scenario: Scenario, boe_rates_df) -> float:
    """Find the monthly rent at which total cost of renting equals total cost of buying.

    Uses the same rent growth and opportunity cost model as total_cost_of_renting.
    Solved analytically by inverting the rent accumulator.
    """
    buy_result = total_cost_of_buying(scenario, boe_rates_df)
    target_rent_cost = buy_result["net_cost"]

    # rent_cost = monthly * 12 * sum((1+g)^y for y in 0..years-1) + moving + renters_ins - investment_income
    years = scenario.plan_to_stay_years
    g = scenario.rent_growth
    growth_sum = sum((1 + g) ** y for y in range(years))

    # Everything non-rent
    if scenario.include_long_term_frictions:
        num_moves = max(1, math.ceil(years / scenario.avg_tenancy_years))
    else:
        num_moves = 1
    non_rent = (
        scenario.moving_cost * num_moves
        + scenario.renters_insurance * years
    )
    # We don't know exact investment income because it depends on the deposit held,
    # which depends on the rent we're solving for. Simplification: compute with
    # current monthly_rent as a proxy. For sensible rents this is within 1-2%.
    rent_result = total_cost_of_renting(scenario)
    investment_income_proxy = rent_result["investment_income"]

    target_rent_total = target_rent_cost - non_rent + investment_income_proxy
    if growth_sum <= 0:
        return 0.0
    breakeven_monthly = target_rent_total / (12 * growth_sum)
    return max(0.0, breakeven_monthly)
```

## Inputs layer (`inputs.py`)

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_district_to_borough() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_district_to_borough.csv")


def load_borough_rents() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_borough_rents.csv")


def load_council_tax() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "london_council_tax.csv")


def load_boe_rates() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "boe_mortgage_rates.csv")


def default_home_price(ppd_df, district_to_borough_df, borough, postcode_district,
                       property_type, new_build) -> int:
    """Return the median sale price for the tightest available filter.

    Tries (district × type × new_build) first; falls back to (borough × type)
    if <10 matching rows; falls back to £500,000 if nothing at all.
    """
    recent = ppd_df[ppd_df["date"] >= pd.Timestamp.now() - pd.DateOffset(years=3)]
    if postcode_district:
        subset = recent[
            (recent["postcode_district"] == postcode_district)
            & (recent["property_type"] == property_type)
            & (recent["new_build"] == ("Y" if new_build else "N"))
        ]
        if len(subset) >= 10:
            return int(subset["price"].median())
    # Fall back to borough via district_to_borough mapping
    borough_districts = district_to_borough_df[
        district_to_borough_df["borough"] == borough
    ]["postcode_district"].tolist()
    subset = recent[
        (recent["postcode_district"].isin(borough_districts))
        & (recent["property_type"] == property_type)
    ]
    if len(subset) > 0:
        return int(subset["price"].median())
    return 500_000


def default_monthly_rent(rents_df, borough) -> int:
    row = rents_df[rents_df["borough"] == borough]
    return int(row["median_monthly_rent"].iloc[0]) if len(row) else 2_000


def default_council_tax(council_tax_df, borough, band: str = "D") -> float:
    row = council_tax_df[council_tax_df["borough"] == borough]
    col = f"band_{band.lower()}"
    return float(row[col].iloc[0]) if len(row) else 1_900.0


def lookup_boe_rate(boe_df, ltv: float, fix_years: int) -> float:
    """Return the quoted rate (as a decimal) for this LTV and fix length."""
    subset = boe_df[boe_df["fix_years"] == fix_years].sort_values("ltv_bracket")
    for _, row in subset.iterrows():
        if ltv <= row["ltv_bracket"]:
            return row["rate_pct"] / 100.0
    return subset.iloc[-1]["rate_pct"] / 100.0
```

## Scenario layer (`scenario.py`)

```python
def run_scenario(scenario: Scenario, boe_rates_df) -> Result:
    buy = total_cost_of_buying(scenario, boe_rates_df)
    rent = total_cost_of_renting(scenario)
    breakeven = compute_breakeven_rent(scenario, boe_rates_df)

    required_upfront = buy["upfront"]
    shortfall = max(0.0, required_upfront - scenario.starting_cash)
    feasible = shortfall == 0

    if scenario.monthly_rent < breakeven:
        verdict = "rent_wins"
    else:
        verdict = "buy_wins"

    # Year-by-year cumulative cost for the chart
    yearly_buy_cost = _yearly_cumulative_buy(scenario, buy, boe_rates_df)
    yearly_rent_cost = _yearly_cumulative_rent(scenario, rent)

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
        yearly_buy_cost=yearly_buy_cost,
        yearly_rent_cost=yearly_rent_cost,
        buy_breakdown=buy["breakdown"],
        rent_breakdown=rent,
    )
```

## Page layout (`16_Rent_vs_Buy.py`)

```
┌─────────────────────────────────────────────────────────────┐
│ # Rent vs Buy — London                                      │
│                                                             │
│ Should you rent or buy a London home? This calculator      │
│ estimates the total cost of both over a time horizon you   │
│ choose. Buying = mortgage + stamp duty + fees +            │
│ maintenance, minus the equity you walk away with at sale.  │
│ Renting = rent with annual growth, minus the investment    │
│ return on the money you didn't spend on a deposit.         │
│                                                             │
│ Inspired by the [NYT rent vs buy calculator]               │
│ (https://...), adapted for the London market — UK mortgage │
│ structure, stamp duty, council tax, LTV-tiered rates from  │
│ the Bank of England, and real price/rent data from HM      │
│ Land Registry and ONS.                                     │
├─────────────────────────────────────────────────────────────┤
│ Location & basics                                           │
│ ┌─────────────────┬──────────────────┬────────────────────┐│
│ │ Borough         │ Postcode district│ Property type      ││
│ │ [Camden ▼]      │ [NW1 ▼] (opt)    │ ( Flat ● )         ││
│ │                 │                  │ ( Terraced )       ││
│ │                 │                  │ ( Semi )           ││
│ │                 │                  │ ( Detached )       ││
│ └─────────────────┴──────────────────┴────────────────────┘│
│ New build: ( Yes ) ( No ● )                                │
│ First-time buyer: [✓] (affects SDLT)                       │
│ Plan to stay: [======●========] 7 years                    │
│ Starting cash: £ [ 150,000 ]                               │
├─────────────────────────────────────────────────────────────┤
│  ┌──── BUYING ────┐   ┌──── RENTING ────┐                  │
│  │ Price £650,000 │   │ Rent  £2,450 /m │                  │
│  │ Deposit  15%   │   │ Growth  3.0%    │                  │
│  │ LTV     85.0%  │   │ Deposit 5 weeks │                  │
│  │ Rate    5.25%  │   │                 │                  │
│  │ [✓] Auto-tier  │   │                 │                  │
│  │ Fix    5 years │   │                 │                  │
│  │ Term   25 years│   │                 │                  │
│  │                │   │                 │                  │
│  │ ▸ Advanced     │   │ ▸ Advanced      │                  │
│  └────────────────┘   └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│ Advanced assumptions (shared)                              │
│ Investment return:  5.0% / year                            │
│ [✓] Assume ISA-protected returns (no CGT)                 │
│ Inflation:          2.5% / year                            │
│ [✓] Include long-term frictions                           │
│     (multiple renter moves + buyer remortgage fees)        │
├─────────────────────────────────────────────────────────────┤
│ [if feasible == False]                                     │
│  ⚠ You'd need roughly £X,XXX more to afford the upfront    │
│    cost of buying. The numbers below assume you find it.   │
│                                                             │
│ 🏠  Over 7 years, renting wins if the monthly rent is      │
│     below  £2,180  /month.                                 │
│     Your entered rent is £2,450 — buying is cheaper by     │
│     about £22,800 over 7 years.                            │
│                                                             │
│ [Plotly chart: cumulative cost over time, both lines]      │
│                                                             │
│ ▸ Buying breakdown  (collapsed)                            │
│ ▸ Renting breakdown  (collapsed)                           │
│ ▸ Assumptions used  (collapsed)                            │
│                                                             │
│ Rate suggestion based on BoE G1.4 snapshot from 2026-03.   │
│ Results shown in nominal future pounds (rent and home      │
│ value grow at their respective rates). Not financial       │
│ advice.                                                    │
│                                                             │
│ Tech: Python · pandas · Plotly · Streamlit · HM Land       │
│ Registry · ONS · Bank of England                           │
└─────────────────────────────────────────────────────────────┘
```

### UI behaviors

- **Live recalculation on every input change.** No Run button. Pure math computation <100ms.
- **Borough change** triggers: new default rent (from ONS), new default council tax, new default home price.
- **Property type change** triggers: new default home price (filtered), new default maintenance %, shows/hides service charge + ground rent + lease length inputs (flats only).
- **New-build toggle** triggers: new default home price (filtered).
- **First-time buyer toggle** triggers: SDLT recalculation with FTB bands.
- **Deposit % slider / Starting cash input** triggers: new LTV, new suggested rate (if `auto_tier_rate` is on).
- **`auto_tier_rate` checkbox** toggles whether the mortgage rate field follows the LTV tier or uses the manual value.
- **Every default** shows a tooltip explaining where it came from and when it was sourced.
- **Manual overrides** — user-edited fields are "stickier" than defaults. Changing the borough doesn't clobber an explicitly edited price (implemented via Streamlit session state tracking which fields have been edited vs which are at their default).

### Conditional display

- Service charge + ground rent + lease years — only shown when `property_type == "F"`
- Lease years warning — only if `lease_years_remaining < 85`
- Interest-rate reset caveat — only if `fix_years < plan_to_stay_years`
- Feasibility banner — only if `shortfall > 0`
- New-build depreciation caveat — only if `new_build == True`

## Testing

### `test_rentbuy_finance.py`

**SDLT** (parametrized against HMRC published table):

```python
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


SDLT_FTB = [
    (   400_000,      0),    # within FTB nil-rate band
    (   425_000,      0),    # at FTB threshold
    (   500_000,   3_750),   # £75k * 5%
    (   625_000,  10_000),   # FTB upper threshold
    (   700_000,  25_000),   # above £625k — reverts to standard bands
]

@pytest.mark.parametrize("price,expected", SDLT_FTB)
def test_sdlt_first_time_buyer(price, expected):
    assert calculate_sdlt(price, first_time_buyer=True) == pytest.approx(expected, abs=1)
```

**Mortgage amortization:**

```python
def test_mortgage_payment_standard_case():
    # £500k loan at 5% for 25 years → monthly payment ≈ £2,923
    payment = monthly_mortgage_payment(500_000, 0.05, 25)
    assert 2_920 < payment < 2_930

def test_mortgage_zero_interest():
    # £240k / 240 months = £1,000
    payment = monthly_mortgage_payment(240_000, 0.0, 20)
    assert abs(payment - 1_000) < 0.01

def test_remaining_balance_partial_term():
    # After 120 months on a 25y loan at 5% from £500k
    remaining = remaining_balance(500_000, 0.05, 25, 120)
    assert 380_000 < remaining < 410_000

def test_remaining_balance_at_end():
    # Exactly at end of term, balance is zero
    assert remaining_balance(500_000, 0.05, 25, 300) < 1.0
```

**LTV tiering:**

```python
@pytest.fixture
def boe_rates_fixture():
    return pd.DataFrame([
        {"fix_years": 5, "ltv_bracket": 0.60, "rate_pct": 4.50, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.75, "rate_pct": 5.00, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.85, "rate_pct": 5.25, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.90, "rate_pct": 5.50, "snapshot_date": "2026-03"},
        {"fix_years": 5, "ltv_bracket": 0.95, "rate_pct": 6.00, "snapshot_date": "2026-03"},
    ])

def test_ltv_tiering_at_boundary(boe_rates_fixture):
    assert suggest_rate_for_ltv(0.60, 5, boe_rates_fixture) == 0.045
    assert suggest_rate_for_ltv(0.75, 5, boe_rates_fixture) == 0.050
    assert suggest_rate_for_ltv(0.95, 5, boe_rates_fixture) == 0.060

def test_ltv_tiering_above_boundary_bumps_to_next(boe_rates_fixture):
    # 0.7501 should use the 85% bracket, not the 75% one
    assert suggest_rate_for_ltv(0.7501, 5, boe_rates_fixture) == 0.0525

def test_ltv_tiering_above_all_brackets(boe_rates_fixture):
    # 0.99 LTV is above the highest bracket — use the highest
    assert suggest_rate_for_ltv(0.99, 5, boe_rates_fixture) == 0.060
```

**Total cost & feasibility:**

```python
def test_feasibility_shortfall(boe_rates_fixture):
    scenario = make_scenario(home_price=650_000, deposit_pct=0.15,
                              starting_cash=50_000)
    result = run_scenario(scenario, boe_rates_fixture)
    assert result.shortfall > 0
    assert result.feasible is False

def test_feasibility_cash_rich(boe_rates_fixture):
    scenario = make_scenario(home_price=650_000, deposit_pct=0.15,
                              starting_cash=500_000)
    result = run_scenario(scenario, boe_rates_fixture)
    assert result.shortfall == 0
    assert result.feasible is True

def test_cash_rich_buyer_gets_investment_return_on_excess(boe_rates_fixture):
    lean = make_scenario(starting_cash=130_000)
    rich = make_scenario(starting_cash=500_000)
    assert (run_scenario(rich, boe_rates_fixture).buy_investment_income
            > run_scenario(lean, boe_rates_fixture).buy_investment_income)

def test_larger_deposit_reduces_total_cost(boe_rates_fixture):
    """Bigger deposit → lower LTV → better rate → lower total cost."""
    small = make_scenario(deposit_pct=0.10, auto_tier_rate=True)
    big   = make_scenario(deposit_pct=0.40, auto_tier_rate=True)
    assert (run_scenario(big, boe_rates_fixture).buy_net_cost
            < run_scenario(small, boe_rates_fixture).buy_net_cost)

def test_house_has_no_service_charge(boe_rates_fixture):
    with_sc = make_scenario(property_type="T", service_charge=5_000)
    no_sc   = make_scenario(property_type="T", service_charge=0)
    assert (run_scenario(with_sc, boe_rates_fixture).buy_net_cost
            == run_scenario(no_sc, boe_rates_fixture).buy_net_cost)

def test_flat_applies_service_charge(boe_rates_fixture):
    with_sc = make_scenario(property_type="F", service_charge=5_000)
    no_sc   = make_scenario(property_type="F", service_charge=0)
    assert (run_scenario(with_sc, boe_rates_fixture).buy_net_cost
            > run_scenario(no_sc, boe_rates_fixture).buy_net_cost)

def test_breakeven_rent_positive_for_reasonable_inputs(boe_rates_fixture):
    scenario = make_scenario(home_price=650_000, plan_to_stay_years=7)
    breakeven = run_scenario(scenario, boe_rates_fixture).breakeven_monthly_rent
    assert 1_000 < breakeven < 5_000

def test_breakeven_increases_with_longer_stay(boe_rates_fixture):
    short = run_scenario(make_scenario(plan_to_stay_years=3), boe_rates_fixture)
    long  = run_scenario(make_scenario(plan_to_stay_years=20), boe_rates_fixture)
    assert long.breakeven_monthly_rent > short.breakeven_monthly_rent

def test_long_term_frictions_toggle_changes_cost(boe_rates_fixture):
    with_f = make_scenario(plan_to_stay_years=15, include_long_term_frictions=True)
    no_f   = make_scenario(plan_to_stay_years=15, include_long_term_frictions=False)
    assert (run_scenario(with_f, boe_rates_fixture).rent_net_cost
            > run_scenario(no_f, boe_rates_fixture).rent_net_cost)
    assert (run_scenario(with_f, boe_rates_fixture).buy_net_cost
            > run_scenario(no_f, boe_rates_fixture).buy_net_cost)
```

### `test_rentbuy_scenario.py`

```python
def test_run_scenario_returns_complete_result(boe_rates_fixture):
    scenario = make_scenario(home_price=650_000, monthly_rent=2_450, plan_to_stay_years=7)
    result = run_scenario(scenario, boe_rates_fixture)
    assert result.buy_net_cost > 0
    assert result.rent_net_cost > 0
    assert result.breakeven_monthly_rent > 0
    assert result.verdict in ("buy_wins", "rent_wins")
    assert len(result.yearly_buy_cost) == 7
    assert len(result.yearly_rent_cost) == 7
```

### `test_rentbuy_inputs.py`

```python
def test_default_home_price_uses_postcode_district():
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = pd.read_csv("data/london_district_to_borough.csv")
    price = default_home_price(ppd, dtb, "Camden", "NW1", "F", False)
    assert 400_000 < price < 2_500_000

def test_default_home_price_falls_back_to_borough():
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = pd.read_csv("data/london_district_to_borough.csv")
    # Obscure district not in dataset — should fall back to borough median
    price = default_home_price(ppd, dtb, "Camden", "ZZ99", "F", False)
    assert 400_000 < price < 2_500_000

def test_default_monthly_rent_known_borough():
    rents = pd.read_csv("data/london_borough_rents.csv")
    rent = default_monthly_rent(rents, "Camden")
    assert 1_500 < rent < 4_000

def test_default_council_tax_known_borough():
    taxes = pd.read_csv("data/london_council_tax.csv")
    tax = default_council_tax(taxes, "Camden", band="D")
    assert 1_200 < tax < 3_000

def test_boe_rates_csv_schema():
    df = pd.read_csv("data/boe_mortgage_rates.csv")
    assert {"fix_years", "ltv_bracket", "rate_pct", "snapshot_date"}.issubset(df.columns)
    assert len(df) > 0
```

### `test_rentbuy_charts.py`

```python
def test_build_cost_over_time_chart(boe_rates_fixture):
    scenario = make_scenario()
    result = run_scenario(scenario, boe_rates_fixture)
    fig = build_cost_over_time_chart(result)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2   # buy line + rent line
```

### Totals

- `test_rentbuy_finance.py` — ~27 tests (8 SDLT standard + 5 SDLT FTB + 4 amortization + 4 LTV + 10 total/breakeven/friction)
- `test_rentbuy_scenario.py` — 1 test
- `test_rentbuy_inputs.py` — 5 tests
- `test_rentbuy_charts.py` — 1 test

**~34 new tests total.** All synchronous, all run in under 2 seconds.

## Data source bundling

### `london_district_to_borough.csv`

~300 rows, columns: `postcode_district, borough`. Hand-built from gov.uk's postcode district → local authority mapping. Covers every postcode district that appears in `london_ppd.parquet`.

### `london_borough_rents.csv`

33 rows (32 London boroughs + City of London), columns:
```
borough, median_monthly_rent, source_year, source_url
```
Source: ONS "Private Rental Market Statistics: Monthly prices by region and administrative area" — most recent 12-month period. Updated once a year.

### `london_council_tax.csv`

33 rows, columns:
```
borough, band_a, band_b, band_c, band_d, band_e, band_f, band_g, band_h, year
```
Source: each borough's 2024/25 council tax leaflet (aggregated from gov.uk council listings). Updated annually.

### `boe_mortgage_rates.csv`

Snapshot of BoE G1.4 series, ~20 rows, columns:
```
fix_years, ltv_bracket, rate_pct, snapshot_date
```
Where `fix_years ∈ {2, 3, 5, 10}` and `ltv_bracket ∈ {0.60, 0.75, 0.85, 0.90, 0.95}`. Refreshed by running `scripts/refresh_boe_rates.py` (not part of page load).

### `scripts/refresh_boe_rates.py`

One-time dev script. Fetches each BoE series via the IADB CSV URL, parses, writes the aggregated CSV. Not imported anywhere, not tested beyond a manual run.

## Blog post

**Path:** `docs/_quant_lab/mini/rent-vs-buy.html` in the **FinBytes** Jekyll repo (separate from QuantLab).

**Length:** ~2500 words, long deep-dive, first-person.

**Structure:**

1. **Lede** (~150 words) — "Should I rent or buy in London?" is the question everyone asks. Hard to answer cleanly because the honest answer depends on ~20 variables. NYT built a good US calculator in 2014, updated 2024. I adapted it for London because the US formula doesn't work here.

2. **Why the NYT formula needed adapting** (~250 words) — Five biggest differences: SDLT is tiered not percentage; UK mortgages are short-fix not 30-year-fixed; no mortgage interest tax deduction; council tax is a flat £ not a %; freehold vs leasehold completely changes the math.

3. **The core math** (~600 words) — Walk through the mortgage payment formula, the SDLT bracket logic (with code), total cost of buying as a sum, total cost of renting as a growth sum, opportunity cost on the deposit, and the breakeven rent derivation.

4. **London-specific quirks** (~400 words) — Leasehold flats (service charge, ground rent, lease depreciation). New build premium and the 5-year erosion. Council tax bands. Buildings vs contents insurance. SDLT first-time buyer relief. LTV tiering on mortgage rates — this is underappreciated and worth a dedicated paragraph.

5. **Data sources** (~400 words) — HM Land Registry (28M rows, free, OGL). ONS rent statistics. Council tax aggregation. **Bank of England G1.4 quoted household rates**, including the series codes I use and how to refresh them. Why I bundle rather than fetch live.

6. **What this calculator gets right / wrong** (~400 words) — Right: real data, London-specific, transparent math. Wrong/simplified: deterministic single trajectory (no Monte Carlo); borough-level rent is coarse; ignores mortgage affordability stress test; assumes you remortgage at today's rate; ignores Section 21 eviction risk; ignores shared ownership; interest-only mortgages not modeled; LISA/Help to Buy boosts not modeled; emotional factors (peace of mind, paint the walls) not modeled.

7. **Try it** (~100 words) — Link to the Streamlit app. Screenshot. "Play with the plan-to-stay slider — it's the single biggest lever."

8. **Closing** (~100 words) — What I learned. Next steps: borough heatmap of breakeven rent, historical comparison, shared ownership as a third path.

**Jekyll frontmatter:**
```yaml
---
layout: quant-lab-mini
title: "Rent vs Buy — London: A Data-Driven Calculator"
date: 2026-04-14
tags: [finance, london, property, calculator, streamlit, python, mortgages]
section: quant-lab
permalink: /quant-lab/rent-vs-buy/
---
```

**Companion entry on the QuantLab landing page** (`docs/_tabs/quant-lab.md`):

```html
<li>
  <a href="{{ "/quant-lab/rent-vs-buy/" | relative_url }}">Rent vs Buy London</a>
  <span class="ql-badges"><span class="ql-badge ql-badge-mini">Mini Project</span><span class="ql-badge ql-badge-calc">Calculator</span></span>
  <span class="ql-desc">Should you rent or buy a London home? Data-driven calculator using HM Land Registry prices, ONS rents, and Bank of England mortgage rates.</span>
  <span class="ql-tech">Python · Streamlit · pandas · Plotly · HM Land Registry · ONS · Bank of England</span>
</li>
```

## Error handling

| Failure | Behavior |
|---|---|
| Missing borough in rents CSV | Default rent falls back to £2,000/month with an italic caption noting "no ONS data for this borough" |
| Missing borough in council tax CSV | Default council tax falls back to £1,900/year with the same caption pattern |
| Postcode district with <10 recent sales | Falls back to borough-wide median price with a caption |
| All defaults missing | Uses hardcoded sensible defaults and shows a yellow warning banner |
| LTV above the highest BoE bracket (>95%) | Uses the 95% bracket rate + a caption "illustrative only, above normal lending LTV" |
| `deposit_pct < 0.05` or `> 1.0` | Capped at [0.05, 1.0] — the UI slider enforces this |
| `home_price <= 0` | UI field prevents this via Streamlit number_input min_value |
| `mortgage_term_years <= 0` | UI field prevents |
| `plan_to_stay_years <= 0` | UI slider min is 1 |
| ISA toggle at unreasonable cash | No limit — the calculator doesn't enforce the £20k/year ISA cap because it's a conservative simplification (we just apply a 20% CGT haircut if the toggle is off) |
| Lease length < 85 years (flats) | Yellow caption warning about mortgage availability and extension costs |
| Fix length < plan to stay | Italic caption below mortgage-rate field explaining the approximation |

No uncaught exceptions propagate to Streamlit's crash page. Every lookup has a fallback.

## Resource budget

- Page load: ~100ms (CSV reads cached via `@st.cache_data`)
- Per-interaction recalculation: <50ms (pure Python math, no I/O)
- No external API calls at runtime
- Memory: parquet is ~5MB, CSVs are <10KB combined
- Streamlit Cloud impact: trivial

## Open questions

None. All design decisions locked.

## Next step

Invoke `superpowers:writing-plans` to break this spec into an implementation plan with TDD-structured tasks.
