"""Pure algorithm implementations for the Big O demo.

Each function is side-effect-free. The runner owns timing; these
functions never call time.perf_counter().

Conventions:
- Fibonacci variants take an int n and return int F(n).
- Pair-sum variants take (list[int], target) and return bool.
"""

from __future__ import annotations

import functools
import sys


# Allow the naive recursive Fibonacci to reach n ~= 40 without hitting
# Python's default recursion limit of 1000 too early on the memoized
# variant (which has the same depth pattern).
if sys.getrecursionlimit() < 2000:
    sys.setrecursionlimit(2000)


# ─────────────────────────────────────────────────────────────
# Fibonacci variants
# ─────────────────────────────────────────────────────────────

def fib_naive(n: int) -> int:
    """Textbook recursive Fibonacci. O(2^n) time."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_iterative(n: int) -> int:
    """Single-loop Fibonacci. O(n) time, O(1) space."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def fib_memoized(n: int) -> int:
    """Recursive Fibonacci with memoization. O(n) time and space.

    A fresh cache is used per call so measurements at different n are
    independent (no warm-cache shortcut from a prior run).
    """

    @functools.lru_cache(maxsize=None)
    def _inner(k: int) -> int:
        if k < 2:
            return k
        return _inner(k - 1) + _inner(k - 2)

    try:
        return _inner(n)
    finally:
        _inner.cache_clear()


def fib_matrix(n: int) -> int:
    """Fibonacci via matrix exponentiation. O(log n) time.

    Uses the identity:
        | 1 1 |^n   | F(n+1) F(n)   |
        | 1 0 |   = | F(n)   F(n-1) |
    """
    if n < 2:
        return n

    def mat_mul(a, b):
        return (
            (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3]),
            (a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3]),
        )

    def mat_pow(m, p):
        result = (1, 0, 0, 1)  # identity
        base = m
        while p:
            if p & 1:
                r = mat_mul(result, base)
                result = (r[0][0], r[0][1], r[1][0], r[1][1])
            b = mat_mul(base, base)
            base = (b[0][0], b[0][1], b[1][0], b[1][1])
            p >>= 1
        return result

    powered = mat_pow((1, 1, 1, 0), n)
    return powered[1]  # top-right element is F(n)


# ─────────────────────────────────────────────────────────────
# Pair-sum variants
# ─────────────────────────────────────────────────────────────

def pair_brute(arr: list, target: int) -> bool:
    """Check every pair. O(n^2) time, O(1) space."""
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] + arr[j] == target:
                return True
    return False


def pair_sorted(arr: list, target: int) -> bool:
    """Sort then two-pointer. O(n log n) time, O(n) or O(1) space."""
    if len(arr) < 2:
        return False
    s = sorted(arr)
    left, right = 0, len(s) - 1
    while left < right:
        total = s[left] + s[right]
        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1
    return False


def pair_hash(arr: list, target: int) -> bool:
    """Single pass with a hash set. O(n) time, O(n) space."""
    seen = set()
    for x in arr:
        if (target - x) in seen:
            return True
        seen.add(x)
    return False
