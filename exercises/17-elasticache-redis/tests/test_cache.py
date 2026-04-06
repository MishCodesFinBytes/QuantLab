import pytest
import fakeredis

from cache import CurveCache


@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def cache(redis_client):
    return CurveCache(redis_client)


class TestCurveCache:
    def test_set_and_get(self, cache):
        data = {"1Y": 4.0, "2Y": 4.5, "10Y": 5.0}
        cache.set_curve("par", "2026-04-04", data)
        result = cache.get_curve("par", "2026-04-04")
        assert result == data

    def test_miss_returns_none(self, cache):
        result = cache.get_curve("par", "2099-01-01")
        assert result is None

    def test_ttl_applied(self, redis_client, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0}, ttl=300)
        ttl = redis_client.ttl("curve:par:2026-04-04")
        assert 0 < ttl <= 300

    def test_invalidate(self, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0})
        cache.invalidate_curve("par", "2026-04-04")
        assert cache.get_curve("par", "2026-04-04") is None

    def test_invalidate_all_for_date(self, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0})
        cache.set_curve("spot", "2026-04-04", {"1Y": 4.0})
        cache.set_curve("fitted", "2026-04-04", {"1Y": 4.0})
        cache.invalidate_date("2026-04-04")
        assert cache.get_curve("par", "2026-04-04") is None
        assert cache.get_curve("spot", "2026-04-04") is None

    def test_set_pricing_result(self, cache):
        result = {"clean_price": 98.5, "ytm": 5.2, "duration": 4.5}
        cache.set_pricing("bond-123", "2026-04-04", result)
        assert cache.get_pricing("bond-123", "2026-04-04") == result

    def test_graceful_fallback_on_redis_error(self):
        """If Redis is unavailable, cache operations should not raise."""
        bad_client = fakeredis.FakeRedis(connected=False, decode_responses=True)
        cache = CurveCache(bad_client)
        assert cache.get_curve("par", "2026-04-04") is None
