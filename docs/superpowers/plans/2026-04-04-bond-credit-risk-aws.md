# QuantLab Phase 2: Bond Pricing & Credit Risk on AWS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 12 exercises (09-20) and 2 capstone projects teaching AWS cloud services and quantitative fixed income/credit risk, extending QuantLab Phase 1.

**Architecture:** Learn-by-building. Each exercise pairs an AWS concept with a finance concept, delivering business context, math, code (TDD), and a blog post. Capstone A (Bond Pricing Engine) assembles exercises 09-14. Capstone B (Credit Risk Platform) assembles exercises 15-20 and imports from A.

**Tech Stack:** Python 3.11+, pytest, Pydantic v2, FastAPI, boto3, AWS (IAM, S3, RDS, Lambda, API Gateway, SQS, SNS, ElastiCache, CloudWatch), Terraform, GitHub Actions, FRED API, scipy, numpy, pandas, Anthropic SDK, SQLAlchemy, Alembic, moto, Streamlit

**Spec:** `docs/superpowers/specs/2026-04-04-bond-credit-risk-aws-design.md`

---

## Repos

| Repo | Path | Purpose |
|------|------|---------|
| quant_lab | `C:\codebase\quant_lab` | Exercises + capstone project code |
| finbytes_git | `C:\codebase\finbytes_git` | Blog posts |

## Directory Structure

```
quant_lab/
├── exercises/
│   ├── 09-aws-fundamentals/
│   │   ├── src/
│   │   │   └── treasury_yields.py
│   │   ├── tests/
│   │   │   └── test_treasury_yields.py
│   │   └── pyproject.toml
│   ├── 10-s3-data-ingestion/
│   │   ├── src/
│   │   │   └��─ s3_ingestion.py
│   │   ├── tests/
│   │   │   └── test_s3_ingestion.py
│   │   └── pyproject.toml
│   ├── 11-rds-postgresql/
│   │   ├── src/
│   │   │   ├── models.py
│   │   │   └── db.py
│   │   ├── tests/
│   │   │   └── test_db.py
│   │   ├── alembic/
│   │   ├── alembic.ini
│   │   └── pyproject.toml
│   ├── 12-lambda-api-gateway/
│   │   ├── src/
│   │   │   ├── bootstrap.py
│   │   │   └── handler.py
│   │   ├── tests/
│   ��   │   └── test_bootstrap.py
│   │   ├── template.yaml
│   │   └── pyproject.toml
│   ├── 13-cicd-github-actions/
│   │   ├── src/
│   │   │   └── forward_rates.py
│   │   ├── tests/
│   │   │   └── test_forward_rates.py
│   │   ├── .github/
│   │   │   └── workflows/
│   │   │       └── deploy.yml
│   │   └── pyproject.toml
│   ├── 14-terraform-curve-fitting/
│   │   ├── src/
│   │   │   └── curve_fitting.py
│   │   ├── tests/
│   │   │   └── test_curve_fitting.py
│   │   ├── terraform/
│   │   │   ├── main.tf
│   │   │   ��── variables.tf
│   │   │   └── outputs.tf
│   │   └── pyproject.toml
│   ├── 15-sqs-sns-credit-spreads/
│   │   ├── src/
│   ��   │   └── credit_spreads.py
│   │   ├── tests/
│   │   │   └── test_credit_spreads.py
│   │   └── pyproject.toml
│   ├── 16-websockets-realtime/
│   │   ├── src/
│   │   │   └── ws_handler.py
│   │   ├── tests/
│   │   │   └── test_ws_handler.py
│   │   └── pyproject.toml
│   ├── 17-elasticache-redis/
│   │   ├── src/
│   │   │   └── cache.py
│   │   ├── tests/
│   ��   │   └── test_cache.py
│   │   └── pyproject.toml
│   ├── 18-terraform-advanced/
│   │   ├── src/
│   │   │   └── default_probabilities.py
│   │   ├── tests/
│   │   │   └── test_default_probabilities.py
│   │   ├── terraform/
│   │   │   ├── modules/
│   │   │   ├── environments/
│   │   │   └── main.tf
│   │   └── pyproject.toml
│   ├── 19-cloudwatch-oas/
│   │   ├── src/
│   │   │   └── oas.py
│   │   ├── tests/
│   │   │   └── test_oas.py
│   │   └── pyproject.toml
│   └── 20-integration-testing-var/
│       ├── src/
│       │   └── credit_var.py
│       ├── tests/
│       │   ├── test_credit_var.py
│       │   └── test_integration.py
│       └── pyproject.toml
└── projects/
    ├── bond-pricing-engine/
    ��   ├── src/engine/
    │   │   ├── __init__.py
    │   │   ├── main.py
    │   │   ├── models.py
    │   │   ├── curves.py
    │   │   ├── pricer.py
    │   │   ├── market_data.py
    │   │   ├── narrative.py
    │   │   ├── db.py
    │   │   └── db_models.py
    │   ├── tests/
    │   ├── terraform/
    │   ├── alembic/
    │   ├── alembic.ini
    │   ├── Dockerfile
    │   └── pyproject.toml
    └── credit-risk-platform/
        ├── src/credit/
        │   ├── __init__.py
        │   ├── main.py
        ���   ├── models.py
        │   ├── spreads.py
        │   ├── cds.py
        │   ├── oas.py
        │   ├── var.py
        │   ├── realtime.py
        │   ├── cache.py
        │   ├── narrative.py
        │   ├── db.py
        │   └── db_models.py
        ├── tests/
        ├── terraform/
        ├── alembic/
        ├── alembic.ini
        ├── Dockerfile
        └── pyproject.toml
```

---

## Phase 1: Exercises 09-14 (AWS Fundamentals + Rates & Curves)

Each exercise follows: **build it -> understand it -> document it**

---

### Task 1: AWS Account Setup, IAM, CLI + Treasury Data Landscape (Exercise 09)

**Concept:** Set up AWS from scratch with proper security. Learn where treasury yield data comes from and what par yields represent. Fetch real yield data from FRED.

**Files:**
- Create: `exercises/09-aws-fundamentals/pyproject.toml`
- Create: `exercises/09-aws-fundamentals/src/treasury_yields.py`
- Create: `exercises/09-aws-fundamentals/tests/test_treasury_yields.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-aws-fundamentals-treasury-data.html`

- [ ] **Step 1: Create AWS account**

Go to https://aws.amazon.com/ and click "Create an AWS Account".

1. Enter email, account name (e.g., "finbytes-quant-lab")
2. Verify email, set root password
3. Enter payment info (required, but free tier means no charges if careful)
4. Choose "Basic (Free)" support plan
5. Sign in to the AWS Management Console

- [ ] **Step 2: Create IAM user (never use root for daily work)**

In AWS Console → IAM → Users → Create user:

1. Username: `quant-lab-dev`
2. Check "Provide user access to the AWS Management Console" (optional for console access)
3. Attach policies directly:
   - `AmazonS3FullAccess`
   - `AmazonRDSFullAccess`
   - `AWSLambda_FullAccess`
   - `AmazonAPIGatewayAdministrator`
   - `AmazonSQSFullAccess`
   - `AmazonSNSFullAccess`
   - `AmazonElastiCacheFullAccess`
   - `CloudWatchFullAccess`
   - `IAMReadOnlyAccess`
4. Create user
5. Go to the user → Security credentials → Create access key → CLI use case
6. Save the Access Key ID and Secret Access Key securely

Note: In production you'd use fine-grained policies. For learning, these managed policies keep things simple.

- [ ] **Step 3: Install and configure AWS CLI**

```bash
# Install AWS CLI (Windows)
winget install Amazon.AWSCLI

# Verify
aws --version

# Configure named profile
aws configure --profile quant-lab
# Enter: Access Key ID, Secret Access Key, region: us-east-1, output: json

# Verify it works
aws sts get-caller-identity --profile quant-lab
```

Expected output:
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/quant-lab-dev"
}
```

- [ ] **Step 4: Set up billing alarm ($5 threshold)**

```bash
# Enable billing alerts (must be done as root user in Console)
# Console → Billing → Billing preferences → Check "Receive Billing Alerts" → Save

# Create SNS topic for billing alerts
aws sns create-topic --name billing-alerts --profile quant-lab

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --profile quant-lab

# Confirm the subscription via the email you receive

# Create CloudWatch billing alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "BillingAlarm-5USD" \
  --alarm-description "Alert when AWS charges exceed $5" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts \
  --dimensions Name=Currency,Value=USD \
  --region us-east-1 \
  --profile quant-lab
```

- [ ] **Step 5: Register for FRED API key**

Go to https://fred.stlouisfed.org/docs/api/api_key.html and register for a free API key. Save it — you'll use it in every exercise.

- [ ] **Step 6: Create pyproject.toml**

```toml
[project]
name = "aws-fundamentals-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fredapi>=0.5.2",
    "numpy>=1.26.0",
    "boto3>=1.35.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "moto[s3]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["treasury_yields"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 7: Write failing tests**

```python
# exercises/09-aws-fundamentals/tests/test_treasury_yields.py

import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from treasury_yields import (
    TREASURY_SERIES,
    fetch_par_yields,
    format_yield_table,
    classify_curve_shape,
)


class TestTreasurySeries:
    def test_series_contains_expected_maturities(self):
        assert "DGS1MO" in TREASURY_SERIES
        assert "DGS10" in TREASURY_SERIES
        assert "DGS30" in TREASURY_SERIES
        assert len(TREASURY_SERIES) >= 11

    def test_series_values_are_maturity_labels(self):
        assert TREASURY_SERIES["DGS1MO"] == "1M"
        assert TREASURY_SERIES["DGS2"] == "2Y"
        assert TREASURY_SERIES["DGS30"] == "30Y"


class TestFetchParYields:
    @patch("treasury_yields.Fred")
    def test_returns_dict_of_maturities_and_rates(self, mock_fred_class):
        mock_fred = MagicMock()
        mock_fred_class.return_value = mock_fred

        # Simulate FRED returning a pandas Series with one value each
        import pandas as pd

        def mock_get_series(series_id, observation_start, observation_end):
            rates = {
                "DGS1MO": 5.25, "DGS3MO": 5.30, "DGS6MO": 5.20,
                "DGS1": 4.80, "DGS2": 4.50, "DGS3": 4.30,
                "DGS5": 4.20, "DGS7": 4.25, "DGS10": 4.30,
                "DGS20": 4.50, "DGS30": 4.45,
            }
            return pd.Series([rates[series_id]])

        mock_fred.get_series.side_effect = mock_get_series

        result = fetch_par_yields(api_key="fake-key")

        assert isinstance(result, dict)
        assert "1M" in result
        assert "10Y" in result
        assert "30Y" in result
        assert result["1M"] == 5.25
        assert result["10Y"] == 4.30

    @patch("treasury_yields.Fred")
    def test_handles_missing_maturity(self, mock_fred_class):
        mock_fred = MagicMock()
        mock_fred_class.return_value = mock_fred

        import pandas as pd

        def mock_get_series(series_id, observation_start, observation_end):
            if series_id == "DGS20":
                return pd.Series(dtype=float)  # empty — no data
            return pd.Series([4.0])

        mock_fred.get_series.side_effect = mock_get_series

        result = fetch_par_yields(api_key="fake-key")
        assert "20Y" not in result
        assert "10Y" in result


class TestFormatYieldTable:
    def test_formats_as_readable_table(self):
        yields = {"1M": 5.25, "3M": 5.30, "6M": 5.20, "1Y": 4.80, "2Y": 4.50}
        table = format_yield_table(yields)
        assert "1M" in table
        assert "5.25" in table
        assert "2Y" in table

    def test_empty_yields_returns_message(self):
        table = format_yield_table({})
        assert "No yield data" in table


class TestClassifyCurveShape:
    def test_normal_curve(self):
        # Short rates < long rates
        yields = {"1M": 3.0, "2Y": 3.5, "10Y": 4.5, "30Y": 5.0}
        assert classify_curve_shape(yields) == "normal"

    def test_inverted_curve(self):
        # Short rates > long rates
        yields = {"1M": 5.5, "2Y": 5.0, "10Y": 4.0, "30Y": 3.5}
        assert classify_curve_shape(yields) == "inverted"

    def test_flat_curve(self):
        # Short and long rates within 0.2% of each other
        yields = {"1M": 4.0, "2Y": 4.05, "10Y": 4.10, "30Y": 4.05}
        assert classify_curve_shape(yields) == "flat"

    def test_humped_curve(self):
        # Mid-term rates higher than both short and long
        yields = {"1M": 4.0, "2Y": 5.0, "10Y": 4.5, "30Y": 4.2}
        assert classify_curve_shape(yields) == "humped"
```

- [ ] **Step 8: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\09-aws-fundamentals
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'treasury_yields'`

- [ ] **Step 9: Implement treasury_yields.py**

```python
# exercises/09-aws-fundamentals/src/treasury_yields.py

from datetime import date, timedelta
from fredapi import Fred


# FRED series IDs → human-readable maturity labels
TREASURY_SERIES = {
    "DGS1MO": "1M",
    "DGS3MO": "3M",
    "DGS6MO": "6M",
    "DGS1": "1Y",
    "DGS2": "2Y",
    "DGS3": "3Y",
    "DGS5": "5Y",
    "DGS7": "7Y",
    "DGS10": "10Y",
    "DGS20": "20Y",
    "DGS30": "30Y",
}

# Ordered list for consistent display and shape classification
MATURITY_ORDER = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]


def fetch_par_yields(api_key: str, as_of: date | None = None) -> dict[str, float]:
    """Fetch US Treasury par yields from FRED.

    Args:
        api_key: FRED API key.
        as_of: Date to fetch yields for. Defaults to most recent available.

    Returns:
        Dict mapping maturity label (e.g. "10Y") to yield in percent (e.g. 4.30).
        Maturities with no data are omitted.
    """
    fred = Fred(api_key=api_key)
    target = as_of or date.today()
    start = target - timedelta(days=7)  # look back a week to handle weekends/holidays

    yields = {}
    for series_id, label in TREASURY_SERIES.items():
        data = fred.get_series(series_id, observation_start=start, observation_end=target)
        data = data.dropna()
        if len(data) > 0:
            yields[label] = round(float(data.iloc[-1]), 2)

    return yields


def format_yield_table(yields: dict[str, float]) -> str:
    """Format yields as a readable ASCII table.

    Args:
        yields: Dict mapping maturity label to yield percent.

    Returns:
        Formatted string table.
    """
    if not yields:
        return "No yield data available."

    lines = []
    lines.append(f"{'Maturity':<10} {'Yield (%)':<10}")
    lines.append("-" * 20)
    for label in MATURITY_ORDER:
        if label in yields:
            lines.append(f"{label:<10} {yields[label]:<10.2f}")
    return "\n".join(lines)


