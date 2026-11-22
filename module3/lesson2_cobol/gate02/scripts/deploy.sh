#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-seir-lab02-cobol}"
ECR_REPO="${ECR_REPO:-seir-lab02-cobol}"
export AWS_DEFAULT_REGION="$AWS_REGION"

if [[ "${GATE01_VALIDATED:-}" != "yes" ]]; then
  echo 'STOP: Validate Gate 01 local integration, then set GATE01_VALIDATED=yes' >&2; exit 2
fi
if [[ "${ACK_COSTS:-}" != "yes" ]]; then
  echo 'STOP: NAT Gateway, ALB, Fargate, EIP and logs incur charges. Set ACK_COSTS=yes only after review.' >&2; exit 2
fi
for cmd in aws docker python3 curl; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done
[[ -n "${ALLOWED_CIDR:-}" ]] || { echo 'Set ALLOWED_CIDR to your public IPv4 /32' >&2; exit 2; }
python3 - "$ALLOWED_CIDR" <<'PY'
import ipaddress,sys
try:
    network=ipaddress.ip_network(sys.argv[1],strict=True)
    assert isinstance(network,ipaddress.IPv4Network) and network.prefixlen==32 and network.network_address.is_global
except (ValueError,AssertionError):
    raise SystemExit('ALLOWED_CIDR must be a valid global public IPv4 /32, e.g. 203.0.113.1/32 is documentation-only and NOT valid')
PY
aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output json
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="$ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"
if ! aws ecr describe-repositories --repository-names "$ECR_REPO" >/dev/null 2>&1; then
  aws ecr create-repository --repository-name "$ECR_REPO" --image-tag-mutability IMMUTABLE \
    --image-scanning-configuration scanOnPush=true >/dev/null
  echo 'Created dedicated immutable lab repository.'
else
  echo "Using existing ECR repo: $ECR_REPO; cleanup can DELETE it. Make sure it is lab-only."
fi
aws ecr get-login-password | docker login --username AWS --password-stdin "$ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com"
TAG="gate02-$(date -u +%Y%m%dT%H%M%SZ)"
docker build --platform linux/amd64 -t "$ECR_URI:$TAG" .
docker push "$ECR_URI:$TAG"
# Deploy by digest, so running tasks use exactly the image tested/uploaded.
DIGEST="$(aws ecr describe-images --repository-name "$ECR_REPO" --image-ids imageTag="$TAG" --query 'imageDetails[0].imageDigest' --output text)"
[[ "$DIGEST" == sha256:* ]] || { echo 'Could not determine ECR image digest' >&2; exit 1; }
IMAGE_URI="$ECR_URI@$DIGEST"
echo "Deploying image: $IMAGE_URI"
aws cloudformation deploy --stack-name "$STACK_NAME" --template-file infra/lab02.yaml \
  --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset \
  --parameter-overrides "ImageUri=$IMAGE_URI" "AllowedCidr=$ALLOWED_CIDR" \
  --tags Project=SEIR-Module3 Lab=Lab02-Gate02
aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs' --output table
cat <<MSG
Deployment requested. Do not assume stack success implies healthy containers.
NEXT: bash scripts/verify.sh
CLEANUP: ACK_DELETE=yes bash scripts/cleanup.sh
ECR REPOSITORY: $ECR_REPO (cleanup deletes the entire repository)
MSG
