"""Rent vs Buy London — data-driven calculator inspired by NYT."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import pandas as pd
import streamlit as st
from tech_footer import render_tech_footer
from nav import render_sidebar
from page_header import render_page_header
from rentbuy import (
    Scenario,
    run_scenario,
    load_district_to_borough,
    load_borough_rents,
    load_borough_rents_by_bedroom,
    load_council_tax,
    load_boe_rates,
    default_home_price,
    default_monthly_rent,
    default_council_tax,
    lookup_boe_rate,
    build_cost_over_time_chart,
)
from rentbuy.finance import SDLT_RULES_AS_OF, SDLT_SOURCE_URL

st.set_page_config(page_title="Rent vs Buy London", page_icon="assets/logo.png", layout="wide")
render_sidebar()
render_page_header("Rent vs Buy — London", "Data-driven calculator using HM Land Registry, ONS, and BoE")

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

with st.expander(f"About the SDLT (Stamp Duty) rules — effective from {SDLT_RULES_AS_OF}"):
    st.markdown(f"""
UK Stamp Duty Land Tax rates **reverted to the pre-September-2022 schedule**
on 1 April 2025, after the temporary higher thresholds expired. This
calculator uses the current post-April-2025 rates.

**Standard residential rates (non-first-time-buyer):**

| Portion of price | Rate |
|---|---|
| Up to £125,000 | 0% |
| £125,001 – £250,000 | 2% |
| £250,001 – £925,000 | 5% |
| £925,001 – £1,500,000 | 10% |
| Above £1,500,000 | 12% |

**First-time buyer relief:**

| Portion of price | Rate |
|---|---|
| Up to £300,000 | 0% |
| £300,001 – £500,000 | 5% |

⚠ First-time buyer relief is **only available on purchases up to £500,000**.
Above £500,000, first-time buyers pay the full standard rates (no relief).

**How SDLT works:** the rate on each band applies *only* to the slice of
the price within that band — a £400k purchase by a non-FTB pays 0% on the
first £125k, 2% on the next £125k, and 5% on the remaining £150k, for a
total of £10,000 (not 5% on the whole £400k).

Source: [{SDLT_SOURCE_URL}]({SDLT_SOURCE_URL})
""")


_PPD_PATH = Path(__file__).resolve().parent.parent / "data" / "london_ppd_with_bedrooms.parquet"


@st.cache_data(show_spinner="Loading London property data...")
def _load_all_data():
    ppd = pd.read_parquet(_PPD_PATH)
    return {
        "ppd": ppd,
        "district_to_borough": load_district_to_borough(),
        "borough_rents": load_borough_rents(),
        "borough_rents_by_bedroom": load_borough_rents_by_bedroom(),
        "council_tax": load_council_tax(),
        "boe_rates": load_boe_rates(),
    }

data = _load_all_data()


st.subheader("Location & basics")

boroughs = sorted(data["borough_rents"]["borough"].tolist())
col_b, col_d, col_t = st.columns([2, 2, 2])

with col_b:
    borough = st.selectbox("Borough", options=boroughs, index=boroughs.index("Camden"))

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

bedrooms_label = st.selectbox(
    "Bedrooms",
    options=["Studio", "1", "2", "3", "4+"],
    index=2,  # 2-bed default
    help="Affects the rent and price defaults.",
)
BEDROOM_MAP = {"Studio": "studio", "1": "1", "2": "2", "3": "3", "4+": "4+"}
bedrooms = BEDROOM_MAP[bedrooms_label]

col_nb, col_ftb, col_stay = st.columns([1, 1, 3])
with col_nb:
    new_build = st.checkbox("New build", value=False)
with col_ftb:
    first_time_buyer = st.checkbox("First-time buyer", value=False,
                                   help="Applies SDLT first-time buyer relief up to £625k")
with col_stay:
    plan_to_stay_years = st.slider("Plan to stay", min_value=1, max_value=30, value=7, step=1)

default_price = default_home_price(
    data["ppd"], data["district_to_borough"],
    borough=borough, postcode_district=postcode_district,
    property_type=property_type, new_build=new_build,
    bedrooms=bedrooms,
)
default_rent = default_monthly_rent(
    data["borough_rents"], data["borough_rents_by_bedroom"],
    borough=borough, bedrooms=bedrooms,
)
default_ctax = default_council_tax(data["council_tax"], borough, band="D")

required_upfront_seed = default_price * 0.15 + default_price * 0.05 + 3_000

starting_cash = st.number_input(
    "Starting cash available (£)",
    min_value=0,
    value=int(required_upfront_seed + 10_000),
    step=5_000,
    help="How much money you have now for deposit + fees.",
)

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
                             help="Uses Bank of England G1.4 data.")

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
        help="Multiple renter moves + buyer remortgage fees. Roughly offset but more honest.",
    )


scenario = Scenario(
    borough=borough,
    postcode_district=postcode_district,
    property_type=property_type,
    new_build=new_build,
    first_time_buyer=first_time_buyer,
    bedrooms=bedrooms,
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


st.divider()

if not result.feasible:
    st.error(
        f"⚠ You'd need roughly **£{result.shortfall:,.0f} more** to afford the upfront cost "
        f"of buying at this price. The numbers below assume you find that shortfall somehow."
    )

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

st.plotly_chart(build_cost_over_time_chart(result), width='stretch')

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

render_tech_footer([
    "Python", "pandas", "Plotly", "Streamlit",
    "HM Land Registry", "ONS", "Bank of England",
])
