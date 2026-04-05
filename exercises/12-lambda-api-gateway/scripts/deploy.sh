#!/usr/bin/env bash
# Deploy the spot-curve bootstrapping Lambda + API Gateway.
#
# Idempotent-ish: create-function will fail if the function exists
# (use update-code.sh to re-deploy code to an existing function).
# API Gateway creation will error if "QuantLab Curves API" already
# exists — delete it first or run the update path below.
#
# Requires:
#   - AWS CLI profile `quant-lab` (or override via AWS_PROFILE)
#   - IAM role `quant-lab-lambda-role` with AWSLambdaBasicExecutionRole
#
# No secrets are baked in. Credentials come from the AWS profile.

set -euo pipefail

AWS_PROFILE="${AWS_PROFILE:-quant-lab}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="349348221529"
FUNCTION_NAME="quant-lab-bootstrap"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/quant-lab-lambda-role"
API_NAME="QuantLab Curves API"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/../src" && pwd)"
ZIP_PATH="$SRC_DIR/deployment.zip"

echo "==> Packaging Lambda deployment zip"
rm -f "$ZIP_PATH"
(cd "$SRC_DIR" && python -c "import zipfile; z=zipfile.ZipFile('deployment.zip','w',zipfile.ZIP_DEFLATED); z.write('bootstrap.py'); z.write('handler.py'); z.close()")

echo "==> Creating Lambda function $FUNCTION_NAME"
aws lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --zip-file "fileb://$ZIP_PATH" \
  --role "$ROLE_ARN" \
  --timeout 10 \
  --memory-size 128 \
  --profile "$AWS_PROFILE"

aws lambda wait function-active-v2 \
  --function-name "$FUNCTION_NAME" \
  --profile "$AWS_PROFILE"

echo "==> Creating API Gateway REST API"
API_ID=$(aws apigateway create-rest-api \
  --name "$API_NAME" \
  --description "Bond curve computation endpoints" \
  --endpoint-configuration types=REGIONAL \
  --profile "$AWS_PROFILE" \
  --query "id" --output text)
echo "    API_ID=$API_ID"

ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --profile "$AWS_PROFILE" --query "items[?path=='/'].id" --output text)

CURVES_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" --parent-id "$ROOT_ID" --path-part curves --profile "$AWS_PROFILE" --query "id" --output text)
BOOT_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" --parent-id "$CURVES_ID" --path-part bootstrap --profile "$AWS_PROFILE" --query "id" --output text)

echo "==> POST method + Lambda proxy integration"
aws apigateway put-method \
  --rest-api-id "$API_ID" \
  --resource-id "$BOOT_ID" \
  --http-method POST \
  --authorization-type NONE \
  --profile "$AWS_PROFILE" > /dev/null

aws apigateway put-integration \
  --rest-api-id "$API_ID" \
  --resource-id "$BOOT_ID" \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}/invocations" \
  --profile "$AWS_PROFILE" > /dev/null

echo "==> Granting API Gateway permission to invoke Lambda"
aws lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id apigw-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/POST/curves/bootstrap" \
  --profile "$AWS_PROFILE" > /dev/null

echo "==> Deploying to dev stage"
aws apigateway create-deployment \
  --rest-api-id "$API_ID" \
  --stage-name dev \
  --profile "$AWS_PROFILE" \
  --query "id" --output text

ENDPOINT="https://${API_ID}.execute-api.${REGION}.amazonaws.com/dev/curves/bootstrap"
echo ""
echo "Deployed. Endpoint:"
echo "  $ENDPOINT"
echo ""
echo "Test with:"
echo "  curl -X POST $ENDPOINT \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"par_yields\":{\"1Y\":4.80,\"2Y\":4.50,\"5Y\":4.20,\"10Y\":4.30}}'"
