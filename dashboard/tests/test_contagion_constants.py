"""Unit tests for contagion constants module."""
from datetime import date

from lib.contagion import constants


def test_periods_cover_expected_date_ranges():
    assert constants.PERIODS["2020_us_iran"]["start"] == date(2019, 11, 1)
    assert constants.PERIODS["2020_us_iran"]["end"] == date(2020, 3, 15)
    assert constants.PERIODS["2024_hormuz"]["start"] == date(2024, 1, 1)
    # End is today-ish; just assert after 2026-01-01 so the test is stable.
    assert constants.PERIODS["2024_hormuz"]["end"] >= date(2026, 1, 1)


def test_every_ticker_has_a_role():
    valid_roles = {"epicenter", "contagion", "safe_haven", "energy", "fear"}
    for ticker, role in constants.TICKER_ROLES.items():
        assert role in valid_roles, f"{ticker} has invalid role {role}"


def test_destination_cities_include_all_five():
    expected = {"IN", "TR", "DE", "US", "GB"}
    assert set(constants.DESTINATION_CITIES.keys()) == expected


def test_epicenter_origin_is_strait_of_hormuz():
    lon, lat = constants.EPICENTER_LONLAT
    assert 55 < lon < 57, "Longitude should be ~56 (Strait of Hormuz)"
    assert 25 < lat < 27, "Latitude should be ~26 (Strait of Hormuz)"


def test_every_destination_city_has_a_ticker_in_roles():
    for country, meta in constants.DESTINATION_CITIES.items():
        assert "ticker" in meta, f"{country} missing ticker"
        assert meta["ticker"] in constants.TICKER_ROLES, (
            f"{country} ticker {meta['ticker']} not in TICKER_ROLES"
        )


def test_correlation_window_is_positive_int():
    assert isinstance(constants.CORRELATION_WINDOW, int)
    assert constants.CORRELATION_WINDOW > 0
