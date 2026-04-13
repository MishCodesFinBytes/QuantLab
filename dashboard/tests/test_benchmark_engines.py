"""Parity tests for pandas and polars engine implementations.

For each of the 7 operations, we run both engines on the tiny fixture
and confirm they produce equivalent results (after sorting and hashing).
"""

import hashlib

import pandas as pd
import polars as pl
import pytest

from lib.benchmark.engines import (
    OPS,
    pd_read,
    pl_read,
    pd_count,
    pl_count,
    pd_filter,
    pl_filter,
    pd_groupby,
    pl_groupby,
    pd_sort,
    pl_sort,
    pd_regex,
    pl_regex,
    pd_write,
    pl_write,
    default_column_config,
)


def _hash_df(df: pd.DataFrame) -> str:
    """Deterministic hash of a DataFrame ignoring row order."""
    if df.empty:
        return "empty"
    sorted_df = df.sort_values(list(df.columns)).reset_index(drop=True)
    vals = pd.util.hash_pandas_object(sorted_df).values.tobytes()
    return hashlib.sha1(vals).hexdigest()


def test_ops_constant_has_seven_entries():
    assert len(OPS) == 7
    assert [op["key"] for op in OPS] == [
        "read", "count", "filter", "groupby", "sort", "regex", "write",
    ]


def test_default_column_config_resolves(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    assert cfg["numeric"] in tiny_ppd_df.columns
    assert cfg["string"] in tiny_ppd_df.columns
    assert cfg["groupby"] in tiny_ppd_df.columns


def test_read_parity(tiny_ppd_path):
    pd_df = pd_read(tiny_ppd_path)
    pl_df = pl_read(tiny_ppd_path).to_pandas()
    assert _hash_df(pd_df) == _hash_df(pl_df)


def test_count_parity(tiny_ppd_df):
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    assert pd_count(pd_df) == pl_count(pl_df) == 100


def test_filter_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    threshold = pd_df[cfg["numeric"]].median()
    pd_out = pd_filter(pd_df, cfg["numeric"], threshold)
    pl_out = pl_filter(pl_df, cfg["numeric"], threshold).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_groupby_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_out = pd_groupby(pd_df, cfg["groupby"], cfg["numeric"])
    pl_out = pl_groupby(pl_df, cfg["groupby"], cfg["numeric"]).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_sort_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_out = pd_sort(pd_df, cfg["numeric"])
    pl_out = pl_sort(pl_df, cfg["numeric"]).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_regex_parity(tiny_ppd_df):
    cfg = default_column_config(tiny_ppd_df)
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pattern = r"^([A-Z]+)"
    pd_out = pd_regex(pd_df, cfg["string"], pattern)
    pl_out = pl_regex(pl_df, cfg["string"], pattern).to_pandas()
    assert _hash_df(pd_out) == _hash_df(pl_out)


def test_write_parity(tiny_ppd_df, tmp_path):
    pd_df = tiny_ppd_df
    pl_df = pl.from_pandas(pd_df)
    pd_path = tmp_path / "pd_out.parquet"
    pl_path = tmp_path / "pl_out.parquet"
    pd_result = pd_write(pd_df, pd_path)
    pl_result = pl_write(pl_df, pl_path)
    assert pd_result["path"] == pd_path
    assert pl_result["path"] == pl_path
    assert pd_path.exists()
    assert pl_path.exists()
    pd_roundtrip = pd.read_parquet(pd_path)
    pl_roundtrip = pd.read_parquet(pl_path)
    assert _hash_df(pd_roundtrip) == _hash_df(pl_roundtrip)
