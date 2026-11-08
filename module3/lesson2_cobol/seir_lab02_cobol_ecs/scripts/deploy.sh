#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGION="${AWS_REGION:-us-east-1}"
STACK="${STACK_NAME:-seir-lab02-cobol}"
REPO="${ECR_REPO:-seir-lab02-cobol}"
: "${ALLOWED_CIDR:?Set ALLOWED_CIDR to your public IP/32, e.g. 203.0.113.42/32}"
if [[ "$ALLOWED_CIDR" == '0.0.0.0/0' ]]; then echo 'Refusing unrestricted ALB CIDR' >&2; exit 1; fi
for cmd in aws docker; do command -v "$cmd" >/dev/null || { echo "Missing $cmd" >&2; exit 1; }; done
aws sts get-caller-identity --region "$REGION" >/dev/null
ACCOUNT="$(aws sts get-caller-identity --query Account --output text --region "$REGION")"
ECR_URI="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO}"
TAG="$(date -u +%Y%m%d%H%M%S)"
IMAGE="${ECR_URI}:${TAG}"
if ! aws ecr describe-repositories --region "$REGION" --repository-names "$REPO" >/dev/null 2>&1; then
  aws ecr create-repository --region "$REGION" --repository-name "$REPO" --image-scanning-configuration scanOnPush=true >/dev/null
fi
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
docker build --platform linux/amd64 -t "$IMAGE" "$ROOT"
docker push "$IMAGE"
echo "Deploying CloudFormation stack $STACK (NAT Gateway, ALB, 2 Fargate tasks incur charges)."
aws cloudformation deploy --region "$REGION" --stack-name "$STACK" \
  --template-file "$ROOT/infra/lab02.yaml" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides "ImageUri=$IMAGE" "AllowedCidr=$ALLOWED_CIDR" \
  --no-fail-on-empty-changeset
aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table
echo 'Wait for both ECS tasks and ALB targets to become healthy, then run scripts/verify.sh.'
