# Stock Risk Scanner — Core Modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the core scanner modules (models, risk calculations, market data, narrative, orchestrator) as pure Python with full test coverage, adapted from exercises 01-06.

**Architecture:** Four focused modules connected through Pydantic models. A thin orchestrator calls them in sequence: fetch prices → calculate risk → generate narrative → return result. Each module is independently testable. External services (yfinance, Claude API) are mocked in tests.

**Tech Stack:** Python 3.11, Pydantic 2, NumPy, Pandas, yfinance, Anthropic SDK, pytest

---

## File Structure

```
projects/stock-risk-scanner/
├── pyproject.toml
├── src/scanner/
│   ├── __init__.py
│   ├── models.py
│   ├── risk.py
│   ├── market_data.py
│   ├── narrative.py
│   └── scanner.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_risk.py
    ├── test_market_data.py
    ├── test_narrative.py
    └── test_scanner.py
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `projects/stock-risk-scanner/pyproject.toml`
- Create: `projects/stock-risk-scanner/src/scanner/__init__.py`
- Create: `projects/stock-risk-scanner/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/src/scanner
mkdir -p C:/codebase/quant_lab/projects/stock-risk-scanner/tests
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "stock-risk-scanner"
version = "0.1.0"
description = "Portfolio risk scanner with AI-generated narratives"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.9.0",
    "yfinance>=0.2.40",
    "numpy>=1.26.0",
    "pandas>=2.0.0",
    "anthropic>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Create __init__.py files**

```python
# projects/stock-risk-scanner/src/scanner/__init__.py
# (empty)
```

```python
# projects/stock-risk-scanner/tests/__init__.py
# (empty)
```

- [ ] **Step 4: Install dev dependencies**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
pip install -e ".[dev]"
```

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): project scaffold with dependencies"
```

---

### Task 2: Pydantic Models (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_models.py`
- Create: `projects/stock-risk-scanner/src/scanner/models.py`

- [ ] **Step 1: Write failing tests for models**

```python
# projects/stock-risk-scanner/tests/test_models.py
import pytest
from datetime import datetime, UTC


class TestScanRequest:
    def test_valid_request(self):
        from src.scanner.models import ScanRequest

        req = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        assert req.tickers == ["AAPL", "MSFT"]
        assert req.weights == [0.6, 0.4]
        assert req.period == "1y"

    def test_tickers_uppercased(self):
        from src.scanner.models import ScanRequest

        req = ScanRequest(tickers=["aapl", "msft"], weights=[0.5, 0.5])
        assert req.tickers == ["AAPL", "MSFT"]

    def test_mismatched_lengths_raises(self):
        from src.scanner.models import ScanRequest

        with pytest.raises(ValueError, match="length"):
            ScanRequest(tickers=["AAPL", "MSFT"], weights=[1.0])

    def test_weights_not_summing_to_one_raises(self):
        from src.scanner.models import ScanRequest

        with pytest.raises(ValueError, match="sum"):
            ScanRequest(tickers=["AAPL"], weights=[0.5])


class TestRiskMetrics:
    def test_risk_metrics_fields(self):
        from src.scanner.models import RiskMetrics

        metrics = RiskMetrics(
            var_pct=-2.15,
            cvar_pct=-3.42,
            max_drawdown_pct=-18.7,
            volatility_pct=22.5,
            sharpe_ratio=1.2,
        )
        assert metrics.var_pct == pytest.approx(-2.15)
        assert metrics.sharpe_ratio == pytest.approx(1.2)


class TestScanResult:
    def test_scan_result_fields(self):
        from src.scanner.models import RiskMetrics, ScanResult

        metrics = RiskMetrics(
            var_pct=-2.0, cvar_pct=-3.0, max_drawdown_pct=-15.0,
            volatility_pct=20.0, sharpe_ratio=0.8,
        )
        result = ScanResult(
            tickers=["AAPL"], weights=[1.0], metrics=metrics,
            narrative="Test", generated_at=datetime.now(UTC),
        )
        assert result.tickers == ["AAPL"]
        assert result.metrics.var_pct == pytest.approx(-2.0)
        assert result.narrative == "Test"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.models'`