def classify_curve_shape(yields: dict[str, float]) -> str:
    """Classify the yield curve shape.

    Uses short-end (1M or shortest available) and long-end (30Y or longest available)
    to determine overall shape, with mid-point check for humped curves.

    Args:
        yields: Dict mapping maturity label to yield percent.

    Returns:
        One of: "normal", "inverted", "flat", "humped".
    """
    ordered = [(label, yields[label]) for label in MATURITY_ORDER if label in yields]
    if len(ordered) < 3:
        return "flat"  # not enough data to classify

    short_rate = ordered[0][1]
    long_rate = ordered[-1][1]
    mid_rate = ordered[len(ordered) // 2][1]

    spread = long_rate - short_rate

    # Humped: mid-term rate is higher than both short and long ends
    if mid_rate > short_rate + 0.2 and mid_rate > long_rate + 0.2:
        return "humped"

    if abs(spread) <= 0.2:
        return "flat"
    elif spread > 0:
        return "normal"
    else:
        return "inverted"
```

- [ ] **Step 10: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 8 passed

- [ ] **Step 11: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/09-aws-fundamentals/
git commit -m "feat(exercises): 09 AWS fundamentals + treasury yield data from FRED"
```

- [ ] **Step 12: Understand it — teaching conversation**

Topics to cover:
- **AWS fundamentals:** Why IAM matters (root vs user), least-privilege principle, named profiles vs environment variables, regions and availability zones
- **Billing:** How AWS charges work, free tier limits, why billing alarms are critical
- **Treasury yields:** What par yields represent — the coupon rate at which a bond of that maturity would price at par (100). The US Treasury issues at these rates.
- **FRED as a data source:** Free, reliable, rate-limited. The go-to for economic and financial time series.
- **Yield curve shapes:**
  - Normal (upward sloping): economy healthy, long-term rates > short-term. Investors demand premium for locking up money longer.
  - Inverted: short rates > long rates. Historically predicts recession — market expects rate cuts ahead.
  - Flat: rates similar across maturities. Transition period, uncertainty.
  - Humped: mid-term peak. Unusual, often signals specific policy expectations.

- [ ] **Step 13: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-aws-fundamentals-treasury-data.html` using the standard FinBytes post frontmatter:

```yaml
---
layout: post
title: "AWS Fundamentals & Treasury Yield Data"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Python fundamentals
tags:
  - aws
  - iam
  - fred
  - treasury
  - yield-curve
permalink: "/2026/04/XX/aws-fundamentals-treasury-data/"
---
```

Sections: Why AWS for quant projects, IAM and security basics, billing protection, FRED API for treasury data, yield curve shapes and what they signal, exercise walkthrough.

- [ ] **Step 14: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-aws-fundamentals-treasury-data.html
git commit -m "post: AWS fundamentals and treasury yield data"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 2: S3 + Par Curve Data Ingestion (Exercise 10)

**Concept:** Use S3 as a data lake for financial time-series. Fetch daily treasury par yields from FRED, store as dated JSON in S3, read back and validate. Learn S3 operations with boto3.

**Files:**
- Create: `exercises/10-s3-data-ingestion/pyproject.toml`
- Create: `exercises/10-s3-data-ingestion/src/s3_ingestion.py`
- Create: `exercises/10-s3-data-ingestion/tests/test_s3_ingestion.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-s3-par-curve-ingestion.html`

- [ ] **Step 1: Create S3 bucket via CLI**

```bash
# Create bucket (bucket names must be globally unique)
aws s3 mb s3://finbytes-quant-lab-data --region us-east-1 --profile quant-lab

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket finbytes-quant-lab-data \
  --versioning-configuration Status=Enabled \
  --profile quant-lab

# Verify
aws s3 ls --profile quant-lab
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "s3-data-ingestion-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.35.0",
    "fredapi>=0.5.2",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "moto[s3]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["s3_ingestion"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write failing tests**

```python
# exercises/10-s3-data-ingestion/tests/test_s3_ingestion.py

import json
import pytest
import boto3
from datetime import date
from unittest.mock import patch, MagicMock
from moto import mock_aws
from s3_ingestion import (
    upload_yields_to_s3,
    download_yields_from_s3,
    list_available_dates,
    ingest_daily_yields,
)

BUCKET = "test-quant-lab-data"
PREFIX = "par-yields"


@pytest.fixture
def s3_bucket():
    """Create a mock S3 bucket for testing."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET)
        yield s3


class TestUploadYields:
    def test_uploads_json_to_correct_key(self, s3_bucket):
        yields = {"1M": 5.25, "10Y": 4.30, "30Y": 4.45}
        target_date = date(2026, 4, 4)

        upload_yields_to_s3(
            yields=yields,
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=target_date,
            s3_client=s3_bucket,
        )

        key = f"{PREFIX}/2026-04-04.json"
        response = s3_bucket.get_object(Bucket=BUCKET, Key=key)
        body = json.loads(response["Body"].read())
        assert body["date"] == "2026-04-04"
        assert body["yields"]["10Y"] == 4.30

    def test_upload_includes_metadata(self, s3_bucket):
        yields = {"1M": 5.25, "10Y": 4.30}
        target_date = date(2026, 4, 4)

        upload_yields_to_s3(
            yields=yields,
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=target_date,
            s3_client=s3_bucket,
        )

        key = f"{PREFIX}/2026-04-04.json"
        response = s3_bucket.get_object(Bucket=BUCKET, Key=key)
        body = json.loads(response["Body"].read())
        assert body["source"] == "FRED"
        assert body["num_maturities"] == 2


class TestDownloadYields:
    def test_downloads_and_parses_json(self, s3_bucket):
        data = {
            "date": "2026-04-04",
            "source": "FRED",
            "num_maturities": 2,
            "yields": {"1M": 5.25, "10Y": 4.30},
        }
        s3_bucket.put_object(
            Bucket=BUCKET,
            Key=f"{PREFIX}/2026-04-04.json",
            Body=json.dumps(data),
        )

        result = download_yields_from_s3(
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )

        assert result["yields"]["10Y"] == 4.30

    def test_missing_date_raises(self, s3_bucket):
        with pytest.raises(FileNotFoundError, match="2099-01-01"):
            download_yields_from_s3(
                bucket=BUCKET,
                prefix=PREFIX,
                as_of=date(2099, 1, 1),
                s3_client=s3_bucket,
            )


class TestListAvailableDates:
    def test_lists_dates_from_keys(self, s3_bucket):
        for d in ["2026-04-01", "2026-04-02", "2026-04-03"]:
            s3_bucket.put_object(
                Bucket=BUCKET,
                Key=f"{PREFIX}/{d}.json",
                Body=json.dumps({"date": d, "yields": {}}),
            )

        dates = list_available_dates(
            bucket=BUCKET, prefix=PREFIX, s3_client=s3_bucket
        )

        assert len(dates) == 3
        assert date(2026, 4, 1) in dates
        assert date(2026, 4, 3) in dates

    def test_empty_bucket_returns_empty_list(self, s3_bucket):
        dates = list_available_dates(
            bucket=BUCKET, prefix=PREFIX, s3_client=s3_bucket
        )
        assert dates == []


class TestIngestDailyYields:
    @patch("s3_ingestion.fetch_par_yields")
    def test_fetches_and_uploads(self, mock_fetch, s3_bucket):
        mock_fetch.return_value = {"1M": 5.25, "10Y": 4.30}

        result = ingest_daily_yields(
            api_key="fake-key",
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )

        assert result["date"] == "2026-04-04"
        assert result["num_maturities"] == 2

        # Verify it was uploaded
        downloaded = download_yields_from_s3(
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )
        assert downloaded["yields"]["10Y"] == 4.30
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\10-s3-data-ingestion
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 's3_ingestion'`

- [ ] **Step 5: Implement s3_ingestion.py**

```python
# exercises/10-s3-data-ingestion/src/s3_ingestion.py

import json
import boto3
from datetime import date

# Import from exercise 09 — reuse FRED fetching logic
import sys
sys.path.insert(0, "../../09-aws-fundamentals/src")
from treasury_yields import fetch_par_yields, TREASURY_SERIES


def upload_yields_to_s3(
    yields: dict[str, float],
    bucket: str,
    prefix: str,
    as_of: date,
    s3_client=None,
) -> dict:
    """Upload par yield data to S3 as a dated JSON file.

    Args:
        yields: Dict mapping maturity label to yield percent.
        bucket: S3 bucket name.
        prefix: Key prefix (e.g. "par-yields").
        as_of: Date for the yield data.
        s3_client: Optional boto3 S3 client (for testing).

    Returns:
        The data dict that was uploaded.
    """
    s3 = s3_client or boto3.client("s3")

    data = {
        "date": as_of.isoformat(),
        "source": "FRED",
        "num_maturities": len(yields),
        "yields": yields,
    }

    key = f"{prefix}/{as_of.isoformat()}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )

    return data


def download_yields_from_s3(
    bucket: str,
    prefix: str,
    as_of: date,
    s3_client=None,
) -> dict:
    """Download par yield data from S3 for a given date.

    Args:
        bucket: S3 bucket name.
        prefix: Key prefix.
        as_of: Date to fetch.
        s3_client: Optional boto3 S3 client.

    Returns:
        Parsed JSON data dict.

    Raises:
        FileNotFoundError: If no data exists for the given date.
    """
    s3 = s3_client or boto3.client("s3")
    key = f"{prefix}/{as_of.isoformat()}.json"

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response["Body"].read())
    except s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"No yield data for {as_of.isoformat()}")
    except Exception as e:
        if "NoSuchKey" in str(e):
            raise FileNotFoundError(f"No yield data for {as_of.isoformat()}")
        raise


def list_available_dates(
    bucket: str,
    prefix: str,
    s3_client=None,
) -> list[date]:
    """List all dates with yield data in S3.

    Args:
        bucket: S3 bucket name.
        prefix: Key prefix.
        s3_client: Optional boto3 S3 client.

    Returns:
        Sorted list of dates.
    """
    s3 = s3_client or boto3.client("s3")

    response = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/")
    if "Contents" not in response:
        return []

    dates = []
    for obj in response["Contents"]:
        # Key format: prefix/YYYY-MM-DD.json
        filename = obj["Key"].split("/")[-1]
        if filename.endswith(".json"):
            date_str = filename.replace(".json", "")
            dates.append(date.fromisoformat(date_str))

    return sorted(dates)


def ingest_daily_yields(
    api_key: str,
    bucket: str,
    prefix: str,
    as_of: date | None = None,
    s3_client=None,
) -> dict:
    """Fetch yields from FRED and upload to S3.

    Args:
        api_key: FRED API key.
        bucket: S3 bucket name.
        prefix: Key prefix.
        as_of: Date to fetch. Defaults to today.
        s3_client: Optional boto3 S3 client.

    Returns:
        The uploaded data dict.
    """
    target = as_of or date.today()
    yields = fetch_par_yields(api_key=api_key, as_of=target)
    return upload_yields_to_s3(
        yields=yields,
        bucket=bucket,
        prefix=prefix,
        as_of=target,
        s3_client=s3_client,
    )
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 7: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/10-s3-data-ingestion/
git commit -m "feat(exercises): 10 S3 data ingestion for treasury par yields"
```

- [ ] **Step 8: Understand it — teaching conversation**

Topics to cover:
- **S3 fundamentals:** Buckets, keys, objects. Not a filesystem — flat namespace with `/` convention. Unlimited storage.
- **Versioning:** Why it matters — overwrite protection, audit trail. Every put creates a new version.
- **Data lake pattern:** Raw data in S3, processed data in database. S3 is cheap, durable (99.999999999% — eleven nines), and supports any format.
- **Par curve as the foundation:** Every other curve (spot, forward, fitted) is derived from par yields. Get this data right, everything else follows.
- **Data quality:** Missing maturities on holidays/weekends. The 7-day lookback window handles this — FRED doesn't publish on non-trading days.
- **moto for testing:** Mock AWS services in-process. No network calls, no AWS account needed for tests. Tests run fast and isolated.

- [ ] **Step 9: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-s3-par-curve-ingestion.html`

```yaml
---
layout: post
title: "S3 for Financial Data: Par Curve Ingestion Pipeline"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Data Engineering
tags:
  - s3
  - boto3
  - treasury
  - par-curve
  - data-lake
permalink: "/2026/04/XX/s3-par-curve-ingestion/"
---
```

Sections: S3 as a data lake for finance, boto3 operations, par curve data structure, moto for testing, daily ingestion pipeline.

- [ ] **Step 10: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-s3-par-curve-ingestion.html
git commit -m "post: S3 for financial data — par curve ingestion"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 3: RDS PostgreSQL on AWS + Yield/Bond Schema Design (Exercise 11)

**Concept:** Provision a managed PostgreSQL database on AWS RDS. Design a relational schema for fixed income data — par yields, computed curves, bond definitions, pricing results. Use SQLAlchemy + Alembic for schema management.

**Files:**
- Create: `exercises/11-rds-postgresql/pyproject.toml`
- Create: `exercises/11-rds-postgresql/src/models.py`
- Create: `exercises/11-rds-postgresql/src/db.py`
- Create: `exercises/11-rds-postgresql/tests/test_db.py`
- Create: `exercises/11-rds-postgresql/alembic.ini`
- Create: `exercises/11-rds-postgresql/alembic/env.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-rds-postgresql-yield-schema.html`

- [ ] **Step 1: Provision RDS PostgreSQL via CLI**

```bash
# Create a security group for RDS
aws ec2 create-security-group \
  --group-name quant-lab-rds-sg \
  --description "Security group for QuantLab RDS" \
  --profile quant-lab

# Allow PostgreSQL access from your IP (replace YOUR_IP)
aws ec2 authorize-security-group-ingress \
  --group-name quant-lab-rds-sg \
  --protocol tcp \
  --port 5432 \
  --cidr YOUR_IP/32 \
  --profile quant-lab

# Create RDS instance (free tier)
aws rds create-db-instance \
  --db-instance-identifier quant-lab-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 16.3 \
  --master-username quantlab \
  --master-user-password CHANGE_THIS_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-XXXX \
  --publicly-accessible \
  --backup-retention-period 1 \
  --no-multi-az \
  --storage-type gp2 \
  --profile quant-lab

# Wait for it to become available (takes ~5 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier quant-lab-db \
  --profile quant-lab

# Get the endpoint
aws rds describe-db-instances \
  --db-instance-identifier quant-lab-db \
  --query "DBInstances[0].Endpoint.Address" \
  --output text \
  --profile quant-lab
```

Save the endpoint — you'll need it for the DATABASE_URL.

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "rds-postgresql-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0", "aiosqlite>=0.20.0"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Write failing tests**

```python
# exercises/11-rds-postgresql/tests/test_db.py

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base, ParYieldRecord, SpotCurveRecord, BondRecord
from db import (
    save_par_yields,
    get_par_yields_by_date,
    get_par_yields_range,
    save_spot_curve,
    get_spot_curve_by_date,
    save_bond,
    get_bond_by_isin,
)


@pytest.fixture
async def session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


class TestParYields:
    async def test_save_and_retrieve(self, session):
        yields_data = {"1M": 5.25, "3M": 5.30, "10Y": 4.30, "30Y": 4.45}
        await save_par_yields(session, date(2026, 4, 4), yields_data)

        result = await get_par_yields_by_date(session, date(2026, 4, 4))
        assert result is not None
        assert result["10Y"] == 4.30
        assert result["30Y"] == 4.45

    async def test_missing_date_returns_none(self, session):
        result = await get_par_yields_by_date(session, date(2099, 1, 1))
        assert result is None

    async def test_upsert_overwrites(self, session):
        await save_par_yields(session, date(2026, 4, 4), {"10Y": 4.30})
        await save_par_yields(session, date(2026, 4, 4), {"10Y": 4.35})

        result = await get_par_yields_by_date(session, date(2026, 4, 4))
        assert result["10Y"] == 4.35

    async def test_range_query(self, session):
        await save_par_yields(session, date(2026, 4, 1), {"10Y": 4.20})
        await save_par_yields(session, date(2026, 4, 2), {"10Y": 4.25})
        await save_par_yields(session, date(2026, 4, 3), {"10Y": 4.30})

        results = await get_par_yields_range(
            session, date(2026, 4, 1), date(2026, 4, 3)
        )
        assert len(results) == 3
        assert results[0]["date"] == date(2026, 4, 1)
        assert results[2]["yields"]["10Y"] == 4.30


class TestSpotCurve:
    async def test_save_and_retrieve(self, session):
        spot_data = {"1Y": 4.80, "2Y": 4.52, "5Y": 4.25, "10Y": 4.35}
        await save_spot_curve(session, date(2026, 4, 4), spot_data)

        result = await get_spot_curve_by_date(session, date(2026, 4, 4))
        assert result is not None
        assert result["2Y"] == 4.52


class TestBond:
    async def test_save_and_retrieve(self, session):
        await save_bond(
            session,
            isin="US912828ZT58",
            coupon=2.875,
            maturity=date(2032, 5, 15),
            face_value=1000.0,
            issue_date=date(2022, 5, 15),
            frequency=2,
        )

        bond = await get_bond_by_isin(session, "US912828ZT58")
        assert bond is not None
        assert bond.coupon == 2.875
        assert bond.frequency == 2

    async def test_missing_isin_returns_none(self, session):
        result = await get_bond_by_isin(session, "DOESNOTEXIST")
        assert result is None
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\11-rds-postgresql
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'models'`

- [ ] **Step 5: Implement models.py**

```python
# exercises/11-rds-postgresql/src/models.py

import json
from datetime import date, datetime, UTC
from sqlalchemy import String, Float, Integer, Date, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ParYieldRecord(Base):
    """Daily US Treasury par yield curve."""
    __tablename__ = "par_yields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    yields_json: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20), default="FRED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    @property
    def yields(self) -> dict[str, float]:
        return json.loads(self.yields_json)

    @yields.setter
    def yields(self, value: dict[str, float]):
        self.yields_json = json.dumps(value)


class SpotCurveRecord(Base):
    """Bootstrapped zero-coupon (spot) rate curve."""
    __tablename__ = "spot_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    rates_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    @property
    def rates(self) -> dict[str, float]:
        return json.loads(self.rates_json)

    @rates.setter
    def rates(self, value: dict[str, float]):
        self.rates_json = json.dumps(value)


class ForwardCurveRecord(Base):
    """Implied forward rate curve."""
    __tablename__ = "forward_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    rates_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    @property
    def rates(self) -> dict[str, float]:
        return json.loads(self.rates_json)

    @rates.setter
    def rates(self, value: dict[str, float]):
        self.rates_json = json.dumps(value)


class FittedCurveRecord(Base):
    """Parametric fitted curve (Nelson-Siegel or Svensson)."""
    __tablename__ = "fitted_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, index=True)
    model: Mapped[str] = mapped_column(String(30))  # "nelson-siegel" or "svensson"
    params_json: Mapped[str] = mapped_column(Text)  # model parameters
    fitted_rates_json: Mapped[str] = mapped_column(Text)  # resulting curve
    rmse: Mapped[float] = mapped_column(Float)  # fit quality
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class BondRecord(Base):
    """Bond definition."""
    __tablename__ = "bonds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isin: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    coupon: Mapped[float] = mapped_column(Float)
    maturity: Mapped[date] = mapped_column(Date)
    face_value: Mapped[float] = mapped_column(Float, default=1000.0)
    issue_date: Mapped[date] = mapped_column(Date)
    frequency: Mapped[int] = mapped_column(Integer, default=2)  # coupons per year
    bond_type: Mapped[str] = mapped_column(String(20), default="treasury")
    callable: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class PricingResultRecord(Base):
    """Bond pricing result."""
    __tablename__ = "pricing_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bond_isin: Mapped[str] = mapped_column(String(12), index=True)
    curve_date: Mapped[date] = mapped_column(Date)
    clean_price: Mapped[float] = mapped_column(Float)
    dirty_price: Mapped[float] = mapped_column(Float)
    ytm: Mapped[float] = mapped_column(Float)
    z_spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration: Mapped[float] = mapped_column(Float)
    modified_duration: Mapped[float] = mapped_column(Float)
    convexity: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
```

- [ ] **Step 6: Implement db.py**

```python
# exercises/11-rds-postgresql/src/db.py

import json
from datetime import date
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import ParYieldRecord, SpotCurveRecord, BondRecord


async def save_par_yields(
    session: AsyncSession, curve_date: date, yields: dict[str, float]
) -> ParYieldRecord:
    """Save par yields for a date. Upserts — overwrites if date exists."""
    existing = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.yields_json = json.dumps(yields)
    else:
        record = ParYieldRecord(curve_date=curve_date, yields_json=json.dumps(yields))
        session.add(record)

    await session.commit()
    return record


async def get_par_yields_by_date(
    session: AsyncSession, curve_date: date
) -> dict[str, float] | None:
    """Get par yields for a specific date. Returns None if not found."""
    result = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return json.loads(record.yields_json)


async def get_par_yields_range(
    session: AsyncSession, start: date, end: date
) -> list[dict]:
    """Get par yields for a date range. Returns list of {date, yields} dicts."""
    result = await session.execute(
        select(ParYieldRecord)
        .where(ParYieldRecord.curve_date >= start)
        .where(ParYieldRecord.curve_date <= end)
        .order_by(ParYieldRecord.curve_date)
    )
    records = result.scalars().all()
    return [
        {"date": r.curve_date, "yields": json.loads(r.yields_json)}
        for r in records
    ]


async def save_spot_curve(
    session: AsyncSession, curve_date: date, rates: dict[str, float]
) -> SpotCurveRecord:
    """Save spot curve for a date. Upserts."""
    existing = await session.execute(
        select(SpotCurveRecord).where(SpotCurveRecord.curve_date == curve_date)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.rates_json = json.dumps(rates)
    else:
        record = SpotCurveRecord(curve_date=curve_date, rates_json=json.dumps(rates))
        session.add(record)

    await session.commit()
    return record


async def get_spot_curve_by_date(
    session: AsyncSession, curve_date: date
) -> dict[str, float] | None:
    """Get spot curve for a specific date. Returns None if not found."""
    result = await session.execute(
        select(SpotCurveRecord).where(SpotCurveRecord.curve_date == curve_date)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return json.loads(record.rates_json)


async def save_bond(
    session: AsyncSession,
    isin: str,
    coupon: float,
    maturity: date,
    face_value: float = 1000.0,
    issue_date: date | None = None,
    frequency: int = 2,
    bond_type: str = "treasury",
    callable: bool = False,
) -> BondRecord:
    """Save a bond definition."""
    record = BondRecord(
        isin=isin,
        coupon=coupon,
        maturity=maturity,
        face_value=face_value,
        issue_date=issue_date or date.today(),
        frequency=frequency,
        bond_type=bond_type,
        callable=callable,
    )
    session.add(record)
    await session.commit()
    return record


async def get_bond_by_isin(session: AsyncSession, isin: str) -> BondRecord | None:
    """Get a bond by ISIN. Returns None if not found."""
    result = await session.execute(
        select(BondRecord).where(BondRecord.isin == isin)
    )
    return result.scalar_one_or_none()
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 8: Set up Alembic**

```bash
cd C:\codebase\quant_lab\exercises\11-rds-postgresql
alembic init alembic
```

Edit `alembic.ini` — set `sqlalchemy.url`:
```ini
sqlalchemy.url = postgresql+asyncpg://quantlab:PASSWORD@YOUR_RDS_ENDPOINT:5432/postgres
```

Edit `alembic/env.py` — add model imports:
```python
# At the top, add:
from models import Base
target_metadata = Base.metadata
```

Create the initial migration:
```bash
alembic revision --autogenerate -m "create yield and bond tables"
alembic upgrade head
```

- [ ] **Step 9: Seed database with historical par yields from S3**

```bash
# Run a quick script to load data from S3 into RDS
python -c "
import asyncio
import json
import boto3
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db import save_par_yields
from models import Base

DATABASE_URL = 'postgresql+asyncpg://quantlab:PASSWORD@ENDPOINT:5432/postgres'

async def seed():
    engine = create_async_engine(DATABASE_URL)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket='finbytes-quant-lab-data', Prefix='par-yields/')
    for obj in response.get('Contents', []):
        data = json.loads(s3.get_object(Bucket='finbytes-quant-lab-data', Key=obj['Key'])['Body'].read())
        async with factory() as session:
            await save_par_yields(session, date.fromisoformat(data['date']), data['yields'])
            print(f'Loaded {data[\"date\"]}')

    await engine.dispose()

asyncio.run(seed())
"
```

- [ ] **Step 10: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/11-rds-postgresql/
git commit -m "feat(exercises): 11 RDS PostgreSQL + yield/bond schema design"
```

- [ ] **Step 11: Understand it — teaching conversation**

Topics to cover:
- **RDS vs self-managed PostgreSQL:** Automated backups, patching, monitoring. You manage the schema, AWS manages the server.
- **Free tier limits:** 750 hours/month of db.t3.micro, 20GB storage. One instance running 24/7 = 720 hours — fits.
- **Schema design for financial time-series:**
  - Why `curve_date` is unique + indexed — point-in-time queries are the primary access pattern
  - JSON columns for flexible yield data (maturities can change) vs normalized rows (one per maturity per date). JSON is simpler, normalized is faster for aggregations. For this data volume, JSON wins on simplicity.
  - No look-ahead bias: when querying "what was the curve on April 1?", only return data available on April 1
- **SQLAlchemy async:** `create_async_engine` + `async_sessionmaker`. Same ORM patterns as sync, but non-blocking I/O.
- **Alembic:** Version-controlled schema migrations. `--autogenerate` compares models to DB and generates migration scripts.

- [ ] **Step 12: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-rds-postgresql-yield-schema.html`

```yaml
---
layout: post
title: "RDS PostgreSQL: Schema Design for Yield Curves"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Databases
tags:
  - rds
  - postgresql
  - sqlalchemy
  - alembic
  - yield-curve
permalink: "/2026/04/XX/rds-postgresql-yield-schema/"
---
```

- [ ] **Step 13: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-rds-postgresql-yield-schema.html
git commit -m "post: RDS PostgreSQL — schema design for yield curves"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 4: Lambda + API Gateway + Spot Curve Bootstrapping (Exercise 12)

**Concept:** Deploy a serverless API endpoint that bootstraps zero-coupon (spot) rates from par yields. Learn Lambda packaging, API Gateway routing, and the critical math of curve bootstrapping.

**Files:**
- Create: `exercises/12-lambda-api-gateway/pyproject.toml`
- Create: `exercises/12-lambda-api-gateway/src/bootstrap.py`
- Create: `exercises/12-lambda-api-gateway/src/handler.py`
- Create: `exercises/12-lambda-api-gateway/tests/test_bootstrap.py`
- Create: `finbytes_git/docs/_posts/2026-04-XX-lambda-spot-curve-bootstrapping.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "lambda-api-gateway-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests for the bootstrap math**

```python
# exercises/12-lambda-api-gateway/tests/test_bootstrap.py

import numpy as np
import pytest
from bootstrap import bootstrap_spot_curve, MATURITY_YEARS


class TestMaturityYears:
    def test_contains_standard_maturities(self):
        assert MATURITY_YEARS["1M"] == pytest.approx(1 / 12)
        assert MATURITY_YEARS["6M"] == 0.5
        assert MATURITY_YEARS["1Y"] == 1.0
        assert MATURITY_YEARS["10Y"] == 10.0
        assert MATURITY_YEARS["30Y"] == 30.0


class TestBootstrapSpotCurve:
    def test_single_maturity_spot_equals_par(self):
        """For a single zero-coupon maturity, spot rate = par yield."""
        par_yields = {"1Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        assert spot["1Y"] == pytest.approx(5.0, abs=0.01)

    def test_two_maturities(self):
        """With 1Y and 2Y par yields, 2Y spot should differ from par."""
        par_yields = {"1Y": 5.0, "2Y": 5.5}
        spot = bootstrap_spot_curve(par_yields)

        # 1Y spot = 1Y par (no intermediate coupons)
        assert spot["1Y"] == pytest.approx(5.0, abs=0.01)
        # 2Y spot should be slightly higher than 2Y par for normal curve
        assert spot["2Y"] > 5.5

    def test_flat_curve_spot_equals_par(self):
        """When all par yields are equal, spot rates should equal par rates."""
        par_yields = {"1Y": 5.0, "2Y": 5.0, "5Y": 5.0, "10Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        for label in par_yields:
            assert spot[label] == pytest.approx(5.0, abs=0.05)

    def test_normal_curve_spot_above_par_at_long_end(self):
        """For a normal (upward sloping) par curve, long-end spot > long-end par."""
        par_yields = {
            "1Y": 3.0, "2Y": 3.5, "3Y": 4.0, "5Y": 4.5, "10Y": 5.0
        }
        spot = bootstrap_spot_curve(par_yields)
        assert spot["10Y"] > par_yields["10Y"]

    def test_preserves_maturity_order(self):
        """Output keys should match input keys."""
        par_yields = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0}
        spot = bootstrap_spot_curve(par_yields)
        assert list(spot.keys()) == ["1Y", "2Y", "5Y"]

    def test_all_rates_positive(self):
        """Spot rates should be positive for reasonable par yields."""
        par_yields = {
            "1M": 5.25, "3M": 5.30, "6M": 5.20,
            "1Y": 4.80, "2Y": 4.50, "3Y": 4.30,
            "5Y": 4.20, "7Y": 4.25, "10Y": 4.30,
        }
        spot = bootstrap_spot_curve(par_yields)
        for rate in spot.values():
            assert rate > 0

    def test_empty_yields_returns_empty(self):
        spot = bootstrap_spot_curve({})
        assert spot == {}
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\12-lambda-api-gateway
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'bootstrap'`

- [ ] **Step 4: Implement bootstrap.py**

```python
# exercises/12-lambda-api-gateway/src/bootstrap.py

"""
Spot curve bootstrapping from par yields.

Math:
  A par bond prices at 100 (face value). For a bond with annual coupon c
  and maturity n years:

    100 = c/(1+s₁) + c/(1+s₂)² + ... + (c+100)/(1+sₙ)ⁿ

  where sᵢ are spot (zero-coupon) rates.

  The bootstrap solves iteratively:
  1. s₁ = par yield for 1Y (trivial — single cash flow)
  2. For each subsequent maturity n, use known s₁...sₙ₋��� to solve for sₙ:
     sₙ = ((c + 100) / (100 - Σ c/(1+sᵢ)ⁱ))^(1/n) - 1

  We convert par yields from percent to decimal for calculation,
  then convert spot rates back to percent for output.
"""

import numpy as np

# Maturity labels → years (for discounting)
MATURITY_YEARS: dict[str, float] = {
    "1M": 1 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "1Y": 1.0,
    "2Y": 2.0,
    "3Y": 3.0,
    "5Y": 5.0,
    "7Y": 7.0,
    "10Y": 10.0,
    "20Y": 20.0,
    "30Y": 30.0,
}

# Ordered list for bootstrapping (must solve short maturities first)
MATURITY_ORDER = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]


def bootstrap_spot_curve(par_yields: dict[str, float]) -> dict[str, float]:
    """Bootstrap zero-coupon (spot) rates from par yields.

    Args:
        par_yields: Dict mapping maturity label to par yield in percent (e.g. 4.30).

    Returns:
        Dict mapping maturity label to spot rate in percent,
        in the same order as input.
    """
    if not par_yields:
        return {}

    # Filter to maturities we have data for, in order
    ordered_labels = [m for m in MATURITY_ORDER if m in par_yields]

    # Convert par yields to decimal
    par_decimal = {m: par_yields[m] / 100.0 for m in ordered_labels}
    years = {m: MATURITY_YEARS[m] for m in ordered_labels}

    spot_decimal: dict[str, float] = {}

    for i, label in enumerate(ordered_labels):
        c = par_decimal[label]  # annual coupon rate (decimal)
        t = years[label]  # maturity in years

        if i == 0:
            # First maturity: spot rate = par yield (single cash flow)
            spot_decimal[label] = c
        else:
            # Sum of PV of intermediate coupons using known spot rates
            pv_coupons = 0.0
            for prev_label in ordered_labels[:i]:
                prev_t = years[prev_label]
                prev_s = spot_decimal[prev_label]
                pv_coupons += c / ((1 + prev_s) ** prev_t)

            # Solve for spot rate at this maturity:
            # 100 = PV(coupons) + (c + 100) / (1 + sₙ)^t
            # => (1 + sₙ)^t = (c + 1) / (1 - PV(coupons))
            # where everything is per 1 unit of face value
            numerator = c + 1.0  # final coupon + face value (per unit)
            denominator = 1.0 - pv_coupons  # remaining PV

            if denominator <= 0:
                # Fallback: if intermediate coupons exceed face value, use par yield
                spot_decimal[label] = c
            else:
                spot_decimal[label] = (numerator / denominator) ** (1.0 / t) - 1.0

    # Convert back to percent, preserve input order
    return {m: round(spot_decimal[m] * 100, 4) for m in ordered_labels}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 6: Implement Lambda handler**

```python
# exercises/12-lambda-api-gateway/src/handler.py

"""
AWS Lambda handler for the spot curve bootstrapping endpoint.

API Gateway event format (REST API):
{
    "httpMethod": "POST",
    "body": "{\"par_yields\": {\"1Y\": 4.80, \"2Y\": 4.50, ...}}"
}

Returns:
{
    "statusCode": 200,
    "body": "{\"spot_curve\": {\"1Y\": 4.80, \"2Y\": 4.52, ...}}"
}
"""

import json
from bootstrap import bootstrap_spot_curve


def lambda_handler(event, context):
    """Handle POST /curves/bootstrap requests."""
    try:
        body = json.loads(event.get("body", "{}"))
        par_yields = body.get("par_yields")

        if not par_yields or not isinstance(par_yields, dict):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "par_yields dict is required"}),
            }

        spot_curve = bootstrap_spot_curve(par_yields)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"spot_curve": spot_curve}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
```

- [ ] **Step 7: Deploy Lambda + API Gateway**

```bash
# Create deployment package
cd C:\codebase\quant_lab\exercises\12-lambda-api-gateway\src
pip install numpy -t package/
cp bootstrap.py handler.py package/
cd package && zip -r ../deployment.zip . && cd ..

# Create Lambda function
aws lambda create-function \
  --function-name quant-lab-bootstrap \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --zip-file fileb://deployment.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/quant-lab-lambda-role \
  --timeout 30 \
  --memory-size 256 \
  --profile quant-lab

# Create REST API in API Gateway
aws apigateway create-rest-api \
  --name "QuantLab Curves API" \
  --profile quant-lab

# Note the API ID from the output, then:
# Create /curves resource
# Create /curves/bootstrap resource
# Create POST method
# Create Lambda integration
# Deploy to "dev" stage

# Test it
curl -X POST https://API_ID.execute-api.us-east-1.amazonaws.com/dev/curves/bootstrap \
  -H "Content-Type: application/json" \
  -d '{"par_yields": {"1Y": 4.80, "2Y": 4.50, "5Y": 4.20, "10Y": 4.30}}'
```

Note: The full API Gateway setup involves multiple CLI commands. During the teaching conversation, we'll walk through the Console UI as well — it's more visual and better for learning.

- [ ] **Step 8: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/12-lambda-api-gateway/
git commit -m "feat(exercises): 12 Lambda + API Gateway with spot curve bootstrapping"
```

- [ ] **Step 9: Understand it — teaching conversation**

Topics to cover:
- **Lambda fundamentals:** Stateless compute. Upload code, AWS runs it on demand. Pay per invocation + duration. Cold starts = first invocation is slow (~1-3s for Python).
- **API Gateway:** Maps HTTP requests to Lambda invocations. Handles routing, CORS, throttling, auth. REST API vs HTTP API (HTTP API is cheaper and simpler — use it when you can).
- **Deployment packaging:** Lambda needs all dependencies bundled. Layers are an alternative — shared dependency bundles reusable across functions.
- **Bootstrap math deep-dive:**
  - Par bond: prices at 100 = face value. The coupon rate that makes this true is the par yield.
  - Spot rate: the yield on a zero-coupon bond. Pure time value of money at that maturity.
  - Why they differ: a 10Y par bond pays coupons at years 1-9 (discounted at shorter spot rates) plus principal at year 10. If shorter spot rates are lower (normal curve), the 10Y spot rate must be higher than the 10Y par yield to compensate.
  - Intuition: spot rates "remove" the coupon effect. They're the building blocks for all pricing.
- **Cold starts:** First invocation = new container + import numpy (~1s). Subsequent invocations are fast. Mitigations: provisioned concurrency (costs money), keep dependencies lean, or use Lambda SnapStart (Java only).

- [ ] **Step 10: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-lambda-spot-curve-bootstrapping.html`

```yaml
---
layout: post
title: "AWS Lambda: Spot Curve Bootstrapping as a Serverless API"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Quantitative Finance
tags:
  - lambda
  - api-gateway
  - spot-curve
  - bootstrapping
  - yield-curve
permalink: "/2026/04/XX/lambda-spot-curve-bootstrapping/"
---
```

Sections: Lambda + API Gateway architecture, the bootstrap method (math + intuition), implementation walkthrough, deployment, cold starts and performance.

- [ ] **Step 11: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-lambda-spot-curve-bootstrapping.html
git commit -m "post: Lambda — spot curve bootstrapping as a serverless API"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 5: CI/CD (GitHub Actions → AWS) + Forward Rate Curve (Exercise 13)

**Concept:** Automate Lambda deployment with GitHub Actions. Derive forward rates from spot curves — the market's implied expectation of future interest rates.

**Files:**
- Create: `exercises/13-cicd-github-actions/pyproject.toml`
- Create: `exercises/13-cicd-github-actions/src/forward_rates.py`
- Create: `exercises/13-cicd-github-actions/tests/test_forward_rates.py`
- Create: `exercises/13-cicd-github-actions/.github/workflows/deploy.yml`
- Create: `finbytes_git/docs/_posts/2026-04-XX-cicd-forward-rate-curve.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "cicd-github-actions-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["forward_rates"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/13-cicd-github-actions/tests/test_forward_rates.py

import pytest
from forward_rates import calculate_forward_rates, forward_rate_between


class TestForwardRateBetween:
    def test_basic_forward_rate(self):
        """f(1,2) from 1Y spot=4% and 2Y spot=5%
        (1.05)^2 = (1.04)(1+f) => f = (1.05^2 / 1.04) - 1 ≈ 6.0096%
        """
        f = forward_rate_between(
            spot_short=4.0, years_short=1.0,
            spot_long=5.0, years_long=2.0,
        )
        assert f == pytest.approx(6.0096, abs=0.01)

    def test_equal_spots_give_same_forward(self):
        """If spot rates are equal, forward = spot."""
        f = forward_rate_between(
            spot_short=5.0, years_short=1.0,
            spot_long=5.0, years_long=2.0,
        )
        assert f == pytest.approx(5.0, abs=0.01)

    def test_inverted_gives_lower_forward(self):
        """If long spot < short spot, forward rate is lower."""
        f = forward_rate_between(
            spot_short=5.0, years_short=1.0,
            spot_long=4.0, years_long=2.0,
        )
        assert f < 4.0


class TestCalculateForwardRates:
    def test_basic_forward_curve(self):
        spot_curve = {"1Y": 4.0, "2Y": 5.0, "5Y": 5.5}
        forwards = calculate_forward_rates(spot_curve)

        assert "1Y-2Y" in forwards
        assert "2Y-5Y" in forwards
        assert len(forwards) == 2

    def test_single_maturity_returns_empty(self):
        spot_curve = {"1Y": 4.0}
        forwards = calculate_forward_rates(spot_curve)
        assert forwards == {}

    def test_forward_rates_are_positive_for_normal_curve(self):
        spot_curve = {"1Y": 3.0, "2Y": 3.5, "3Y": 4.0, "5Y": 4.5, "10Y": 5.0}
        forwards = calculate_forward_rates(spot_curve)
        for rate in forwards.values():
            assert rate > 0

    def test_empty_curve_returns_empty(self):
        forwards = calculate_forward_rates({})
        assert forwards == {}

    def test_forward_values_are_reasonable(self):
        """Forward rates should be in a reasonable range given the spot rates."""
        spot_curve = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0}
        forwards = calculate_forward_rates(spot_curve)

        # 1Y-2Y forward should be higher than 2Y spot for normal curve
        assert forwards["1Y-2Y"] > spot_curve["2Y"]
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\13-cicd-github-actions
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'forward_rates'`

- [ ] **Step 4: Implement forward_rates.py**

```python
# exercises/13-cicd-github-actions/src/forward_rates.py

"""
Forward rate curve derivation from spot rates.

Math:
  The forward rate f(t₁, t₂) is the implied rate for borrowing/lending
  between time t₁ and t₂, derived from spot rates.

  No-arbitrage condition:
    (1 + s₂)^t₂ = (1 + s₁)^t₁ × (1 + f(t₁,t₂))^(t₂-t₁)

  Solving for f(t₁,t���):
    f(t₁,t₂) = [(1 + s₂)^t₂ / (1 + s₁)^t₁]^(1/(t₂-t₁)) − 1

  Intuition:
    If 2Y spot is 5% and 1Y spot is 4%, the market implies that
    1Y rates one year from now will be ~6%. If you could lock in
    5% for 2 years or 4% for 1 year and roll, the forward rate
    is what makes you indifferent.

  Business use:
    - Pricing Forward Rate Agreements (FRAs)
    - Swap valuation (floating leg expectations)
    - Market expectations of future rate moves
"""

# Maturity labels → years (same as bootstrap module)
MATURITY_YEARS: dict[str, float] = {
    "1M": 1 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "1Y": 1.0,
    "2Y": 2.0,
    "3Y": 3.0,
    "5Y": 5.0,
    "7Y": 7.0,
    "10Y": 10.0,
    "20Y": 20.0,
    "30Y": 30.0,
}

MATURITY_ORDER = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]


def forward_rate_between(
    spot_short: float,
    years_short: float,
    spot_long: float,
    years_long: float,
) -> float:
    """Calculate the forward rate between two maturities.

    Args:
        spot_short: Spot rate for the shorter maturity (percent).
        years_short: Time to shorter maturity in years.
        spot_long: Spot rate for the longer maturity (percent).
        years_long: Time to longer maturity in years.

    Returns:
        Forward rate in percent.
    """
    s1 = spot_short / 100.0
    s2 = spot_long / 100.0
    t1 = years_short
    t2 = years_long
    dt = t2 - t1

    # f = [(1+s2)^t2 / (1+s1)^t1]^(1/dt) - 1
    forward = ((1 + s2) ** t2 / (1 + s1) ** t1) ** (1 / dt) - 1

    return round(forward * 100, 4)


def calculate_forward_rates(spot_curve: dict[str, float]) -> dict[str, float]:
    """Calculate forward rates between consecutive spot curve maturities.

    Args:
        spot_curve: Dict mapping maturity label to spot rate in percent.

    Returns:
        Dict mapping forward period label (e.g. "1Y-2Y") to forward rate in percent.
    """
    if len(spot_curve) < 2:
        return {}

    ordered = [(m, spot_curve[m]) for m in MATURITY_ORDER if m in spot_curve]
    forwards = {}

    for i in range(1, len(ordered)):
        label_short, rate_short = ordered[i - 1]
        label_long, rate_long = ordered[i]
        t_short = MATURITY_YEARS[label_short]
        t_long = MATURITY_YEARS[label_long]

        fwd = forward_rate_between(rate_short, t_short, rate_long, t_long)
        forwards[f"{label_short}-{label_long}"] = fwd

    return forwards
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 8 passed

- [ ] **Step 6: Create GitHub Actions workflow**

```yaml
# exercises/13-cicd-github-actions/.github/workflows/deploy.yml

name: Deploy Curves API to AWS Lambda

on:
  push:
    branches: [working]
    paths:
      - 'exercises/13-cicd-github-actions/**'
  pull_request:
    branches: [master]
    paths:
      - 'exercises/13-cicd-github-actions/**'

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        working-directory: exercises/13-cicd-github-actions
        run: pip install -e ".[dev]"
      - name: Run tests
        working-directory: exercises/13-cicd-github-actions
        run: pytest -v

  deploy:
    needs: test
    if: github.ref == 'refs/heads/working'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - name: Package Lambda
        working-directory: exercises/13-cicd-github-actions/src
        run: |
          pip install numpy -t package/
          cp forward_rates.py handler.py package/ 2>/dev/null || true
          cd package && zip -r ../deployment.zip .

      - name: Deploy to Lambda
        working-directory: exercises/13-cicd-github-actions/src
        run: |
          aws lambda update-function-code \
            --function-name quant-lab-forward-rates \
            --zip-file fileb://deployment.zip
```

Note: Setting up OIDC between GitHub and AWS requires creating an IAM Identity Provider and Role in AWS. We'll walk through this in the teaching conversation.

- [ ] **Step 7: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/13-cicd-github-actions/
git commit -m "feat(exercises): 13 CI/CD GitHub Actions + forward rate curve"
```

- [ ] **Step 8: Understand it — teaching conversation**

Topics to cover:
- **CI/CD pipeline:** Test on every push, deploy on push to working. No manual deployment.
- **OIDC vs access keys:** OIDC = no long-lived secrets in GitHub. AWS trusts GitHub's identity token. Better security.
- **Forward rate math deep-dive:**
  - No-arbitrage: two strategies must yield the same result — invest for 2Y at s₂, or invest for 1Y at s₁ and roll into 1Y forward at f₁₂
  - If forward > market expectation of future rate → borrowers prefer fixed, lenders prefer floating
  - Expectations hypothesis: forward rate = market's expectation of future spot rate (simplified, doesn't account for term premium)
  - Reality: forward rates include a term premium — investors demand extra yield for bearing duration risk
- **FRA pricing:** A Forward Rate Agreement pays the difference between the contracted forward rate and the realized rate. The forward curve tells you the "fair" FRA rate.

- [ ] **Step 9: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-cicd-forward-rate-curve.html`

```yaml
---
layout: post
title: "CI/CD to AWS: Forward Rate Curves from Spot Rates"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Quantitative Finance
tags:
  - cicd
  - github-actions
  - forward-rate
  - yield-curve
permalink: "/2026/04/XX/cicd-forward-rate-curve/"
---
```

- [ ] **Step 10: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-cicd-forward-rate-curve.html
git commit -m "post: CI/CD to AWS — forward rate curve derivation"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

### Task 6: Terraform Basics + Nelson-Siegel / Svensson Curve Fitting (Exercise 14)

**Concept:** Define all AWS infrastructure as code with Terraform. Implement parametric curve fitting — Nelson-Siegel and Svensson models that produce smooth yield curves from noisy market data.

**Files:**
- Create: `exercises/14-terraform-curve-fitting/pyproject.toml`
- Create: `exercises/14-terraform-curve-fitting/src/curve_fitting.py`
- Create: `exercises/14-terraform-curve-fitting/tests/test_curve_fitting.py`
- Create: `exercises/14-terraform-curve-fitting/terraform/main.tf`
- Create: `exercises/14-terraform-curve-fitting/terraform/variables.tf`
- Create: `exercises/14-terraform-curve-fitting/terraform/outputs.tf`
- Create: `finbytes_git/docs/_posts/2026-04-XX-terraform-nelson-siegel.html`

- [ ] **Step 1: Install Terraform**

```bash
winget install HashiCorp.Terraform
terraform --version
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "terraform-curve-fitting-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26.0",
    "scipy>=1.14.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["curve_fitting"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write failing tests**

```python
# exercises/14-terraform-curve-fitting/tests/test_curve_fitting.py

import numpy as np
import pytest
from curve_fitting import (
    nelson_siegel,
    nelson_siegel_svensson,
    fit_nelson_siegel,
    fit_svensson,
    cubic_spline_interpolate,
)


class TestNelsonSiegel:
    def test_level_component(self):
        """beta0 is the long-term rate (as tau → ∞)."""
        rate = nelson_siegel(tau=30.0, beta0=5.0, beta1=0.0, beta2=0.0, lam=1.0)
        assert rate == pytest.approx(5.0, abs=0.01)

    def test_slope_component(self):
        """beta1 affects short end. At tau=0, NS → beta0 + beta1."""
        rate = nelson_siegel(tau=0.01, beta0=5.0, beta1=-2.0, beta2=0.0, lam=1.0)
        assert rate == pytest.approx(3.0, abs=0.1)

    def test_curvature_component(self):
        """beta2 creates a hump at intermediate maturities."""
        short = nelson_siegel(tau=0.5, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        mid = nelson_siegel(tau=2.0, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        long = nelson_siegel(tau=20.0, beta0=5.0, beta1=0.0, beta2=3.0, lam=2.0)
        # Mid-term should be the hump
        assert mid > short or mid > long


class TestNelsonSiegelSvensson:
    def test_reduces_to_ns_when_beta3_zero(self):
        """With beta3=0, NSS should equal NS."""
        ns = nelson_siegel(tau=5.0, beta0=5.0, beta1=-1.0, beta2=2.0, lam=1.5)
        nss = nelson_siegel_svensson(
            tau=5.0, beta0=5.0, beta1=-1.0, beta2=2.0, beta3=0.0,
            lam1=1.5, lam2=1.0,
        )
        assert nss == pytest.approx(ns, abs=0.001)


class TestFitNelsonSiegel:
    def test_fits_normal_curve(self):
        """Fit NS to a simple normal yield curve."""
        maturities = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0])
        yields = np.array([4.80, 4.70, 4.50, 4.30, 4.20, 4.15, 4.18, 4.25, 4.40, 4.45])

        params, fitted, rmse = fit_nelson_siegel(maturities, yields)

        assert "beta0" in params
        assert "beta1" in params
        assert "beta2" in params
        assert "lambda" in params
        assert len(fitted) == len(maturities)
        assert rmse < 0.2  # reasonable fit

    def test_fitted_values_close_to_input(self):
        maturities = np.array([1.0, 2.0, 5.0, 10.0])
        yields = np.array([4.0, 4.2, 4.5, 4.8])

        _, fitted, _ = fit_nelson_siegel(maturities, yields)

        np.testing.assert_allclose(fitted, yields, atol=0.3)


class TestFitSvensson:
    def test_fits_humped_curve(self):
        """NSS should handle humped curves better than NS."""
        maturities = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0])
        yields = np.array([4.80, 4.90, 5.10, 5.20, 5.15, 4.90, 4.70, 4.50, 4.40, 4.45])

        params, fitted, rmse = fit_svensson(maturities, yields)

        assert "beta3" in params
        assert "lambda2" in params
        assert rmse < 0.2


class TestCubicSpline:
    def test_interpolates_between_points(self):
        maturities = np.array([1.0, 2.0, 5.0, 10.0, 30.0])
        yields = np.array([4.0, 4.2, 4.5, 4.8, 5.0])
        target = np.array([3.0, 7.0, 20.0])

        interpolated = cubic_spline_interpolate(maturities, yields, target)

        assert len(interpolated) == 3
        # 3Y should be between 2Y and 5Y
        assert 4.2 < interpolated[0] < 4.5
        # 7Y should be between 5Y and 10Y
        assert 4.5 < interpolated[1] < 4.8

    def test_exact_at_knot_points(self):
        maturities = np.array([1.0, 5.0, 10.0])
        yields = np.array([4.0, 4.5, 5.0])

        interpolated = cubic_spline_interpolate(maturities, yields, maturities)

        np.testing.assert_allclose(interpolated, yields, atol=0.001)
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\14-terraform-curve-fitting
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 5: Implement curve_fitting.py**

```python
# exercises/14-terraform-curve-fitting/src/curve_fitting.py

"""
Parametric yield curve fitting: Nelson-Siegel and Nelson-Siegel-Svensson models.

Nelson-Siegel (1987) — 4 parameters:
  y(τ) = β₀ + β₁ × [(1-e^(-τ/λ))/(τ/λ)]
             + β₂ × [(1-e^(-τ/λ))/(τ/λ) - e^(-τ/λ)]

  β₀ = long-term level (as τ → ∞, y → β₀)
  β₁ = short-term component (slope). β₀+β₁ = instantaneous rate.
  β₂ = medium-term component (curvature/hump)
  λ  = decay factor (controls where the hump peaks)

Svensson (1994) — 6 parameters:
  Adds a second hump term for better long-end fit:
  y(τ) = NS(τ) + β₃ × [(1-e^(-τ/λ₂))/(τ/λ₂) - e^(-τ/λ₂)]

Business context:
  Central banks (ECB, Bundesbank) use Nelson-Siegel-Svensson to publish
  official yield curves. Traders use fitted curves to identify rich/cheap
  bonds — if a bond's yield is above the fitted curve, it's cheap relative
  to the model.

Cubic spline:
  An alternative that passes exactly through observed points. Useful for
  interpolation but can oscillate between points. Not parametric — no
  economic interpretation of parameters.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline


def nelson_siegel(
    tau: float, beta0: float, beta1: float, beta2: float, lam: float
) -> float:
    """Evaluate the Nelson-Siegel model at maturity tau.

    Args:
        tau: Time to maturity in years.
        beta0: Long-term level.
        beta1: Short-term component.
        beta2: Medium-term component.
        lam: Decay factor.

    Returns:
        Yield in percent.
    """
    if tau < 1e-6:
        return beta0 + beta1

    x = tau / lam
    factor1 = (1 - np.exp(-x)) / x
    factor2 = factor1 - np.exp(-x)

    return beta0 + beta1 * factor1 + beta2 * factor2


def nelson_siegel_svensson(
    tau: float,
    beta0: float, beta1: float, beta2: float, beta3: float,
    lam1: float, lam2: float,
) -> float:
    """Evaluate the Nelson-Siegel-Svensson model at maturity tau.

    Args:
        tau: Time to maturity in years.
        beta0-beta3: Model parameters.
        lam1, lam2: Decay factors.

    Returns:
        Yield in percent.
    """
    ns = nelson_siegel(tau, beta0, beta1, beta2, lam1)

    if tau < 1e-6:
        return ns

    x2 = tau / lam2
    factor = (1 - np.exp(-x2)) / x2 - np.exp(-x2)

    return ns + beta3 * factor


def fit_nelson_siegel(
    maturities: np.ndarray, yields: np.ndarray
) -> tuple[dict[str, float], np.ndarray, float]:
    """Fit Nelson-Siegel model to observed yields.

    Args:
        maturities: Array of maturities in years.
        yields: Array of observed yields in percent.

    Returns:
        Tuple of (parameters dict, fitted yields array, RMSE).
    """
    def objective(params):
        b0, b1, b2, lam = params
        if lam <= 0.01:
            return 1e10
        fitted = np.array([nelson_siegel(t, b0, b1, b2, lam) for t in maturities])
        return np.sum((fitted - yields) ** 2)

    # Initial guess: level ≈ long rate, slope ≈ short-long spread
    b0_init = float(yields[-1])
    b1_init = float(yields[0] - yields[-1])
    x0 = [b0_init, b1_init, 0.0, 1.5]

    result = minimize(objective, x0, method="Nelder-Mead",
                      options={"maxiter": 10000, "xatol": 1e-8})

    b0, b1, b2, lam = result.x
    fitted = np.array([nelson_siegel(t, b0, b1, b2, lam) for t in maturities])
    rmse = float(np.sqrt(np.mean((fitted - yields) ** 2)))

    params = {"beta0": round(b0, 4), "beta1": round(b1, 4),
              "beta2": round(b2, 4), "lambda": round(lam, 4)}

    return params, fitted, rmse


def fit_svensson(
    maturities: np.ndarray, yields: np.ndarray
) -> tuple[dict[str, float], np.ndarray, float]:
    """Fit Nelson-Siegel-Svensson model to observed yields.

    Args:
        maturities: Array of maturities in years.
        yields: Array of observed yields in percent.

    Returns:
        Tuple of (parameters dict, fitted yields array, RMSE).
    """
    def objective(params):
        b0, b1, b2, b3, lam1, lam2 = params
        if lam1 <= 0.01 or lam2 <= 0.01:
            return 1e10
        fitted = np.array([
            nelson_siegel_svensson(t, b0, b1, b2, b3, lam1, lam2)
            for t in maturities
        ])
        return np.sum((fitted - yields) ** 2)

    b0_init = float(yields[-1])
    b1_init = float(yields[0] - yields[-1])
    x0 = [b0_init, b1_init, 0.0, 0.0, 1.5, 3.0]

    result = minimize(objective, x0, method="Nelder-Mead",
                      options={"maxiter": 20000, "xatol": 1e-8})

    b0, b1, b2, b3, lam1, lam2 = result.x
    fitted = np.array([
        nelson_siegel_svensson(t, b0, b1, b2, b3, lam1, lam2)
        for t in maturities
    ])
    rmse = float(np.sqrt(np.mean((fitted - yields) ** 2)))

    params = {
        "beta0": round(b0, 4), "beta1": round(b1, 4),
        "beta2": round(b2, 4), "beta3": round(b3, 4),
        "lambda1": round(lam1, 4), "lambda2": round(lam2, 4),
    }

    return params, fitted, rmse


def cubic_spline_interpolate(
    maturities: np.ndarray, yields: np.ndarray, target_maturities: np.ndarray
) -> np.ndarray:
    """Interpolate yields at target maturities using cubic spline.

    Args:
        maturities: Observed maturities in years.
        yields: Observed yields in percent.
        target_maturities: Maturities to interpolate at.

    Returns:
        Interpolated yields array.
    """
    cs = CubicSpline(maturities, yields)
    return cs(target_maturities)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 9 passed

- [ ] **Step 7: Create Terraform configuration**

```hcl
# exercises/14-terraform-curve-fitting/terraform/variables.tf

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "quant-lab"
}

variable "s3_bucket_name" {
  description = "S3 bucket for yield data"
  type        = string
  default     = "finbytes-quant-lab-data"
}
```

```hcl
# exercises/14-terraform-curve-fitting/terraform/main.tf

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state in S3 (create this bucket manually first)
  backend "s3" {
    bucket = "finbytes-quant-lab-tfstate"
    key    = "exercises/14-curve-fitting/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "quant-lab"
}

# --- S3 Bucket for yield data ---
resource "aws_s3_bucket" "data" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- IAM Role for Lambda ---
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.project_name}-lambda-s3"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.data.arn,
        "${aws_s3_bucket.data.arn}/*"
      ]
    }]
  })
}

# --- Lambda Function for curve fitting ---
resource "aws_lambda_function" "curve_fitting" {
  function_name = "${var.project_name}-curve-fitting"
  runtime       = "python3.11"
  handler       = "handler.lambda_handler"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 60
  memory_size   = 512

  filename         = "${path.module}/../src/deployment.zip"
  source_code_hash = filebase64sha256("${path.module}/../src/deployment.zip")
}

# --- API Gateway ---
resource "aws_apigatewayv2_api" "curves" {
  name          = "${var.project_name}-curves-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.curves.id
  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "curve_fitting" {
  api_id                 = aws_apigatewayv2_api.curves.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.curve_fitting.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "fit_curve" {
  api_id    = aws_apigatewayv2_api.curves.id
  route_key = "POST /curves/fit"
  target    = "integrations/${aws_apigatewayv2_integration.curve_fitting.id}"
}

resource "aws_lambda_permission" "apigw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.curve_fitting.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.curves.execution_arn}/*/*"
}
```

```hcl
# exercises/14-terraform-curve-fitting/terraform/outputs.tf

output "api_url" {
  value       = aws_apigatewayv2_stage.dev.invoke_url
  description = "Base URL of the Curves API"
}

output "lambda_function_name" {
  value = aws_lambda_function.curve_fitting.function_name
}

output "s3_bucket" {
  value = aws_s3_bucket.data.bucket
}
```

- [ ] **Step 8: Deploy with Terraform**

```bash
# Create the state bucket first (one-time)
aws s3 mb s3://finbytes-quant-lab-tfstate --region us-east-1 --profile quant-lab

# Build deployment package
cd C:\codebase\quant_lab\exercises\14-terraform-curve-fitting\src
pip install numpy scipy -t package/
cp curve_fitting.py package/
# Create handler.py for Lambda (similar to exercise 12)
cd package && zip -r ../deployment.zip . && cd ..

# Deploy
cd C:\codebase\quant_lab\exercises\14-terraform-curve-fitting\terraform
terraform init
terraform plan
terraform apply
```

- [ ] **Step 9: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/14-terraform-curve-fitting/
git commit -m "feat(exercises): 14 Terraform + Nelson-Siegel/Svensson curve fitting"
```

- [ ] **Step 10: Understand it — teaching conversation**

Topics to cover:
- **Terraform fundamentals:** Declarative infra — describe what you want, Terraform figures out how to get there. `plan` shows the diff, `apply` executes it, `destroy` tears it down.
- **State management:** Terraform tracks what exists via state file. Remote state in S3 = shared, versioned, locked.
- **Nelson-Siegel intuition:**
  - β₀ is the level — where rates converge at very long maturities (the market's long-run inflation + real rate expectation)
  - β₁ is the slope — negative β₁ means normal curve (short rates below long rates). Driven by rate expectations.
  - β₂ is the curvature — creates a hump. Driven by uncertainty about medium-term rates.
  - λ controls where the hump peaks — smaller λ = hump at shorter maturities
- **Why central banks use NSS:** The ECB publishes daily NSS parameters. The 6 parameters compress the entire curve into a handful of interpretable numbers. Analysts track β₀ over time to see long-run rate expectations evolve.
- **Cubic spline vs parametric:** Spline passes through every point (zero error) but can oscillate. NS/NSS smooth the noise but may miss local features. Use spline for interpolation, NS/NSS for economic interpretation.

- [ ] **Step 11: Document it — write blog post**

Create `finbytes_git/docs/_posts/2026-04-XX-terraform-nelson-siegel.html`

```yaml
---
layout: post
title: "Terraform & Nelson-Siegel: Infrastructure as Code Meets Curve Fitting"
date: 2026-04-XX
published: true
status: publish
categories:
  - AWS
  - Quantitative Finance
tags:
  - terraform
  - iac
  - nelson-siegel
  - curve-fitting
  - yield-curve
permalink: "/2026/04/XX/terraform-nelson-siegel/"
---
```

- [ ] **Step 12: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-04-XX-terraform-nelson-siegel.html
git commit -m "post: Terraform + Nelson-Siegel/Svensson curve fitting"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

## Capstone A: Bond Pricing Engine (Task 7)

**Goal:** Assemble exercises 09-14 into a complete bond pricing service. Daily yield ingestion, curve construction (spot, forward, fitted), bond pricing (DCF, Z-spread, duration, convexity), Claude AI narrative. Deployed on AWS with Terraform and CI/CD.

**Files:**
- Create: `projects/bond-pricing-engine/pyproject.toml`
- Create: `projects/bond-pricing-engine/src/engine/__init__.py`
- Create: `projects/bond-pricing-engine/src/engine/models.py`
- Create: `projects/bond-pricing-engine/src/engine/market_data.py`
- Create: `projects/bond-pricing-engine/src/engine/curves.py`
- Create: `projects/bond-pricing-engine/src/engine/pricer.py`
- Create: `projects/bond-pricing-engine/src/engine/narrative.py`
- Create: `projects/bond-pricing-engine/src/engine/db.py`
- Create: `projects/bond-pricing-engine/src/engine/db_models.py`
- Create: `projects/bond-pricing-engine/src/engine/main.py`
- Create: `projects/bond-pricing-engine/tests/test_curves.py`
- Create: `projects/bond-pricing-engine/tests/test_pricer.py`
- Create: `projects/bond-pricing-engine/tests/test_api.py`
- Create: `projects/bond-pricing-engine/terraform/`
- Create: `projects/bond-pricing-engine/Dockerfile`
- Create: `projects/bond-pricing-engine/alembic.ini`
- Create: `projects/bond-pricing-engine/alembic/`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-bond-pricing-engine-capstone.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "bond-pricing-engine"
version = "0.1.0"
description = "Bond pricing engine with yield curve construction and AI narratives"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.9.0",
    "numpy>=1.26.0",
    "scipy>=1.14.0",
    "pandas>=2.0.0",
    "fredapi>=0.5.2",
    "anthropic>=0.40.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "boto3>=1.35.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
    "httpx>=0.27.0",
    "moto[s3]>=5.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create Pydantic models**

```python
# projects/bond-pricing-engine/src/engine/models.py

from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class ParYields(BaseModel):
    """Treasury par yield curve for a single date."""
    curve_date: date
    yields: dict[str, float]  # e.g. {"1M": 5.25, "10Y": 4.30}
    source: str = "FRED"


class SpotCurve(BaseModel):
    """Bootstrapped zero-coupon rate curve."""
    curve_date: date
    rates: dict[str, float]


class ForwardCurve(BaseModel):
    """Implied forward rate curve."""
    curve_date: date
    rates: dict[str, float]  # e.g. {"1Y-2Y": 5.02, "2Y-5Y": 4.80}


class FittedCurve(BaseModel):
    """Parametric fitted curve (Nelson-Siegel or Svensson)."""
    curve_date: date
    model: str  # "nelson-siegel" or "svensson"
    params: dict[str, float]
    fitted_rates: dict[str, float]
    rmse: float


class CurveSet(BaseModel):
    """All curves for a single date."""
    curve_date: date
    par: dict[str, float]
    spot: dict[str, float]
    forward: dict[str, float]
    fitted_ns: FittedCurve | None = None
    fitted_nss: FittedCurve | None = None


class BondSpec(BaseModel):
    """Bond specification for pricing."""
    coupon: float = Field(..., ge=0, description="Annual coupon rate in percent")
    maturity: date
    face_value: float = Field(default=1000.0, gt=0)
    frequency: int = Field(default=2, ge=1, le=12, description="Coupons per year")
    callable: bool = False


class PricingResult(BaseModel):
    """Bond pricing output."""
    clean_price: float
    dirty_price: float
    accrued_interest: float
    ytm: float  # yield to maturity in percent
    z_spread: float | None = None  # basis points
    macaulay_duration: float  # years
    modified_duration: float
    convexity: float
    dv01: float  # dollar value of 1bp yield change


class BondAnalysis(BaseModel):
    """Full bond analysis with narrative."""
    bond: BondSpec
    pricing: PricingResult
    curve_date: date
    narrative: str
    generated_at: datetime


class PriceRequest(BaseModel):
    """API request body for bond pricing."""
    coupon: float = Field(..., ge=0)
    maturity: date
    face_value: float = Field(default=1000.0, gt=0)
    frequency: int = Field(default=2)
    curve_date: date | None = None  # defaults to latest

    @field_validator("maturity")
    @classmethod
    def maturity_in_future(cls, v: date) -> date:
        if v <= date.today():
            raise ValueError("maturity must be in the future")
        return v


class AnalyzeRequest(BaseModel):
    """API request body for full analysis with narrative."""
    coupon: float = Field(..., ge=0)
    maturity: date
    face_value: float = Field(default=1000.0, gt=0)
    frequency: int = Field(default=2)
    curve_date: date | None = None
```

- [ ] **Step 3: Write failing tests for curves module**

```python
# projects/bond-pricing-engine/tests/test_curves.py

import numpy as np
import pytest
from engine.curves import (
    bootstrap_spot_curve,
    calculate_forward_rates,
    fit_curves,
)


class TestBootstrapSpotCurve:
    def test_spot_from_par(self):
        par = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0, "10Y": 5.5}
        spot = bootstrap_spot_curve(par)
        assert "1Y" in spot
        assert "10Y" in spot
        assert spot["1Y"] == pytest.approx(4.0, abs=0.01)
        assert spot["10Y"] > par["10Y"]  # normal curve → spot > par at long end

    def test_empty_returns_empty(self):
        assert bootstrap_spot_curve({}) == {}


class TestForwardRates:
    def test_forward_from_spot(self):
        spot = {"1Y": 4.0, "2Y": 4.5, "5Y": 5.0}
        forward = calculate_forward_rates(spot)
        assert "1Y-2Y" in forward
        assert "2Y-5Y" in forward
        assert forward["1Y-2Y"] > spot["2Y"]


class TestFitCurves:
    def test_fit_returns_ns_and_nss(self):
        par = {
            "1M": 5.25, "3M": 5.30, "6M": 5.20,
            "1Y": 4.80, "2Y": 4.50, "3Y": 4.30,
            "5Y": 4.20, "7Y": 4.25, "10Y": 4.30,
        }
        ns, nss = fit_curves(par)
        assert ns.model == "nelson-siegel"
        assert nss.model == "svensson"
        assert ns.rmse < 0.5
        assert "beta0" in ns.params
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\projects\bond-pricing-engine
pip install -e ".[dev]"
pytest tests/test_curves.py -v
```

Expected: FAIL

- [ ] **Step 5: Implement curves.py**

```python
# projects/bond-pricing-engine/src/engine/curves.py

"""
Yield curve construction: bootstrap, forward rates, and parametric fitting.
Reuses math from exercises 12-14, assembled into a single module.
"""

import numpy as np
from datetime import date
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline
from engine.models import FittedCurve

MATURITY_YEARS: dict[str, float] = {
    "1M": 1/12, "3M": 3/12, "6M": 6/12,
    "1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0,
    "7Y": 7.0, "10Y": 10.0, "20Y": 20.0, "30Y": 30.0,
}
MATURITY_ORDER = ["1M","3M","6M","1Y","2Y","3Y","5Y","7Y","10Y","20Y","30Y"]


def bootstrap_spot_curve(par_yields: dict[str, float]) -> dict[str, float]:
    """Bootstrap zero-coupon spot rates from par yields (percent)."""
    if not par_yields:
        return {}

    ordered = [m for m in MATURITY_ORDER if m in par_yields]
    par_dec = {m: par_yields[m] / 100.0 for m in ordered}
    years = {m: MATURITY_YEARS[m] for m in ordered}
    spot_dec: dict[str, float] = {}

    for i, label in enumerate(ordered):
        c = par_dec[label]
        t = years[label]
        if i == 0:
            spot_dec[label] = c
        else:
            pv = sum(c / ((1 + spot_dec[p]) ** years[p]) for p in ordered[:i])
            denom = 1.0 - pv
            spot_dec[label] = ((c + 1.0) / denom) ** (1.0 / t) - 1.0 if denom > 0 else c

    return {m: round(spot_dec[m] * 100, 4) for m in ordered}


def calculate_forward_rates(spot_curve: dict[str, float]) -> dict[str, float]:
    """Calculate forward rates between consecutive spot curve maturities (percent)."""
    if len(spot_curve) < 2:
        return {}

    ordered = [(m, spot_curve[m]) for m in MATURITY_ORDER if m in spot_curve]
    forwards = {}
    for i in range(1, len(ordered)):
        lbl_s, r_s = ordered[i-1]
        lbl_l, r_l = ordered[i]
        t_s, t_l = MATURITY_YEARS[lbl_s], MATURITY_YEARS[lbl_l]
        s1, s2 = r_s / 100, r_l / 100
        dt = t_l - t_s
        fwd = ((1+s2)**t_l / (1+s1)**t_s) ** (1/dt) - 1
        forwards[f"{lbl_s}-{lbl_l}"] = round(fwd * 100, 4)
    return forwards


def _nelson_siegel(tau, b0, b1, b2, lam):
    if tau < 1e-6:
        return b0 + b1
    x = tau / lam
    f1 = (1 - np.exp(-x)) / x
    return b0 + b1 * f1 + b2 * (f1 - np.exp(-x))


def _nelson_siegel_svensson(tau, b0, b1, b2, b3, lam1, lam2):
    ns = _nelson_siegel(tau, b0, b1, b2, lam1)
    if tau < 1e-6:
        return ns
    x2 = tau / lam2
    return ns + b3 * ((1 - np.exp(-x2)) / x2 - np.exp(-x2))


def fit_curves(
    par_yields: dict[str, float], curve_date: date | None = None
) -> tuple[FittedCurve, FittedCurve]:
    """Fit Nelson-Siegel and Svensson models to par yields.

    Returns (ns_curve, nss_curve).
    """
    cd = curve_date or date.today()
    ordered = [(m, par_yields[m]) for m in MATURITY_ORDER if m in par_yields]
    mats = np.array([MATURITY_YEARS[m] for m, _ in ordered])
    ylds = np.array([y for _, y in ordered])

    # Fit Nelson-Siegel
    def ns_obj(p):
        b0, b1, b2, lam = p
        if lam <= 0.01: return 1e10
        return np.sum((_nelson_siegel(t, b0, b1, b2, lam) - y)**2 for t, y in zip(mats, ylds))

    ns_res = minimize(ns_obj, [ylds[-1], ylds[0]-ylds[-1], 0, 1.5],
                      method="Nelder-Mead", options={"maxiter": 10000})
    b0, b1, b2, lam = ns_res.x
    ns_fitted = {m: round(_nelson_siegel(MATURITY_YEARS[m], b0, b1, b2, lam), 4)
                 for m, _ in ordered}
    ns_rmse = float(np.sqrt(np.mean([(ns_fitted[m]-y)**2 for m, y in ordered])))

    ns_curve = FittedCurve(
        curve_date=cd, model="nelson-siegel",
        params={"beta0": round(b0,4), "beta1": round(b1,4), "beta2": round(b2,4), "lambda": round(lam,4)},
        fitted_rates=ns_fitted, rmse=round(ns_rmse, 4),
    )

    # Fit Svensson
    def nss_obj(p):
        b0, b1, b2, b3, l1, l2 = p
        if l1 <= 0.01 or l2 <= 0.01: return 1e10
        return np.sum((_nelson_siegel_svensson(t, b0, b1, b2, b3, l1, l2) - y)**2 for t, y in zip(mats, ylds))

    nss_res = minimize(nss_obj, [ylds[-1], ylds[0]-ylds[-1], 0, 0, 1.5, 3.0],
                       method="Nelder-Mead", options={"maxiter": 20000})
    b0, b1, b2, b3, l1, l2 = nss_res.x
    nss_fitted = {m: round(_nelson_siegel_svensson(MATURITY_YEARS[m], b0, b1, b2, b3, l1, l2), 4)
                  for m, _ in ordered}
    nss_rmse = float(np.sqrt(np.mean([(nss_fitted[m]-y)**2 for m, y in ordered])))

    nss_curve = FittedCurve(
        curve_date=cd, model="svensson",
        params={"beta0": round(b0,4), "beta1": round(b1,4), "beta2": round(b2,4),
                "beta3": round(b3,4), "lambda1": round(l1,4), "lambda2": round(l2,4)},
        fitted_rates=nss_fitted, rmse=round(nss_rmse, 4),
    )

    return ns_curve, nss_curve
```

- [ ] **Step 6: Run curve tests to verify they pass**

```bash
pytest tests/test_curves.py -v
```

Expected: 4 passed

- [ ] **Step 7: Write failing tests for the bond pricer**

```python
# projects/bond-pricing-engine/tests/test_pricer.py

import pytest
from datetime import date
from engine.pricer import price_bond, calculate_z_spread
from engine.models import BondSpec


class TestPriceBond:
    def test_par_bond_prices_at_par(self):
        """A bond with coupon = YTM should price at ~100 (per 100 face)."""
        bond = BondSpec(coupon=5.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        # Flat spot curve at 5%
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        result = price_bond(bond, spot, as_of=date(2026, 4, 4))
        assert result.clean_price == pytest.approx(100.0, abs=1.0)

    def test_discount_bond(self):
        """Bond with coupon below market rates should price below par."""
        bond = BondSpec(coupon=2.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        result = price_bond(bond, spot, as_of=date(2026, 4, 4))
        assert result.clean_price < 100.0

    def test_premium_bond(self):
        """Bond with coupon above market rates should price above par."""
        bond = BondSpec(coupon=8.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        result = price_bond(bond, spot, as_of=date(2026, 4, 4))
        assert result.clean_price > 100.0

    def test_duration_positive(self):
        bond = BondSpec(coupon=5.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        result = price_bond(bond, spot, as_of=date(2026, 4, 4))
        assert result.macaulay_duration > 0
        assert result.modified_duration > 0
        assert result.convexity > 0

    def test_longer_maturity_higher_duration(self):
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0, "10Y": 5.0}
        bond_5y = BondSpec(coupon=5.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        bond_10y = BondSpec(coupon=5.0, maturity=date(2036, 4, 4), face_value=100.0, frequency=2)
        r5 = price_bond(bond_5y, spot, as_of=date(2026, 4, 4))
        r10 = price_bond(bond_10y, spot, as_of=date(2026, 4, 4))
        assert r10.macaulay_duration > r5.macaulay_duration


class TestZSpread:
    def test_z_spread_zero_for_treasury(self):
        """A bond priced exactly off the spot curve has Z-spread ≈ 0."""
        bond = BondSpec(coupon=5.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        result = price_bond(bond, spot, as_of=date(2026, 4, 4))
        z = calculate_z_spread(bond, spot, result.clean_price, as_of=date(2026, 4, 4))
        assert abs(z) < 5  # within 5 bps of zero

    def test_z_spread_positive_for_cheap_bond(self):
        """A bond trading below model price has positive Z-spread."""
        bond = BondSpec(coupon=5.0, maturity=date(2031, 4, 4), face_value=100.0, frequency=2)
        spot = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        # Price below par → positive spread
        z = calculate_z_spread(bond, spot, 95.0, as_of=date(2026, 4, 4))
        assert z > 0
```

- [ ] **Step 8: Run pricer tests to verify they fail**

```bash
pytest tests/test_pricer.py -v
```

Expected: FAIL

- [ ] **Step 9: Implement pricer.py**

```python
# projects/bond-pricing-engine/src/engine/pricer.py

"""
Bond pricing: DCF from spot curve, Z-spread, duration, convexity.

Pricing formula:
  P = Σ (CF_i / (1 + s_i + z)^t_i)

  where CF_i = coupon/frequency for intermediate, coupon/frequency + face for final
        s_i  = interpolated spot rate for cash flow time t_i
        z    = Z-spread (0 for treasury pricing)

Duration (Macaulay):
  D = (1/P) × Σ (t_i × CF_i / (1+y)^t_i)
  Weighted average time to cash flows.

Modified duration:
  D_mod = D_mac / (1 + y/k)
  Price sensitivity: ΔP/P ≈ -D_mod × Δy

Convexity:
  C = (1/P) × Σ (t_i × (t_i+1/k) × CF_i / (1+y/k)^(t_i×k+2))
  Second-order correction: ΔP/P ≈ -D_mod × Δy + 0.5 × C × Δy²
"""

import numpy as np
from datetime import date
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from engine.models import BondSpec, PricingResult

MATURITY_YEARS = {
    "1M": 1/12, "3M": 3/12, "6M": 6/12,
    "1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0,
    "7Y": 7.0, "10Y": 10.0, "20Y": 20.0, "30Y": 30.0,
}


def _interpolate_spot(spot_curve: dict[str, float], target_years: np.ndarray) -> np.ndarray:
    """Interpolate spot rates at arbitrary maturities using cubic spline."""
    mats = sorted([(MATURITY_YEARS[m], spot_curve[m]) for m in spot_curve])
    x = np.array([m[0] for m in mats])
    y = np.array([m[1] for m in mats])
    cs = CubicSpline(x, y, extrapolate=True)
    return cs(target_years)


def _cash_flow_schedule(bond: BondSpec, as_of: date) -> tuple[np.ndarray, np.ndarray]:
    """Generate cash flow times (years) and amounts.

    Returns (times, cash_flows) arrays.
    """
    coupon_per_period = bond.coupon / bond.frequency * bond.face_value / 100.0
    total_years = (bond.maturity - as_of).days / 365.25
    periods = int(np.ceil(total_years * bond.frequency))

    times = []
    cfs = []
    for i in range(1, periods + 1):
        t = i / bond.frequency
        if t <= total_years + 0.01:  # small tolerance
            cf = coupon_per_period
            if i == periods:
                cf += bond.face_value  # final payment includes principal
            times.append(t)
            cfs.append(cf)

    return np.array(times), np.array(cfs)


def price_bond(
    bond: BondSpec,
    spot_curve: dict[str, float],
    as_of: date,
    z_spread_bps: float = 0.0,
) -> PricingResult:
    """Price a bond using DCF from spot curve.

    Args:
        bond: Bond specification.
        spot_curve: Spot rates in percent.
        as_of: Pricing date.
        z_spread_bps: Z-spread in basis points to add to spot rates.

    Returns:
        PricingResult with price, yield, duration, convexity.
    """
    times, cfs = _cash_flow_schedule(bond, as_of)
    spots_pct = _interpolate_spot(spot_curve, times)
    spots = spots_pct / 100.0 + z_spread_bps / 10000.0

    # Discounted cash flows
    discount_factors = 1.0 / (1 + spots) ** times
    pv = cfs * discount_factors
    clean_price = float(np.sum(pv))

    # Accrued interest (simplified — assumes linear accrual)
    period_years = 1.0 / bond.frequency
    time_since_last = period_years - (times[0] if len(times) > 0 else 0)
    coupon_per_period = bond.coupon / bond.frequency * bond.face_value / 100.0
    accrued = coupon_per_period * (time_since_last / period_years) if time_since_last > 0 else 0.0
    dirty_price = clean_price + accrued

    # YTM — solve for yield that gives this price
    def ytm_objective(y):
        df = 1.0 / (1 + y / bond.frequency) ** (times * bond.frequency)
        return float(np.sum(cfs * df)) - clean_price

    try:
        ytm = brentq(ytm_objective, -0.05, 0.50) * 100
    except ValueError:
        ytm = 0.0

    # Macaulay duration
    y_dec = ytm / 100.0
    df_ytm = 1.0 / (1 + y_dec / bond.frequency) ** (times * bond.frequency)
    pv_ytm = cfs * df_ytm
    mac_duration = float(np.sum(times * pv_ytm) / np.sum(pv_ytm))

    # Modified duration
    mod_duration = mac_duration / (1 + y_dec / bond.frequency)

    # Convexity
    k = bond.frequency
    convexity = float(np.sum(times * (times + 1/k) * cfs * df_ytm / (1 + y_dec/k)**2) / np.sum(pv_ytm))

    # DV01 — dollar value of 1bp yield change
    dv01 = mod_duration * clean_price / 10000.0

    return PricingResult(
        clean_price=round(clean_price, 4),
        dirty_price=round(dirty_price, 4),
        accrued_interest=round(accrued, 4),
        ytm=round(ytm, 4),
        z_spread=round(z_spread_bps, 2) if z_spread_bps != 0 else None,
        macaulay_duration=round(mac_duration, 4),
        modified_duration=round(mod_duration, 4),
        convexity=round(convexity, 4),
        dv01=round(dv01, 4),
    )


def calculate_z_spread(
    bond: BondSpec,
    spot_curve: dict[str, float],
    market_price: float,
    as_of: date,
) -> float:
    """Calculate Z-spread: constant spread over spot curve matching market price.

    Args:
        bond: Bond specification.
        spot_curve: Spot rates in percent.
        market_price: Observed market price.
        as_of: Pricing date.

    Returns:
        Z-spread in basis points.
    """
    def objective(z_bps):
        result = price_bond(bond, spot_curve, as_of, z_spread_bps=z_bps)
        return result.clean_price - market_price

    try:
        z = brentq(objective, -500, 2000)
        return round(z, 2)
    except ValueError:
        return 0.0
```

- [ ] **Step 10: Run pricer tests to verify they pass**

```bash
pytest tests/test_pricer.py -v
```

Expected: 7 passed

- [ ] **Step 11: Implement market_data.py**

```python
# projects/bond-pricing-engine/src/engine/market_data.py

"""Fetch treasury yield data from FRED and S3."""

import json
import boto3
from datetime import date, timedelta
from fredapi import Fred

TREASURY_SERIES = {
    "DGS1MO": "1M", "DGS3MO": "3M", "DGS6MO": "6M",
    "DGS1": "1Y", "DGS2": "2Y", "DGS3": "3Y", "DGS5": "5Y",
    "DGS7": "7Y", "DGS10": "10Y", "DGS20": "20Y", "DGS30": "30Y",
}


def fetch_par_yields(api_key: str, as_of: date | None = None) -> dict[str, float]:
    """Fetch US Treasury par yields from FRED."""
    fred = Fred(api_key=api_key)
    target = as_of or date.today()
    start = target - timedelta(days=7)

    yields = {}
    for series_id, label in TREASURY_SERIES.items():
        data = fred.get_series(series_id, observation_start=start, observation_end=target)
        data = data.dropna()
        if len(data) > 0:
            yields[label] = round(float(data.iloc[-1]), 2)
    return yields


def upload_to_s3(yields: dict[str, float], bucket: str, as_of: date, s3_client=None):
    """Upload yield data to S3."""
    s3 = s3_client or boto3.client("s3")
    data = {"date": as_of.isoformat(), "source": "FRED", "yields": yields}
    s3.put_object(
        Bucket=bucket,
        Key=f"par-yields/{as_of.isoformat()}.json",
        Body=json.dumps(data),
        ContentType="application/json",
    )
    return data
```

- [ ] **Step 12: Implement narrative.py**

```python
# projects/bond-pricing-engine/src/engine/narrative.py

"""Claude AI narrative generation for bond pricing analysis."""

import os
from anthropic import Anthropic
from engine.models import BondSpec, PricingResult, CurveSet


class BondNarrator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

    def generate(
        self,
        bond: BondSpec,
        pricing: PricingResult,
        curves: CurveSet,
    ) -> str:
        """Generate a plain-English analysis of the bond pricing."""
        prompt = f"""You are a fixed income analyst. Explain this bond pricing result
in clear, non-technical language that a portfolio manager would find useful.

Bond: {bond.coupon}% coupon, matures {bond.maturity}, {bond.frequency}x/year payments
Clean price: {pricing.clean_price}
YTM: {pricing.ytm}%
Z-spread: {pricing.z_spread} bps
Duration: {pricing.macaulay_duration} years (modified: {pricing.modified_duration})
Convexity: {pricing.convexity}
DV01: ${pricing.dv01}

Current yield curve shape: short end ({list(curves.par.items())[:2]}), long end ({list(curves.par.items())[-2:]})

Cover:
1. Is this bond trading at a premium, discount, or par, and why?
2. What does the duration tell us about interest rate risk?
3. What does the current curve shape suggest about the rate environment?
4. One actionable insight.

Keep it under 200 words. No jargon without explanation."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
```

- [ ] **Step 13: Implement db_models.py and db.py**

```python
# projects/bond-pricing-engine/src/engine/db_models.py

"""SQLAlchemy models for bond pricing engine database."""

import json
from datetime import date, datetime, UTC
from sqlalchemy import String, Float, Integer, Date, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ParYieldRecord(Base):
    __tablename__ = "par_yields"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    yields_json: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20), default="FRED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class SpotCurveRecord(Base):
    __tablename__ = "spot_curves"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    rates_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class FittedCurveRecord(Base):
    __tablename__ = "fitted_curves"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curve_date: Mapped[date] = mapped_column(Date, index=True)
    model: Mapped[str] = mapped_column(String(30))
    params_json: Mapped[str] = mapped_column(Text)
    fitted_rates_json: Mapped[str] = mapped_column(Text)
    rmse: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class BondRecord(Base):
    __tablename__ = "bonds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isin: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    coupon: Mapped[float] = mapped_column(Float)
    maturity: Mapped[date] = mapped_column(Date)
    face_value: Mapped[float] = mapped_column(Float, default=1000.0)
    issue_date: Mapped[date] = mapped_column(Date)
    frequency: Mapped[int] = mapped_column(Integer, default=2)
    bond_type: Mapped[str] = mapped_column(String(20), default="treasury")
    is_callable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class PricingResultRecord(Base):
    __tablename__ = "pricing_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bond_isin: Mapped[str] = mapped_column(String(12), index=True)
    curve_date: Mapped[date] = mapped_column(Date)
    clean_price: Mapped[float] = mapped_column(Float)
    ytm: Mapped[float] = mapped_column(Float)
    z_spread_bps: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration: Mapped[float] = mapped_column(Float)
    modified_duration: Mapped[float] = mapped_column(Float)
    convexity: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
```

```python
# projects/bond-pricing-engine/src/engine/db.py

"""Database operations for bond pricing engine."""

import json
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from engine.db_models import ParYieldRecord, SpotCurveRecord, BondRecord


async def save_par_yields(session: AsyncSession, curve_date: date, yields: dict[str, float]):
    existing = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date))
    record = existing.scalar_one_or_none()
    if record:
        record.yields_json = json.dumps(yields)
    else:
        record = ParYieldRecord(curve_date=curve_date, yields_json=json.dumps(yields))
        session.add(record)
    await session.commit()
    return record


