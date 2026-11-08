#!/usr/bin/env bash
set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
STACK="${STACK_NAME:-seir-lab02-cobol}"
OUT="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" --output json)"
get_output() { printf '%s' "$OUT" | python3 -c 'import json,sys; x=json.load(sys.stdin)["Stacks"][0]["Outputs"];print(next(v["OutputValue"] for v in x if v["OutputKey"]==sys.argv[1]))' "$1"; }
ENDPOINT="$(get_output Endpoint)"
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET="$(get_output TargetGroupArn)"
echo "Service: $CLUSTER / $SERVICE"
aws ecs describe-services --region "$REGION" --cluster "$CLUSTER" --services "$SERVICE" --query 'services[0].[desiredCount,runningCount,pendingCount]' --output table
aws elbv2 describe-target-health --region "$REGION" --target-group-arn "$TARGET" --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State,TargetHealth.Reason]' --output table
echo "Endpoint: $ENDPOINT"
curl --fail --show-error --silent "$ENDPOINT/ready"; echo
curl --fail --show-error --silent -H 'Content-Type: application/json' -d '{"principal":"1000.00","annual_rate_percent":"5.00","years":2}' "$ENDPOINT/v1/interest"; echo
curl --fail --show-error --silent -H 'Content-Type: application/json' -d '{"principal":"1200.00","annual_rate_percent":"0","months":12}' "$ENDPOINT/v1/loan-payment"; echo
curl --fail --show-error --silent -H 'Content-Type: application/json' -d '{"amount":"250.00","available_balance":"500.00"}' "$ENDPOINT/v1/transfer/validate"; echo
for i in {1..12}; do curl --fail --show-error --silent "$ENDPOINT/v1/info"; echo; done