- [ ] **Step 3: Implement models.py**

```python
# projects/stock-risk-scanner/src/scanner/models.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_models.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): Pydantic models with validation"
```

---

### Task 3: Risk Calculations (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_risk.py`
- Create: `projects/stock-risk-scanner/src/scanner/risk.py`

- [ ] **Step 1: Write failing tests for risk module**

```python
# projects/stock-risk-scanner/tests/test_risk.py
import pytest
import numpy as np
import pandas as pd


class TestCalculateRiskMetrics:
    def _make_prices(self, data: dict, n_days: int = 252) -> pd.DataFrame:
        """Helper to create a price DataFrame from daily return sequences."""
        np.random.seed(42)
        df = {}
        for ticker, (start, daily_mean, daily_std) in data.items():
            returns = np.random.normal(daily_mean, daily_std, n_days)
            prices = [start]
            for r in returns:
                prices.append(prices[-1] * (1 + r))
            df[ticker] = prices
        return pd.DataFrame(df)

    def test_var_and_cvar(self):
        from src.scanner.risk import calculate_risk_metrics

        # Create a predictable declining asset
        prices = pd.DataFrame({"A": np.linspace(100, 80, 252)})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        # Steadily declining: VaR should be negative
        assert metrics.var_pct < 0
        # CVaR should be worse (more negative) than VaR
        assert metrics.cvar_pct <= metrics.var_pct

    def test_max_drawdown(self):
        from src.scanner.risk import calculate_risk_metrics

        # Price goes 100 -> 120 -> 90 -> 110
        prices = pd.DataFrame({"A": [100.0, 110.0, 120.0, 90.0, 100.0, 110.0]})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        # Max drawdown: peak 120 to trough 90 = -25%
        assert metrics.max_drawdown_pct == pytest.approx(-25.0, abs=1.0)

    def test_sharpe_ratio_sign(self):
        from src.scanner.risk import calculate_risk_metrics

        # Upward trending asset should have positive Sharpe
        prices = pd.DataFrame({"A": np.linspace(100, 130, 252)})
        metrics = calculate_risk_metrics(prices, weights=[1.0])
        assert metrics.sharpe_ratio > 0

        # Downward trending asset should have negative Sharpe
        prices_down = pd.DataFrame({"A": np.linspace(100, 70, 252)})
        metrics_down = calculate_risk_metrics(prices_down, weights=[1.0])
        assert metrics_down.sharpe_ratio < 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_risk.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.risk'`

- [ ] **Step 3: Implement risk.py**

```python
# projects/stock-risk-scanner/src/scanner/risk.py
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

    # Max drawdown from cumulative returns
    cumulative = np.cumprod(1 + portfolio_returns)
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_risk.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): risk calculations with VaR, CVaR, drawdown, vol, Sharpe"
```

---

### Task 4: Market Data Fetcher (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_market_data.py`
- Create: `projects/stock-risk-scanner/src/scanner/market_data.py`

- [ ] **Step 1: Write failing tests for market data**

```python
# projects/stock-risk-scanner/tests/test_market_data.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


class TestFetchPrices:
    @patch("src.scanner.market_data.yf.download")
    def test_successful_fetch(self, mock_download):
        from src.scanner.market_data import fetch_prices

        # Simulate yfinance returning a MultiIndex DataFrame for 2 tickers
        dates = pd.date_range("2024-01-01", periods=5)
        mock_data = pd.DataFrame(
            {
                ("Close", "AAPL"): [150.0, 151.0, 152.0, 153.0, 154.0],
                ("Close", "MSFT"): [300.0, 301.0, 302.0, 303.0, 304.0],
            },
            index=dates,
        )
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_download.return_value = mock_data

        result = fetch_prices(["AAPL", "MSFT"], period="5d")
        assert list(result.columns) == ["AAPL", "MSFT"]
        assert len(result) == 5
        assert result["AAPL"].iloc[0] == 150.0

    @patch("src.scanner.market_data.yf.download")
    def test_empty_data_raises(self, mock_download):
        from src.scanner.market_data import fetch_prices

        mock_download.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No price data"):
            fetch_prices(["INVALID"], period="1y")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_market_data.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.market_data'`