async def get_par_yields(session: AsyncSession, curve_date: date) -> dict[str, float] | None:
    result = await session.execute(
        select(ParYieldRecord).where(ParYieldRecord.curve_date == curve_date))
    record = result.scalar_one_or_none()
    return json.loads(record.yields_json) if record else None


async def get_latest_par_yields(session: AsyncSession) -> tuple[date, dict[str, float]] | None:
    result = await session.execute(
        select(ParYieldRecord).order_by(ParYieldRecord.curve_date.desc()).limit(1))
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return record.curve_date, json.loads(record.yields_json)
```

- [ ] **Step 14: Implement main.py (FastAPI app)**

```python
# projects/bond-pricing-engine/src/engine/main.py

import os
from contextlib import asynccontextmanager
from datetime import date, datetime, UTC

import structlog
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.models import (
    PriceRequest, AnalyzeRequest, BondSpec, CurveSet, BondAnalysis,
)
from engine.curves import bootstrap_spot_curve, calculate_forward_rates, fit_curves
from engine.pricer import price_bond, calculate_z_spread
from engine.narrative import BondNarrator
from engine.db import get_par_yields, get_latest_par_yields, save_par_yields
from engine.db_models import Base

structlog.configure(processors=[
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.JSONRenderer(),
])
log = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///engine.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(DATABASE_URL)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("app_started", database=DATABASE_URL)
    yield
    await engine.dispose()


