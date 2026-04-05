import json

from handler import lambda_handler


def _event(body: dict | str | None) -> dict:
    if body is None:
        return {"httpMethod": "POST"}
    return {"httpMethod": "POST", "body": body if isinstance(body, str) else json.dumps(body)}


class TestLambdaHandler:
    def test_happy_path(self):
        event = _event({"par_yields": {"1Y": 5.0, "2Y": 5.5}})
        response = lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert response["headers"]["Content-Type"] == "application/json"
        body = json.loads(response["body"])
        assert "spot_curve" in body
        assert body["spot_curve"]["1Y"] == 5.0
        assert body["spot_curve"]["2Y"] > 5.5

    def test_missing_par_yields_returns_400(self):
        response = lambda_handler(_event({}), None)
        assert response["statusCode"] == 400
        assert "par_yields" in json.loads(response["body"])["error"]

    def test_par_yields_not_a_dict_returns_400(self):
        response = lambda_handler(_event({"par_yields": [1, 2, 3]}), None)
        assert response["statusCode"] == 400

    def test_empty_body_returns_400(self):
        response = lambda_handler({"httpMethod": "POST"}, None)
        assert response["statusCode"] == 400

    def test_malformed_json_returns_500(self):
        response = lambda_handler(_event("{not json"), None)
        assert response["statusCode"] == 500
        assert "error" in json.loads(response["body"])

    def test_empty_par_yields_returns_400(self):
        """An empty par_yields dict is unusable — reject it."""
        response = lambda_handler(_event({"par_yields": {}}), None)
        assert response["statusCode"] == 400