- [ ] **Step 3: Implement market_data.py**

```python
# projects/stock-risk-scanner/src/scanner/market_data.py
import yfinance as yf
import pandas as pd


def fetch_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f"No price data returned for {tickers}")

    # yfinance returns MultiIndex columns for multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        # Single ticker — no MultiIndex
        prices = data[["Close"]].rename(columns={"Close": tickers[0]})

    # Drop rows where all values are NaN, forward-fill remaining gaps
    prices = prices.dropna(how="all").ffill()

    if prices.empty:
        raise ValueError(f"No price data returned for {tickers}")

    return prices
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_market_data.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): market data fetcher with yfinance"
```

---

### Task 5: Narrative Generator (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_narrative.py`
- Create: `projects/stock-risk-scanner/src/scanner/narrative.py`

- [ ] **Step 1: Write failing tests for narrative module**

```python
# projects/stock-risk-scanner/tests/test_narrative.py
import pytest
from unittest.mock import patch, MagicMock


def _make_metrics():
    from src.scanner.models import RiskMetrics

    return RiskMetrics(
        var_pct=-2.15, cvar_pct=-3.42, max_drawdown_pct=-18.7,
        volatility_pct=22.5, sharpe_ratio=1.2,
    )


class TestRiskNarrator:
    @patch("src.scanner.narrative.anthropic.Anthropic")
    def test_generate_with_api(self, mock_anthropic_cls):
        from src.scanner.narrative import RiskNarrator

        # Set up mock client and response
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="The portfolio shows moderate risk.")]
        mock_client.messages.create.return_value = mock_response

        narrator = RiskNarrator()
        result = narrator.generate(["AAPL", "MSFT"], _make_metrics())
        assert result == "The portfolio shows moderate risk."
        mock_client.messages.create.assert_called_once()

    @patch("src.scanner.narrative.anthropic.Anthropic")
    def test_generate_api_error_returns_fallback(self, mock_anthropic_cls):
        from src.scanner.narrative import RiskNarrator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        narrator = RiskNarrator()
        result = narrator.generate(["AAPL"], _make_metrics())
        assert "VaR" in result
        assert "-2.15" in result

    @patch("src.scanner.narrative.anthropic.Anthropic")
    def test_generate_no_api_key_returns_fallback(self, mock_anthropic_cls):
        from src.scanner.narrative import RiskNarrator

        mock_anthropic_cls.side_effect = Exception("No API key")

        narrator = RiskNarrator()
        assert narrator.client is None
        result = narrator.generate(["AAPL", "MSFT"], _make_metrics())
        assert "AAPL, MSFT" in result
        assert "VaR" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_narrative.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.narrative'`

- [ ] **Step 3: Implement narrative.py**