async def get_session(request: Request) -> AsyncSession:
    factory = request.app.state.session_factory
    async with factory() as session:
        yield session


def create_app() -> FastAPI:
    application = FastAPI(title="Bond Pricing Engine", version="0.1.0", lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["https://mish-codes.github.io", "https://finbytes.streamlit.app", "http://localhost:8501"],
        allow_methods=["*"], allow_headers=["*"],
    )

    @application.get("/health")
    def health():
        return {"status": "ok"}

    @application.get("/curves/{curve_date}")
    async def get_curves(curve_date: date, session: AsyncSession = Depends(get_session)):
        par = await get_par_yields(session, curve_date)
        if par is None:
            raise HTTPException(404, f"No curve data for {curve_date}")
        spot = bootstrap_spot_curve(par)
        forward = calculate_forward_rates(spot)
        ns, nss = fit_curves(par, curve_date)
        return CurveSet(curve_date=curve_date, par=par, spot=spot, forward=forward,
                        fitted_ns=ns, fitted_nss=nss)

    @application.get("/curves/latest")
    async def get_latest_curves(session: AsyncSession = Depends(get_session)):
        result = await get_latest_par_yields(session)
        if result is None:
            raise HTTPException(404, "No curve data available")
        curve_date, par = result
        spot = bootstrap_spot_curve(par)
        forward = calculate_forward_rates(spot)
        ns, nss = fit_curves(par, curve_date)
        return CurveSet(curve_date=curve_date, par=par, spot=spot, forward=forward,
                        fitted_ns=ns, fitted_nss=nss)

    @application.post("/price")
    async def price(req: PriceRequest, session: AsyncSession = Depends(get_session)):
        if req.curve_date:
            par = await get_par_yields(session, req.curve_date)
        else:
            result = await get_latest_par_yields(session)
            par = result[1] if result else None
        if par is None:
            raise HTTPException(404, "No curve data available")

        spot = bootstrap_spot_curve(par)
        bond = BondSpec(coupon=req.coupon, maturity=req.maturity,
                        face_value=req.face_value, frequency=req.frequency)
        return price_bond(bond, spot, as_of=req.curve_date or date.today())

    @application.post("/analyze")
    async def analyze(req: AnalyzeRequest, session: AsyncSession = Depends(get_session)):
        if req.curve_date:
            par = await get_par_yields(session, req.curve_date)
            cd = req.curve_date
        else:
            result = await get_latest_par_yields(session)
            if result is None:
                raise HTTPException(404, "No curve data available")
            cd, par = result
        if par is None:
            raise HTTPException(404, "No curve data available")

        spot = bootstrap_spot_curve(par)
        forward = calculate_forward_rates(spot)
        ns, nss = fit_curves(par, cd)
        curves = CurveSet(curve_date=cd, par=par, spot=spot, forward=forward,
                          fitted_ns=ns, fitted_nss=nss)

        bond = BondSpec(coupon=req.coupon, maturity=req.maturity,
                        face_value=req.face_value, frequency=req.frequency)
        pricing = price_bond(bond, spot, as_of=cd)

        narrator = BondNarrator()
        narrative = narrator.generate(bond, pricing, curves)

        return BondAnalysis(bond=bond, pricing=pricing, curve_date=cd,
                            narrative=narrative, generated_at=datetime.now(UTC))

    return application


