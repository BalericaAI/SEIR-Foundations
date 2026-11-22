#!/usr/bin/env bash
# Gate 03 Step 3 (continued) - prove the scheduler replaced the stopped task.
# Compares the baseline task ARNs with the current RUNNING task ARNs and
# requires EXACTLY one changed ARN and one unchanged ARN.
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
for cmd in aws python3; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done

[[ -n "${BASELINE_TASKS_FILE:-}" ]] || { echo "STOP: export BASELINE_TASKS_FILE='evidence/gate03/baseline-YYYYMMDDTHHMMSSZ/task-arns.json' (your actual baseline directory)." >&2; exit 2; }
[[ -f "$BASELINE_TASKS_FILE" ]] || { echo "STOP: $BASELINE_TASKS_FILE does not exist. Use the task-arns.json from YOUR baseline evidence directory." >&2; exit 2; }

get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
  --desired-status RUNNING --output json > /tmp/gate03-compare-current.json

python3 - "$BASELINE_TASKS_FILE" <<'PY'
import json, sys
before = set(json.load(open(sys.argv[1]))["taskArns"])
after = set(json.load(open("/tmp/gate03-compare-current.json"))["taskArns"])
retained = sorted(before & after)
replaced = sorted(before - after)
new = sorted(after - before)
suffix = lambda a: "..." + a.split("/")[-1][-12:]
for arn in retained:
    print(f"RETAINED : {suffix(arn)}  ({arn})")
for arn in replaced:
    print(f"STOPPED  : {suffix(arn)}  ({arn})")
for arn in new:
    print(f"NEW      : {suffix(arn)}  ({arn})")
if not (len(before) == 2 and len(after) == 2 and len(retained) == 1 and len(replaced) == 1 and len(new) == 1):
    raise SystemExit("FAIL: expected exactly one replaced task ARN and one retained ARN (2 before, 2 after). If both changed, something else disturbed the service; investigate the ECS events before grading.")
print("PASS: exactly one task was replaced and one survived.")
PY
