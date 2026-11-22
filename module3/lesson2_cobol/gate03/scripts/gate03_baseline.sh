#!/usr/bin/env bash
# Gate 03 Step 1 - capture a read-only baseline of the Gate 02 deployment.
# Writes timestamped JSON evidence and FAILS unless the service is at a
# known-good state: desired=2, running=2, pending=0, two healthy ALB targets.
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
for cmd in aws python3; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done

get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET_GROUP="$(get_output TargetGroupArn)"
[[ "$CLUSTER" != "None" && -n "$CLUSTER" ]] || { echo "Stack $STACK_NAME has no ClusterName output. Is Gate 02 deployed in this account/region?" >&2; exit 2; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="evidence/gate03/baseline-$STAMP"
mkdir -p "$EVIDENCE_DIR"
echo "Baseline evidence directory: $EVIDENCE_DIR (read-only AWS calls)"

aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --output json > "$EVIDENCE_DIR/service.json"
aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
  --desired-status RUNNING --output json > "$EVIDENCE_DIR/task-arns.json"
TASKS="$(aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
  --desired-status RUNNING --query 'taskArns' --output text)"
if [[ -n "$TASKS" && "$TASKS" != "None" ]]; then
  # --output text is tab-separated; split intentionally.
  read -r -a TASK_ARNS <<< "$TASKS"
  aws ecs describe-tasks --cluster "$CLUSTER" --tasks "${TASK_ARNS[@]}" \
    --output json > "$EVIDENCE_DIR/tasks.json"
fi
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
  --output json > "$EVIDENCE_DIR/target-health.json"
aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].events[:25]' --output json > "$EVIDENCE_DIR/service-events.json"

python3 - "$EVIDENCE_DIR" <<'PY'
import json, sys
d = sys.argv[1]
svc = json.load(open(f"{d}/service.json"))["services"][0]
arns = json.load(open(f"{d}/task-arns.json"))["taskArns"]
targets = json.load(open(f"{d}/target-health.json"))["TargetHealthDescriptions"]
healthy = [t for t in targets if t["TargetHealth"]["State"] == "healthy"]
print(f"desired={svc['desiredCount']} running={svc['runningCount']} pending={svc['pendingCount']}")
print(f"ALB targets: {len(targets)} total, {len(healthy)} healthy")
for arn in arns:
    print(f"RUNNING task: ...{arn.split('/')[-1][-12:]}  ({arn})")
ok = (svc["desiredCount"] == 2 and svc["runningCount"] == 2
      and svc["pendingCount"] == 0 and len(arns) == 2 and len(healthy) == 2)
if not ok:
    raise SystemExit("BASELINE FAIL: require desired=2, running=2, pending=0, two RUNNING tasks and two healthy ALB targets. Do NOT stop any task; investigate first.")
print("BASELINE PASS")
PY
echo "Keep this directory. gate03_compare.sh needs: export BASELINE_TASKS_FILE='$EVIDENCE_DIR/task-arns.json'"
