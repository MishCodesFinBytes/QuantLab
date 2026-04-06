"""Redis cache layer for bond pricing engine.

Cache-aside pattern
-------------------
1. Check cache first.
2. On miss, compute the result from the source (DB, API, calculation).
3. Store result in cache with a TTL.
4. Return result.

The caller owns the compute step — this module only handles 1, 3, and 4.

TTL strategy
------------
Different data types have different staleness tolerances:

  - Par/spot/forward/fitted curves: 24 h (source data updates daily).
  - Bond pricing: 5 min (depends on intraday market inputs).
  - Monte Carlo VaR: 1 h (expensive, inputs shift slowly).

Graceful degradation
--------------------
If Redis is unavailable (network blip, ElastiCache maintenance window),
every cache operation returns None or succeeds silently. The application
continues to function — just slower, because every request computes
fresh. This is the right trade-off for a caching layer: availability of
the app should never depend on the cache.
"""

from __future__ import annotations

import json

import redis


class CurveCache:
    """Cache layer for yield curves and pricing results."""

    DEFAULT_TTLS = {
        "par": 86400,       # 24 hours
        "spot": 86400,
        "forward": 86400,
        "fitted": 86400,
        "pricing": 300,     # 5 minutes
        "var": 3600,        # 1 hour
    }

    def __init__(self, redis_client: redis.Redis):
        self._r = redis_client

    def _safe(self, fn, default=None):
        """Execute a Redis operation; return *default* on any error."""
        try:
            return fn()
        except (redis.ConnectionError, redis.TimeoutError, Exception):
            return default

    # ---- curves ----

    def set_curve(self, curve_type: str, date_str: str, data: dict, ttl: int | None = None):
        """Cache a curve (par, spot, forward, fitted)."""
        key = f"curve:{curve_type}:{date_str}"
        ttl = ttl or self.DEFAULT_TTLS.get(curve_type, 3600)
        self._safe(lambda: self._r.setex(key, ttl, json.dumps(data)))

    def get_curve(self, curve_type: str, date_str: str) -> dict | None:
        """Retrieve a cached curve. Returns None on miss or error."""
        key = f"curve:{curve_type}:{date_str}"
        result = self._safe(lambda: self._r.get(key))
        return json.loads(result) if result else None

    def invalidate_curve(self, curve_type: str, date_str: str):
        """Remove a specific curve from cache."""
        key = f"curve:{curve_type}:{date_str}"
        self._safe(lambda: self._r.delete(key))

    def invalidate_date(self, date_str: str):
        """Remove all curve types for a given date."""
        for curve_type in ("par", "spot", "forward", "fitted"):
            self.invalidate_curve(curve_type, date_str)

    # ---- pricing ----

    def set_pricing(self, bond_id: str, date_str: str, result: dict, ttl: int | None = None):
        """Cache a bond pricing result."""
        key = f"pricing:{bond_id}:{date_str}"
        ttl = ttl or self.DEFAULT_TTLS["pricing"]
        self._safe(lambda: self._r.setex(key, ttl, json.dumps(result)))

    def get_pricing(self, bond_id: str, date_str: str) -> dict | None:
        """Retrieve a cached pricing result."""
        key = f"pricing:{bond_id}:{date_str}"
        result = self._safe(lambda: self._r.get(key))
        return json.loads(result) if result else None
