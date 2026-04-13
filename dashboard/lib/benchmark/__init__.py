"""Benchmark Lab package — pandas vs polars timing suite.

Public API:
- run_benchmark(path, ...) -> list[OpResult]
- get_available_presets() -> dict[str, dict]
- build_overview_chart(results) -> plotly.graph_objects.Figure
- build_op_card(result) -> dict
- OpResult, EngineResult (dataclasses)
"""

from .runner import run_benchmark, OpResult, EngineResult
from .datasets import get_available_presets, PRESETS
from .report import build_overview_chart, build_op_card

__all__ = [
    "run_benchmark",
    "OpResult",
    "EngineResult",
    "get_available_presets",
    "PRESETS",
    "build_overview_chart",
    "build_op_card",
]
