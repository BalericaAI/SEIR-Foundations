#!/usr/bin/env bash
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
get_output() {
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
CLUSTER="$(get_output ClusterName)"
SERVICE="$(get_output ServiceName)"
TARGET_GROUP="$(get_output TargetGroupArn)"
BASE="$(get_output AlbUrl)"
LOG_GROUP="$(get_output LogGroupName)"
echo "Stack: $STACK_NAME | Cluster: $CLUSTER | Service: $SERVICE"
aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].{status:status,desired:desiredCount,running:runningCount,pending:pendingCount,deployments:deployments[*].{status:status,rollout:rolloutState}}' --output json
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"
echo 'Target group health:'
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
  --query 'TargetHealthDescriptions[*].{target:Target.Id,status:TargetHealth.State,reason:TargetHealth.Reason}' --output table
python3 - "$CLUSTER" "$SERVICE" "$TARGET_GROUP" <<'PY'
import json,subprocess,sys
cluster,service,tg=sys.argv[1:]
def aws(*args):
 return json.loads(subprocess.check_output(['aws',*args,'--output','json'],text=True))
s=aws('ecs','describe-services','--cluster',cluster,'--services',service)['services'][0]
t=aws('elbv2','describe-target-health','--target-group-arn',tg)['TargetHealthDescriptions']
if s['desiredCount']!=2 or s['runningCount']!=2 or len(t)!=2 or any(x['TargetHealth']['State']!='healthy' for x in t):
 raise SystemExit('FAIL: require desired=2, running=2, and two healthy targets')
print('PASS: desired=2, running=2, 2 healthy IP targets')
PY
BASE="$BASE" bash "$(dirname "$0")/smoke.sh"
echo 'Running task network placement:'
TASKS="$(aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" --desired-status RUNNING --query 'taskArns' --output text)"
if [[ -n "$TASKS" ]]; then
  # TASKS from --output text is tab-separated, split intentionally.
  read -r -a TASK_ARNS <<< "$TASKS"
  aws ecs describe-tasks --cluster "$CLUSTER" --tasks "${TASK_ARNS[@]}" \
    --query 'tasks[*].{task:taskArn,subnet:attachments[0].details[?name==`subnetId`].value|[0],status:lastStatus}' --output table
fi
echo "CloudWatch log group: $LOG_GROUP"
echo 'Collect screenshots for ECS service, healthy targets, task placement, ECR image and logs.'
