import boto3
import pytest
from moto import mock_aws

from ws_handler import (
    get_connected_clients,
    handle_connect,
    handle_disconnect,
    handle_message,
)

TABLE_NAME = "ws-connections"


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


class TestConnectionManagement:
    def test_connect_stores_connection(self, dynamodb_table):
        handle_connect("conn-123", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert "conn-123" in clients

    def test_disconnect_removes_connection(self, dynamodb_table):
        handle_connect("conn-456", table=dynamodb_table)
        handle_disconnect("conn-456", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert "conn-456" not in clients

    def test_multiple_connections(self, dynamodb_table):
        handle_connect("conn-1", table=dynamodb_table)
        handle_connect("conn-2", table=dynamodb_table)
        handle_connect("conn-3", table=dynamodb_table)
        clients = get_connected_clients(table=dynamodb_table)
        assert len(clients) == 3


class TestMessageHandling:
    def test_subscribe_to_rating(self, dynamodb_table):
        handle_connect("conn-789", table=dynamodb_table)
        result = handle_message(
            "conn-789",
            {"action": "subscribe", "rating": "BBB"},
            table=dynamodb_table,
        )
        assert result["subscribed"] == "BBB"
