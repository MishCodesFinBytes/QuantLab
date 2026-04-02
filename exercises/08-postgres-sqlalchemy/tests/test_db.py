import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
async def session():
    """In-memory SQLite for fast tests."""
    from src.models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


class TestScanRecord:
    async def test_save_and_retrieve(self, session):
        from src.db import save_scan, get_recent_scans

        await save_scan(session, tickers=["AAPL", "MSFT"], var_pct=-2.15, narrative="Test narrative")
        scans = await get_recent_scans(session, limit=10)
        assert len(scans) == 1
        assert scans[0].tickers == "AAPL,MSFT"
        assert scans[0].var_pct == pytest.approx(-2.15)
        assert scans[0].narrative == "Test narrative"

    async def test_recent_scans_ordered_by_date(self, session):
        from src.db import save_scan, get_recent_scans

        await save_scan(session, tickers=["AAPL"], var_pct=-1.0, narrative="First")
        await save_scan(session, tickers=["MSFT"], var_pct=-2.0, narrative="Second")
        scans = await get_recent_scans(session, limit=10)
        assert scans[0].narrative == "Second"  # most recent first
        assert scans[1].narrative == "First"

    async def test_limit_works(self, session):
        from src.db import save_scan, get_recent_scans

        for i in range(5):
            await save_scan(session, tickers=[f"T{i}"], var_pct=-float(i), narrative=f"Scan {i}")
        scans = await get_recent_scans(session, limit=3)
        assert len(scans) == 3
