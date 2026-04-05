#!/usr/bin/env bash
# Re-deploy handler code to the existing Lambda function.
# Use this after editing bootstrap.py or handler.py.

set -euo pipefail

AWS_PROFILE="${AWS_PROFILE:-quant-lab}"
FUNCTION_NAME="quant-lab-bootstrap"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/../src" && pwd)"
ZIP_PATH="$SRC_DIR/deployment.zip"

rm -f "$ZIP_PATH"
(cd "$SRC_DIR" && python -c "import zipfile; z=zipfile.ZipFile('deployment.zip','w',zipfile.ZIP_DEFLATED); z.write('bootstrap.py'); z.write('handler.py'); z.close()")

aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file "fileb://$ZIP_PATH" \
  --profile "$AWS_PROFILE" \
  --query "[FunctionName,LastUpdateStatus]" --output table
