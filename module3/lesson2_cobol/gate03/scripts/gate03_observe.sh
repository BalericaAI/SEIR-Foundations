#!/usr/bin/env bash
# Gate 03 Step 3 - observe ECS reconciliation after the controlled stop.
# Polls service counts and ALB target states into a CSV timeline, requires
# running=2 AND two healthy targets before declaring recovery, captures
# scheduler events, then runs the smoke suite against the ALB.
# Tune with POLL_INTERVAL (seconds, default 10) and MAX_POLLS (default 48).
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
POLL_INTERVAL="${POLL_INTERVAL:-10}"
MAX_POLLS="${MAX_POLLS:-48}"
export AWS_DEFAULT_REGION="$AWS_REGION"
for cmd in aws python3 curl; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done

get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET_GROUP="$(get_output TargetGroupArn)"
BASE="$(get_output AlbUrl)"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="evidence/gate03/observe-$STAMP"
mkdir -p "$EVIDENCE_DIR"
TIMELINE="$EVIDENCE_DIR/timeline.csv"
echo 'utc_timestamp,desired,running,pending,targets_total,targets_healthy,target_states' > "$TIMELINE"
echo "Polling up to $MAX_POLLS times every ${POLL_INTERVAL}s. Timeline: $TIMELINE"

RECOVERED=no
for ((i = 1; i <= MAX_POLLS; i++)); do
  aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
    --output json > "$EVIDENCE_DIR/service-poll.json"
  aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
    --output json > "$EVIDENCE_DIR/targets-poll.json"
  LINE="$(python3 - "$EVIDENCE_DIR" <<'PY'
import datetime, json, sys
d = sys.argv[1]
svc = json.load(open(f"{d}/service-poll.json"))["services"][0]
targets = json.load(open(f"{d}/targets-poll.json"))["TargetHealthDescriptions"]
states = "+".join(sorted(t["TargetHealth"]["State"] for t in targets)) or "none"
healthy = sum(1 for t in targets if t["TargetHealth"]["State"] == "healthy")
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print(f"{now},{svc['desiredCount']},{svc['runningCount']},{svc['pendingCount']},{len(targets)},{healthy},{states}")
PY
)"
  echo "$LINE" | tee -a "$TIMELINE"
  RUNNING="$(echo "$LINE" | cut -d, -f3)"
  PENDING="$(echo "$LINE" | cut -d, -f4)"
  HEALTHY="$(echo "$LINE" | cut -d, -f6)"
  if [[ "$RUNNING" == "2" && "$PENDING" == "0" && "$HEALTHY" == "2" ]]; then
    RECOVERED=yes
    break
  fi
  sleep "$POLL_INTERVAL"
done

aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].events[:25]' --output json > "$EVIDENCE_DIR/service-events.json"
if [[ "$RECOVERED" != "yes" ]]; then
  echo "NOT RECOVERED after $MAX_POLLS polls: still waiting for running=2 and two healthy targets." >&2
  echo "Inspect $EVIDENCE_DIR/service-events.json and ECS stopped-task reasons; rerun with larger MAX_POLLS if recovery is merely slow." >&2
  exit 1
fi
echo 'Counts recovered; waiting for ECS service stability (CLI waiter may take several minutes)...'
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"
echo 'Service stable. Running smoke tests against the ALB:'
BASE="$BASE" bash "$(dirname "$0")/smoke.sh"
echo "RECOVERY CONFIRMED. Evidence: $EVIDENCE_DIR"
echo "NEXT: export BASELINE_TASKS_FILE='evidence/gate03/baseline-.../task-arns.json' and run bash scripts/gate03_compare.sh"
