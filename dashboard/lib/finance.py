"""Shared finance calculation functions for dashboard pages."""

from __future__ import annotations
import numpy as np


def credit_card_payoff(balance: float, apr: float, monthly_payment: float) -> dict:
    """Calculate credit card payoff schedule.

    Returns dict with months, total_interest, schedule (list of dicts).
    """
    monthly_rate = apr / 100 / 12
    remaining = balance
    schedule = []
    total_interest = 0.0
    month = 0

    while remaining > 0.01 and month < 600:
        month += 1
        interest = remaining * monthly_rate
        total_interest += interest
        principal = min(monthly_payment - interest, remaining)
        if principal <= 0:
            return {"months": -1, "total_interest": 0, "schedule": [],
                    "error": "Payment too low to cover interest"}
        remaining -= principal
        schedule.append({
            "month": month, "payment": principal + interest,
            "principal": principal, "interest": interest,
            "balance": max(remaining, 0),
        })

    return {"months": month, "total_interest": round(total_interest, 2), "schedule": schedule}


def loan_amortization(principal: float, annual_rate: float, years: int,
                      payments_per_year: int = 12) -> list[dict]:
    """Generate loan amortization schedule."""
    rate = annual_rate / 100 / payments_per_year
    n = years * payments_per_year
    if rate == 0:
        payment = principal / n
    else:
        payment = principal * rate * (1 + rate) ** n / ((1 + rate) ** n - 1)

    balance = principal
    schedule = []
    for i in range(1, n + 1):
        interest = balance * rate
        princ = payment - interest
        balance -= princ
        schedule.append({
            "period": i, "payment": round(payment, 2),
            "principal": round(princ, 2), "interest": round(interest, 2),
            "balance": round(max(balance, 0), 2),
        })
    return schedule


def retirement_projection(current_savings: float, monthly_contribution: float,
                          annual_return: float, years: int,
                          simulations: int = 0, vol: float = 0.15) -> dict:
    """Project retirement savings. If simulations > 0, runs Monte Carlo."""
    months = years * 12
    monthly_return = annual_return / 100 / 12

    # Deterministic projection
    balances = [current_savings]
    for _ in range(months):
        balances.append(balances[-1] * (1 + monthly_return) + monthly_contribution)

    result = {"deterministic": balances, "final": round(balances[-1], 2)}

    if simulations > 0:
        rng = np.random.default_rng(42)
        monthly_vol = vol / np.sqrt(12)
        all_paths = np.zeros((simulations, months + 1))
        all_paths[:, 0] = current_savings
        for m in range(months):
            returns = rng.normal(monthly_return, monthly_vol, simulations)
            all_paths[:, m + 1] = all_paths[:, m] * (1 + returns) + monthly_contribution

        result["p10"] = np.percentile(all_paths, 10, axis=0).tolist()
        result["p50"] = np.percentile(all_paths, 50, axis=0).tolist()
        result["p90"] = np.percentile(all_paths, 90, axis=0).tolist()
        result["finals"] = all_paths[:, -1].tolist()

    return result


def compound_growth(initial: float, monthly_add: float, annual_rate: float,
                    years: int) -> list[dict]:
    """Calculate compound growth month by month."""
    monthly_rate = annual_rate / 100 / 12
    balance = initial
    schedule = []
    total_contributions = initial

    for month in range(1, years * 12 + 1):
        interest = balance * monthly_rate
        balance += interest + monthly_add
        total_contributions += monthly_add
        if month % 12 == 0 or month == 1:
            schedule.append({
                "year": month / 12, "balance": round(balance, 2),
                "contributions": round(total_contributions, 2),
                "growth": round(balance - total_contributions, 2),
            })

    return schedule


def budget_summary(income: float, expenses: dict[str, float]) -> dict:
    """Summarise a budget: total expenses, surplus, percentages."""
    total = sum(expenses.values())
    surplus = income - total
    breakdown = [
        {"category": k, "amount": v, "pct": round(v / income * 100, 1) if income > 0 else 0}
        for k, v in sorted(expenses.items(), key=lambda x: -x[1])
    ]
    return {
        "income": income, "total_expenses": round(total, 2),
        "surplus": round(surplus, 2), "breakdown": breakdown,
    }
