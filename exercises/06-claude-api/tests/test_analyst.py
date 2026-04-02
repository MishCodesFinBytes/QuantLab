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
