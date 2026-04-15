# FinBytes QuantLabs — Maintenance Guide

Things that need periodic attention to keep the live demo running.

---

## Render PostgreSQL — Recreate Every 30 Days

> **Note:** Render's free Postgres expires **30 days** after creation (not 90 as the old plan assumed).

**Current DB:** `finbytes-scanner-db` — created 2026-04-03, expires **2026-05-03**, region `frankfurt`

**How to check:** Visit [quantlabs.streamlit.app/Churros](https://quantlabs.streamlit.app/Churros) → unlock → **Render DB** tab shows days-until-expiry with a colour badge.

**How to fix (automated):**
1. Unlock the Churros admin page
2. Go to the **Render DB** tab
3. Type `finbytes-scanner-db` to confirm and click **Recreate database now**
4. Watch the 6-step progress — delete, create, rewire `DATABASE_URL`, redeploy
5. **Update `render.postgres_id` in Streamlit secrets** to the new `dpg-...` id the tab shows you
6. Done — tables auto-create on startup, seed data lost (fine for demo)

**How to fix (manual fallback):**
1. Go to [render.com](https://render.com) → delete the expired database
2. New → PostgreSQL → name: `finbytes-scanner-db` → Free plan → region `Frankfurt` → Create
3. Copy the **Internal Database URL**
4. Go to web service `finbytes-scanner` → Environment → edit `DATABASE_URL`
5. Replace `postgres://` with `postgresql+asyncpg://` in the URL
6. Save — auto-redeploys, tables auto-created on startup

---

## Render Web Service — Cold Starts

The free tier sleeps after 15 minutes of no traffic. First request after sleep takes 30-60 seconds. This is normal — the dashboard shows "Backend warming up..." during this time.

**Nothing to do** — just be aware when demoing. Hit the health endpoint first to wake it up.

---

## Streamlit Cloud

Auto-deploys from `master` branch. No maintenance needed. If the app crashes, check the logs: Streamlit Cloud dashboard → your app → Manage app → Logs.

---

## GitHub Actions CI

Free tier: 2000 minutes/month. Each run takes ~1 minute. At current usage, nowhere near the limit.

**If CI stops running:** Check [github.com/mish-codes/QuantLab/actions](https://github.com/mish-codes/QuantLab/actions) for error details.

---

## Anthropic API Key (Optional)

Currently set to `skip` (fallback mode). To enable AI narratives:
1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Get API key ($5 free credits = ~1,600 scans)
3. Render dashboard → `finbytes-scanner` → Environment → set `ANTHROPIC_API_KEY`
4. No auto-billing — stops working when credits run out, you must manually add payment method

---

## Domains & URLs

| Service | URL | Auto-deploys from |
|---------|-----|-------------------|
| Dashboard | [quantlabs.streamlit.app](https://quantlabs.streamlit.app) | `master` branch |
| Scanner API | [finbytes-scanner.onrender.com](https://finbytes-scanner.onrender.com) | `master` branch |
| Blog | [mish-codes.github.io/FinBytes](https://mish-codes.github.io/FinBytes/) | `master` branch |
| GitHub | [github.com/mish-codes/QuantLab](https://github.com/mish-codes/QuantLab) | — |

---

## Calendar Reminders

| What | When | Action |
|------|------|--------|
| Renew scanner DB | 2026-05-03 | Use Churros → Render DB tab (1-click) |
| Check CI minutes | Monthly | Should be well under 2000 min/month |
| Check Anthropic credits | If API key is added | Set spending cap in Anthropic console |

---

## Refreshing London PPD with bedroom data

The Rent vs Buy London calculator uses
`dashboard/data/london_ppd_with_bedrooms.parquet`, which is built by
joining Land Registry PPD with the EPC (Energy Performance Certificates)
dataset on postcode to enrich each sale with a bedroom band.

To refresh after a new PPD release:

1. Download the latest London PPD CSV from
   https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads
   and rebuild `dashboard/data/london_ppd.parquet` with your existing
   PPD prep flow.
2. Make sure `dashboard/.env.local` has `EPC_API_EMAIL` and
   `EPC_API_TOKEN` set (free registration at
   https://epc.opendatacommunities.org/).
3. Run from the repo root:

   ```bash
   python dashboard/scripts/build_ppd_with_bedrooms.py --refresh-epc
   ```

   This refreshes the EPC cache from the API (32 local authorities,
   ~3-5 minutes) and rebuilds the enriched parquet.
4. Verify the printed match rate is at least 50% — anything lower
   means the EPC API returned partial data and the script should be
   re-run.
5. Commit `dashboard/data/london_ppd_with_bedrooms.parquet`.

The EPC cache lives at `dashboard/data/_cache/epc/<la_code>/certificates.csv`
and is gitignored — only the parquet output is committed.
