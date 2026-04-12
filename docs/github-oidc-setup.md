# GitHub → AWS OIDC Setup

The `.github/workflows/deploy-forward-rates.yml` workflow deploys to AWS
Lambda without storing long-lived access keys in GitHub Secrets. Instead,
GitHub Actions presents an OIDC token to AWS on each run, AWS verifies
the token, and a scoped IAM role is assumed for the duration of the job.

One-time setup (root console). After this, pushes to `master` that touch
`exercises/13-cicd-github-actions/src/**` will auto-deploy.

## 1. Create IAM Identity Provider for GitHub

Root → IAM → **Identity providers** → **Add provider**

- **Provider type:** OpenID Connect
- **Provider URL:** `https://token.actions.githubusercontent.com`
- Click **Get thumbprint**
- **Audience:** `sts.amazonaws.com`
- **Add provider**

## 2. Create the deploy role

IAM → **Roles** → **Create role**

- **Trusted entity type:** Web identity
- **Identity provider:** `token.actions.githubusercontent.com`
- **Audience:** `sts.amazonaws.com`
- **GitHub organization:** `mish-codes`
- **GitHub repository:** `QuantLab`
- **GitHub branch:** leave blank (we'll edit the trust policy after)
- **Next**

**Permissions policies:** skip for now (we'll attach an inline policy next) → **Next**

- **Role name:** `github-actions-quantlab-deploy`
- **Create role**

## 3. Edit the trust policy (restrict to master branch)

Open the new role → **Trust relationships** → **Edit trust policy**. Replace
with:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::349348221529:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:mish-codes/QuantLab:ref:refs/heads/master"
                }
            }
        }
    ]
}
```

**Update policy**.

The `sub` condition is what prevents a fork or a feature branch from
assuming this role — only pushes to `master` in this specific repo can.

## 4. Attach the deploy permissions

Same role → **Permissions** tab → **Add permissions** → **Create inline policy** → JSON:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionCode",
                "lambda:GetFunction",
                "lambda:PublishVersion"
            ],
            "Resource": "arn:aws:lambda:us-east-1:349348221529:function:quant-lab-forward-rates"
        }
    ]
}
```

Policy name: `QuantLabLambdaDeploy` → **Create policy**.

## 5. Copy the role ARN

Back on the role page, copy the **ARN** at the top:
`arn:aws:iam::349348221529:role/github-actions-quantlab-deploy`

## 6. Add as a GitHub secret

GitHub → `mish-codes/QuantLab` → **Settings** → **Secrets and
variables** → **Actions** → **New repository secret**

- **Name:** `AWS_DEPLOY_ROLE_ARN`
- **Value:** the role ARN from step 5
- **Add secret**

## 7. Trigger a deploy

Push to `master` touching `exercises/13-cicd-github-actions/src/**` or
this workflow file. Watch the run at **Actions** → **Deploy
forward-rates Lambda**.

## Verify

```bash
# Edit src/forward_rates.py slightly (e.g. add a comment)
# Commit and push on master
# Check GitHub Actions → Deploy forward-rates Lambda → green run
# Then:
aws lambda get-function --function-name quant-lab-forward-rates \
  --query "Configuration.LastModified" --profile quant-lab
# Should show today's timestamp
```
