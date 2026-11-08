#!/usr/bin/env bash
set -euo pipefail
REGION="${AWS_REGION:-us-east-1}"
STACK="${STACK_NAME:-seir-lab02-cobol}"
REPO="${ECR_REPO:-seir-lab02-cobol}"
echo "Deleting stack $STACK and ECR repository $REPO in $REGION."
read -r -p 'Type DELETE to continue: ' ANSWER
[[ "$ANSWER" == 'DELETE' ]] || exit 1
aws cloudformation delete-stack --region "$REGION" --stack-name "$STACK"
aws cloudformation wait stack-delete-complete --region "$REGION" --stack-name "$STACK"
aws ecr delete-repository --region "$REGION" --repository-name "$REPO" --force
printf 'Cleanup complete. Review billing dashboard for any resources created outside this lab.\n'
