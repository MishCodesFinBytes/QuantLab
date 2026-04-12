# Claude API Risk Analysis — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Learn the Anthropic SDK through TDD, building a RiskAnalyst class that generates plain-English risk commentary from portfolio metrics.

**Architecture:** Single class (`RiskAnalyst`) with one method (`analyze`). Takes tickers and metrics dict, calls Claude API with a system prompt (risk analyst persona) and formatted user prompt, returns narrative string. Graceful fallback on API errors. All tests mock the Anthropic client.

**Tech Stack:** Python 3.11+, anthropic SDK (>=0.40.0), pytest (>=8.0.0)

---

## File Structure

```
exercises/06-claude-api/
├── pyproject.toml              # project config, deps, pytest settings
├── src/
│   └── analyst.py              # RiskAnalyst class
└── tests/
    └── test_analyst.py         # 5 tests
```

---

### Task 1: Project Setup

**Files:**
- Create: `exercises/06-claude-api/pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "claude-api-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["anthropic>=0.40.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["analyst"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p exercises/06-claude-api/src exercises/06-claude-api/tests
```

---

### Task 2: Write Failing Tests

**Files:**
- Create: `exercises/06-claude-api/tests/test_analyst.py`

- [ ] **Step 1: Write all 5 tests**

```python
import pytest
from unittest.mock import patch, MagicMock
from analyst import RiskAnalyst


@pytest.fixture
def mock_anthropic():
    with patch("analyst.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="The portfolio shows elevated risk due to concentration.")]
        mock_client.messages.create.return_value = mock_response
        yield mock_client


@pytest.fixture
def analyst():
    return RiskAnalyst()


@pytest.fixture
def sample_metrics():
    return {
        "var_pct": -2.15,
        "cvar_pct": -3.42,
        "max_drawdown_pct": -18.7,
        "annualized_vol": 22.5,
        "sharpe_ratio": 0.85,
    }


class TestRiskAnalyst:
    def test_generate_returns_string(self, mock_anthropic, analyst, sample_metrics):
        result = analyst.analyze(tickers=["AAPL", "MSFT"], metrics=sample_metrics)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_uses_system_prompt(self, mock_anthropic, analyst, sample_metrics):
        analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "system" in call_kwargs
        assert "risk" in call_kwargs["system"].lower()

    def test_includes_metrics_in_prompt(self, mock_anthropic, analyst, sample_metrics):
        analyst.analyze(tickers=["AAPL", "MSFT"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        user_msg = call_kwargs["messages"][0]["content"]
        assert "VaR" in user_msg or "var" in user_msg.lower()
        assert "AAPL" in user_msg

    def test_fallback_on_api_error(self, analyst, sample_metrics):
        with patch("analyst.anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = Exception("API timeout")
            result = analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
            assert "unable" in result.lower() or "error" in result.lower()

    def test_custom_model(self, mock_anthropic, sample_metrics):
        analyst = RiskAnalyst(model="claude-haiku-4-5-20251001")
        analyst.analyze(tickers=["AAPL"], metrics=sample_metrics)
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
```

- [ ] **Step 2: Install dependencies and run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\06-claude-api
pip install -e ".[dev]"
python -m pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'analyst'`

---

### Task 3: Implement analyst.py

**Files:**
- Create: `exercises/06-claude-api/src/analyst.py`

- [ ] **Step 1: Implement RiskAnalyst class**

```python
import anthropic


