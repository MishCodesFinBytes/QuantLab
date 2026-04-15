"""Build dashboard/data/london_ppd_with_bedrooms.parquet.

Joins Land Registry Price Paid Data with the EPC dataset on
(postcode, normalised first line of address) so each sale is
enriched with a bedroom count derived from EPC's
`number-habitable-rooms` field.

Usage:
    python dashboard/scripts/build_ppd_with_bedrooms.py
    python dashboard/scripts/build_ppd_with_bedrooms.py --refresh-epc

The --refresh-epc flag re-fetches EPC data from the API even if
the cache is populated. Without it, cached EPC CSVs are reused.

Credentials: reads EPC_API_EMAIL and EPC_API_TOKEN from
dashboard/.env.local (see https://epc.opendatacommunities.org/).

Inputs:  dashboard/data/london_ppd.parquet
         + dashboard/data/_cache/epc/<la_code>/certificates.csv
           (downloaded from the EPC Open Data API)
Output:  dashboard/data/london_ppd_with_bedrooms.parquet
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = DATA_DIR / "_cache"
EPC_CACHE = CACHE_DIR / "epc"
PPD_PARQUET = DATA_DIR / "london_ppd.parquet"
OUTPUT_PARQUET = DATA_DIR / "london_ppd_with_bedrooms.parquet"
ENV_LOCAL = REPO_ROOT / ".env.local"

EPC_API_BASE = "https://epc.opendatacommunities.org/api/v1/domestic/search"
EPC_PAGE_SIZE = 5000
EPC_MAX_RECORDS_PER_LA = 10_000  # API hard limit without scroll

# 32 London local authority codes used by the EPC API + their human names.
LONDON_LAS: list[tuple[str, str]] = [
    ("E09000001", "City of London"),
    ("E09000002", "Barking and Dagenham"),
    ("E09000003", "Barnet"),
    ("E09000004", "Bexley"),
    ("E09000005", "Brent"),
    ("E09000006", "Bromley"),
    ("E09000007", "Camden"),
    ("E09000008", "Croydon"),
    ("E09000009", "Ealing"),
    ("E09000010", "Enfield"),
    ("E09000011", "Greenwich"),
    ("E09000012", "Hackney"),
    ("E09000013", "Hammersmith and Fulham"),
    ("E09000014", "Haringey"),
    ("E09000015", "Harrow"),
    ("E09000016", "Havering"),
    ("E09000017", "Hillingdon"),
    ("E09000018", "Hounslow"),
    ("E09000019", "Islington"),
    ("E09000020", "Kensington and Chelsea"),
    ("E09000021", "Kingston upon Thames"),
    ("E09000022", "Lambeth"),
    ("E09000023", "Lewisham"),
    ("E09000024", "Merton"),
    ("E09000025", "Newham"),
    ("E09000026", "Redbridge"),
    ("E09000027", "Richmond upon Thames"),
    ("E09000028", "Southwark"),
    ("E09000029", "Sutton"),
    ("E09000030", "Tower Hamlets"),
    ("E09000031", "Waltham Forest"),
    ("E09000032", "Wandsworth"),
    ("E09000033", "Westminster"),
]


# ──────────────────────────────────────────────────────────────
# .env.local loader (no external dependency on python-dotenv)
# ──────────────────────────────────────────────────────────────

def load_env_local() -> dict[str, str]:
    """Parse dashboard/.env.local for KEY=value pairs."""
    if not ENV_LOCAL.exists():
        print(f"ERROR: {ENV_LOCAL} not found.", file=sys.stderr)
        sys.exit(2)
    env: dict[str, str] = {}
    for line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


# ──────────────────────────────────────────────────────────────
# EPC API client
# ──────────────────────────────────────────────────────────────

def build_auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def fetch_la_certificates(
    la_code: str,
    la_name: str,
    auth_header: str,
    cache_path: Path,
    refresh: bool,
) -> int:
    """Download domestic EPC certificates for one local authority.

    Writes a CSV to cache_path with the columns we care about. Returns
    the number of rows written. Skips the API call if the cache exists
    and refresh is False.
    """
    if cache_path.exists() and not refresh:
        try:
            cached = pd.read_csv(cache_path)
            return len(cached)
        except Exception:
            pass  # corrupted cache — refetch

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "Accept": "text/csv",
        "Authorization": auth_header,
    }
    params = {
        "local-authority": la_code,
        "size": EPC_PAGE_SIZE,
    }

    pages: list[pd.DataFrame] = []
    fetched = 0
    from_offset = 0

    while fetched < EPC_MAX_RECORDS_PER_LA:
        params["from"] = from_offset
        try:
            response = requests.get(
                EPC_API_BASE, headers=headers, params=params, timeout=60
            )
        except requests.RequestException as exc:
            print(f"  HTTP error for {la_code}: {exc}", file=sys.stderr)
            return 0

        if response.status_code == 401:
            print(
                f"  AUTH FAILED for {la_code} — check EPC_API_EMAIL "
                f"and EPC_API_TOKEN in dashboard/.env.local",
                file=sys.stderr,
            )
            sys.exit(2)

        if response.status_code != 200:
            print(
                f"  HTTP {response.status_code} for {la_code}: {response.text[:200]}",
                file=sys.stderr,
            )
            return 0

        # Empty response (no more rows) returns an empty body or just headers
        text = response.text.strip()
        if not text or text.count("\n") < 1:
            break

        from io import StringIO
        page_df = pd.read_csv(StringIO(text))
        if len(page_df) == 0:
            break

        pages.append(page_df)
        fetched += len(page_df)
        from_offset += len(page_df)

        if len(page_df) < EPC_PAGE_SIZE:
            # Last page reached
            break

    if not pages:
        print(f"  no rows for {la_code} ({la_name})")
        return 0

    df = pd.concat(pages, ignore_index=True)

    # Keep only the columns we need (case-insensitive lookup)
    wanted = ["postcode", "address1", "number-habitable-rooms"]
    available_lower = {c.lower(): c for c in df.columns}
    keep_cols = [available_lower[w] for w in wanted if w in available_lower]
    if len(keep_cols) < 3:
        print(
            f"  WARNING: {la_code} response missing expected columns. "
            f"Got {list(df.columns)[:8]}...",
            file=sys.stderr,
        )
        return 0
    df = df[keep_cols]
    df.columns = ["postcode", "address1", "number_habitable_rooms"]
    df.to_csv(cache_path, index=False)
    return len(df)


def ensure_epc_downloaded(refresh: bool) -> None:
    """Download EPC certificates for every London LA into the cache."""
    env = load_env_local()
    email = env.get("EPC_API_EMAIL", "")
    token = env.get("EPC_API_TOKEN", "")
    if not email or not token:
        print(
            "ERROR: EPC_API_EMAIL or EPC_API_TOKEN missing from "
            f"{ENV_LOCAL}",
            file=sys.stderr,
        )
        sys.exit(2)
    auth_header = build_auth_header(email, token)
    EPC_CACHE.mkdir(parents=True, exist_ok=True)
    for code, name in LONDON_LAS:
        cache_path = EPC_CACHE / code / "certificates.csv"
        action = "refreshing" if refresh or not cache_path.exists() else "cached"
        print(f"  {code} {name:30} {action}...", end=" ", flush=True)
        n = fetch_la_certificates(code, name, auth_header, cache_path, refresh)
        print(f"{n:,} rows")


# ──────────────────────────────────────────────────────────────
# Address normalisation
# ──────────────────────────────────────────────────────────────

_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]")


def normalise_address(value: str | float) -> str:
    if not isinstance(value, str):
        return ""
    s = value.lower()
    s = _NON_ALNUM_RE.sub(" ", s)
    s = _WHITESPACE_RE.sub(" ", s).strip()
    return s


def normalise_postcode(value: str | float) -> str:
    if not isinstance(value, str):
        return ""
    return value.upper().replace(" ", "")


# ──────────────────────────────────────────────────────────────
# EPC + PPD loaders and join
# ──────────────────────────────────────────────────────────────

def load_all_epc() -> pd.DataFrame:
    """Load EPC certificates from cache and aggregate to one row per postcode.

    Our PPD parquet only has postcode (no street address), so we cannot
    join address-to-address. Instead we collapse every EPC at a postcode
    into a single row that captures the typical bedroom count there —
    using the mode (most common bedroom band) of all certificates with
    that postcode. This is approximate but data-driven, and works because
    most London postcodes are small (5-15 households, often the same
    building or terrace).
    """
    frames = []
    for code, _ in LONDON_LAS:
        certs = EPC_CACHE / code / "certificates.csv"
        if not certs.exists():
            continue
        df = pd.read_csv(certs)
        if not {"postcode", "number_habitable_rooms"}.issubset(df.columns):
            continue
        df["postcode_norm"] = df["postcode"].map(normalise_postcode)
        df = df[["postcode_norm", "number_habitable_rooms"]]
        df = df.rename(columns={"number_habitable_rooms": "habitable_rooms"})
        df = df.dropna(subset=["habitable_rooms"])
        frames.append(df)
    if not frames:
        print("ERROR: no EPC files found in cache", file=sys.stderr)
        sys.exit(2)
    raw = pd.concat(frames, ignore_index=True)
    raw["bedrooms"] = raw["habitable_rooms"].map(bucket_bedrooms)
    raw = raw[raw["bedrooms"] != ""]

    # Mode bedroom band per postcode (ties broken by alphabetical).
    grouped = raw.groupby("postcode_norm")["bedrooms"].agg(
        lambda s: s.value_counts().idxmax()
    )
    return grouped.reset_index()


def load_ppd() -> pd.DataFrame:
    df = pd.read_parquet(PPD_PARQUET)
    df["postcode_norm"] = df["postcode"].map(normalise_postcode)
    return df


def bucket_bedrooms(habitable_rooms: float | int) -> str:
    if pd.isna(habitable_rooms):
        return ""
    rooms = int(habitable_rooms)
    bedrooms = rooms - 1
    if bedrooms <= 0:
        return "studio"
    if bedrooms == 1:
        return "1"
    if bedrooms == 2:
        return "2"
    if bedrooms == 3:
        return "3"
    return "4+"


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--refresh-epc",
        action="store_true",
        help="Re-download EPC data from the API even if cached.",
    )
    p.add_argument(
        "--min-match-rate",
        type=float,
        default=0.20,
        help="Fail if join match rate is below this fraction (default 0.20).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    print(f"PPD source: {PPD_PARQUET}")
    print(f"EPC cache:  {EPC_CACHE}")
    print(f"Output:     {OUTPUT_PARQUET}")
    print()

    print("Fetching EPC data per London LA...")
    ensure_epc_downloaded(refresh=args.refresh_epc)

    print()
    print("Loading PPD...")
    ppd = load_ppd()
    print(f"  {len(ppd):,} sales loaded")

    print("Loading EPC...")
    epc = load_all_epc()
    print(f"  {len(epc):,} unique addresses loaded")

    print("Joining on postcode...")
    merged = ppd.merge(epc, on="postcode_norm", how="left")

    matched = int(merged["bedrooms"].notna().sum())
    match_rate = matched / max(len(merged), 1)
    print(f"  matched: {matched:,} / {len(merged):,}  ({match_rate:.1%})")

    if match_rate < args.min_match_rate:
        print(
            f"ERROR: match rate {match_rate:.1%} is below threshold "
            f"{args.min_match_rate:.1%}",
            file=sys.stderr,
        )
        return 2

    drop_cols = ["postcode_norm"]
    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

    print("Writing output...")
    tmp_path = OUTPUT_PARQUET.with_suffix(".parquet.tmp")
    merged.to_parquet(tmp_path, index=False)
    tmp_path.replace(OUTPUT_PARQUET)
    print(f"  wrote {OUTPUT_PARQUET} ({len(merged):,} rows)")

    print()
    print("Bedroom distribution:")
    print(merged["bedrooms"].value_counts(dropna=False).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
