# SEIR Foundations — Module 3 — Lab 02 — Gate 02

> Prefer a single start-to-finish checklist with exact commands and expected outputs? Follow [`runbook.md`](runbook.md) — it is fully self-contained.

## Deploy the validated COBOL + FastAPI service to AWS ECS Fargate

**Jira:** M3-1 (tracking Epic; this package is *not* automatically synced to Jira).

**Gate progression:** Gate 01 = local FastAPI/GnuCOBOL implementation and tests; **Gate 02 = ECR + infrastructure + private ECS Fargate service + ALB + verification**; Gate 03 = deliberate failure and recovery.

> **Instructor caution:** This package is prepared for deployment, not deployed or verified in your AWS account. Do not set `GATE01_VALIDATED=yes` until the Gate 01 local Docker integration actually passes. No real banking data, customer information, or live transfers.

## Architecture

```text
Public IPv4 /32 student workstation
          |
    HTTP port 80  [WARNING: no TLS]
          |
Internet-facing ALB (public subnet A + B)
    ALB SG: inbound TCP 80 ONLY from student's public /32
          |
    ALB target group (type ip; /ready == 200)
          |
  +-------+---------------------------+
  |                                   |
Private subnet A / AZ1       Private subnet B / AZ2
Fargate task A              Fargate task B
FastAPI :8080 -> GnuCOBOL   FastAPI :8080 -> GnuCOBOL
  |                                   |
  +---------- CloudWatch Logs --------+

ECR image via one shared NAT Gateway in public subnet A
Execution IAM role: AmazonECSTaskExecutionRolePolicy
```

This is an **instructional** two-AZ application deployment, not a fully AZ-resilient egress design: its single NAT gateway is an availability and cost tradeoff. ALB has no HTTPS, WAF, or user authentication in this gate; it accepts synthetic examples only. Do not use for production. VPCs, subnets, route tables, IGW, EIP, NAT, security groups, ALB, target group, IAM, cluster, service, and logs are all owned by the CloudFormation stack.

### What students must understand

1. Why the ALB is internet-facing while Fargate tasks have `AssignPublicIp: DISABLED`.
2. The difference between a task definition, a running task, and a long-running ECS service.
3. Why `TargetType: ip` is required for Fargate `awsvpc` networking.
4. Why ALB `/ready` measures the COBOL dependency rather than FastAPI process uptime.
5. Why private tasks need outbound networking to fetch ECR images and write CloudWatch logs.
6. Why image digest pinning, deployment circuit breaker, and desired count matter.
7. Why paying for a NAT gateway and ALB continues even if no clients issue requests.

## Prerequisites

- Gate 01 **actually validated** with a local Docker build, direct COBOL execution, the six API endpoints, and the broken-COBOL readiness test.
- AWS CLI v2, Docker Linux mode, Python 3, Bash, curl, outbound internet, and permission to create CloudFormation, EC2/VPC resources, ECR, ECS, IAM roles / `iam:PassRole`, ALB, and CloudWatch Logs. A sanctioned lab account is strongly preferred.
- AWS account quota for two AZs, two Fargate tasks, one internet-facing ALB, one NAT gateway, and an Elastic IP.
- The student's current externally visible PUBLIC IPv4 (not a private IPv4), formatted as `/32`.
- Sufficient budget for **NAT gateway, ALB, Fargate tasks, EIP/public IPv4, ECR, and logs**. AWS pricing varies by region; don't leave this running overnight.

**Deployment risk:** The lab ALB is **HTTP-only** (no encryption) and CIDR-restricted, suitable only for synthetic learning data. Gate 03/security follow-ups may add ACM/HTTPS, WAF, and authentication.