class RiskAnalyst:
    """AI-powered risk analyst using Claude API."""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    def analyze(self, tickers: list[str], metrics: dict) -> str:
        """Generate a plain-English risk narrative from portfolio metrics.

        Args:
            tickers: List of stock symbols in the portfolio.
            metrics: Dict with keys: var_pct, cvar_pct, max_drawdown_pct,
                     annualized_vol, sharpe_ratio.

        Returns:
            Risk narrative string. Falls back to generic message on API failure.
        """
        system_prompt = (
            "You are a senior risk analyst at an investment bank. "
            "Summarize portfolio risk in 3-4 sentences for a trader. "
            "Be direct, specific, and flag any concerning metrics. "
            "Use plain English, not jargon."
        )

        user_prompt = (
            f"Portfolio: {', '.join(tickers)}\n"
            f"VaR (95%): {metrics['var_pct']:.2f}%\n"
            f"CVaR (Expected Shortfall): {metrics['cvar_pct']:.2f}%\n"
            f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%\n"
            f"Annualized Volatility: {metrics['annualized_vol']:.2f}%\n"
            f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}"
        )

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception:
            return (
                f"Unable to generate AI analysis. Key metrics — "
                f"VaR: {metrics['var_pct']:.2f}%, "
                f"CVaR: {metrics['cvar_pct']:.2f}%, "
                f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%."
            )
```

- [ ] **Step 2: Run all tests to verify they pass**

```bash
cd C:\codebase\quant_lab\exercises\06-claude-api
python -m pytest -v
```

Expected: 5 passed

---

### Task 4: Commit

- [ ] **Step 1: Commit exercise to quant_lab**

```bash
cd C:\codebase\quant_lab
git add exercises/06-claude-api/
git commit -m "feat(exercises): 06 Claude API risk analyst"
```

---

### Task 5: Understand It — Teaching Conversation

No code changes. Interactive discussion covering:

- **Anthropic SDK** — client, messages.create, system vs user prompts
- **Model selection** — Opus vs Sonnet vs Haiku: cost/speed/quality trade-offs
- **Prompt engineering** — specificity, tone, constraints for financial output
- **Structured output** — getting JSON back from Claude (for future use)
- **Error handling** — timeouts, rate limits, graceful degradation
- **API key management** — env vars, .env files, never in code

---

### Task 6: Document It — Write Blog Post

**Files:**
- Create: `C:\codebase\finbytes_git\docs\_posts\2026-04-02-claude-api-ai-risk-analysis.html`

- [ ] **Step 1: Write the blog post**

Use this frontmatter (clean format):

```yaml
---
layout: post
title: "Claude API — AI-Powered Risk Analysis"
date: 2026-04-02
tags: [claude, anthropic, ai, risk-analysis, finance, python, quant-lab]
categories:
- Python fundamentals
permalink: "/2026/04/02/claude-api-ai-risk-analysis/"
---
```

Sections to cover:
- What the Anthropic SDK does and how messages.create works
- System prompts vs user prompts — the risk analyst persona
- Formatting financial metrics into clear prompts
- Model selection — Opus/Sonnet/Haiku trade-offs
- Graceful degradation — fallback when the API is unavailable
- Testing with mocks — no API key needed for tests
- Link to the exercise code in quant_lab repo

---

### Task 7: Commit Blog Post

- [ ] **Step 1: Commit blog post in finbytes_git**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-02-claude-api-ai-risk-analysis.html
git commit -m "post: Claude API — AI-powered risk analysis"
```

- [ ] **Step 2: Push working branch**

```bash
git push origin working
```

- [ ] **Step 3: Merge to master and push**

```bash
git checkout master
git merge working --no-edit
git push origin master
git checkout working
```

- [ ] **Step 4: Verify blog post is live**

Check: `https://mish-codes.github.io/FinBytes/2026/04/02/claude-api-ai-risk-analysis/`

---

### Task 8: Commit quant_lab docs and push

- [ ] **Step 1: Commit spec and plan files**

```bash
cd C:\codebase\quant_lab
git add docs/superpowers/specs/2026-04-02-claude-api-risk-analysis-design.md
git add docs/superpowers/plans/2026-04-02-claude-api-risk-analysis.md
git push origin working
```

- [ ] **Step 2: Create PR from working to master**

```bash
gh pr create --title "feat: exercise 06 Claude API risk analyst" --body "..." --base master --head working
```

- [ ] **Step 3: Merge PR and sync locally**

After merge on GitHub:

```bash
git fetch origin
git checkout master && git pull origin master
git checkout working
```
