import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
async def session():
    from src.scanner.db_models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


class TestCreatePendingScan:
    async def test_creates_pending_record(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan

        request = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        record = await create_pending_scan(session, request)
        assert record.id is not None
        assert record.status == "pending"
        assert record.tickers == "AAPL,MSFT"
        assert record.weights == "0.6,0.4"
        assert record.var_pct is None


class TestCompleteScan:
    async def test_updates_to_complete(self, session):
        from src.scanner.models import ScanRequest, ScanResult, RiskMetrics
        from src.scanner.db import create_pending_scan, complete_scan, get_scan
        from datetime import datetime, UTC

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        metrics = RiskMetrics(
            var_pct=-2.15, cvar_pct=-3.42, max_drawdown_pct=-18.7,
            volatility_pct=22.5, sharpe_ratio=1.2,
        )
        result = ScanResult(
            tickers=["AAPL"], weights=[1.0], metrics=metrics,
            narrative="Looks good.", generated_at=datetime.now(UTC),
        )
        await complete_scan(session, record.id, result)

        updated = await get_scan(session, record.id)
        assert updated.status == "complete"
        assert updated.var_pct == pytest.approx(-2.15)
        assert updated.narrative == "Looks good."
        assert updated.completed_at is not None


class TestFailScan:
    async def test_updates_to_failed(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan, fail_scan, get_scan

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        await fail_scan(session, record.id, "yfinance timeout")

        updated = await get_scan(session, record.id)
        assert updated.status == "failed"
        assert updated.error_message == "yfinance timeout"
        assert updated.completed_at is not None


class TestGetScan:
    async def test_returns_record_by_id(self, session):
        from src.scanner.models import ScanRequest
        from src.scanner.db import create_pending_scan, get_scan

        request = ScanRequest(tickers=["AAPL"], weights=[1.0])
        record = await create_pending_scan(session, request)

        found = await get_scan(session, record.id)
        assert found is not None
        assert found.id == record.id

    async def test_returns_none_for_missing_id(self, session):
        from src.scanner.db import get_scan

        found = await get_scan(session, 9999)
        assert found is None


class TestGetRecentScans:
    async def test_returns_completed_scans_newest_first(self, session):
        from src.scanner.models import ScanRequest, ScanResult, RiskMetrics
        from src.scanner.db import create_pending_scan, complete_scan, get_recent_scans
        from datetime import datetime, UTC

        metrics = RiskMetrics(
            var_pct=-1.0, cvar_pct=-2.0, max_drawdown_pct=-10.0,
            volatility_pct=15.0, sharpe_ratio=0.5,
        )

        for ticker in ["AAPL", "MSFT"]:
            req = ScanRequest(tickers=[ticker], weights=[1.0])
            rec = await create_pending_scan(session, req)
            result = ScanResult(
                tickers=[ticker], weights=[1.0], metrics=metrics,
                narrative=f"{ticker} scan", generated_at=datetime.now(UTC),
            )
            await complete_scan(session, rec.id, result)

        pending_req = ScanRequest(tickers=["GOOG"], weights=[1.0])
        await create_pending_scan(session, pending_req)

        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 2
        assert scans[0].tickers == "MSFT"
