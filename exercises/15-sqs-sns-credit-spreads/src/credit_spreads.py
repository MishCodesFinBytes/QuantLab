"""Credit spread calculation, CDS default-probability bootstrapping,
and AWS messaging (SQS/SNS) for credit-risk alerting.

Credit spread
-------------
spread = corporate bond yield − treasury yield (same maturity).
Measured in basis points (bps). 1% = 100 bps.
Represents the market's price for credit risk.

CDS and default probabilities
-----------------------------
CDS spread = annual premium paid for default protection.
Under a hazard-rate model with constant hazard λ:
    CDS_spread ≈ λ × (1 − recovery_rate)
    → λ ≈ CDS_spread / (1 − recovery_rate)
    → P(default by T) = 1 − exp(−λT)

This is a standard simplification. Full bootstrapping uses the exact CDS
premium/protection cash-flow legs, but the closed-form approximation is
what desks reach for when they want a quick read on implied default risk.
"""

from __future__ import annotations

import json

import boto3
import numpy as np

CDS_TENOR_YEARS = {
    "1Y": 1.0,
    "2Y": 2.0,
    "3Y": 3.0,
    "5Y": 5.0,
    "7Y": 7.0,
    "10Y": 10.0,
}


def calculate_credit_spread(corporate_yield: float, treasury_yield: float) -> float:
    """Credit spread in percentage points (corporate yield minus treasury)."""
    return round(corporate_yield - treasury_yield, 4)


def fetch_credit_indices(api_key: str) -> dict[str, float]:
    """Fetch latest ICE BofA credit-spread indices from FRED, by rating.

    Returns a dict mapping rating label to spread in basis points.
    """
    from datetime import date, timedelta

    from fredapi import Fred

    fred = Fred(api_key=api_key)
    today = date.today()
    start = today - timedelta(days=7)

    series = {
        "BAMLC0A1CAAA": "AAA",
        "BAMLC0A2CAA": "AA",
        "BAMLC0A3CA": "A",
        "BAMLC0A4CBBB": "BBB",
        "BAMLH0A1HYBB": "BB",
        "BAMLH0A2HYB": "B",
    }

    spreads: dict[str, float] = {}
    for series_id, rating in series.items():
        data = fred.get_series(series_id, observation_start=start, observation_end=today)
        data = data.dropna()
        if len(data) > 0:
            spreads[rating] = round(float(data.iloc[-1]) * 100, 2)

    return spreads


def bootstrap_default_probabilities(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Bootstrap cumulative default probabilities from CDS spreads.

    Uses the hazard-rate approximation:
        λ ≈ CDS_spread_bps / (10000 × (1 − R))
        P(default by T) = 1 − exp(−λ × T)

    Args:
        cds_spreads: Tenor label → CDS spread in bps.
        recovery_rate: Expected recovery rate, 0..1.

    Returns:
        Tenor label → cumulative default probability.
    """
    lgd = 1.0 - recovery_rate
    probs: dict[str, float] = {}

    for tenor, spread_bps in cds_spreads.items():
        years = CDS_TENOR_YEARS.get(tenor, float(tenor.replace("Y", "")))
        hazard_rate = (spread_bps / 10000.0) / lgd
        cum_default_prob = 1.0 - np.exp(-hazard_rate * years)
        probs[tenor] = round(float(cum_default_prob), 6)

    return probs


def check_spread_threshold(spread_bps: float, threshold: float) -> bool:
    """Return True if the observed spread exceeds the alert threshold."""
    return spread_bps > threshold


def send_to_queue(queue_url: str, message: dict, sqs_client=None) -> dict:
    """Send a JSON message to an SQS queue."""
    sqs = sqs_client or boto3.client("sqs")
    return sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
    )


def publish_alert(topic_arn: str, message: str, sns_client=None) -> dict:
    """Publish a credit-spread alert to an SNS topic."""
    sns = sns_client or boto3.client("sns")
    return sns.publish(
        TopicArn=topic_arn,
        Subject="Credit Spread Alert",
        Message=message,
    )
