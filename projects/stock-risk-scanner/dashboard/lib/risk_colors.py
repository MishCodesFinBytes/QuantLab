def var_color(val: float) -> str:
    if val < -3:
        return "🔴"
    elif val < -1.5:
        return "🟡"
    return "🟢"


def cvar_color(val: float) -> str:
    if val < -4:
        return "🔴"
    elif val < -2:
        return "🟡"
    return "🟢"


def drawdown_color(val: float) -> str:
    if val < -20:
        return "🔴"
    elif val < -10:
        return "🟡"
    return "🟢"


def volatility_color(val: float) -> str:
    if val > 30:
        return "🔴"
    elif val > 20:
        return "🟡"
    return "🟢"


def sharpe_color(val: float) -> str:
    if val > 1:
        return "🟢"
    elif val > 0.5:
        return "🟡"
    return "🔴"
