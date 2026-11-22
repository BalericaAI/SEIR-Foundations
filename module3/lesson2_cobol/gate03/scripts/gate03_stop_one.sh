#!/usr/bin/env bash
# Gate 03 Step 2 - stop exactly ONE running task of this service, once.
# Refuses to act without TASK_ARN and ACK_STOP_TASK=yes, if the selected
# task is not a RUNNING member of this service, or if the live state is not
# the healthy 2/2 baseline.
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
for cmd in aws python3; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done

[[ "${ACK_STOP_TASK:-}" == "yes" ]] || { echo 'STOP: This intentionally disrupts a running task. Set ACK_STOP_TASK=yes only with instructor approval.' >&2; exit 2; }
[[ -n "${TASK_ARN:-}" ]] || { echo 'STOP: Set TASK_ARN to one FULL task ARN from your PASS baseline (see evidence/gate03/baseline-*/task-arns.json).' >&2; exit 2; }
[[ "$TASK_ARN" == arn:aws:ecs:*:task/* ]] || { echo "STOP: '$TASK_ARN' is not a full ECS task ARN (arn:aws:ecs:REGION:ACCOUNT:task/CLUSTER/ID)." >&2; exit 2; }

get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET_GROUP="$(get_output TargetGroupArn)"

# Re-verify live health immediately before disrupting anything, and confirm
# the selected ARN belongs to THIS service in THIS cluster.
aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
  --desired-status RUNNING --output json > /tmp/gate03-current-tasks.json
aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --output json > /tmp/gate03-current-service.json
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
  --output json > /tmp/gate03-current-targets.json
python3 - "$TASK_ARN" <<'PY'
import json, sys
task_arn = sys.argv[1]
arns = json.load(open("/tmp/gate03-current-tasks.json"))["taskArns"]
svc = json.load(open("/tmp/gate03-current-service.json"))["services"][0]
targets = json.load(open("/tmp/gate03-current-targets.json"))["TargetHealthDescriptions"]
healthy = [t for t in targets if t["TargetHealth"]["State"] == "healthy"]
if task_arn not in arns:
    raise SystemExit(f"STOP: {task_arn} is not a RUNNING task of this ECS service. Never paste an ARN from another account, cluster or environment.")
if not (svc["desiredCount"] == 2 and svc["runningCount"] == 2 and len(healthy) == 2):
    raise SystemExit("STOP: live state is not the healthy baseline (desired=2, running=2, two healthy targets). Investigate before injecting failure.")
print("Pre-stop checks passed.")
PY

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="evidence/gate03"
mkdir -p "$EVIDENCE_DIR"
echo "Stopping ONE task: $TASK_ARN"
aws ecs stop-task --cluster "$CLUSTER" --task "$TASK_ARN" \
  --reason "SEIR Gate03 controlled desired-state recovery exercise" \
  --output json > "$EVIDENCE_DIR/stop-$STAMP.json"
echo "stop-task issued once; response saved to $EVIDENCE_DIR/stop-$STAMP.json"
echo "Do NOT stop another task. NEXT: bash scripts/gate03_observe.sh"