```python
# projects/stock-risk-scanner/src/scanner/narrative.py
import anthropic
from src.scanner.models import RiskMetrics

SYSTEM_PROMPT = (
    "You are a senior risk analyst at an investment bank. "
    "Given portfolio risk metrics, provide a clear 3-4 sentence summary "
    "in plain English. Focus on what the numbers mean for the investor, "
    "not on the math."
)


class RiskNarrator:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        try:
            self.client = anthropic.Anthropic()
        except Exception:
            self.client = None

    def generate(self, tickers: list[str], metrics: RiskMetrics) -> str:
        if self.client is None:
            return self._fallback(tickers, metrics)

        user_prompt = (
            f"Portfolio: {', '.join(tickers)}\n"
            f"VaR (95%): {metrics.var_pct:.2f}%\n"
            f"CVaR: {metrics.cvar_pct:.2f}%\n"
            f"Max Drawdown: {metrics.max_drawdown_pct:.2f}%\n"
            f"Volatility: {metrics.volatility_pct:.2f}%\n"
            f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}"
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception:
            return self._fallback(tickers, metrics)

    def _fallback(self, tickers: list[str], metrics: RiskMetrics) -> str:
        return (
            f"Portfolio {', '.join(tickers)}: "
            f"VaR {metrics.var_pct:.2f}%, "
            f"CVaR {metrics.cvar_pct:.2f}%, "
            f"Max Drawdown {metrics.max_drawdown_pct:.2f}%, "
            f"Volatility {metrics.volatility_pct:.2f}%, "
            f"Sharpe {metrics.sharpe_ratio:.2f}"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_narrative.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): Claude narrative generator with fallback"
```

---

### Task 6: Scanner Orchestrator (TDD)

**Files:**
- Create: `projects/stock-risk-scanner/tests/test_scanner.py`
- Create: `projects/stock-risk-scanner/src/scanner/scanner.py`

- [ ] **Step 1: Write failing test for orchestrator**

```python
# projects/stock-risk-scanner/tests/test_scanner.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


class TestScan:
    @patch("src.scanner.scanner.RiskNarrator")
    @patch("src.scanner.scanner.fetch_prices")
    def test_full_pipeline(self, mock_fetch, mock_narrator_cls):
        from src.scanner.models import ScanRequest
        from src.scanner.scanner import scan

        # Mock fetch_prices to return synthetic price data
        dates = pd.date_range("2024-01-01", periods=252)
        mock_fetch.return_value = pd.DataFrame(
            {"AAPL": np.linspace(150, 170, 252), "MSFT": np.linspace(300, 320, 252)},
            index=dates,
        )

        # Mock narrator
        mock_narrator = mock_narrator_cls.return_value
        mock_narrator.generate.return_value = "Portfolio looks healthy."

        request = ScanRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        result = scan(request)

        assert result.tickers == ["AAPL", "MSFT"]
        assert result.weights == [0.6, 0.4]
        assert result.metrics.var_pct < 0  # VaR should be negative
        assert result.metrics.volatility_pct > 0
        assert result.narrative == "Portfolio looks healthy."
        assert result.generated_at is not None

        mock_fetch.assert_called_once_with(["AAPL", "MSFT"], "1y")
        mock_narrator.generate.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_scanner.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.scanner.scanner'`

- [ ] **Step 3: Implement scanner.py**

```python
# projects/stock-risk-scanner/src/scanner/scanner.py
from datetime import datetime, UTC
from src.scanner.models import ScanRequest, ScanResult
from src.scanner.risk import calculate_risk_metrics
from src.scanner.market_data import fetch_prices
from src.scanner.narrative import RiskNarrator


def scan(request: ScanRequest) -> ScanResult:
    prices = fetch_prices(request.tickers, request.period)
    metrics = calculate_risk_metrics(prices, request.weights)
    narrator = RiskNarrator()
    narrative = narrator.generate(request.tickers, metrics)

    return ScanResult(
        tickers=request.tickers,
        weights=request.weights,
        metrics=metrics,
        narrative=narrative,
        generated_at=datetime.now(UTC),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/test_scanner.py -v
```

Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): orchestrator wiring fetch → risk → narrative"
```

---

### Task 7: Full Test Suite Verification

- [ ] **Step 1: Run all tests**

```bash
cd C:/codebase/quant_lab/projects/stock-risk-scanner
python -m pytest tests/ -v
```

Expected: 13 passed (4 models + 3 risk + 2 market_data + 3 narrative + 1 scanner)

- [ ] **Step 2: Final commit**

```bash
cd C:/codebase/quant_lab
git add projects/stock-risk-scanner/
git commit -m "feat(scanner): capstone sub-project A complete — all 13 tests pass"
```
