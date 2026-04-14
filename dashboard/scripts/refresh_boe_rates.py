"""Refresh boe_mortgage_rates.csv from the Bank of England IADB.

Run manually by the developer every few months.

Usage:
    cd dashboard && python scripts/refresh_boe_rates.py
"""

from __future__ import annotations

import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd


SERIES = [
    (2, 0.60, "IUMBV24"),
    (2, 0.75, "IUMBV34"),
    (2, 0.85, "IUMBV37"),
    (2, 0.90, "IUMBV42"),
    (2, 0.95, "IUMBV45"),
    (3, 0.60, "IUMBV48"),
    (3, 0.75, "IUMBV51"),
    (3, 0.85, "IUMBV54"),
    (3, 0.90, "IUMBV57"),
    (3, 0.95, "IUMBV60"),
    (5, 0.60, "IUMBV34"),
    (5, 0.75, "IUMBV37"),
    (5, 0.85, "IUMBV42"),
    (5, 0.90, "IUMBV45"),
    (5, 0.95, "IUMBV48"),
    (10, 0.60, "IUMBV51"),
    (10, 0.75, "IUMBV54"),
    (10, 0.85, "IUMBV57"),
    (10, 0.90, "IUMBV60"),
    (10, 0.95, "IUMBV63"),
]

IADB_URL_TEMPLATE = (
    "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?"
    "Travel=NIxAZxSUx&FromSeries=1&ToSeries=50&DAT=RNG"
    "&FD=1&FM={from_m}&FY={from_y}&TD=31&TM={to_m}&TY={to_y}"
    "&FNY=Y&CSVF=TN&html.x=66&html.y=26"
    "&SeriesCodes={code}&UsingCodes=Y&Filter=N&title={code}&VPD=Y"
)

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "boe_mortgage_rates.csv"


def fetch_series_latest(code: str):
    now = dt.date.today()
    three_months_ago = now - dt.timedelta(days=100)
    url = IADB_URL_TEMPLATE.format(
        from_m=three_months_ago.strftime("%b"),
        from_y=three_months_ago.year,
        to_m=now.strftime("%b"),
        to_y=now.year,
        code=code,
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as exc:
        print(f"  {code}: fetch failed — {exc}")
        return None

    try:
        df = pd.read_csv(io.StringIO(raw))
        if df.empty or len(df.columns) < 2:
            return None
        latest = df.iloc[-1, 1]
        return float(latest)
    except Exception as exc:
        print(f"  {code}: parse failed — {exc}")
        return None


def main() -> int:
    rows = []
    snapshot_date = dt.date.today().strftime("%Y-%m")
    print(f"Refreshing BoE rates — snapshot {snapshot_date}")

    for fix_years, ltv_bracket, code in SERIES:
        rate = fetch_series_latest(code)
        if rate is not None:
            rows.append({
                "fix_years": fix_years,
                "ltv_bracket": ltv_bracket,
                "rate_pct": rate,
                "snapshot_date": snapshot_date,
            })
            print(f"  {code} (fix={fix_years}, ltv={ltv_bracket}): {rate:.2f}%")

    if not rows:
        print("No data fetched. Leaving existing CSV untouched.")
        return 1

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
