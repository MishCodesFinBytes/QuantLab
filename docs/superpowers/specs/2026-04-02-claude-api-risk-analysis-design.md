# Task 6: Claude API — AI-Powered Risk Analysis — Design Spec

**Date:** 2026-04-02
**Exercise:** `exercises/06-claude-api/`
**Concept:** Anthropic SDK, messages API, system prompts, model selection, graceful error handling. Build a risk analyst that turns portfolio metrics into plain-English commentary.

---

## Class: RiskAnalyst

### Constructor
| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| model | str | "claude-sonnet-4-6" | Anthropic model ID |

### analyze method
| | |
|--|--|
| **Signature** | `def analyze(self, tickers: list[str], metrics: dict) -> str` |
| **Purpose** | Generate plain-English risk narrative from portfolio metrics |
| **System prompt** | Senior risk analyst persona, 3-4 sentences, plain English |
| **User prompt** | Formatted tickers + metrics (VaR, CVaR, max drawdown, vol, Sharpe) |
| **Error handling** | Returns fallback string with key metrics on any API exception |

### Input metrics dict
| Key | Type | Example | Description |
|-----|------|---------|-------------|
| var_pct | float | -2.15 | Value at Risk (95%) as percentage |
| cvar_pct | float | -3.42 | Conditional VaR / Expected Shortfall |
| max_drawdown_pct | float | -18.7 | Maximum peak-to-trough decline |
| annualized_vol | float | 22.5 | Annualized volatility percentage |
| sharpe_ratio | float | 0.85 | Risk-adjusted return ratio |

## Anthropic SDK Features Covered

- `anthropic.Anthropic()` — client initialization (uses ANTHROPIC_API_KEY env var)
- `client.messages.create()` — messages API call
- `system` parameter — system prompt (separate from messages)
- `messages` parameter — user message list
- `model` parameter — model selection
- `max_tokens` — output length control
- `response.content[0].text` — extracting text from response
- Graceful degradation on API errors

## Tests (5 total)

1. `test_generate_returns_string` — mock API, verify result is non-empty string
2. `test_uses_system_prompt` — verify system kwarg contains "risk"
3. `test_includes_metrics_in_prompt` — verify user message contains VaR and tickers
4. `test_fallback_on_api_error` — API raises, verify fallback string with "unable"
5. `test_custom_model` — verify constructor model passed to API call

## Test Infrastructure
- `mock_anthropic` fixture — patches `anthropic.Anthropic`, returns mock client with canned response
- `sample_metrics` fixture — realistic risk metrics dict
- All tests fully mocked — no real API calls, no API key needed for tests

## File Structure

```
exercises/06-claude-api/
├── pyproject.toml              # anthropic SDK, pytest
├── src/
│   └── analyst.py              # RiskAnalyst class
└── tests/
    └── test_analyst.py         # 5 tests
```

## TDD Flow

1. Create pyproject.toml
2. Write failing tests (5 tests)
3. Run tests — verify they fail (ModuleNotFoundError)
4. Implement analyst.py
5. Run tests — verify all 5 pass
6. Commit to quant_lab (working branch)
7. Teaching conversation (Anthropic SDK, prompt engineering)
8. Write blog post to finbytes_git
9. Commit blog post (working → master via merge)
