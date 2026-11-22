#!/usr/bin/env bash
# Gate 03 Step 4 - collect post-recovery diagnostics (all read-only):
# service details, target health, running and recently stopped task metadata,
# scheduler events, and CloudWatch log stream metadata.
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
command -v aws >/dev/null || { echo 'Missing: aws' >&2; exit 2; }

get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET_GROUP="$(get_output TargetGroupArn)"
LOG_GROUP="$(get_output LogGroupName)"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="evidence/gate03/collect-$STAMP"
mkdir -p "$EVIDENCE_DIR"

aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --output json > "$EVIDENCE_DIR/service.json"
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
  --output json > "$EVIDENCE_DIR/target-health.json"
aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].events[:50]' --output json > "$EVIDENCE_DIR/service-events.json"

collect_tasks() {
  local status="$1" outfile="$2" arns
  arns="$(aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
    --desired-status "$status" --query 'taskArns' --output text)"
  if [[ -n "$arns" && "$arns" != "None" ]]; then
    # --output text is tab-separated; split intentionally.
    read -r -a ARR <<< "$arns"
    aws ecs describe-tasks --cluster "$CLUSTER" --tasks "${ARR[@]}" \
      --output json > "$outfile"
  else
    echo '{"tasks": [], "note": "ECS keeps stopped tasks visible only briefly; rely on service events and your observe-phase evidence if empty."}' > "$outfile"
  fi
}
collect_tasks RUNNING "$EVIDENCE_DIR/running-tasks.json"
collect_tasks STOPPED "$EVIDENCE_DIR/stopped-tasks.json"

aws logs describe-log-streams --log-group-name "$LOG_GROUP" \
  --order-by LastEventTime --descending --max-items 10 \
  --output json > "$EVIDENCE_DIR/log-streams.json"

echo "Diagnostics saved to $EVIDENCE_DIR"
echo "Read application logs with:"
echo "  aws logs tail \"$LOG_GROUP\" --since 30m --region \"$AWS_REGION\""
