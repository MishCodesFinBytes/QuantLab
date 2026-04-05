# AWS Setup Guide — QuantLab Phase 2

One-time setup steps for the AWS exercises (09-20) and capstones (Bond Pricing Engine, Credit Risk Platform). Do this once; reuse throughout Phase 2.

---

## Prerequisites

- Valid email address
- Credit/debit card (required for AWS free tier, won't be charged if you stay within limits)
- Phone for SMS verification

---

## Step 1: Create AWS Account

1. Go to https://aws.amazon.com/ → **Create an AWS Account**
2. Account type: **Personal**
3. Support plan: **Basic support - Free**
4. After signup, sign in to the AWS Management Console
5. Set region to **US East (N. Virginia) us-east-1** (top-right region selector)
6. Note your 12-digit Account ID (top-right, click your account name)

---

## Step 2: Create IAM User (Never Use Root)

**Console → IAM → Users → Create user**

- Username: `finbytes` (or your preferred name)
- Enable console access (optional)
- Attach these policies directly:
  - `AmazonS3FullAccess`
  - `AmazonRDSFullAccess`
  - `AmazonEC2FullAccess` (needed for security groups + VPC — `ec2:*` covers both)
  - `AWSLambda_FullAccess`
  - `AmazonAPIGatewayAdministrator`
  - `AmazonSQSFullAccess`
  - `AmazonSNSFullAccess`
  - `AmazonElastiCacheFullAccess`
  - `CloudWatchFullAccess`
  - `IAMReadOnlyAccess`

**Then create an Access Key:** User → Security credentials → Create access key → CLI use case → Download CSV.

> **Note:** IAM Identity Center (SSO) is AWS's recommended approach for production. IAM users with access keys are simpler for learning and fine for a personal project.

---

## Step 3: Install & Configure AWS CLI

```bash
winget install Amazon.AWSCLI
# Close and reopen terminal after install

aws --version
aws configure --profile quant-lab
#   Access Key ID:     <from CSV>
#   Secret Access Key: <from CSV>
#   Region:            us-east-1
#   Output format:     json

# Verify
aws sts get-caller-identity --profile quant-lab
```

The `Arn` in the output should end in `user/<your-username>`.

---

## Step 4: $5 Billing Alarm (Safety Net)

**Enable billing alerts:**
- Console → Billing and Cost Management → Billing preferences → Edit alert preferences
- Check "Receive AWS Free Tier alerts" and "Receive CloudWatch billing alerts"
- Save your email

**Create SNS topic (region must be us-east-1 — billing metrics only exist there):**
- SNS → Topics → Create topic → Standard, name `billing-alerts`
- Create subscription: Email protocol, your email address
- **Confirm the subscription via the email AWS sends you**

**Create CloudWatch alarm:**
- CloudWatch → Alarms → All alarms → Create alarm
- Select metric: Billing → Total Estimated Charge → USD
- Statistic: Maximum | Period: 6 hours | Threshold: > 5
- Action: SNS topic `billing-alerts`
- Name: `BillingAlarm-5USD`

---

## Step 5: FRED API Key (Free)

1. Register at https://fred.stlouisfed.org/ → create account
2. Go to https://fredaccount.stlouisfed.org/apikeys → request API key
3. Fill in form (Application URL can be `http://localhost`)
4. Copy the 32-character key

**Store as environment variable:**

```bash
# Windows (persistent — requires terminal restart)
setx FRED_API_KEY "your-32-char-key"

# Or add to .env file at repo root (git-ignored)
```

---

## What to Do When the Billing Alarm Fires

The alarm tells you charges are climbing — not why. Find the culprit:

**Step 1 — Identify cost driver:**
- Billing → **Cost Explorer**
- Filter by Service, group by Usage Type

**Step 2 — Common culprits:**

| Service | Typical cause | Fix |
|---------|--------------|-----|
| RDS | Running past 750hr/month free tier | Stop or delete instance |
| EC2 | Instance + attached EIP | Stop instance, release EIP |
| **NAT Gateway** | **~$32/month, NO free tier** | **Delete it immediately** |
| ElastiCache | Running past free tier | Delete cluster |
| Data Transfer | Large S3 egress | Review access patterns |
| EBS volumes | Orphaned from deleted EC2 | Delete unused volumes |

**Step 3 — Nuclear option (tear down all QuantLab infra):**

```bash
cd C:\codebase\quant_lab\exercises\<exercise>\terraform
terraform destroy --auto-approve

cd C:\codebase\quant_lab\projects\bond-pricing-engine\terraform
terraform destroy --auto-approve
```

**Step 4 — For resources created manually via Console:**

Service consoles (region us-east-1):
- RDS: https://console.aws.amazon.com/rds/home?region=us-east-1#databases:
- Lambda: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
- S3: https://s3.console.aws.amazon.com/s3/home?region=us-east-1
- EC2/Volumes/EIPs: https://console.aws.amazon.com/ec2/home?region=us-east-1
- ElastiCache: https://console.aws.amazon.com/elasticache/home?region=us-east-1
- CloudWatch Alarms: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:

---

## RDS Lifecycle Helper

To avoid burning free-tier hours, stop the RDS instance when not actively using it. A helper script at `scripts/rds.py` wraps the boto3 calls:

```bash
python scripts/rds.py status         # show current state
python scripts/rds.py stop --wait    # stop and block until stopped
python scripts/rds.py start --wait   # start and block until available
```

Env vars override defaults: `RDS_INSTANCE_ID` (default `quant-lab-db`), `AWS_PROFILE` (default `quant-lab`), `AWS_REGION` (default `us-east-1`).

## Golden Rules

1. **Stop RDS when not actively learning** — free tier is 750 hrs/month, a 24/7 instance = 720 hrs. Two running = over limit. Use `scripts/rds.py stop` to save hours.
2. **Never create NAT Gateways** — #1 surprise AWS bill.
3. **Confirm region** with `aws configure list --profile quant-lab` before creating resources.
4. **Run `terraform destroy` at end of each learning session** where you provisioned things.
5. **Never commit secrets** — keep everything in `.env` (git-ignored).

---

## Quick Reference

| Account item | Value |
|---|---|
| AWS Region | `us-east-1` |
| AWS Profile | `quant-lab` |
| IAM User | `finbytes` |
| S3 Bucket (data) | `finbytes-quant-lab-data` |
| S3 Bucket (TF state) | `finbytes-quant-lab-tfstate` |
| Billing alarm | `BillingAlarm-5USD` |
| SNS topic | `billing-alerts` |
