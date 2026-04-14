"""Big O benchmark runner: per-variant time-budget skip + correctness."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .problems import Problem, AlgorithmVariant


@dataclass
class NPoint:
    n: int
    wall_ms: float = 0.0
    result_hash: str = ""
    error: str | None = None
    skipped: bool = False


@dataclass
class VariantResult:
    variant: AlgorithmVariant
    points: list = field(default_factory=list)


@dataclass
class ProblemResult:
    problem: Problem
    variant_results: list
    correctness: dict = field(default_factory=dict)


def _hash_result(value: Any) -> str:
    """Deterministic string hash of a variant's return value."""
    if isinstance(value, (int, float, bool)):
        return f"scalar:{value}"
    if isinstance(value, (list, tuple)):
        try:
            return "list:" + str(sorted(value))
        except TypeError:
            return "list:" + str(value)
    return "obj:" + repr(value)


def run_problem(problem: Problem, budget_ms: float = 2000.0) -> ProblemResult:
    """Time every variant at every n in problem.n_values.

    For each variant, walks n_values in ascending order. Single call per
    n (no warmup, no median — noise is acceptable for a teaching demo).
    If a call takes longer than budget_ms, that n is recorded and all
    larger n for that variant are marked skipped.

    Exceptions from a variant are caught per-n and recorded in NPoint.error
    without aborting the run.

    After timing, fills ProblemResult.correctness: for each n, the first
    successful variant's result_hash is the "truth"; subsequent variants
    are compared against it. Mismatch = correctness[(variant_key, n)] = False.
    """
    variant_results: list = []
    # truth[n] = result_hash from the first successful variant at that n
    truth: dict = {}
    correctness: dict = {}

    for variant in problem.variants:
        points: list = []
        exceeded_budget = False
        for n in problem.n_values:
            if exceeded_budget:
                points.append(NPoint(n=n, skipped=True))
                continue
            try:
                args = problem.input_factory(n)
                t0 = time.perf_counter()
                value = variant.fn(*args)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                result_hash = _hash_result(value)
                points.append(NPoint(n=n, wall_ms=wall_ms, result_hash=result_hash))
                # Correctness check vs the truth table
                if n not in truth:
                    truth[n] = result_hash
                    correctness[(variant.key, n)] = True
                else:
                    correctness[(variant.key, n)] = (result_hash == truth[n])
                if wall_ms > budget_ms:
                    exceeded_budget = True
            except Exception as exc:
                msg = f"{type(exc).__name__}: {exc}"
                points.append(NPoint(n=n, error=msg))
                correctness[(variant.key, n)] = False
        variant_results.append(VariantResult(variant=variant, points=points))

    return ProblemResult(
        problem=problem,
        variant_results=variant_results,
        correctness=correctness,
    )
