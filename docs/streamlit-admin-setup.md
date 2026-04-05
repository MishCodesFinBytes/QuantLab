# Streamlit Admin Page — Setup

The `dashboard/pages/99_Admin.py` page starts/stops the RDS instance to save
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

Visit https://finbytes.streamlit.app/Admin — enter the admin password, then
status / stop / start.

## 4. Rotate if leaked

Delete the access key in IAM → User → Security credentials, create a new
one, update the Streamlit secret.
