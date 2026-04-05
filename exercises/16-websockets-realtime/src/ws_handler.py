"""WebSocket connection management for real-time spread monitoring.

Architecture: API Gateway WebSocket API handles the WS protocol and routes
events ($connect, $disconnect, $default) to Lambda. Connection state lives
in DynamoDB (serverless-friendly — no sticky sessions to manage). To push
a message out to a client, Lambda calls the API Gateway Management API's
``post_to_connection`` with the client's connectionId.

Why DynamoDB rather than in-memory: Lambda executions are ephemeral and
may be served by different containers, so there's nowhere inside the
Lambda runtime to durably hold "who's connected". DynamoDB gives you a
shared, low-latency, pay-per-request store that survives cold starts.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import boto3

TABLE_NAME = "ws-connections"


def handle_connect(connection_id: str, table=None) -> dict:
    """Store a new WebSocket connection."""
    tbl = table or _get_table()
    tbl.put_item(
        Item={
            "connectionId": connection_id,
            "connectedAt": datetime.now(UTC).isoformat(),
            "subscriptions": [],
        }
    )
    return {"statusCode": 200}


def handle_disconnect(connection_id: str, table=None) -> dict:
    """Remove a WebSocket connection."""
    tbl = table or _get_table()
    tbl.delete_item(Key={"connectionId": connection_id})
    return {"statusCode": 200}


def handle_message(connection_id: str, message: dict, table=None) -> dict:
    """Handle incoming WebSocket message from a client."""
    tbl = table or _get_table()
    action = message.get("action")

    if action == "subscribe":
        rating = message.get("rating", "")
        tbl.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression=(
                "SET subscriptions = list_append("
                "if_not_exists(subscriptions, :empty), :rating)"
            ),
            ExpressionAttributeValues={":rating": [rating], ":empty": []},
        )
        return {"subscribed": rating}

    return {"error": f"Unknown action: {action}"}


def get_connected_clients(table=None) -> list[str]:
    """Return all currently connected client IDs."""
    tbl = table or _get_table()
    response = tbl.scan(ProjectionExpression="connectionId")
    return [item["connectionId"] for item in response.get("Items", [])]


def broadcast_spread_update(
    spread_data: dict,
    api_url: str,
    table=None,
) -> int:
    """Broadcast a spread update to all connected clients.

    Stale connections (GoneException) are pruned from the table automatically.

    Args:
        spread_data: Dict with spread info to send.
        api_url: API Gateway Management API endpoint URL.
        table: DynamoDB table (optional, for testing).

    Returns:
        Number of clients successfully notified.
    """
    clients = get_connected_clients(table)
    apigw = boto3.client("apigatewaymanagementapi", endpoint_url=api_url)
    sent = 0

    for conn_id in clients:
        try:
            apigw.post_to_connection(
                ConnectionId=conn_id,
                Data=json.dumps(spread_data).encode(),
            )
            sent += 1
        except Exception:
            handle_disconnect(conn_id, table)

    return sent


def _get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(TABLE_NAME)


# --- Lambda entry points for API Gateway WebSocket routes ---


def lambda_connect(event, context):
    connection_id = event["requestContext"]["connectionId"]
    return handle_connect(connection_id)


def lambda_disconnect(event, context):
    connection_id = event["requestContext"]["connectionId"]
    return handle_disconnect(connection_id)


def lambda_default(event, context):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body", "{}"))
    result = handle_message(connection_id, body)
    return {"statusCode": 200, "body": json.dumps(result)}
