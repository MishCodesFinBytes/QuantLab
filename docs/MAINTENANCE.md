# FinBytes QuantLabs — Maintenance Guide

Things that need periodic attention to keep the live demo running.

---

## Render PostgreSQL — Recreate Every 90 Days

**Current DB:** `finbytes-scanner-db` — created 2026-04-03, expires ~2026-07-02

**How to check:** Visit [finbytes.streamlit.app](https://finbytes.streamlit.app) → System Health → Database shows red.

**How to fix:**
1. Go to [render.com](https://render.com) → delete the expired database
2. New → PostgreSQL → name: `finbytes-scanner-db` → Free plan → Create
3. Copy the **Internal Database URL**
4. Go to web service `finbytes-scanner` → Environment → edit `DATABASE_URL`
5. Replace `postgres://` with `postgresql+asyncpg://` in the URL
6. Save — auto-redeploys, tables auto-created on startup
7. Data is lost (empty DB) — fine for a demo

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

**If CI stops running:** Check [github.com/MishCodesFinBytes/QuantLab/actions](https://github.com/MishCodesFinBytes/QuantLab/actions) for error details.

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
| Dashboard | [finbytes.streamlit.app](https://finbytes.streamlit.app) | `master` branch |
| Scanner API | [finbytes-scanner.onrender.com](https://finbytes-scanner.onrender.com) | `master` branch |
| Blog | [mishcodesfinbytes.github.io/FinBytes](https://mishcodesfinbytes.github.io/FinBytes/) | `master` branch |
| GitHub | [github.com/MishCodesFinBytes/QuantLab](https://github.com/MishCodesFinBytes/QuantLab) | — |

---

## Calendar Reminders

| What | When | Action |
|------|------|--------|
| Renew scanner DB | ~2026-07-02 | Recreate on Render (see above) |
| Check CI minutes | Monthly | Should be well under 2000 min/month |
| Check Anthropic credits | If API key is added | Set spending cap in Anthropic console |
