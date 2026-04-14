"""Correctness tests for all Big O demo algorithm variants."""

import pytest

from lib.bigo.algorithms import (
    fib_naive,
    fib_iterative,
    fib_memoized,
    fib_matrix,
    pair_brute,
    pair_sorted,
    pair_hash,
)


KNOWN_FIB = {
    0: 0,
    1: 1,
    2: 1,
    5: 5,
    10: 55,
    20: 6765,
    25: 75025,
}

FIB_VARIANTS = [fib_naive, fib_iterative, fib_memoized, fib_matrix]


@pytest.mark.parametrize("n,expected", list(KNOWN_FIB.items()))
@pytest.mark.parametrize("variant", FIB_VARIANTS)
def test_fib_variant_correct(variant, n, expected):
    assert variant(n) == expected


PAIR_CASES = [
    ([1, 2, 3, 4], 5, True),
    ([1, 2, 3, 4], 8, False),
    ([], 5, False),
    ([5], 5, False),
    ([3, 3], 6, True),
    ([1, 2, 3, 4, 5], 9, True),
    ([10, 20, 30], 15, False),
]

PAIR_VARIANTS = [pair_brute, pair_sorted, pair_hash]


@pytest.mark.parametrize("arr,target,expected", PAIR_CASES)
@pytest.mark.parametrize("variant", PAIR_VARIANTS)
def test_pair_variant_correct(variant, arr, target, expected):
    assert variant(arr, target) is expected
