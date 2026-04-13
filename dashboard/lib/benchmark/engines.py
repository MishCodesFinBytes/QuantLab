"""Pure pandas + polars implementations of 7 dataframe operations.

Each function is side-effect-free except `pd_write` / `pl_write`, which
accept a target path. No timing, memory, or logging — the runner owns
those concerns.

Column roles:
- numeric: the column filtered, sorted, and aggregated
- string:  the column regex is applied to
- groupby: the column rows are grouped by
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import polars as pl


OPS = [
    {"key": "read",    "label": "Read parquet"},
    {"key": "count",   "label": "Count rows"},
    {"key": "filter",  "label": "Filter"},
    {"key": "groupby", "label": "Groupby + aggregate"},
    {"key": "sort",    "label": "Sort"},
    {"key": "regex",   "label": "String extract (regex)"},
    {"key": "write",   "label": "Write parquet"},
]


def default_column_config(df: pd.DataFrame) -> dict:
    """Pick sensible numeric/string/groupby columns from the schema.

    - numeric: first numeric dtype column
    - string:  first object/string dtype column
    - groupby: first string column whose nunique is less than the row count
    """
    numeric = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])), None)
    string = next((c for c in df.columns if pd.api.types.is_object_dtype(df[c])), None)
    groupby = next(
        (c for c in df.columns
         if pd.api.types.is_object_dtype(df[c]) and df[c].nunique() < len(df)),
        string,
    )
    if numeric is None or string is None or groupby is None:
        raise ValueError(
            f"Could not auto-detect columns from schema {list(df.columns)}. "
            "Pass an explicit column_config."
        )
    return {"numeric": numeric, "string": string, "groupby": groupby}


# --- Op 1: Read parquet ----------------------------------------------------

def pd_read(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def pl_read(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)


# --- Op 2: Count rows ------------------------------------------------------

def pd_count(df: pd.DataFrame) -> int:
    return len(df)


def pl_count(df: pl.DataFrame) -> int:
    return df.height


# --- Op 3: Filter ----------------------------------------------------------

def pd_filter(df: pd.DataFrame, col: str, threshold) -> pd.DataFrame:
    return df[df[col] > threshold]


def pl_filter(df: pl.DataFrame, col: str, threshold) -> pl.DataFrame:
    return df.filter(pl.col(col) > threshold)


# --- Op 4: Groupby + aggregate ---------------------------------------------

def pd_groupby(df: pd.DataFrame, group_col: str, numeric_col: str) -> pd.DataFrame:
    return (
        df.groupby(group_col)[numeric_col]
        .agg(["mean", "median", "count"])
        .reset_index()
    )


def pl_groupby(df: pl.DataFrame, group_col: str, numeric_col: str) -> pl.DataFrame:
    return df.group_by(group_col).agg([
        pl.col(numeric_col).mean().alias("mean"),
        pl.col(numeric_col).median().alias("median"),
        pl.col(numeric_col).count().alias("count"),
    ])


# --- Op 5: Sort ------------------------------------------------------------

def pd_sort(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.sort_values(col, ascending=False).reset_index(drop=True)


def pl_sort(df: pl.DataFrame, col: str) -> pl.DataFrame:
    return df.sort(col, descending=True)


# --- Op 6: String extract (regex) ------------------------------------------

def pd_regex(df: pd.DataFrame, col: str, pattern: str) -> pd.DataFrame:
    extracted = df[col].str.extract(pattern, expand=False)
    return pd.DataFrame({col: df[col], "extracted": extracted})


def pl_regex(df: pl.DataFrame, col: str, pattern: str) -> pl.DataFrame:
    return df.select([
        pl.col(col),
        pl.col(col).str.extract(pattern, 1).alias("extracted"),
    ])


# --- Op 7: Write parquet ---------------------------------------------------

def pd_write(df: pd.DataFrame, path: Path) -> dict:
    df.to_parquet(path, index=False)
    return {"path": path, "bytes_written": path.stat().st_size}


def pl_write(df: pl.DataFrame, path: Path) -> dict:
    df.write_parquet(path)
    return {"path": path, "bytes_written": path.stat().st_size}
