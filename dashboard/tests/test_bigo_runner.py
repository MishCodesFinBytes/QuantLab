"""Tests for the Big O benchmark runner."""

import time

import pytest

from lib.bigo.runner import run_problem, ProblemResult, VariantResult, NPoint
from lib.bigo.problems import PROBLEMS, Problem, AlgorithmVariant


def test_run_problem_returns_expected_structure():
    result = run_problem(PROBLEMS["fibonacci"])
    assert isinstance(result, ProblemResult)
    assert result.problem is PROBLEMS["fibonacci"]
    assert len(result.variant_results) == 4
    for vr in result.variant_results:
        assert isinstance(vr, VariantResult)
        assert len(vr.points) == len(PROBLEMS["fibonacci"].n_values)
        for p in vr.points:
            assert isinstance(p, NPoint)
            assert isinstance(p.n, int)
            assert p.wall_ms >= 0.0 or p.skipped or p.error


def test_run_problem_skips_past_budget():
    """A variant that takes >budget_ms on its first n should skip the rest."""
    def slow_variant(n):
        time.sleep(0.05)
        return 0

    fake = Problem(
        key="slow",
        label="Slow",
        description="",
        explainer="",
        n_values=[1, 2, 3],
        input_factory=lambda n: (n,),
        variants=[AlgorithmVariant("slow_v", "Slow variant", "O(?)", slow_variant)],
    )
    # 30 ms budget → first point (~50ms) exceeds, rest skipped
    result = run_problem(fake, budget_ms=30.0)
    points = result.variant_results[0].points
    assert points[0].wall_ms >= 40.0
    assert points[1].skipped is True
    assert points[2].skipped is True


def test_run_problem_correctness_check():
    result = run_problem(PROBLEMS["fibonacci"])
    # At n=10 every variant should produce the same F(10) = 55
    for vr in result.variant_results:
        point = next(p for p in vr.points if p.n == 10)
        assert point.error is None
        key = (vr.variant.key, 10)
        assert result.correctness.get(key, True) is True


def test_run_problem_captures_exception():
    def broken(n):
        raise ValueError("intentional")

    def ok(n):
        return n * 2

    fake = Problem(
        key="mixed",
        label="Mixed",
        description="",
        explainer="",
        n_values=[1, 2],
        input_factory=lambda n: (n,),
        variants=[
            AlgorithmVariant("broken_v", "Broken", "O(?)", broken),
            AlgorithmVariant("ok_v",     "OK",     "O(?)", ok),
        ],
    )
    result = run_problem(fake)
    broken_points = result.variant_results[0].points
    ok_points = result.variant_results[1].points
    assert all("intentional" in (p.error or "") for p in broken_points)
    assert all(p.error is None for p in ok_points)
