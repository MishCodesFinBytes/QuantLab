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
