from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ScanRecord


async def save_scan(
    session: AsyncSession,
    tickers: list[str],
    var_pct: float,
    narrative: str,
) -> ScanRecord:
    record = ScanRecord(
        tickers=",".join(tickers),
        var_pct=var_pct,
        narrative=narrative,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]:
    stmt = select(ScanRecord).order_by(ScanRecord.created_at.desc(), ScanRecord.id.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
