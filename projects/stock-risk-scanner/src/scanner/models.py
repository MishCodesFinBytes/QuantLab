from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class ScanRequest(BaseModel):
    tickers: list[str]
    weights: list[float]
    period: str = "1y"

    @field_validator("tickers")
    @classmethod
    def uppercase_tickers(cls, v: list[str]) -> list[str]:
        return [t.upper() for t in v]

    @model_validator(mode="after")
    def validate_lengths_and_weights(self) -> "ScanRequest":
        if len(self.tickers) != len(self.weights):
            raise ValueError(
                f"tickers length ({len(self.tickers)}) must match "
                f"weights length ({len(self.weights)})"
            )
        if abs(sum(self.weights) - 1.0) > 0.01:
            raise ValueError(
                f"weights must sum to 1.0 (got {sum(self.weights):.4f})"
            )
        return self


class RiskMetrics(BaseModel):
    var_pct: float
    cvar_pct: float
    max_drawdown_pct: float
    volatility_pct: float
    sharpe_ratio: float


class ScanResult(BaseModel):
    tickers: list[str]
    weights: list[float]
    metrics: RiskMetrics
    narrative: str
    generated_at: datetime
