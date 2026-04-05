"""SQLAlchemy models for yield curves, bonds, and pricing results.

Design notes
------------
- Each curve record has a unique ``curve_date`` with an index. The primary
  access pattern is point-in-time: "give me the curve for 2026-04-04",
  which makes a unique index the right trade-off.
- Yields/rates are stored as a JSON string rather than one row per
  maturity. This keeps the schema simple for a tiny, flexible payload
  (maturity labels can change over time). For large aggregations a
  normalised one-row-per-maturity table would be better.
- ``bonds`` is keyed by ISIN (the global identifier for a security).
- ``pricing_results`` keeps the full analytical output per bond per date.
"""

import json
from datetime import date, datetime, UTC
from sqlalchemy import String, Float, Integer, Date, DateTime, Text, Boolean

# created_at columns are tz-aware UTC. Postgres stores these as timestamptz;
# without timezone=True asyncpg rejects the tz-aware default with a "can't
# subtract offset-naive and offset-aware datetimes" DataError.
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ParYieldRecord(Base):
    """Daily US Treasury par yield curve."""

    __tablename__ = "par_yields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    yields_json: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20), default="FRED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class SpotCurveRecord(Base):
    """Bootstrapped zero-coupon (spot) rate curve."""

    __tablename__ = "spot_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    rates_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class ForwardCurveRecord(Base):
    """Implied forward rate curve derived from spot rates."""

    __tablename__ = "forward_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    rates_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class FittedCurveRecord(Base):
    """Parametric fitted curve (Nelson-Siegel or Svensson)."""

    __tablename__ = "fitted_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, index=True)
    model: Mapped[str] = mapped_column(String(30))  # "nelson-siegel" or "svensson"
    params_json: Mapped[str] = mapped_column(Text)
    fitted_rates_json: Mapped[str] = mapped_column(Text)
    rmse: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class BondRecord(Base):
    """Bond definition (treasury or corporate)."""

    __tablename__ = "bonds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isin: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    coupon: Mapped[float] = mapped_column(Float)
    maturity: Mapped[date] = mapped_column(Date)
    face_value: Mapped[float] = mapped_column(Float, default=1000.0)
    issue_date: Mapped[date] = mapped_column(Date)
    frequency: Mapped[int] = mapped_column(Integer, default=2)  # coupons per year
    bond_type: Mapped[str] = mapped_column(String(20), default="treasury")
    is_callable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class PricingResultRecord(Base):
    """Analytical pricing output for a bond on a given curve date."""

    __tablename__ = "pricing_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bond_isin: Mapped[str] = mapped_column(String(12), index=True)
    curve_date: Mapped[date] = mapped_column(Date)
    clean_price: Mapped[float] = mapped_column(Float)
    dirty_price: Mapped[float] = mapped_column(Float)
    ytm: Mapped[float] = mapped_column(Float)
    z_spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration: Mapped[float] = mapped_column(Float)
    modified_duration: Mapped[float] = mapped_column(Float)
    convexity: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
