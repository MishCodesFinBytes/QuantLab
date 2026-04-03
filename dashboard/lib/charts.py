import numpy as np
import pandas as pd
import plotly.graph_objects as go


def price_history_chart(prices: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col in prices.columns:
        fig.add_trace(go.Scatter(
            x=prices.index, y=prices[col], mode="lines", name=col
        ))
    fig.update_layout(
        title="Price History",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def cumulative_return_chart(prices: pd.DataFrame, weights: list[float]) -> go.Figure:
    log_returns = np.log(prices / prices.shift(1)).dropna()
    portfolio_returns = log_returns.values @ np.array(weights)
    cumulative = np.exp(np.cumsum(portfolio_returns))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices.index[1:],
        y=cumulative,
        mode="lines",
        name="Portfolio",
        line=dict(color="#2a7ae2", width=2),
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="Portfolio Cumulative Return",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (1.0 = start)",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def drawdown_chart(prices: pd.DataFrame, weights: list[float]) -> go.Figure:
    log_returns = np.log(prices / prices.shift(1)).dropna()
    portfolio_returns = log_returns.values @ np.array(weights)
    cumulative = np.exp(np.cumsum(portfolio_returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices.index[1:],
        y=drawdown,
        mode="lines",
        name="Drawdown",
        fill="tozeroy",
        line=dict(color="red", width=1),
        fillcolor="rgba(255, 0, 0, 0.2)",
    ))
    fig.update_layout(
        title="Portfolio Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def weight_pie_chart(tickers: list[str], weights: list[float]) -> go.Figure:
    fig = go.Figure(data=[go.Pie(
        labels=tickers,
        values=[w * 100 for w in weights],
        textinfo="label+percent",
        hole=0.3,
    )])
    fig.update_layout(
        title="Portfolio Allocation",
        template="plotly_white",
        showlegend=False,
    )
    return fig
