#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:=us-east-1}"
export AWS_REGION
command -v aws >/dev/null || { echo 'AWS CLI missing' >&2; exit 1; }
command -v docker >/dev/null || { echo 'Docker missing' >&2; exit 1; }
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REPO=seir-cobol-finance
CLUSTER=seir-module3
FAMILY=seir-cobol-batch
LOGGROUP=/ecs/seir-cobol-batch
ROLE=seir-ecs-task-execution-lab
REGISTRY="${ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE="${REGISTRY}/${REPO}:lab1"
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text --region "$AWS_REGION")
if [[ -z "$VPC" || "$VPC" == None ]]; then echo 'Default VPC not found. Use a dedicated lab VPC, or create a default VPC only if your lab policy permits.' >&2; exit 1; fi
SUBNET=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC}" --query 'Subnets[0].SubnetId' --output text --region "$AWS_REGION")
if [[ -z "$SUBNET" || "$SUBNET" == None ]]; then echo 'No subnet found' >&2; exit 1; fi
SG=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=${VPC}" Name=group-name,Values=seir-cobol-no-ingress --query 'SecurityGroups[0].GroupId' --output text --region "$AWS_REGION")
if [[ "$SG" == None ]]; then SG=$(aws ec2 create-security-group --group-name seir-cobol-no-ingress --description 'SEIR COBOL lab outbound only' --vpc-id "$VPC" --query GroupId --output text --region "$AWS_REGION"); fi
if ! aws iam get-role --role-name "$ROLE" >/dev/null 2>&1; then
  cat > /tmp/seir-ecs-trust.json <<'JSON'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
JSON
  aws iam create-role --role-name "$ROLE" --assume-role-policy-document file:///tmp/seir-ecs-trust.json >/dev/null
  aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
  echo 'IAM role created; allowing IAM propagation.'
  sleep 15
fi
aws ecr describe-repositories --repository-names "$REPO" --region "$AWS_REGION" >/dev/null 2>&1 || aws ecr create-repository --repository-name "$REPO" --image-scanning-configuration scanOnPush=true --region "$AWS_REGION" >/dev/null
aws ecs describe-clusters --clusters "$CLUSTER" --query 'clusters[0].status' --output text --region "$AWS_REGION" | grep -qx ACTIVE || aws ecs create-cluster --cluster-name "$CLUSTER" --region "$AWS_REGION" >/dev/null
aws logs create-log-group --log-group-name "$LOGGROUP" --region "$AWS_REGION" 2>/dev/null || true
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
docker build --platform linux/amd64 -t "${REPO}:lab1" .
docker tag "${REPO}:lab1" "$IMAGE"
docker push "$IMAGE"
cat > task-definition.json <<JSON
{"family":"${FAMILY}","requiresCompatibilities":["FARGATE"],"networkMode":"awsvpc","cpu":"256","memory":"512","executionRoleArn":"arn:aws:iam::${ACCOUNT}:role/${ROLE}","runtimePlatform":{"cpuArchitecture":"X86_64","operatingSystemFamily":"LINUX"},"containerDefinitions":[{"name":"cobol","image":"${IMAGE}","essential":true,"readonlyRootFilesystem":true,"logConfiguration":{"logDriver":"awslogs","options":{"awslogs-group":"${LOGGROUP}","awslogs-region":"${AWS_REGION}","awslogs-stream-prefix":"ecs"}}}]}
JSON
aws ecs register-task-definition --cli-input-json file://task-definition.json --region "$AWS_REGION" >/dev/null
TASK=$(aws ecs run-task --cluster "$CLUSTER" --launch-type FARGATE --task-definition "$FAMILY" --count 1 --network-configuration "awsvpcConfiguration={subnets=[${SUBNET}],securityGroups=[${SG}],assignPublicIp=ENABLED}" --query 'tasks[0].taskArn' --output text --region "$AWS_REGION")
if [[ "$TASK" == None || -z "$TASK" ]]; then echo 'Task launch failed; check ECS run-task output' >&2; exit 1; fi
printf 'Task: %s\n' "$TASK"
aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$TASK" --region "$AWS_REGION"
EXIT=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$TASK" --query 'tasks[0].containers[0].exitCode' --output text --region "$AWS_REGION")
REASON=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$TASK" --query 'tasks[0].stoppedReason' --output text --region "$AWS_REGION")
echo "Exit code: $EXIT; stopped reason: $REASON"
aws logs tail "$LOGGROUP" --since 20m --region "$AWS_REGION" || true
[[ "$EXIT" == 0 ]] || exit 1
