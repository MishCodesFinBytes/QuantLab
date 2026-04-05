import json

import boto3
import pytest
from moto import mock_aws

from credit_spreads import (
    bootstrap_default_probabilities,
    calculate_credit_spread,
    check_spread_threshold,
    publish_alert,
    send_to_queue,
)


class TestCreditSpread:
    def test_spread_is_corporate_minus_treasury(self):
        spread = calculate_credit_spread(corporate_yield=5.5, treasury_yield=4.0)
        assert spread == pytest.approx(1.5, abs=0.01)

    def test_negative_spread_possible(self):
        """Rare but possible (e.g., swap spreads went negative in 2015)."""
        spread = calculate_credit_spread(corporate_yield=3.8, treasury_yield=4.0)
        assert spread == pytest.approx(-0.2, abs=0.01)


class TestDefaultProbabilities:
    def test_basic_default_probability(self):
        """CDS spread of 100bps with 40% recovery → ~1.67% annual default prob."""
        cds_spreads = {"1Y": 100}
        recovery_rate = 0.40

        probs = bootstrap_default_probabilities(cds_spreads, recovery_rate)

        assert "1Y" in probs
        assert 0.01 < probs["1Y"] < 0.03

    def test_higher_spread_higher_default_prob(self):
        low = bootstrap_default_probabilities({"5Y": 50}, 0.40)
        high = bootstrap_default_probabilities({"5Y": 200}, 0.40)
        assert high["5Y"] > low["5Y"]

    def test_term_structure(self):
        """Longer tenors should have higher cumulative default probability."""
        cds_spreads = {"1Y": 100, "3Y": 120, "5Y": 150}
        probs = bootstrap_default_probabilities(cds_spreads, 0.40)
        assert probs["5Y"] > probs["3Y"] > probs["1Y"]

    def test_zero_spread_zero_default(self):
        probs = bootstrap_default_probabilities({"1Y": 0}, 0.40)
        assert probs["1Y"] == pytest.approx(0.0, abs=0.001)


class TestSpreadThreshold:
    def test_above_threshold(self):
        assert check_spread_threshold(180, threshold=150) is True

    def test_below_threshold(self):
        assert check_spread_threshold(120, threshold=150) is False


class TestSQS:
    @mock_aws
    def test_send_to_queue(self):
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="credit-calc-queue")
        queue_url = queue["QueueUrl"]

        send_to_queue(
            queue_url=queue_url,
            message={"rating": "BBB", "spread": 180},
            sqs_client=sqs,
        )

        msgs = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        body = json.loads(msgs["Messages"][0]["Body"])
        assert body["rating"] == "BBB"
        assert body["spread"] == 180


class TestSNS:
    @mock_aws
    def test_publish_alert(self):
        sns = boto3.client("sns", region_name="us-east-1")
        topic = sns.create_topic(Name="spread-alerts")
        topic_arn = topic["TopicArn"]

        result = publish_alert(
            topic_arn=topic_arn,
            message="BBB spreads at 180bps — above 150bps threshold",
            sns_client=sns,
        )

        assert "MessageId" in result
