import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, UTC

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.scanner.db import (
    complete_scan,
    create_pending_scan,
    fail_scan,
    get_recent_scans,
    get_scan,
)
from src.scanner.models import ScanRequest, ScanResult
from src.scanner.scanner import scan

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///scanner.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(DATABASE_URL)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Auto-run migrations on startup (needed for Render free tier — no shell access)
    from src.scanner.db_models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("app_started", database=DATABASE_URL)

    yield
    await engine.dispose()
    log.info("app_stopped")


def _record_to_dict(record) -> dict:
    return {
        "id": record.id,
        "tickers": record.tickers.split(","),
        "weights": [float(w) for w in record.weights.split(",")],
        "period": record.period,
        "status": record.status,
        "var_pct": record.var_pct,
        "cvar_pct": record.cvar_pct,
        "max_drawdown_pct": record.max_drawdown_pct,
        "volatility_pct": record.volatility_pct,
        "sharpe_ratio": record.sharpe_ratio,
        "narrative": record.narrative,
        "error_message": record.error_message,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
    }


async def _run_scan(scan_id: int, request: ScanRequest, session_factory):
    async with session_factory() as session:
        try:
            log.info("scan_started", scan_id=scan_id, tickers=request.tickers)
            result = scan(request)
            await complete_scan(session, scan_id, result)
            log.info("scan_completed", scan_id=scan_id, var=result.metrics.var_pct)
        except Exception as e:
            await fail_scan(session, scan_id, str(e))
            log.error("scan_failed", scan_id=scan_id, error=str(e))


async def get_session(request: Request) -> AsyncSession:
    factory: async_sessionmaker = request.app.state.session_factory
    async with factory() as session:
        yield session


def create_app() -> FastAPI:
    application = FastAPI(title="Stock Risk Scanner", lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://mish-codes.github.io",
            "https://quantlabs.streamlit.app",
            "https://finbytes.streamlit.app",
            "http://localhost:8501",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health():
        return {"status": "ok"}

    @application.get("/api/health/db")
    async def health_db(session: AsyncSession = Depends(get_session)):
        try:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            return {"status": "error", "database": str(e)}

    @application.post("/api/scan", status_code=202)
    async def create_scan(
        request: ScanRequest,
        session: AsyncSession = Depends(get_session),
        http_request: Request = None,
    ):
        record = await create_pending_scan(session, request)
        log.info("scan_requested", scan_id=record.id, tickers=request.tickers)
        asyncio.ensure_future(
            _run_scan(record.id, request, http_request.app.state.session_factory)
        )
        return {"id": record.id, "status": "pending"}

    @application.get("/api/scans/{scan_id}")
    async def read_scan(scan_id: int, session: AsyncSession = Depends(get_session)):
        record = await get_scan(session, scan_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Scan not found")
        return _record_to_dict(record)

    @application.get("/api/scans")
    async def list_scans(limit: int = 10, session: AsyncSession = Depends(get_session)):
        records = await get_recent_scans(session, limit=limit)
        return [_record_to_dict(r) for r in records]

    return application


app = create_app()
