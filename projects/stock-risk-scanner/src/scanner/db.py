from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.scanner.db_models import ScanRecord
from src.scanner.models import ScanRequest, ScanResult


async def create_pending_scan(session: AsyncSession, request: ScanRequest) -> ScanRecord:
    record = ScanRecord(
        tickers=",".join(request.tickers),
        weights=",".join(str(w) for w in request.weights),
        period=request.period,
        status="pending",
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def complete_scan(session: AsyncSession, scan_id: int, result: ScanResult) -> None:
    record = await session.get(ScanRecord, scan_id)
    if record is None:
        raise ValueError(f"Scan record {scan_id} not found")
    record.status = "complete"
    record.var_pct = result.metrics.var_pct
    record.cvar_pct = result.metrics.cvar_pct
    record.max_drawdown_pct = result.metrics.max_drawdown_pct
    record.volatility_pct = result.metrics.volatility_pct
    record.sharpe_ratio = result.metrics.sharpe_ratio
    record.narrative = result.narrative
    record.completed_at = datetime.now(UTC)
    await session.commit()


async def fail_scan(session: AsyncSession, scan_id: int, error: str) -> None:
    record = await session.get(ScanRecord, scan_id)
    if record is None:
        raise ValueError(f"Scan record {scan_id} not found")
    record.status = "failed"
    record.error_message = error
    record.completed_at = datetime.now(UTC)
    await session.commit()


async def get_scan(session: AsyncSession, scan_id: int) -> ScanRecord | None:
    return await session.get(ScanRecord, scan_id)


async def get_recent_scans(session: AsyncSession, limit: int = 10) -> list[ScanRecord]:
    stmt = (
        select(ScanRecord)
        .where(ScanRecord.status == "complete")
        .order_by(ScanRecord.created_at.desc(), ScanRecord.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
