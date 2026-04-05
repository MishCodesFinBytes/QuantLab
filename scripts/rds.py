"""RDS instance lifecycle manager for QuantLab.

Stop / start / status commands for a single RDS instance. The point is to
save free-tier hours when you're not actively using the database, which is
easy to forget during a learning project.

Usage:
    python scripts/rds.py status
    python scripts/rds.py stop
    python scripts/rds.py start

Config via env vars (or defaults):
    AWS_PROFILE=quant-lab
    AWS_REGION=us-east-1
    RDS_INSTANCE_ID=quant-lab-db
"""

import argparse
import os
import sys
import time

import boto3
from botocore.exceptions import ClientError


DEFAULT_INSTANCE_ID = os.environ.get("RDS_INSTANCE_ID", "quant-lab-db")
DEFAULT_PROFILE = os.environ.get("AWS_PROFILE", "quant-lab")
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")


def _client(profile: str, region: str):
    session = boto3.Session(profile_name=profile, region_name=region)
    return session.client("rds")


def _describe(rds, instance_id: str) -> dict | None:
    try:
        response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
        return response["DBInstances"][0]
    except ClientError as e:
        if e.response["Error"]["Code"] == "DBInstanceNotFound":
            return None
        raise


def _print_status(instance: dict) -> None:
    status = instance["DBInstanceStatus"]
    endpoint = instance.get("Endpoint") or {}
    host = endpoint.get("Address", "—")
    storage = instance.get("AllocatedStorage", "?")
    klass = instance.get("DBInstanceClass", "?")
    print(f"  ID:        {instance['DBInstanceIdentifier']}")
    print(f"  Status:    {status}")
    print(f"  Class:     {klass}")
    print(f"  Storage:   {storage} GB")
    print(f"  Endpoint:  {host}")


def cmd_status(args) -> int:
    rds = _client(args.profile, args.region)
    instance = _describe(rds, args.instance)
    if instance is None:
        print(f"Instance {args.instance!r} not found in {args.region}.")
        return 1
    print("RDS instance:")
    _print_status(instance)
    return 0


def cmd_stop(args) -> int:
    rds = _client(args.profile, args.region)
    instance = _describe(rds, args.instance)
    if instance is None:
        print(f"Instance {args.instance!r} not found.")
        return 1

    status = instance["DBInstanceStatus"]
    if status in ("stopped", "stopping"):
        print(f"Instance is already {status}. No action.")
        return 0
    if status != "available":
        print(f"Cannot stop — current status is {status!r}.")
        return 1

    rds.stop_db_instance(DBInstanceIdentifier=args.instance)
    print(f"Stop requested for {args.instance}.")

    if args.wait:
        _wait_for_status(rds, args.instance, target="stopped", timeout_min=10)
    return 0


def cmd_start(args) -> int:
    rds = _client(args.profile, args.region)
    instance = _describe(rds, args.instance)
    if instance is None:
        print(f"Instance {args.instance!r} not found.")
        return 1

    status = instance["DBInstanceStatus"]
    if status in ("available", "starting"):
        print(f"Instance is already {status}. No action.")
        return 0
    if status != "stopped":
        print(f"Cannot start — current status is {status!r}.")
        return 1

    rds.start_db_instance(DBInstanceIdentifier=args.instance)
    print(f"Start requested for {args.instance}.")

    if args.wait:
        _wait_for_status(rds, args.instance, target="available", timeout_min=15)
    return 0


def _wait_for_status(rds, instance_id: str, target: str, timeout_min: int) -> None:
    """Poll until the instance reaches the target status or timeout."""
    deadline = time.time() + timeout_min * 60
    last_status = ""
    while time.time() < deadline:
        instance = _describe(rds, instance_id)
        if instance is None:
            print("Instance disappeared.")
            return
        status = instance["DBInstanceStatus"]
        if status != last_status:
            print(f"  status: {status}")
            last_status = status
        if status == target:
            print(f"Reached {target!r}.")
            return
        time.sleep(15)
    print(f"Timed out waiting for {target!r}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="RDS lifecycle manager")
    parser.add_argument(
        "--instance", default=DEFAULT_INSTANCE_ID,
        help=f"RDS instance ID (default: {DEFAULT_INSTANCE_ID})"
    )
    parser.add_argument(
        "--profile", default=DEFAULT_PROFILE,
        help=f"AWS CLI profile (default: {DEFAULT_PROFILE})"
    )
    parser.add_argument(
        "--region", default=DEFAULT_REGION,
        help=f"AWS region (default: {DEFAULT_REGION})"
    )
    parser.add_argument(
        "--wait", action="store_true",
        help="Wait for the operation to complete"
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show instance status")
    sub.add_parser("stop", help="Stop the instance")
    sub.add_parser("start", help="Start the instance")

    args = parser.parse_args()

    handlers = {
        "status": cmd_status,
        "stop": cmd_stop,
        "start": cmd_start,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
