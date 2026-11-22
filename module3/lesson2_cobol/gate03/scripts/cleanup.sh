#!/usr/bin/env bash
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
ECR_REPO="${ECR_REPO:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"
[[ "${ACK_DELETE:-}" == "yes" ]] || { echo 'STOP: cleanup deletes the stack and ENTIRE ECR_REPO. Set ACK_DELETE=yes after confirming names.' >&2; exit 2; }
echo "DELETE stack=$STACK_NAME region=$AWS_REGION repo=$ECR_REPO"
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" >/dev/null 2>&1; then
  aws cloudformation delete-stack --stack-name "$STACK_NAME"
  aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"
fi
if aws ecr describe-repositories --repository-names "$ECR_REPO" >/dev/null 2>&1; then
  aws ecr delete-repository --repository-name "$ECR_REPO" --force >/dev/null
fi
echo 'Deleted lab stack and dedicated ECR repository. Confirm in AWS Console and billing dashboard.'
