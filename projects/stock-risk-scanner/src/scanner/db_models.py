from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    tickers: Mapped[str] = mapped_column(String(200))
    weights: Mapped[str] = mapped_column(String(200))
    period: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    var_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cvar_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volatility_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    narrative: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
