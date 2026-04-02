import numpy as np
import pandas as pd
from src.scanner.models import RiskMetrics


def calculate_risk_metrics(prices: pd.DataFrame, weights: list[float]) -> RiskMetrics:
    # Daily log returns per asset
    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Portfolio returns (weighted sum)
    w = np.array(weights)
    portfolio_returns = log_returns.values @ w

    # VaR (95%) — 5th percentile
    var = float(np.percentile(portfolio_returns, 5))

    # CVaR — mean of returns worse than VaR
    cvar = float(portfolio_returns[portfolio_returns <= var].mean())

    # Max drawdown from cumulative returns (use exp(cumsum) for log returns)
    cumulative = np.exp(np.cumsum(portfolio_returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max
    max_dd = float(drawdowns.min())

    # Annualized volatility
    vol = float(portfolio_returns.std() * np.sqrt(252))

    # Sharpe ratio (risk-free rate = 0)
    annual_return = float(portfolio_returns.mean() * 252)
    sharpe = annual_return / vol if vol > 0 else 0.0

    return RiskMetrics(
        var_pct=round(var * 100, 2),
        cvar_pct=round(cvar * 100, 2),
        max_drawdown_pct=round(max_dd * 100, 2),
        volatility_pct=round(vol * 100, 2),
        sharpe_ratio=round(sharpe, 2),
    )
