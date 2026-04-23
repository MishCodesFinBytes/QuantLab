import logging
import anthropic
from src.scanner.models import RiskMetrics

logger = logging.getLogger(__name__)

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
            logger.warning("Anthropic client unavailable — will use fallback narrative")
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
            logger.exception("Claude API call failed — using fallback narrative")
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
