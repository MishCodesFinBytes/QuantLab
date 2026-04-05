"""AWS Lambda handler for the spot curve bootstrapping endpoint.

API Gateway (REST API) passes the request as:

    {
        "httpMethod": "POST",
        "body": "{\"par_yields\": {\"1Y\": 4.80, ...}}"
    }

We parse the body, validate, call bootstrap_spot_curve, and return the
standard Lambda-proxy integration response shape. Validation errors map
to 400; unexpected failures (bad JSON, math blow-ups) to 500. Returning
a structured JSON error is what lets API Gateway hand the client
something useful without a stack trace.
"""

import json

from bootstrap import bootstrap_spot_curve


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body)
        par_yields = body.get("par_yields")

        if not isinstance(par_yields, dict) or not par_yields:
            return _response(400, {"error": "par_yields must be a non-empty object"})

        spot_curve = bootstrap_spot_curve(par_yields)
        return _response(200, {"spot_curve": spot_curve})

    except json.JSONDecodeError as exc:
        return _response(500, {"error": f"invalid JSON: {exc}"})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
