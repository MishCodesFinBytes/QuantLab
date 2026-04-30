"""Admin controls for QuantLab — Render DB lifecycle.

Password-gated page with three tabs:
    Status     — read-only overview of Render services
    Render DB  — one-click recreate of the 30-day Render Postgres
    Tests      — frontend test results

Required st.secrets keys:
    admin.password              the gate
    render.*                    see render_admin.py docstring
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
from test_tab import render_test_tab
from render_admin import RenderClient, RenderConfig, RenderError, rewrite_scheme

st.set_page_config(page_title="Admin", page_icon="assets/logo.png", layout="centered")
st.title("Admin")
st.caption("Lifecycle controls for the QuantLab infra.")

# --- Auth gate ------------------------------------------------------------

if "admin_authed" not in st.session_state:
    st.session_state.admin_authed = False

if not st.session_state.admin_authed:
    with st.form("auth"):
        pw = st.text_input("Admin password", type="password")
        if st.form_submit_button("Unlock"):
            expected = st.secrets.get("admin", {}).get("password")
            if expected and pw == expected:
                st.session_state.admin_authed = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

# --- Render config --------------------------------------------------------

render_secrets = st.secrets.get("render", {})
render_missing = [k for k in ("api_key", "owner_id", "postgres_id", "service_id", "db_name")
                  if not render_secrets.get(k)]
render_cfg = None
render_client = None
if not render_missing:
    render_cfg = RenderConfig(
        api_key=render_secrets["api_key"],
        owner_id=render_secrets["owner_id"],
        postgres_id=render_secrets["postgres_id"],
        service_id=render_secrets["service_id"],
        db_name=render_secrets["db_name"],
        plan=render_secrets.get("plan", "free"),
        region=render_secrets.get("region", "oregon"),
        env_var_key=render_secrets.get("env_var_key", "DATABASE_URL"),
        url_scheme=render_secrets.get("url_scheme", "postgresql+asyncpg"),
    )
    render_client = RenderClient(render_cfg)


def _render_days_left() -> tuple[int | None, str]:
    """Return (days_left, status) using expiresAt from the Render API."""
    if not render_client or not render_cfg:
        return None, "not configured"
    try:
        info = render_client.get_postgres(render_cfg.postgres_id)
    except RenderError as exc:
        return None, f"read error: {exc}"
    expires_raw = info.get("expiresAt")
    if not expires_raw:
        return None, info.get("status", "?")
    try:
        expires_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
        days_left = (expires_dt - datetime.now(timezone.utc)).days
        return days_left, info.get("status", "?")
    except ValueError:
        return None, info.get("status", "?")


# --- Tabs -----------------------------------------------------------------

tab_status, tab_render, tab_tests = st.tabs(["Status", "Render DB", "Tests"])

# ============================================================ Status tab
with tab_status:
    st.subheader("Service health")

    days_left, rstatus = _render_days_left()
    if days_left is None:
        st.markdown(f"**Render DB** — :gray[{rstatus}]")
    else:
        colour = "red" if days_left < 14 else "orange" if days_left < 30 else "green"
        st.markdown(
            f"**Render DB** `{render_cfg.db_name}` — "
            f":{colour}[**{days_left} days left**] · {rstatus}"
        )

    st.markdown("---")
    if st.button("Refresh status", width='stretch', key="refresh_status"):
        st.rerun()

# ========================================================== Render DB tab
with tab_render:
    st.subheader("Render PostgreSQL")
    st.caption(
        "Free Render Postgres expires 30 days after creation. Recreate the DB "
        "with the same name and rewire DATABASE_URL in one click."
    )

    if render_missing:
        st.warning(
            "Render tab not configured. Add the following keys to Streamlit "
            f"secrets under `[render]`: {', '.join(render_missing)}"
        )
        with st.expander("Example secrets block"):
            st.code(
                "[render]\n"
                'api_key = "rnd_..."\n'
                'owner_id = "tea_..."       # or usr_...\n'
                'postgres_id = "dpg-..."    # current DB\n'
                'service_id = "srv-..."     # web service to rewire\n'
                'db_name = "finbytes-scanner-db"\n'
                'plan = "free"\n'
                'region = "oregon"\n'
                'env_var_key = "DATABASE_URL"\n'
                'url_scheme = "postgresql+asyncpg"',
                language="toml",
            )
    else:
        try:
            info = render_client.get_postgres(render_cfg.postgres_id)
        except RenderError as exc:
            st.error(f"Could not read Postgres status: {exc}")
            info = None

        if info:
            rstatus = info.get("status", "?")
            badge = {"available": "green", "creating": "blue", "suspended": "gray"}.get(rstatus, "red")
            st.markdown(f"**Status:** :{badge}[**{rstatus}**]  ·  "
                        f"**Name:** `{info.get('name', '?')}`")

            expires_raw = info.get("expiresAt")
            created_raw = info.get("createdAt")
            if expires_raw:
                try:
                    expires_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                    days_left = (expires_dt - datetime.now(timezone.utc)).days
                    colour = "red" if days_left < 7 else "orange" if days_left < 14 else "green"
                    st.markdown(f"**Days until expiry:** :{colour}[**{days_left}**]")
                    st.caption(f"Expires {expires_dt:%Y-%m-%d}")
                    if created_raw:
                        try:
                            created_dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                            st.caption(f"Created {created_dt:%Y-%m-%d}")
                        except ValueError:
                            pass
                except ValueError:
                    st.caption(f"Expires: {expires_raw}")

            with st.expander("Advanced"):
                st.markdown(f"**DB id:** `{render_cfg.postgres_id}`")
                st.markdown(f"**Plan:** `{info.get('plan', '?')}` · "
                            f"**Region:** `{info.get('region', '?')}`")

        st.markdown("---")
        st.markdown("### Recreate database")
        st.warning(
            "This will **delete the current Postgres and all its data**, then "
            "create a fresh one with the same name. The connected web service "
            "will redeploy automatically. Type the DB name to confirm."
        )

        confirm = st.text_input("Type the DB name to confirm", key="render_confirm")
        do_recreate = st.button(
            "Recreate database now",
            disabled=(confirm != render_cfg.db_name),
            type="primary",
        )

        if do_recreate:
            with st.status("Recreating Render Postgres...", expanded=True) as status_box:
                try:
                    st.write(f"1/6 Deleting old Postgres `{render_cfg.postgres_id}`...")
                    render_client.delete_postgres(render_cfg.postgres_id)

                    st.write("2/6 Waiting 10s for deletion to propagate...")
                    time.sleep(10)

                    st.write(f"3/6 Creating new Postgres `{render_cfg.db_name}`...")
                    new_db = render_client.create_postgres()
                    new_pid = new_db.get("id") or new_db.get("postgres", {}).get("id")
                    if not new_pid:
                        raise RenderError(f"Create response missing id: {new_db}")
                    st.write(f"    → new id: `{new_pid}`")

                    st.write("4/6 Waiting for new DB to become available (up to 10 min)...")
                    render_client.wait_postgres_available(new_pid, timeout=600, poll=10)

                    st.write("5/6 Fetching connection string and updating DATABASE_URL...")
                    internal = render_client.internal_url(new_pid)
                    rewired = rewrite_scheme(internal, render_cfg.url_scheme)
                    render_client.set_env_var(render_cfg.env_var_key, rewired)

                    st.write("6/6 Triggering service redeploy...")
                    render_client.trigger_deploy()

                    status_box.update(
                        label="Recreation complete — service redeploying.",
                        state="complete",
                        expanded=True,
                    )
                    st.success(
                        f"New Postgres id: `{new_pid}`. **Update your Streamlit "
                        f"secret `render.postgres_id` to this value** so the status "
                        f"tab reads the correct DB next time."
                    )
                    st.info(
                        "The backend will auto-create tables on startup. Seed data "
                        "(if any) is lost — fine for the demo."
                    )
                except (RenderError, ValueError) as exc:
                    status_box.update(label="Recreation failed.", state="error")
                    st.error(f"Failed: {exc}")
                    st.info(
                        "Check the Render dashboard. You may need to manually "
                        "complete the remaining steps from docs/MAINTENANCE.md."
                    )

# ============================================================= Tests tab
with tab_tests:
    render_test_tab("test_churros.py")

# --- Log out --------------------------------------------------------------

st.markdown("---")
if st.button("Log out"):
    st.session_state.admin_authed = False
    st.rerun()

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "Streamlit"])