## Step 1 — Local smoke test

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
# Or use your existing Gate 01 validation evidence.
docker build --platform linux/amd64 -t seir-cobol-lab02:gate02-local .
docker run --rm --platform linux/amd64 -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate02-local
# Second terminal:
BASE=http://127.0.0.1:8080 bash scripts/smoke.sh
```

Stop the local container after testing. Gate 01 may still be in the instructor's validation process; do not skip these checks.

## Step 2 — Set AWS context / explicit acknowledgements

```bash
export AWS_REGION=us-east-1  # Example only: choose your assigned region
export STACK_NAME=seir-lab02-cobol
export ECR_REPO=seir-lab02-cobol
export ALLOWED_CIDR='YOUR_REAL_PUBLIC_IPV4/32'
export GATE01_VALIDATED=yes   # ONLY after your real local integration validation
export ACK_COSTS=yes         # ONLY after reviewing the billable resources
aws sts get-caller-identity
```

The deploy script rejects an unacknowledged Gate 01, missing cost acknowledgement, or an invalid/non-public/non-/32 allowlist. Never use `0.0.0.0/0`.

## Step 3 — Deploy

```bash
bash scripts/deploy.sh
```

The script:

1. Verifies AWS identity, prerequisites, public source IPv4, and explicit acknowledgements.
2. Creates a **dedicated immutable-tag ECR repository** if missing (otherwise reuses one with that name — ensure it is lab-only).
3. Builds a `linux/amd64` image and uploads it under a unique timestamp tag.
4. Resolves its immutable digest, then deploys `infra/lab02.yaml` with `ImageUri=repo@sha256:...`.
5. Creates all network resources and a two-task ECS service in private subnets.
6. Outputs the ALB URL and AWS resource identifiers.

**Do not assume `CREATE_COMPLETE` means all targets are healthy.** Validate them separately.

## Step 4 — Verify AWS deployment

```bash
bash scripts/verify.sh
```

Pass requirements: ECS desired `2`, running `2`, two healthy ALB IP targets, and working HTTP requests from your *allowed public IPv4*. The script then calls the existing six-endpoint smoke suite, and lists running tasks/subnets.

**If an ALB call times out:** Check your public IP, VPN egress, ALB security group, internet gateway route, load balancer DNS and target health. Wait for DNS and health checks to converge; do not broaden access to `0.0.0.0/0`.

**If targets are unhealthy:** Follow CloudFormation Events, ECS service Events, stopped-task reasons, the task ENIs, target-group health reasons, ECR image digest, and CloudWatch logs. `/health=200` but `/ready=503` means FastAPI is running but COBOL execution is broken.

## Step 5 — Student evidence

- AWS STS caller identity: show account/ARN, redact sensitive data as appropriate.
- ECR repo and image digest (`sha256:...`).
- CloudFormation CREATE_COMPLETE and output resources.
- ECS desired `2`/running `2`, with tasks placed in separate AZs (verify, not guaranteed by desired count alone).
- ALB target group showing **two healthy IP targets**.
- CLI output for `/health`, `/ready`, `/v1/info`, `/v1/interest`, `/v1/loan-payment`, `/v1/transfer/validate`.
- CloudWatch JSON application request logs.
- Diagram or 5–10 sentence explanation of network/data flow and difference between `/health` and `/ready`.
- Cleanup evidence that no NAT/ALB/service/EIP remains.

## Step 6 — Cleanup (mandatory)

```bash
ACK_DELETE=yes bash scripts/cleanup.sh
```

**WARNING:** This intentionally deletes the named CloudFormation stack and **every image in the named ECR repository**, even if the repository predates this lab. Never point `ECR_REPO` to a shared repository. If stack deletion fails, investigate it before retrying. Inspect AWS Console afterwards for orphaned resources or costs.

## Troubleshooting

| Symptom | Check |
|---|---|
| `CannotPullContainerError` | ECR URI, digest, region, execution IAM role, private route/NAT |
| ECS PENDING or failures | ECS service events, account quotas, task definition, ENI networking |
| Target unhealthy | `/ready`, COBOL binary, port 8080, task SG ingress only from ALB SG |
| ALB unreachable | External IPv4 /32, HTTP port 80, public route, subnet placements |
| ECS desired 2 but healthy 1 | Task startup and ALB health checks; don't advance |
| CloudFormation rollback | View CloudFormation Events; investigate actual failure before redeploy |
| `AccessDenied` on `iam:PassRole` | Use instructor-approved least-privilege deployment role; do not add blanket admin rights |
| Charges after cleanup | Ensure NAT gateway, ALB, EIP, Fargate tasks, ECR and log group have been removed |

## Documentation

- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ecs-service.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-elasticloadbalancingv2-targetgroup.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/networking-outbound.html

**Gate 03 is reserved for deliberate task termination, observability, desired-state reconciliation, and recovery. Do not perform intentional failures as part of Gate 02.**
