"""RDS admin controls for QuantLab.

Password-gated page to start/stop the RDS PostgreSQL instance. The aim is
avoiding forgotten-on-24/7 instances that would blow the free-tier hour
budget. AWS credentials and the admin password come from Streamlit Cloud
secrets — nothing sensitive lives in the repo.

Required st.secrets keys:
    admin.password              the gate
    aws.access_key_id           scoped IAM user (quant-lab-streamlit)
    aws.secret_access_key
    aws.region                  default us-east-1
    aws.rds_instance_id         default quant-lab-db
"""

from datetime import datetime, timezone

import boto3
import streamlit as st
from botocore.exceptions import ClientError

st.set_page_config(page_title="Admin · RDS", page_icon="🔒", layout="centered")
st.title("RDS Admin")
st.caption("Start / stop the QuantLab RDS instance to conserve free-tier hours.")

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

# --- AWS client -----------------------------------------------------------

try:
    aws_cfg = st.secrets["aws"]
    client = boto3.client(
        "rds",
        aws_access_key_id=aws_cfg["access_key_id"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        region_name=aws_cfg.get("region", "us-east-1"),
    )
    instance_id = aws_cfg.get("rds_instance_id", "quant-lab-db")
except KeyError as e:
    st.error(f"Missing Streamlit secret: {e}")
    st.stop()


def describe():
    try:
        resp = client.describe_db_instances(DBInstanceIdentifier=instance_id)
        return resp["DBInstances"][0]
    except ClientError as exc:
        st.error(f"AWS error: {exc.response['Error']['Message']}")
        return None


# --- Status ---------------------------------------------------------------

instance = describe()
if instance is None:
    st.stop()

status = instance["DBInstanceStatus"]
endpoint = (instance.get("Endpoint") or {}).get("Address", "—")
created = instance.get("InstanceCreateTime")

colour = {
    "available": "green",
    "stopped": "gray",
    "starting": "blue",
    "stopping": "orange",
    "creating": "blue",
}.get(status, "red")

st.markdown(f"**Instance:** `{instance_id}`")
st.markdown(f"**Status:** :{colour}[**{status}**]")
st.markdown(f"**Endpoint:** `{endpoint}`")
st.markdown(f"**Class:** `{instance.get('DBInstanceClass', '?')}`  ·  "
            f"**Storage:** {instance.get('AllocatedStorage', '?')} GB")

if created:
    age_hours = (datetime.now(timezone.utc) - created).total_seconds() / 3600
    st.caption(f"Instance created {created:%Y-%m-%d %H:%M UTC} "
               f"({age_hours:,.0f} hours ago). Free tier allows 750 hours/month.")

st.markdown("---")

# --- Controls -------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Refresh", use_container_width=True):
        st.rerun()

with col2:
    disabled = status != "available"
    if st.button("Stop instance", disabled=disabled, use_container_width=True):
        try:
            client.stop_db_instance(DBInstanceIdentifier=instance_id)
            st.success("Stop requested. Refresh in ~1 minute.")
        except ClientError as exc:
            st.error(f"Stop failed: {exc.response['Error']['Message']}")

with col3:
    disabled = status != "stopped"
    if st.button("Start instance", disabled=disabled, use_container_width=True):
        try:
            client.start_db_instance(DBInstanceIdentifier=instance_id)
            st.success("Start requested. Refresh in a few minutes.")
        except ClientError as exc:
            st.error(f"Start failed: {exc.response['Error']['Message']}")

st.markdown("---")
if st.button("Log out"):
    st.session_state.admin_authed = False
    st.rerun()
