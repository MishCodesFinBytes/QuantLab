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
