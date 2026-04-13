"""Tests for the benchmark dataset preset lookup."""

from pathlib import Path

import pytest

from lib.benchmark.datasets import PRESETS, get_available_presets


def test_presets_has_small_and_large_keys():
    assert set(PRESETS.keys()) == {"small", "large"}


def test_preset_entries_have_required_fields():
    for key, entry in PRESETS.items():
        assert "label" in entry
        assert "path" in entry
        assert "description" in entry
        assert isinstance(entry["path"], Path)


def test_get_available_presets_filters_missing_files():
    """Only presets whose file exists on disk should be returned."""
    available = get_available_presets()
    for key, entry in available.items():
        assert entry["path"].exists(), f"{key} preset path does not exist"
    # Small should always be available since london_ppd.parquet is committed
    assert "small" in available
