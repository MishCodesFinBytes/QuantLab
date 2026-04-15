# Streamlit Admin Page — Setup

The `dashboard/pages/99_Churros.py` page (obfuscated URL — formerly `99_Admin.py`) starts/stops the RDS instance to save
free-tier hours. It needs a **scoped IAM user** (not `quant-lab-dev`) and
**Streamlit Cloud secrets**.

## 1. Create IAM user via AWS Console

Sign in as root → IAM → Users → Create user:

- **User name:** `quant-lab-streamlit`
- **AWS access type:** Programmatic access only (no console)
- **Permissions:** *Attach policies directly* → *Create inline policy*

Paste this JSON (also saved at `docs/rds-admin-policy.json`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ControlQuantLabRDS",
            "Effect": "Allow",
            "Action": [
                "rds:StartDBInstance",
                "rds:StopDBInstance",
                "rds:DescribeDBInstances"
            ],
            "Resource": "arn:aws:rds:us-east-1:349348221529:db:quant-lab-db"
        },
        {
            "Sid": "DescribeAllRequiredByAPI",
            "Effect": "Allow",
            "Action": "rds:DescribeDBInstances",
            "Resource": "*"
        }
    ]
}
```

Policy name: `QuantLabRDSLifecycle`.

Then on the user's *Security credentials* tab, **Create access key** →
*Application running outside AWS*. Copy the access key ID + secret key.

## 2. Add Streamlit Cloud secrets

On share.streamlit.io → your app → Settings → Secrets, paste:

```toml
[admin]
password = "wlwu2vGYVNRMii8g8yjj"

[aws]
access_key_id = "AKIA..."
secret_access_key = "..."
region = "us-east-1"
rds_instance_id = "quant-lab-db"
```

Save — Streamlit restarts the app.

## 3. Access the page

Visit https://quantlabs.streamlit.app/Admin — enter the admin password, then
status / stop / start.

## 4. Expand policy for AWS status panel (optional)

The admin page also shows a read-only status of Lambda, API Gateway and
S3 resources. If the panel shows "read failed" warnings, the
`QuantLabRDSLifecycle` policy needs the additional statements in
`docs/rds-admin-policy.json` (scoped to the Lambda ARN, the REST API ID,
and the S3 bucket ARN).

Sign in as root → IAM → Users → `quant-lab-streamlit` → the inline
policy `QuantLabRDSLifecycle` → **Edit** → replace JSON with the current
content of `docs/rds-admin-policy.json` → Review → Save.

## 5. Rotate if leaked

Delete the access key in IAM → User → Security credentials, create a new
one, update the Streamlit secret.
