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
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = load_district_to_borough()
    price = default_home_price(ppd, dtb, borough="Camden",
                                postcode_district="NW1",
                                property_type="F", new_build=False)
    assert 300_000 < price < 3_000_000


def test_default_home_price_falls_back_to_london_median():
    """Unknown borough + unknown district → returns fallback."""
    ppd = pd.read_parquet("data/london_ppd.parquet")
    dtb = load_district_to_borough()
    price = default_home_price(ppd, dtb, borough="ZZZ",
                                postcode_district=None,
                                property_type="F", new_build=False)
    assert price > 0