app = create_app()
```

- [ ] **Step 15: Write API tests**

```python
# projects/bond-pricing-engine/tests/test_api.py

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from engine.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestPricing:
    def test_price_returns_422_for_past_maturity(self, client):
        resp = client.post("/price", json={
            "coupon": 5.0,
            "maturity": "2020-01-01",
            "face_value": 100.0,
        })
        assert resp.status_code == 422
```

- [ ] **Step 16: Run all tests**

```bash
pytest -v
```

Expected: all tests pass

- [ ] **Step 17: Create Dockerfile**

```dockerfile
# projects/bond-pricing-engine/Dockerfile

FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM base AS production
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
EXPOSE 8000
CMD ["uvicorn", "engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 18: Create Terraform for full deployment**

This extends the Terraform from exercise 14 with RDS, full Lambda setup, and all IAM roles. Use the same pattern from `exercises/14-terraform-curve-fitting/terraform/` but add RDS module.

- [ ] **Step 19: Commit Capstone A**

```bash
cd C:\codebase\quant_lab
git add projects/bond-pricing-engine/
git commit -m "feat(bond-pricing-engine): capstone A — yield curves, bond pricing, AI narratives on AWS"
```

- [ ] **Step 20: Extend Streamlit dashboard**

Add a "Bond Pricing" page to the existing Streamlit dashboard:
- Curve visualization (par, spot, forward, fitted — matplotlib charts)
- Bond pricer form (coupon, maturity, face value → pricing results)
- Nelson-Siegel parameter display
- Historical curve comparison

- [ ] **Step 21: Understand it — teaching conversation**

Capstone-level topics:
- How all pieces fit together: S3 → RDS → Lambda → API Gateway → Dashboard
- Bond pricing in practice: clean vs dirty price, accrued interest, settlement conventions
- Duration as a risk measure: "my portfolio has 7 years duration = 7% loss if rates rise 1%"
- Z-spread as relative value: bonds with higher Z-spread are "cheap" to the curve (or riskier)

- [ ] **Step 22: Write capstone blog post**

Create `finbytes_git/docs/_posts/2026-XX-XX-bond-pricing-engine-capstone.html`

- [ ] **Step 23: Commit blog post**

```bash
cd C:\codebase\finbytes_git
git checkout working
git add docs/_posts/2026-XX-XX-bond-pricing-engine-capstone.html
git commit -m "feat: Bond Pricing Engine capstone blog post"
git checkout master && git merge working --no-edit && git push origin master working
git checkout working
```

---

## Phase 2: Exercises 15-20 (Advanced AWS + Credit Risk)

---

### Task 8: SQS/SNS + Credit Spreads & CDS Curves (Exercise 15)

**Concept:** Use message queues for async processing and notifications for alerting. Calculate credit spreads and bootstrap default probabilities from CDS curves.

**Files:**
- Create: `exercises/15-sqs-sns-credit-spreads/pyproject.toml`
- Create: `exercises/15-sqs-sns-credit-spreads/src/credit_spreads.py`
- Create: `exercises/15-sqs-sns-credit-spreads/tests/test_credit_spreads.py`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-sqs-sns-credit-spreads.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "sqs-sns-credit-spreads-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.35.0",
    "numpy>=1.26.0",
    "fredapi>=0.5.2",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "moto[sqs,sns]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["credit_spreads"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/15-sqs-sns-credit-spreads/tests/test_credit_spreads.py

import json
import pytest
import numpy as np
import boto3
from moto import mock_aws
from credit_spreads import (
    calculate_credit_spread,
    fetch_credit_indices,
    bootstrap_default_probabilities,
    check_spread_threshold,
    send_to_queue,
    publish_alert,
)


class TestCreditSpread:
    def test_spread_is_corporate_minus_treasury(self):
        spread = calculate_credit_spread(
            corporate_yield=5.5,
            treasury_yield=4.0,
        )
        assert spread == pytest.approx(1.5, abs=0.01)

    def test_negative_spread_possible(self):
        """Rare but possible (e.g., swap spreads went negative in 2015)."""
        spread = calculate_credit_spread(
            corporate_yield=3.8,
            treasury_yield=4.0,
        )
        assert spread == pytest.approx(-0.2, abs=0.01)


class TestDefaultProbabilities:
    def test_basic_default_probability(self):
        """CDS spread of 100bps with 40% recovery → ~1.67% annual default prob."""
        cds_spreads = {"1Y": 100}  # 100 bps
        recovery_rate = 0.40

        probs = bootstrap_default_probabilities(cds_spreads, recovery_rate)

        assert "1Y" in probs
        assert 0.01 < probs["1Y"] < 0.03  # rough range

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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\15-sqs-sns-credit-spreads
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement credit_spreads.py**

```python
# exercises/15-sqs-sns-credit-spreads/src/credit_spreads.py

"""
Credit spread calculation, CDS default probability bootstrapping,
and AWS messaging (SQS/SNS) for credit risk alerting.

Credit spread:
  spread = corporate bond yield − treasury yield (same maturity)
  Measured in basis points (bps). 1% = 100 bps.
  Represents the market's price for credit risk.

CDS and default probabilities:
  CDS spread = annual premium paid for default protection.
  Under the hazard rate model with constant hazard λ:
    CDS_spread ≈ λ × (1 − recovery_rate)
    → λ ≈ CDS_spread / (1 − recovery_rate)
    → P(default by T) = 1 − exp(−λT)

  This is simplified — full bootstrapping uses exact CDS cash flows,
  but this approximation is standard for quick analysis.
"""

import json
import numpy as np
import boto3

CDS_TENOR_YEARS = {"1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0}


def calculate_credit_spread(corporate_yield: float, treasury_yield: float) -> float:
    """Calculate credit spread in percentage points.

    Args:
        corporate_yield: Corporate bond yield in percent.
        treasury_yield: Treasury yield at same maturity in percent.

    Returns:
        Credit spread in percentage points.
    """
    return round(corporate_yield - treasury_yield, 4)


def fetch_credit_indices(api_key: str) -> dict[str, float]:
    """Fetch ICE BofA credit spread indices from FRED.

    Returns dict mapping rating to spread in bps.
    """
    from fredapi import Fred
    from datetime import date, timedelta

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

    spreads = {}
    for series_id, rating in series.items():
        data = fred.get_series(series_id, observation_start=start, observation_end=today)
        data = data.dropna()
        if len(data) > 0:
            spreads[rating] = round(float(data.iloc[-1]) * 100, 2)  # convert to bps

    return spreads


def bootstrap_default_probabilities(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Bootstrap cumulative default probabilities from CDS spreads.

    Uses the hazard rate approximation:
      λ ≈ CDS_spread_bps / (10000 × (1 − R))
      P(default by T) = 1 − exp(−λ × T)

    Args:
        cds_spreads: Dict mapping tenor label to CDS spread in bps.
        recovery_rate: Expected recovery rate (0 to 1).

    Returns:
        Dict mapping tenor label to cumulative default probability.
    """
    lgd = 1.0 - recovery_rate
    probs = {}

    for tenor, spread_bps in cds_spreads.items():
        years = CDS_TENOR_YEARS.get(tenor, float(tenor.replace("Y", "")))
        hazard_rate = (spread_bps / 10000.0) / lgd
        cum_default_prob = 1.0 - np.exp(-hazard_rate * years)
        probs[tenor] = round(float(cum_default_prob), 6)

    return probs


def check_spread_threshold(spread_bps: float, threshold: float) -> bool:
    """Check if a spread exceeds the alert threshold."""
    return spread_bps > threshold


def send_to_queue(
    queue_url: str, message: dict, sqs_client=None
) -> dict:
    """Send a message to an SQS queue."""
    sqs = sqs_client or boto3.client("sqs")
    return sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
    )


def publish_alert(
    topic_arn: str, message: str, sns_client=None
) -> dict:
    """Publish an alert to an SNS topic."""
    sns = sns_client or boto3.client("sns")
    return sns.publish(
        TopicArn=topic_arn,
        Subject="Credit Spread Alert",
        Message=message,
    )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 9 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/15-sqs-sns-credit-spreads/
git commit -m "feat(exercises): 15 SQS/SNS + credit spreads & CDS default probabilities"
```

- [ ] **Step 7: Understand it — teaching conversation**

Topics to cover:
- **SQS:** Decouples producers from consumers. Standard queue (at-least-once, best-effort ordering) vs FIFO (exactly-once, ordered). Dead letter queue catches failures.
- **SNS:** Pub/sub. One message → many subscribers (email, SQS, Lambda, HTTP). Fan-out pattern: SNS → multiple SQS queues for different consumers.
- **Credit spreads:** The market's real-time pricing of credit risk. When spreads widen, the market is demanding more compensation for default risk. Tracks fear/greed cycle.
- **CDS mechanics:** Buyer pays quarterly premium (spread). Seller pays par − recovery on default. CDS spread widens when market sees more default risk.
- **Hazard rate model:** λ = instantaneous default intensity. Under constant λ: survival probability = exp(−λT). Higher spread → higher λ → higher default probability.
- **Recovery rate:** What bondholders recover after default. Senior unsecured: ~40% (industry convention). Subordinated: ~20%. Secured: ~60%.

- [ ] **Step 8-10: Blog post + commit** (same pattern as previous exercises)

---

### Task 9: WebSockets + Real-Time Spread Monitoring (Exercise 16)

**Concept:** Push real-time spread updates to connected clients via WebSockets. Learn API Gateway WebSocket APIs and Lambda connection management.

**Files:**
- Create: `exercises/16-websockets-realtime/pyproject.toml`
- Create: `exercises/16-websockets-realtime/src/ws_handler.py`
- Create: `exercises/16-websockets-realtime/tests/test_ws_handler.py`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-websockets-realtime-spreads.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "websockets-realtime-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["boto3>=1.35.0", "websockets>=13.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0", "moto[dynamodb,apigateway]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["ws_handler"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/16-websockets-realtime/tests/test_ws_handler.py

import json
import pytest
import boto3
from moto import mock_aws
from ws_handler import (
    handle_connect,
    handle_disconnect,
    handle_message,
    get_connected_clients,
    broadcast_spread_update,
)

TABLE_NAME = "ws-connections"


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


class TestConnectionManagement:
    def test_connect_stores_connection(self, dynamodb_table):
        handle_connect("conn-123", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert "conn-123" in clients

    def test_disconnect_removes_connection(self, dynamodb_table):
        handle_connect("conn-456", table=dynamodb_table)
        handle_disconnect("conn-456", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert "conn-456" not in clients

    def test_multiple_connections(self, dynamodb_table):
        handle_connect("conn-1", table=dynamodb_table)
        handle_connect("conn-2", table=dynamodb_table)
        handle_connect("conn-3", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert len(clients) == 3


class TestMessageHandling:
    def test_subscribe_to_rating(self, dynamodb_table):
        handle_connect("conn-789", table=dynamodb_table)
        result = handle_message(
            "conn-789",
            {"action": "subscribe", "rating": "BBB"},
            table=dynamodb_table,
        )
        assert result["subscribed"] == "BBB"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\16-websockets-realtime
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement ws_handler.py**

```python
# exercises/16-websockets-realtime/src/ws_handler.py

"""
WebSocket connection management for real-time spread monitoring.

Uses DynamoDB to track connected clients (serverless-friendly).
API Gateway WebSocket API handles the actual WS protocol.
Lambda functions handle $connect, $disconnect, and $default routes.
"""

import json
import boto3
from datetime import datetime, UTC


def handle_connect(connection_id: str, table=None) -> dict:
    """Store a new WebSocket connection."""
    tbl = table or _get_table()
    tbl.put_item(Item={
        "connectionId": connection_id,
        "connectedAt": datetime.now(UTC).isoformat(),
        "subscriptions": [],
    })
    return {"statusCode": 200}


def handle_disconnect(connection_id: str, table=None) -> dict:
    """Remove a WebSocket connection."""
    tbl = table or _get_table()
    tbl.delete_item(Key={"connectionId": connection_id})
    return {"statusCode": 200}


def handle_message(connection_id: str, message: dict, table=None) -> dict:
    """Handle incoming WebSocket message."""
    tbl = table or _get_table()
    action = message.get("action")

    if action == "subscribe":
        rating = message.get("rating", "")
        tbl.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="SET subscriptions = list_append(if_not_exists(subscriptions, :empty), :rating)",
            ExpressionAttributeValues={":rating": [rating], ":empty": []},
        )
        return {"subscribed": rating}

    return {"error": f"Unknown action: {action}"}


def get_connected_clients(table=None) -> list[str]:
    """Get all connected client IDs."""
    tbl = table or _get_table()
    response = tbl.scan(ProjectionExpression="connectionId")
    return [item["connectionId"] for item in response.get("Items", [])]


def broadcast_spread_update(
    spread_data: dict,
    api_url: str,
    table=None,
) -> int:
    """Broadcast spread update to all connected clients.

    Args:
        spread_data: Dict with spread info to send.
        api_url: API Gateway management URL.
        table: DynamoDB table.

    Returns:
        Number of clients notified.
    """
    clients = get_connected_clients(table)
    apigw = boto3.client("apigatewaymanagementapi", endpoint_url=api_url)
    sent = 0

    for conn_id in clients:
        try:
            apigw.post_to_connection(
                ConnectionId=conn_id,
                Data=json.dumps(spread_data).encode(),
            )
            sent += 1
        except Exception:
            # Connection stale — remove it
            handle_disconnect(conn_id, table)

    return sent


def _get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table("ws-connections")


# Lambda entry points for API Gateway WebSocket routes

def lambda_connect(event, context):
    connection_id = event["requestContext"]["connectionId"]
    return handle_connect(connection_id)


def lambda_disconnect(event, context):
    connection_id = event["requestContext"]["connectionId"]
    return handle_disconnect(connection_id)


def lambda_default(event, context):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body", "{}"))
    result = handle_message(connection_id, body)
    return {"statusCode": 200, "body": json.dumps(result)}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/16-websockets-realtime/
git commit -m "feat(exercises): 16 WebSockets + real-time spread monitoring"
```

- [ ] **Step 7-9: Teaching conversation + blog post + commit** (same pattern)

---

### Task 10: ElastiCache/Redis + Caching Bond Prices & Curves (Exercise 17)

**Concept:** Cache expensive calculations (curve fitting, bond pricing) in Redis. Learn cache-aside pattern, TTL strategies, and graceful fallback.

**Files:**
- Create: `exercises/17-elasticache-redis/pyproject.toml`
- Create: `exercises/17-elasticache-redis/src/cache.py`
- Create: `exercises/17-elasticache-redis/tests/test_cache.py`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-elasticache-bond-caching.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "elasticache-redis-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["redis>=5.0.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "fakeredis>=2.21.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["cache"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/17-elasticache-redis/tests/test_cache.py

import json
import pytest
import fakeredis
from cache import CurveCache


@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def cache(redis_client):
    return CurveCache(redis_client)


class TestCurveCache:
    def test_set_and_get(self, cache):
        data = {"1Y": 4.0, "2Y": 4.5, "10Y": 5.0}
        cache.set_curve("par", "2026-04-04", data)
        result = cache.get_curve("par", "2026-04-04")
        assert result == data

    def test_miss_returns_none(self, cache):
        result = cache.get_curve("par", "2099-01-01")
        assert result is None

    def test_ttl_applied(self, redis_client, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0}, ttl=300)
        ttl = redis_client.ttl("curve:par:2026-04-04")
        assert 0 < ttl <= 300

    def test_invalidate(self, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0})
        cache.invalidate_curve("par", "2026-04-04")
        assert cache.get_curve("par", "2026-04-04") is None

    def test_invalidate_all_for_date(self, cache):
        cache.set_curve("par", "2026-04-04", {"1Y": 4.0})
        cache.set_curve("spot", "2026-04-04", {"1Y": 4.0})
        cache.set_curve("fitted", "2026-04-04", {"1Y": 4.0})
        cache.invalidate_date("2026-04-04")
        assert cache.get_curve("par", "2026-04-04") is None
        assert cache.get_curve("spot", "2026-04-04") is None

    def test_set_pricing_result(self, cache):
        result = {"clean_price": 98.5, "ytm": 5.2, "duration": 4.5}
        cache.set_pricing("bond-123", "2026-04-04", result)
        assert cache.get_pricing("bond-123", "2026-04-04") == result

    def test_graceful_fallback_on_redis_error(self):
        """If Redis is unavailable, cache operations should not raise."""
        bad_client = fakeredis.FakeRedis(connected=False, decode_responses=True)
        cache = CurveCache(bad_client)
        # Should not raise, just return None
        assert cache.get_curve("par", "2026-04-04") is None
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\17-elasticache-redis
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement cache.py**

```python
# exercises/17-elasticache-redis/src/cache.py

"""
Redis cache layer for bond pricing engine.

Cache-aside pattern:
  1. Check cache first
  2. If miss, compute result
  3. Store in cache with TTL
  4. Return result

TTL strategy:
  - Par yields: 24h (updates daily)
  - Spot/forward/fitted curves: 24h (derived from daily data)
  - Bond pricing: 5min (may depend on market data)
  - Monte Carlo VaR: 1h (expensive, relatively stable)

Graceful degradation:
  If Redis is unavailable, all cache operations return None/succeed silently.
  The app continues to work, just slower.
"""

import json
import redis


class CurveCache:
    """Cache layer for yield curves and pricing results."""

    DEFAULT_TTLS = {
        "par": 86400,      # 24 hours
        "spot": 86400,
        "forward": 86400,
        "fitted": 86400,
        "pricing": 300,    # 5 minutes
        "var": 3600,       # 1 hour
    }

    def __init__(self, redis_client: redis.Redis):
        self._r = redis_client

    def _safe(self, fn, default=None):
        """Execute Redis operation with graceful error handling."""
        try:
            return fn()
        except (redis.ConnectionError, redis.TimeoutError, Exception):
            return default

    def set_curve(self, curve_type: str, date_str: str, data: dict, ttl: int | None = None):
        """Cache a curve."""
        key = f"curve:{curve_type}:{date_str}"
        ttl = ttl or self.DEFAULT_TTLS.get(curve_type, 3600)
        self._safe(lambda: self._r.setex(key, ttl, json.dumps(data)))

    def get_curve(self, curve_type: str, date_str: str) -> dict | None:
        """Get a cached curve. Returns None on miss or error."""
        key = f"curve:{curve_type}:{date_str}"
        result = self._safe(lambda: self._r.get(key))
        return json.loads(result) if result else None

    def invalidate_curve(self, curve_type: str, date_str: str):
        """Remove a specific curve from cache."""
        key = f"curve:{curve_type}:{date_str}"
        self._safe(lambda: self._r.delete(key))

    def invalidate_date(self, date_str: str):
        """Remove all curves for a date."""
        for curve_type in ["par", "spot", "forward", "fitted"]:
            self.invalidate_curve(curve_type, date_str)

    def set_pricing(self, bond_id: str, date_str: str, result: dict, ttl: int | None = None):
        """Cache a pricing result."""
        key = f"pricing:{bond_id}:{date_str}"
        ttl = ttl or self.DEFAULT_TTLS["pricing"]
        self._safe(lambda: self._r.setex(key, ttl, json.dumps(result)))

    def get_pricing(self, bond_id: str, date_str: str) -> dict | None:
        """Get a cached pricing result."""
        key = f"pricing:{bond_id}:{date_str}"
        result = self._safe(lambda: self._r.get(key))
        return json.loads(result) if result else None
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/17-elasticache-redis/
git commit -m "feat(exercises): 17 ElastiCache/Redis caching for bond prices & curves"
```

- [ ] **Step 7-9: Teaching conversation + blog post + commit**

---

### Task 11: Terraform Advanced + Default Probabilities (Exercise 18)

**Concept:** Multi-service Terraform with modules, environments, and remote state. Calculate term structure of default probabilities, survival curves, and expected loss.

**Files:**
- Create: `exercises/18-terraform-advanced/pyproject.toml`
- Create: `exercises/18-terraform-advanced/src/default_probabilities.py`
- Create: `exercises/18-terraform-advanced/tests/test_default_probabilities.py`
- Create: `exercises/18-terraform-advanced/terraform/`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-terraform-advanced-default-probs.html`

- [ ] **Step 1-5: pyproject.toml + tests + implementation** (same TDD pattern)

The `default_probabilities.py` module expands on exercise 15's basic hazard rate model:

```python
# exercises/18-terraform-advanced/src/default_probabilities.py

"""
Full term structure of default probabilities from CDS curves.

Builds on exercise 15 with:
- Piecewise constant hazard rates (different λ for each tenor interval)
- Survival curves: S(T) = exp(−∫���ᵀ λ(t)dt)
- Expected loss: EL = PD × LGD × EAD
- Recovery rate sensitivity analysis
"""

import numpy as np

CDS_TENOR_YEARS = {"1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0}
TENOR_ORDER = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y"]


def bootstrap_hazard_rates(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Bootstrap piecewise constant hazard rates from CDS term structure.

    Args:
        cds_spreads: Dict mapping tenor to CDS spread in bps.
        recovery_rate: Recovery rate (0 to 1).

    Returns:
        Dict mapping tenor intervals to hazard rates.
    """
    lgd = 1.0 - recovery_rate
    ordered = [(t, cds_spreads[t]) for t in TENOR_ORDER if t in cds_spreads]

    hazard_rates = {}
    cum_hazard = 0.0
    prev_years = 0.0

    for i, (tenor, spread_bps) in enumerate(ordered):
        years = CDS_TENOR_YEARS[tenor]
        dt = years - prev_years

        # CDS_spread(T) ≈ λ_avg × LGD × 10000
        # λ_avg(0,T) = spread / (LGD × 10000)
        lambda_avg = (spread_bps / 10000.0) / lgd
        cum_hazard_target = lambda_avg * years

        # Piecewise: λ_i = (cum_hazard_target − cum_hazard_prev) / dt
        lambda_i = (cum_hazard_target - cum_hazard) / dt if dt > 0 else lambda_avg
        lambda_i = max(lambda_i, 0.0)

        interval = f"{int(prev_years)}Y-{tenor}" if prev_years > 0 else f"0-{tenor}"
        hazard_rates[interval] = round(lambda_i, 6)

        cum_hazard = cum_hazard_target
        prev_years = years

    return hazard_rates


def survival_curve(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
    time_points: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate survival probability curve.

    Args:
        cds_spreads: Dict mapping tenor to CDS spread in bps.
        recovery_rate: Recovery rate.
        time_points: Array of times in years (defaults to 0-10 annual).

    Returns:
        Tuple of (times, survival_probabilities).
    """
    if time_points is None:
        time_points = np.arange(0, 11, 0.5)

    hazards = bootstrap_hazard_rates(cds_spreads, recovery_rate)
    ordered = [(t, cds_spreads[t]) for t in TENOR_ORDER if t in cds_spreads]
    lgd = 1.0 - recovery_rate

    survival = np.ones_like(time_points)
    for i, t in enumerate(time_points):
        if t == 0:
            continue
        lambda_avg = 0.0
        for tenor, spread_bps in ordered:
            years = CDS_TENOR_YEARS[tenor]
            if years >= t:
                lambda_avg = (spread_bps / 10000.0) / lgd
                break
        else:
            # Extrapolate from last tenor
            lambda_avg = (ordered[-1][1] / 10000.0) / lgd

        survival[i] = np.exp(-lambda_avg * t)

    return time_points, survival


def default_probability_term_structure(
    cds_spreads: dict[str, float],
    recovery_rate: float = 0.40,
) -> dict[str, float]:
    """Calculate cumulative default probabilities at each CDS tenor.

    Returns dict mapping tenor to P(default by T).
    """
    lgd = 1.0 - recovery_rate
    probs = {}
    for tenor in TENOR_ORDER:
        if tenor not in cds_spreads:
            continue
        years = CDS_TENOR_YEARS[tenor]
        lambda_avg = (cds_spreads[tenor] / 10000.0) / lgd
        probs[tenor] = round(1.0 - np.exp(-lambda_avg * years), 6)
    return probs


def expected_loss(
    default_prob: float,
    lgd: float,
    exposure: float,
) -> float:
    """Calculate expected loss.

    EL = PD × LGD × EAD

    Args:
        default_prob: Probability of default (0 to 1).
        lgd: Loss given default (0 to 1).
        exposure: Exposure at default (dollar amount).

    Returns:
        Expected loss in dollars.
    """
    return round(default_prob * lgd * exposure, 2)
```

Tests and Terraform config follow the same patterns. The Terraform for this exercise defines modules for each AWS service and uses workspaces for dev/prod.

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/18-terraform-advanced/
git commit -m "feat(exercises): 18 Terraform advanced + default probability term structure"
```

- [ ] **Step 7-9: Teaching conversation + blog post + commit**

---

### Task 12: CloudWatch + OAS & Z-Spread (Exercise 19)

**Concept:** Custom CloudWatch metrics and dashboards for API monitoring. Implement OAS calculation using a binomial interest rate tree for callable bonds.

**Files:**
- Create: `exercises/19-cloudwatch-oas/pyproject.toml`
- Create: `exercises/19-cloudwatch-oas/src/oas.py`
- Create: `exercises/19-cloudwatch-oas/tests/test_oas.py`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-cloudwatch-oas-zspreads.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "cloudwatch-oas-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26.0", "scipy>=1.14.0", "boto3>=1.35.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "moto[cloudwatch]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["oas"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/19-cloudwatch-oas/tests/test_oas.py

import numpy as np
import pytest
from oas import (
    build_rate_tree,
    price_bond_on_tree,
    price_callable_bond_on_tree,
    calculate_z_spread,
    calculate_oas,
)


class TestBuildRateTree:
    def test_root_node(self):
        """Root node should be the short rate."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=3, dt=1.0)
        assert tree[0][0] == pytest.approx(5.0, abs=0.01)

    def test_tree_size(self):
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=4, dt=1.0)
        assert len(tree) == 5  # steps + 1 levels
        assert len(tree[4]) == 5  # last level has steps+1 nodes

    def test_up_down_symmetry(self):
        """Tree should be recombining: up-down = down-up."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.15, steps=3, dt=1.0)
        # After 2 steps, middle node should exist
        assert len(tree[2]) == 3


class TestPriceBondOnTree:
    def test_zero_coupon_discounting(self):
        """A zero-coupon bond should be discounted at tree rates."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.0, steps=3, dt=1.0)
        price = price_bond_on_tree(tree, coupon=0.0, face=100.0, dt=1.0)
        # Flat 5% for 3 years: 100 / 1.05^3 ≈ 86.38
        assert price == pytest.approx(86.38, abs=0.5)

    def test_par_bond_near_par(self):
        """A bond with coupon ≈ yield should price near par."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.0, steps=5, dt=1.0)
        price = price_bond_on_tree(tree, coupon=5.0, face=100.0, dt=1.0)
        assert abs(price - 100.0) < 2.0


class TestCallableBond:
    def test_callable_le_noncallable(self):
        """Callable bond price ≤ non-callable (issuer has the option)."""
        tree = build_rate_tree(short_rate=5.0, volatility=0.20, steps=5, dt=1.0)
        nc_price = price_bond_on_tree(tree, coupon=6.0, face=100.0, dt=1.0)
        c_price = price_callable_bond_on_tree(
            tree, coupon=6.0, face=100.0, call_price=100.0, dt=1.0
        )
        assert c_price <= nc_price + 0.01


class TestOAS:
    def test_oas_less_than_z_spread_for_callable(self):
        """OAS < Z-spread for callable bonds (option value removed)."""
        spot_curve = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        market_price = 98.0
        z = calculate_z_spread(spot_curve, coupon=5.0, maturity_years=5, face=100.0,
                                market_price=market_price)
        oas = calculate_oas(spot_curve, coupon=5.0, maturity_years=5, face=100.0,
                            call_price=100.0, market_price=market_price, volatility=0.20)
        assert oas < z

    def test_oas_equals_z_spread_for_noncallable(self):
        """Without call option, OAS ≈ Z-spread."""
        spot_curve = {"1Y": 5.0, "2Y": 5.0, "3Y": 5.0, "5Y": 5.0}
        market_price = 98.0
        z = calculate_z_spread(spot_curve, coupon=5.0, maturity_years=5, face=100.0,
                                market_price=market_price)
        oas = calculate_oas(spot_curve, coupon=5.0, maturity_years=5, face=100.0,
                            call_price=None, market_price=market_price, volatility=0.20)
        assert abs(oas - z) < 5  # within 5 bps
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\19-cloudwatch-oas
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement oas.py**

```python
# exercises/19-cloudwatch-oas/src/oas.py

"""
OAS (Option-Adjusted Spread) and Z-spread calculation.

Binomial interest rate tree:
  At each node, rate can go up or down:
    r_up = r × exp(σ√Δt)
    r_down = r × exp(−σ√Δt)
  Probability of up/down = 0.5 (risk-neutral).

Bond pricing on tree (backward induction):
  At maturity: value = face + coupon
  At earlier nodes: value = (0.5 × V_up + 0.5 × V_down) / (1 + r_node × Δt) + coupon

Callable bond:
  At each node, issuer calls if call_price < continuation value.
  value = min(continuation_value, call_price)

Z-spread:
  Constant spread z over spot curve such that:
  P = Σ CF_i / (1 + s_i + z)^t_i = market_price
  Solved by bisection.

OAS:
  Spread z added to EVERY rate on the tree such that model price = market price.
  For non-callable bonds, OAS ≈ Z-spread.
  For callable bonds, OAS < Z-spread (the option has value to the issuer).
"""

import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline

MATURITY_YEARS = {
    "1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0,
    "7Y": 7.0, "10Y": 10.0, "20Y": 20.0, "30Y": 30.0,
}


def build_rate_tree(
    short_rate: float, volatility: float, steps: int, dt: float = 1.0
) -> list[list[float]]:
    """Build a recombining binomial interest rate tree.

    Args:
        short_rate: Initial short rate in percent.
        volatility: Rate volatility (annualized, as decimal e.g. 0.15).
        steps: Number of time steps.
        dt: Time step size in years.

    Returns:
        List of lists — tree[i][j] = rate at step i, node j (percent).
    """
    tree = []
    u = np.exp(volatility * np.sqrt(dt))
    d = 1.0 / u

    for i in range(steps + 1):
        level = []
        for j in range(i + 1):
            rate = short_rate * (u ** (i - 2 * j))
            level.append(round(rate, 6))
        tree.append(level)

    return tree


def price_bond_on_tree(
    tree: list[list[float]],
    coupon: float,
    face: float,
    dt: float = 1.0,
) -> float:
    """Price a non-callable bond using backward induction on rate tree.

    Args:
        tree: Interest rate tree (percent).
        coupon: Annual coupon rate in percent.
        face: Face value.
        dt: Time step in years.

    Returns:
        Bond price.
    """
    steps = len(tree) - 1
    coupon_payment = coupon / 100.0 * face * dt

    # Terminal values
    values = [face + coupon_payment for _ in tree[steps]]

    # Backward induction
    for i in range(steps - 1, -1, -1):
        new_values = []
        for j in range(len(tree[i])):
            r = tree[i][j] / 100.0
            discount = 1.0 / (1.0 + r * dt)
            expected = 0.5 * values[j] + 0.5 * values[j + 1]
            pv = expected * discount + coupon_payment
            new_values.append(pv)
        values = new_values

    return round(values[0], 4)


def price_callable_bond_on_tree(
    tree: list[list[float]],
    coupon: float,
    face: float,
    call_price: float,
    dt: float = 1.0,
    oas_bps: float = 0.0,
) -> float:
    """Price a callable bond using backward induction.

    At each node, issuer calls if call_price < continuation value.
    """
    steps = len(tree) - 1
    coupon_payment = coupon / 100.0 * face * dt
    oas_dec = oas_bps / 10000.0

    values = [face + coupon_payment for _ in tree[steps]]

    for i in range(steps - 1, -1, -1):
        new_values = []
        for j in range(len(tree[i])):
            r = tree[i][j] / 100.0 + oas_dec
            discount = 1.0 / (1.0 + r * dt)
            expected = 0.5 * values[j] + 0.5 * values[j + 1]
            continuation = expected * discount + coupon_payment
            # Issuer calls if it's cheaper
            value = min(continuation, call_price + coupon_payment) if i > 0 else continuation
            new_values.append(value)
        values = new_values

    return round(values[0], 4)


def calculate_z_spread(
    spot_curve: dict[str, float],
    coupon: float,
    maturity_years: int,
    face: float,
    market_price: float,
) -> float:
    """Calculate Z-spread in basis points."""
    mats_known = sorted([(MATURITY_YEARS[m], spot_curve[m]) for m in spot_curve])
    x = np.array([m[0] for m in mats_known])
    y = np.array([m[1] for m in mats_known])
    cs = CubicSpline(x, y, extrapolate=True)

    times = np.arange(1, maturity_years + 1, dtype=float)
    spots = cs(times) / 100.0
    cfs = np.full_like(times, coupon / 100.0 * face)
    cfs[-1] += face

    def objective(z_bps):
        z = z_bps / 10000.0
        price = sum(cf / (1 + s + z) ** t for cf, s, t in zip(cfs, spots, times))
        return price - market_price

    return round(brentq(objective, -500, 3000), 2)


def calculate_oas(
    spot_curve: dict[str, float],
    coupon: float,
    maturity_years: int,
    face: float,
    call_price: float | None,
    market_price: float,
    volatility: float = 0.15,
) -> float:
    """Calculate OAS in basis points.

    For non-callable bonds (call_price=None), OAS ≈ Z-spread.
    For callable bonds, OAS < Z-spread.
    """
    # Build tree from average short rate
    mats_known = sorted([(MATURITY_YEARS[m], spot_curve[m]) for m in spot_curve])
    short_rate = mats_known[0][1]  # use shortest rate as starting point

    tree = build_rate_tree(short_rate, volatility, maturity_years, dt=1.0)

    def objective(oas_bps):
        if call_price is not None:
            price = price_callable_bond_on_tree(
                tree, coupon, face, call_price, dt=1.0, oas_bps=oas_bps
            )
        else:
            # Non-callable: add OAS to all tree rates and price normally
            shifted_tree = [
                [r + oas_bps / 100.0 for r in level] for level in tree
            ]
            price = price_bond_on_tree(shifted_tree, coupon, face, dt=1.0)
        return price - market_price

    return round(brentq(objective, -500, 3000), 2)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/19-cloudwatch-oas/
git commit -m "feat(exercises): 19 CloudWatch + OAS/Z-spread with binomial tree"
```

- [ ] **Step 7-9: Teaching conversation + blog post + commit**

---

### Task 13: Integration Testing + Duration, Convexity, Portfolio Credit VaR (Exercise 20)

**Concept:** End-to-end testing for distributed AWS services. Monte Carlo portfolio credit VaR with correlated spread simulation.

**Files:**
- Create: `exercises/20-integration-testing-var/pyproject.toml`
- Create: `exercises/20-integration-testing-var/src/credit_var.py`
- Create: `exercises/20-integration-testing-var/tests/test_credit_var.py`
- Create: `exercises/20-integration-testing-var/tests/test_integration.py`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-integration-testing-credit-var.html`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "integration-testing-var-exercise"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26.0", "scipy>=1.14.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "moto[s3,sqs,sns]>=5.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["credit_var"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write failing tests**

```python
# exercises/20-integration-testing-var/tests/test_credit_var.py

import numpy as np
import pytest
from credit_var import (
    generate_correlated_spread_shocks,
    spread_duration,
    portfolio_credit_var,
)


class TestCorrelatedShocks:
    def test_output_shape(self):
        corr = np.array([[1.0, 0.5], [0.5, 1.0]])
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr,
            num_simulations=1000,
            seed=42,
        )
        assert shocks.shape == (1000, 2)

    def test_correlation_preserved(self):
        corr = np.array([[1.0, 0.8], [0.8, 1.0]])
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr,
            num_simulations=10000,
            seed=42,
        )
        realized_corr = np.corrcoef(shocks.T)
        assert realized_corr[0, 1] == pytest.approx(0.8, abs=0.05)

    def test_uncorrelated(self):
        corr = np.eye(3)
        shocks = generate_correlated_spread_shocks(
            correlation_matrix=corr,
            num_simulations=10000,
            seed=42,
        )
        realized_corr = np.corrcoef(shocks.T)
        assert abs(realized_corr[0, 1]) < 0.05


class TestSpreadDuration:
    def test_positive_duration(self):
        """Spread duration (CS01) should be positive."""
        sd = spread_duration(
            price=98.0,
            coupon=5.0,
            maturity_years=5,
            spread_bps=100,
            face=100.0,
        )
        assert sd > 0

    def test_longer_maturity_higher_duration(self):
        sd5 = spread_duration(price=98.0, coupon=5.0, maturity_years=5, spread_bps=100, face=100.0)
        sd10 = spread_duration(price=95.0, coupon=5.0, maturity_years=10, spread_bps=100, face=100.0)
        assert sd10 > sd5


class TestPortfolioCreditVaR:
    def test_var_is_negative(self):
        """VaR should represent a loss (negative P&L)."""
        positions = [
            {"price": 98.0, "coupon": 5.0, "maturity_years": 5, "spread_bps": 100, "face": 100.0, "quantity": 1000},
            {"price": 95.0, "coupon": 4.5, "maturity_years": 10, "spread_bps": 150, "face": 100.0, "quantity": 500},
        ]
        corr = np.array([[1.0, 0.6], [0.6, 1.0]])
        spread_vols = np.array([50, 80])  # bps

        var = portfolio_credit_var(
            positions=positions,
            correlation_matrix=corr,
            spread_volatilities=spread_vols,
            confidence=0.95,
            num_simulations=10000,
            seed=42,
        )

        assert var < 0  # it's a loss

    def test_higher_correlation_higher_var(self):
        """More correlation → more portfolio risk → higher VaR (more negative)."""
        positions = [
            {"price": 98.0, "coupon": 5.0, "maturity_years": 5, "spread_bps": 100, "face": 100.0, "quantity": 1000},
            {"price": 95.0, "coupon": 4.5, "maturity_years": 10, "spread_bps": 150, "face": 100.0, "quantity": 500},
        ]
        spread_vols = np.array([50, 80])

        low_corr = np.array([[1.0, 0.2], [0.2, 1.0]])
        high_corr = np.array([[1.0, 0.9], [0.9, 1.0]])

        var_low = portfolio_credit_var(positions, low_corr, spread_vols, 0.95, 10000, seed=42)
        var_high = portfolio_credit_var(positions, high_corr, spread_vols, 0.95, 10000, seed=42)

        assert var_high < var_low  # more negative = worse loss
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd C:\codebase\quant_lab\exercises\20-integration-testing-var
pip install -e ".[dev]"
pytest -v
```

Expected: FAIL

- [ ] **Step 4: Implement credit_var.py**

```python
# exercises/20-integration-testing-var/src/credit_var.py

"""
Portfolio Credit VaR via Monte Carlo simulation.

Process:
  1. Generate correlated spread shocks using Cholesky decomposition
  2. For each simulation, apply shocks to current spreads
  3. Reprice each position under the shocked spread
  4. Calculate portfolio P&L
  5. VaR = percentile of P&L distribution

Cholesky decomposition:
  Given correlation matrix Σ, find lower triangular L where LL^T = Σ.
  Then: correlated_shocks = L × independent_standard_normals
  This transforms independent N(0,1) random variables into
  correlated random variables with the specified correlation structure.

Spread duration (CS01):
  ΔP/P ≈ −SD × Δspread
  The price sensitivity to a 1bp spread change.
  Analogous to modified duration for interest rates.
"""

import numpy as np
from scipy.linalg import cholesky


def generate_correlated_spread_shocks(
    correlation_matrix: np.ndarray,
    num_simulations: int,
    seed: int | None = None,
) -> np.ndarray:
    """Generate correlated standard normal shocks via Cholesky decomposition.

    Args:
        correlation_matrix: n×n correlation matrix.
        num_simulations: Number of Monte Carlo paths.
        seed: Random seed for reproducibility.

    Returns:
        Array of shape (num_simulations, n) with correlated standard normals.
    """
    rng = np.random.default_rng(seed)
    n = correlation_matrix.shape[0]

    # Cholesky: L where LL^T = Σ
    L = cholesky(correlation_matrix, lower=True)

    # Independent standard normals
    Z = rng.standard_normal((num_simulations, n))

    # Correlated shocks: each row = L @ z
    return Z @ L.T


def spread_duration(
    price: float,
    coupon: float,
    maturity_years: int,
    spread_bps: float,
    face: float = 100.0,
    bump_bps: float = 1.0,
) -> float:
    """Calculate spread duration (CS01) via finite difference.

    Args:
        price: Current clean price.
        coupon: Annual coupon rate in percent.
        maturity_years: Years to maturity.
        spread_bps: Current spread in bps.
        face: Face value.
        bump_bps: Bump size in bps.

    Returns:
        Spread duration: price change per 1bp spread move (dollar terms per 100 face).
    """
    def _price_at_spread(s_bps):
        discount_rate = (coupon / 100.0) + (s_bps / 10000.0)
        if discount_rate <= 0:
            discount_rate = 0.001
        times = np.arange(1, maturity_years + 1, dtype=float)
        cfs = np.full_like(times, coupon / 100.0 * face)
        cfs[-1] += face
        pv = sum(cf / (1 + discount_rate) ** t for cf, t in zip(cfs, times))
        return pv

    price_up = _price_at_spread(spread_bps + bump_bps)
    price_down = _price_at_spread(spread_bps - bump_bps)

    return abs((price_up - price_down) / (2 * bump_bps))


def portfolio_credit_var(
    positions: list[dict],
    correlation_matrix: np.ndarray,
    spread_volatilities: np.ndarray,
    confidence: float = 0.95,
    num_simulations: int = 10000,
    seed: int | None = None,
) -> float:
    """Calculate portfolio credit VaR via Monte Carlo.

    Args:
        positions: List of position dicts with keys:
            price, coupon, maturity_years, spread_bps, face, quantity
        correlation_matrix: Correlation matrix of spread changes.
        spread_volatilities: Array of spread volatilities in bps.
        confidence: VaR confidence level (e.g. 0.95).
        num_simulations: Number of Monte Carlo paths.
        seed: Random seed.

    Returns:
        VaR as a negative dollar amount (loss).
    """
    n = len(positions)

    # Generate correlated spread shocks (standard normals × volatilities)
    shocks = generate_correlated_spread_shocks(
        correlation_matrix, num_simulations, seed
    )
    # Scale by volatilities to get spread changes in bps
    spread_changes = shocks * spread_volatilities

    # Calculate spread duration for each position
    durations = []
    for pos in positions:
        sd = spread_duration(
            pos["price"], pos["coupon"], pos["maturity_years"],
            pos["spread_bps"], pos["face"],
        )
        durations.append(sd)

    # Simulate P&L for each path
    pnl = np.zeros(num_simulations)
    for i, pos in enumerate(positions):
        # P&L ≈ −SD × Δspread × quantity × face/100
        position_pnl = -durations[i] * spread_changes[:, i] * pos["quantity"] * pos["face"] / 100.0
        pnl += position_pnl

    # VaR = percentile of P&L distribution
    var_percentile = (1.0 - confidence) * 100  # e.g. 5th percentile for 95% confidence
    var = float(np.percentile(pnl, var_percentile))

    return round(var, 2)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
cd C:\codebase\quant_lab
git add exercises/20-integration-testing-var/
git commit -m "feat(exercises): 20 integration testing + portfolio credit VaR (Monte Carlo)"
```

- [ ] **Step 7-9: Teaching conversation + blog post + commit**

---

## Capstone B: Credit Risk Platform (Task 14)

**Goal:** Assemble exercises 15-20 into a full credit risk platform. Imports Capstone A's curve engine. Adds credit spreads, CDS default probabilities, OAS, portfolio VaR, real-time monitoring, caching, and alerting. Deployed on AWS with full Terraform.

**Files:**
- Create: `projects/credit-risk-platform/pyproject.toml`
- Create: `projects/credit-risk-platform/src/credit/__init__.py`
- Create: `projects/credit-risk-platform/src/credit/models.py`
- Create: `projects/credit-risk-platform/src/credit/spreads.py`
- Create: `projects/credit-risk-platform/src/credit/cds.py`
- Create: `projects/credit-risk-platform/src/credit/oas.py`
- Create: `projects/credit-risk-platform/src/credit/var.py`
- Create: `projects/credit-risk-platform/src/credit/realtime.py`
- Create: `projects/credit-risk-platform/src/credit/cache.py`
- Create: `projects/credit-risk-platform/src/credit/narrative.py`
- Create: `projects/credit-risk-platform/src/credit/db.py`
- Create: `projects/credit-risk-platform/src/credit/db_models.py`
- Create: `projects/credit-risk-platform/src/credit/main.py`
- Create: `projects/credit-risk-platform/tests/`
- Create: `projects/credit-risk-platform/terraform/`
- Create: `projects/credit-risk-platform/Dockerfile`
- Create: `finbytes_git/docs/_posts/2026-XX-XX-credit-risk-platform-capstone.html`

Capstone B follows the same assembly pattern as Capstone A — each module is drawn from the corresponding exercise, wired together with FastAPI, deployed via Terraform. The key addition is that it **imports from Capstone A** for curve construction and base bond pricing.

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "credit-risk-platform"
version = "0.1.0"
description = "Credit risk platform with spreads, CDS, OAS, VaR, and real-time monitoring"
requires-python = ">=3.11"
dependencies = [
    "bond-pricing-engine",
    "pydantic>=2.9.0",
    "numpy>=1.26.0",
    "scipy>=1.14.0",
    "pandas>=2.0.0",
    "fredapi>=0.5.2",
    "anthropic>=0.40.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "boto3>=1.35.0",
    "redis>=5.0.0",
    "structlog>=24.1.0",
    "websockets>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
    "httpx>=0.27.0",
    "moto[s3,sqs,sns,dynamodb,cloudwatch]>=5.0.0",
    "fakeredis>=2.21.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2-15: Build each module following TDD**

Each module (spreads.py, cds.py, oas.py, var.py, realtime.py, cache.py, narrative.py, db.py, main.py) follows the same pattern:
1. Write failing tests
2. Implement module (code from exercises 15-20, adapted for the capstone structure)
3. Run tests, verify pass
4. Commit

The main.py wires everything into a FastAPI app with these endpoints:
- `GET /health` — health check
- `GET /spreads/{rating}` — credit spread curve
- `GET /spreads/history?rating=&start=&end=` — historical spreads
- `POST /credit/price` — corporate bond pricing
- `POST /credit/cds` — default probabilities from CDS
- `POST /credit/oas` — OAS for callable bonds
- `POST /portfolio/var` — Monte Carlo credit VaR
- `WS /ws/spreads` — real-time spread WebSocket
- `GET /alerts` — recent alerts

- [ ] **Step 16: Create Terraform for full deployment**

Full multi-service Terraform: Lambda, API Gateway (REST + WebSocket), RDS, S3, SQS, SNS, ElastiCache, CloudWatch, DynamoDB (connection tracking), with modules and dev/prod environments.

- [ ] **Step 17: Create Dockerfile**

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM base AS production
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
EXPOSE 8000
CMD ["uvicorn", "credit.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 18: Commit Capstone B**

```bash
cd C:\codebase\quant_lab
git add projects/credit-risk-platform/
git commit -m "feat(credit-risk-platform): capstone B — credit spreads, CDS, OAS, VaR, real-time on AWS"
```

- [ ] **Step 19: Extend Streamlit dashboard**

Add "Credit Risk" page to the FinBytes dashboard:
- Credit spread charts by rating (AAA through B)
- Default probability / survival curves from CDS
- OAS vs Z-spread comparison tool
- Portfolio VaR simulation with configurable scenarios
- Alert history and threshold configuration
- System health for credit risk API

- [ ] **Step 20: Teaching conversation + capstone blog post + commit**

---

## Summary

| # | Task | Exercise | AWS Concept | Finance Concept |
|---|------|----------|-------------|-----------------|
| 1 | AWS Setup + Treasury Data | 09 | IAM, CLI, billing | Par yields, curve shapes |
| 2 | S3 Data Ingestion | 10 | S3, boto3 | Par curve, data quality |
| 3 | RDS PostgreSQL | 11 | RDS, security groups | Yield/bond schema design |
| 4 | Lambda + API Gateway | 12 | Lambda, API GW | Spot curve bootstrapping |
| 5 | CI/CD | 13 | GitHub Actions | Forward rate curve |
| 6 | Terraform | 14 | Terraform, IaC | Nelson-Siegel/Svensson |
| 7 | **Capstone A** | — | S3+RDS+Lambda+APIGW+TF | **Bond Pricing Engine** |
| 8 | SQS/SNS | 15 | SQS, SNS | Credit spreads, CDS |
| 9 | WebSockets | 16 | API GW WebSocket | Real-time monitoring |
| 10 | ElastiCache | 17 | Redis caching | Cache strategies |
| 11 | Terraform Advanced | 18 | Modules, environments | Default probabilities |
| 12 | CloudWatch | 19 | Metrics, dashboards | OAS, Z-spread |
| 13 | Integration Testing | 20 | moto, LocalStack | Credit VaR (Monte Carlo) |
| 14 | **Capstone B** | �� | Full AWS stack | **Credit Risk Platform** |
