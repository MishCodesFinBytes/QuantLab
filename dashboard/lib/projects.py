"""Project registry — single source of truth for the landing page.

Edit this file to add or remove projects from the QuantLab landing.
The landing page (app.py) reads PROJECTS_BY_CATEGORY and FEATURED_KEYS
to render the featured grid and the categorised grids.

Note: 99_Churros.py (admin page) is intentionally excluded from this
registry so it does not appear on the public landing page.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Project:
    key: str
    label: str
    description: str
    tech: list
    page_link: str
    is_capstone: bool = False


PROJECTS_BY_CATEGORY: dict = {
    "Personal finance & property": [
        Project(
            key="london_house_prices",
            label="London House Prices",
            description="Postcode growth, comparison, and brand effect — 10 years of Land Registry data",
            tech=["Python", "Plotly", "GeoPandas", "OpenStreetMap"],
            page_link="pages/42_London_House_Prices.py",
        ),
        Project(
            key="rent_vs_buy",
            label="Rent vs Buy London",
            description="Data-driven calculator using HM Land Registry, ONS, and Bank of England",
            tech=["Python", "Streamlit", "pandas", "Plotly"],
            page_link="pages/16_Rent_vs_Buy.py",
        ),
        Project(
            key="credit_card_calculator",
            label="Credit Card Calculator",
            description="Payoff schedule, total interest, two calculation modes",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/10_Credit_Card_Calculator.py",
        ),
        Project(
            key="loan_amortization",
            label="Loan Amortization",
            description="PMT formula, principal vs interest breakdown, monthly schedule",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/11_Loan_Amortization.py",
        ),
        Project(
            key="loan_comparison",
            label="Loan Comparison",
            description="Side-by-side loan analysis with rate sensitivity",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/12_Loan_Comparison.py",
        ),
        Project(
            key="retirement_calculator",
            label="Retirement Calculator",
            description="Compound growth projection with Monte Carlo simulation",
            tech=["Python", "NumPy", "Plotly", "Monte Carlo"],
            page_link="pages/13_Retirement_Calculator.py",
        ),
        Project(
            key="investment_planner",
            label="Investment Planner",
            description="Compound growth with contributions and what-if scenarios",
            tech=["Python", "NumPy", "Plotly", "Streamlit"],
            page_link="pages/14_Investment_Planner.py",
        ),
        Project(
            key="budget_tracker",
            label="Budget Tracker",
            description="Income vs expenses, spending breakdown, surplus or deficit",
            tech=["Python", "Plotly", "Streamlit"],
            page_link="pages/15_Budget_Tracker.py",
        ),
        Project(
            key="personal_finance",
            label="Personal Finance",
            description="Net worth, savings rate, debt-to-income ratio",
            tech=["Python", "Plotly", "Streamlit"],
            page_link="pages/24_Personal_Finance.py",
        ),
    ],

    "Stocks & markets": [
        Project(
            key="stock_tracker",
            label="Stock Tracker",
            description="Candlestick charts, volume bars, 52-week range",
            tech=["Python", "yfinance", "Plotly", "Streamlit"],
            page_link="pages/21_Stock_Tracker.py",
        ),
        Project(
            key="stock_analysis",
            label="Stock Analysis",
            description="SMA, EMA, RSI, MACD, and Bollinger Bands overlays",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/22_Stock_Analysis.py",
        ),
        Project(
            key="stock_prediction",
            label="Stock Prediction",
            description="Feature engineering and regression for price forecasting",
            tech=["Python", "scikit-learn", "Plotly"],
            page_link="pages/38_Stock_Prediction.py",
        ),
        Project(
            key="portfolio_optimization",
            label="Portfolio Optimization",
            description="Efficient frontier, max Sharpe and min volatility portfolios",
            tech=["Python", "NumPy", "SciPy", "Plotly"],
            page_link="pages/36_Portfolio_Optimization.py",
        ),
        Project(
            key="algo_trading",
            label="Algo Trading Backtest",
            description="SMA crossover and momentum strategies with equity curves",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/37_Algo_Trading.py",
        ),
        Project(
            key="var_cvar",
            label="VaR & CVaR",
            description="Historical and parametric Value at Risk, Conditional VaR",
            tech=["Python", "yfinance", "NumPy", "SciPy"],
            page_link="pages/30_VaR_CVaR.py",
        ),
        Project(
            key="time_series",
            label="Time Series",
            description="Trend, seasonal, and residual decomposition with ACF",
            tech=["Python", "yfinance", "statsmodels"],
            page_link="pages/31_Time_Series.py",
        ),
        Project(
            key="anomaly_detection",
            label="Anomaly Detection",
            description="Z-score and Isolation Forest on stock returns",
            tech=["Python", "yfinance", "scikit-learn"],
            page_link="pages/33_Anomaly_Detection.py",
        ),
        Project(
            key="crypto_portfolio",
            label="Crypto Portfolio",
            description="Live crypto valuation, allocation pie, 24h change",
            tech=["Python", "CoinGecko API", "Plotly"],
            page_link="pages/23_Crypto_Portfolio.py",
        ),
        Project(
            key="stock_risk_scanner",
            label="Stock Risk Scanner",
            description="Full-stack portfolio risk analysis with FastAPI, Postgres, Docker, Claude",
            tech=["Python", "FastAPI", "PostgreSQL", "Docker", "Claude API"],
            page_link="pages/1_Stock_Risk_Scanner.py",
            is_capstone=True,
        ),
    ],

    "Analytics & Fintech": [
        Project(
            key="benchmark_rates",
            label="Benchmark Rates",
            description="SOFR, SONIA, and ESTR — fixed vs floating rate swap value",
            tech=["Python", "pandas", "Plotly"],
            page_link="pages/40_Benchmark_Rates.py",
        ),
        Project(
            key="currency_dashboard",
            label="Currency Dashboard",
            description="Live exchange rates, currency converter, rate comparison",
            tech=["Python", "Exchange Rate API", "Plotly"],
            page_link="pages/20_Currency_Dashboard.py",
        ),
        Project(
            key="sentiment_analysis",
            label="Sentiment Analysis",
            description="VADER and TextBlob applied to financial headlines",
            tech=["Python", "VADER", "TextBlob", "Plotly"],
            page_link="pages/32_Sentiment_Analysis.py",
        ),
        Project(
            key="market_insights",
            label="Market Insights",
            description="Sentiment-price correlation dashboard",
            tech=["Python", "yfinance", "VADER", "Plotly"],
            page_link="pages/39_Market_Insights.py",
        ),
        Project(
            key="esg_tracker",
            label="ESG Tracker",
            description="ESG score comparison, radar chart, sector averages",
            tech=["Python", "yfinance", "Plotly"],
            page_link="pages/25_ESG_Tracker.py",
        ),
        Project(
            key="loan_default",
            label="Loan Default Prediction",
            description="Logistic Regression and Random Forest classification",
            tech=["Python", "scikit-learn", "NumPy", "Plotly"],
            page_link="pages/34_Loan_Default.py",
        ),
        Project(
            key="clustering",
            label="Customer Clustering",
            description="K-Means and DBSCAN segmentation with editable data",
            tech=["Python", "scikit-learn", "NumPy", "Plotly"],
            page_link="pages/35_Clustering.py",
        ),
        Project(
            key="financial_reporting",
            label="Financial Reporting",
            description="Auto-generated stats, charts, and CSV export",
            tech=["Python", "yfinance", "pandas", "Plotly"],
            page_link="pages/26_Financial_Reporting.py",
        ),
        Project(
            key="bond_credit_aws",
            label="Bond/Credit Risk AWS",
            description="12-exercise arc — AWS fundamentals through Monte Carlo Credit VaR",
            tech=["Python", "AWS", "Terraform", "WebSockets", "Redis"],
            page_link="pages/40_Benchmark_Rates.py",
            is_capstone=True,
        ),
    ],

    "Geopolitics & risk": [
        Project(
            key="global_contagion",
            label="Global Contagion",
            description=(
                "Replay geopolitical shocks across a 3D globe — "
                "bond-yield contagion from Middle East to world markets"
            ),
            tech=["Python", "Streamlit", "pydeck", "pandas", "yfinance"],
            page_link="pages/70_Global_Contagion.py",
        ),
    ],

    "Tech demos & references": [
        Project(
            key="big_o",
            label="Big O Notation",
            description="Same problem, different complexities — log-log curves of Fibonacci and Pair-sum",
            tech=["Python", "Plotly", "pytest"],
            page_link="pages/60_Big_O.py",
        ),
        Project(
            key="etymology",
            label="Etymology",
            description="Force-directed graph of English word roots — Greek, Latin, and Proto-Indo-European",
            tech=["D3.js", "vanilla JS", "YAML"],
            page_link="pages/50_Etymology.py",
        ),
        Project(
            key="plotting_libraries",
            label="Plotting Libraries Compared",
            description="Same data rendered in Plotly, Matplotlib, Altair, and Bokeh side-by-side",
            tech=["Python", "Plotly", "Matplotlib", "Altair", "Bokeh"],
            page_link="pages/41_Plotting_Libraries.py",
        ),
    ],
}


FEATURED_KEYS = [
    "rent_vs_buy",
    "london_house_prices",
    "etymology",
    "big_o",
    "portfolio_optimization",
    "plotting_libraries",
]


def all_projects() -> list:
    """Flatten the categorised dict into a single list."""
    return [p for projs in PROJECTS_BY_CATEGORY.values() for p in projs]


def featured() -> list:
    """Return the featured projects in FEATURED_KEYS order."""
    by_key = {p.key: p for p in all_projects()}
    return [by_key[k] for k in FEATURED_KEYS if k in by_key]


def category_with_capstones_last(category: str) -> list:
    """Return projects for one category with capstones bumped to the end."""
    projs = PROJECTS_BY_CATEGORY.get(category, [])
    non_capstones = [p for p in projs if not p.is_capstone]
    capstones = [p for p in projs if p.is_capstone]
    return non_capstones + capstones
