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

import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
import streamlit as st
from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from test_tab import render_test_tab

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

# --- AWS resource status -------------------------------------------------
#
# Read-only view of the other QuantLab AWS resources. IAM permissions
# are scoped to specific ARNs in QuantLabRDSLifecycle; see
# docs/rds-admin-policy.json.

st.subheader("AWS Resources")


def _lambda_status() -> None:
    lam = boto3.client(
        "lambda",
        aws_access_key_id=aws_cfg["access_key_id"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        region_name=aws_cfg.get("region", "us-east-1"),
    )
    try:
        fn = lam.get_function(FunctionName="quant-lab-bootstrap")["Configuration"]
        state = fn.get("State", "?")
        badge = {"Active": "green", "Inactive": "orange", "Failed": "red"}.get(state, "gray")
        st.markdown(f"**Lambda** `quant-lab-bootstrap` — :{badge}[{state}]")
        st.caption(
            f"Runtime: {fn.get('Runtime', '?')} · "
            f"{fn.get('MemorySize', '?')}MB · "
            f"timeout {fn.get('Timeout', '?')}s · "
            f"last modified {fn.get('LastModified', '?')[:10]}"
        )
    except ClientError as exc:
        st.warning(f"Lambda read failed: {exc.response['Error']['Code']}")


def _apigw_status() -> None:
    gw = boto3.client(
        "apigateway",
        aws_access_key_id=aws_cfg["access_key_id"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        region_name=aws_cfg.get("region", "us-east-1"),
    )
    api_id = "5wsgaoptef"
    try:
        api = gw.get_rest_api(restApiId=api_id)
        stages = gw.get_stages(restApiId=api_id).get("item", [])
        st.markdown(f"**API Gateway** `{api['name']}` — :green[deployed]")
        for stage in stages:
            name = stage["stageName"]
            url = f"https://{api_id}.execute-api.{aws_cfg.get('region', 'us-east-1')}.amazonaws.com/{name}/curves/bootstrap"
            st.caption(f"stage `{name}` → {url}")
    except ClientError as exc:
        st.warning(f"API Gateway read failed: {exc.response['Error']['Code']}")


def _s3_status() -> None:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_cfg["access_key_id"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        region_name=aws_cfg.get("region", "us-east-1"),
    )
    bucket = "finbytes-quant-lab-data"
    try:
        prefixes = ["par-yields/", "spot-curves/"]
        counts: dict[str, int] = {}
        for prefix in prefixes:
            resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            counts[prefix] = resp.get("KeyCount", 0)
        st.markdown(f"**S3** `{bucket}` — :green[accessible]")
        parts = [f"`{p}` {n}" for p, n in counts.items()]
        st.caption("objects: " + " · ".join(parts))
    except ClientError as exc:
        st.warning(f"S3 read failed: {exc.response['Error']['Code']}")


_lambda_status()
_apigw_status()
_s3_status()

# -- Tests ----------------------------------------------------------------
with st.expander("Test Results"):
    render_test_tab("test_admin.py")

st.markdown("---")
if st.button("Log out"):
    st.session_state.admin_authed = False
    st.rerun()
