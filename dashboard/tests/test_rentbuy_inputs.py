"""Tests for the rentbuy inputs layer (data file loaders + defaults)."""

import pandas as pd
import pytest

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


def test_load_district_to_borough_schema():
    df = load_district_to_borough()
    assert {"postcode_district", "borough"}.issubset(df.columns)
    assert len(df) > 30


def test_load_borough_rents_schema():
    df = load_borough_rents()
    assert {"borough", "median_monthly_rent", "source_year", "source_url"}.issubset(df.columns)
    assert len(df) > 30


def test_load_borough_rents_by_bedroom_schema():
    from lib.rentbuy.inputs import load_borough_rents_by_bedroom
    df = load_borough_rents_by_bedroom()
    assert {
        "borough", "beds_studio", "beds_1", "beds_2", "beds_3", "beds_4plus",
        "source_year", "source_url",
    }.issubset(df.columns)
    assert len(df) == 33


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


def test_default_home_price_with_bedrooms_filters():
    """A 4+ bed home should default to a higher price than a 1-bed in
    the same borough + property type."""
    from pathlib import Path
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


def test_default_home_price_falls_back_when_borough_missing():
    """When the borough is unknown the function should fall through to
    the hardcoded £500k."""
    from pathlib import Path
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
    assert price == 500_000


def test_default_home_price_without_bedrooms_uses_legacy_chain():
    """Calling default_home_price without bedrooms should still work
    using the existing logic (backwards compatible)."""
    from pathlib import Path
    import pandas as pd
    ppd = pd.read_parquet(
        Path(__file__).resolve().parent.parent / "data" / "london_ppd_with_bedrooms.parquet"
    )
    d2b = load_district_to_borough()
    price = default_home_price(
        ppd, d2b, borough="Camden", postcode_district=None,
        property_type="F", new_build=False,
    )
    assert 200_000 < price < 5_000_000
