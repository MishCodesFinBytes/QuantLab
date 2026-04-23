def _rag(val: float, t1: float, t2: float) -> str:
    """t1 < t2 → lower is worse; t1 > t2 → higher is worse."""
    if t1 < t2:
        return "🔴" if val < t1 else ("🟡" if val < t2 else "🟢")
    return "🔴" if val > t1 else ("🟡" if val > t2 else "🟢")


def var_color(val: float) -> str:      return _rag(val, -3, -1.5)
def cvar_color(val: float) -> str:     return _rag(val, -4, -2)
def drawdown_color(val: float) -> str: return _rag(val, -20, -10)
def volatility_color(val: float) -> str: return _rag(val, 30, 20)
def sharpe_color(val: float) -> str:   return _rag(val, 0.5, 1)
