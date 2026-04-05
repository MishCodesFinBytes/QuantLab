"""Seed par_yields table from S3 par-yields objects.

Walks s3://finbytes-quant-lab-data/par-yields/ and upserts each day's curve
into RDS via the yield_store.db helpers. Safe to re-run — save_par_yields
upserts by curve_date.

Config via env:
    DATABASE_URL     async URL, e.g. postgresql+asyncpg://user:pw@host:5432/postgres
    S3_BUCKET        default: finbytes-quant-lab-data
    S3_PREFIX        default: par-yields/
    AWS_PROFILE      default: quant-lab
"""

import asyncio
import json
import os
from datetime import date

import boto3
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from yield_store.db import save_par_yields

BUCKET = os.environ.get("S3_BUCKET", "finbytes-quant-lab-data")
PREFIX = os.environ.get("S3_PREFIX", "par-yields/")
PROFILE = os.environ.get("AWS_PROFILE", "quant-lab")


async def seed() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    s3 = boto3.Session(profile_name=PROFILE).client("s3")
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)

    loaded = 0
    for obj in response.get("Contents", []):
        if not obj["Key"].endswith(".json"):
            continue
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read()
        data = json.loads(body)
        curve_date = date.fromisoformat(data["date"])
        async with factory() as session:
            await save_par_yields(session, curve_date, data["yields"])
        print(f"  loaded {data['date']} ({len(data['yields'])} tenors)")
        loaded += 1

    await engine.dispose()
    print(f"Seeded {loaded} par-yield rows into {BUCKET}/{PREFIX}.")


if __name__ == "__main__":
    asyncio.run(seed())
