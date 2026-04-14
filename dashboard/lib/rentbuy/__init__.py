"""Rent vs Buy London calculator package.

Public API (populated after all submodules exist):
- Scenario, Result (dataclasses)
- run_scenario(scenario, boe_rates_df) -> Result
- default_home_price, default_monthly_rent, default_council_tax, lookup_boe_rate
- load_borough_rents, load_council_tax, load_district_to_borough, load_boe_rates
- calculate_sdlt, monthly_mortgage_payment, suggest_rate_for_ltv
- build_cost_over_time_chart
"""
