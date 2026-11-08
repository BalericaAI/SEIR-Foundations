# SEIR Foundations — Module 3 — Lab 02

## COBOL as an always-on financial service on Amazon ECS Fargate

**Outcome:** Convert the Lab 01 idea (run COBOL once in an ECS task) into a stateless COBOL-backed HTTP application, managed by an ECS **service** that maintains two running tasks behind an Application Load Balancer.

**Scope:** Synthetic financial calculations only. No actual banking operations, balances, customer data, authentication, RDS, AgentCore, or production integrations.

### Architecture

```text
Student IP /32
      |
      v
Internet-facing ALB (HTTP port 80, IP-restricted, no TLS)
      |
      v
Target group (type: ip; GET /ready)
      |
  +---+----------------------------------+
  |   |                                  |
  v   v                                  v
ECS Task A                          ECS Task B
(private subnet AZ1)                (private subnet AZ2)
HTTP adapter -> GnuCOBOL            HTTP adapter -> GnuCOBOL
  |                                      |
  +----------- CloudWatch Logs -----------+

ECR --> ECS execution role --> task image pulling
Private subnets --> NAT gateway --> outbound ECR/Logs connectivity
```

The ALB is in two public subnets; ECS tasks are in private subnets with no public IPs. The task SG permits port 8080 only from the ALB SG. The NAT gateway exists to allow the private Fargate tasks to pull ECR images and send logs. This is a teaching design rather than a cost-optimized production architecture.

### Learning objectives

1. Explain **run-task** versus **service / desired count**.
2. Compile a GnuCOBOL program into a Linux image with a Python HTTP adapter.
3. Push an immutable version-tagged image to Amazon ECR.
4. Deploy an ALB, target group, private task networking and a two-task ECS Fargate service.
5. Explain the difference between `/health` (HTTP process) and `/ready` (actually invoking COBOL).
6. Validate functional results, task replacement, load-balancer health and CloudWatch records.
7. Remove all costly lab resources after testing.

## Prerequisites

- An AWS student sandbox account in a region with Fargate, ECS, ECR and ALB.
- AWS CLI v2 configured (`aws sts get-caller-identity`).
- Docker Desktop / Docker Engine with Linux container support; on Apple Silicon the script builds `linux/amd64` explicitly.
- Python 3 and `curl` locally for verification.
- Permissions for CloudFormation, VPC/EC2 networking, NAT gateway, IAM role creation and `iam:PassRole`, ECS, ECR, ALB, CloudWatch Logs, and the ECS service-linked role. In a restricted organization, ask the instructor for an approved deployment role rather than widening student privileges.
- Your current **public IPv4 address /32** for the ALB allowlist, e.g. `198.51.100.7/32`. This must be your real external public IP, not a private `192.168.x.x` address. Never set `0.0.0.0/0`.
- Available quota for one NAT gateway, one ALB, two Fargate tasks, and an Elastic IP.

**Cost warning:** NAT gateway has hourly/data-processing charges, the ALB has hourly/usage charges, and both Fargate tasks incur compute charges. These costs continue while the stack remains active. Use a sandbox budget and delete promptly after the lab. Check pricing in your chosen AWS region.

**Security warning:** The training ALB intentionally uses **HTTP**, not TLS, to avoid certificate/domain dependencies. It is CIDR-restricted, but traffic is unencrypted. Use only synthetic data. Do not expose this application on the open internet or use it with real customer information. HTTPS/ACM, authentication, WAF and service authorization belong to the hardening lab.

## Step 1 — Get the lab and run local tests

```bash
cd seir_lab02_cobol_ecs
python3 -m unittest discover -s tests -v
```

Build and run locally:

```bash
docker build --platform linux/amd64 -t seir-cobol-lab02:local .
docker run --rm --platform linux/amd64 -p 127.0.0.1:8080:8080 seir-cobol-lab02:local
```

In a second terminal:

```bash
curl -s http://127.0.0.1:8080/ready
curl -s -H 'Content-Type: application/json' \
  -d '{"principal":"1000.00","annual_rate_percent":"5.00","years":2}' \
  http://127.0.0.1:8080/v1/interest
curl -s -H 'Content-Type: application/json' \
  -d '{"principal":"1200.00","annual_rate_percent":"0.00","months":12}' \
  http://127.0.0.1:8080/v1/loan-payment
curl -s -H 'Content-Type: application/json' \
  -d '{"amount":"250.00","available_balance":"500.00"}' \
  http://127.0.0.1:8080/v1/transfer/validate
```

Expected JSON values (field order may vary):

```json
{"status":"ready"}
{"interest":"100.00","total":"1100.00","currency":"USD","method":"simple"}
{"monthly_payment":"100.00","currency":"USD"}
{"decision":"APPROVED","posted":false}
```

These are educational calculations, not a production-grade lending engine. Amount validation is performed by the adapter; the GnuCOBOL code performs the calculation. The transfer endpoint **does not move money**.

## Step 2 — Select account, region and allowlisted IP

```bash
export AWS_REGION=us-east-1
export STACK_NAME=seir-lab02-cobol
export ECR_REPO=seir-lab02-cobol
export ALLOWED_CIDR='YOUR_PUBLIC_IP/32'
aws sts get-caller-identity
```

Substitute your actual public IPv4 address. The deployment script refuses a fully open allowlist. Corporate VPN IP changes may make your endpoint unreachable until you update `AllowedCidr` in CloudFormation.

## Step 3 — Deploy

```bash
bash scripts/deploy.sh
```

The script creates an ECR repository if needed, builds a new `linux/amd64` image, pushes it with a timestamped tag, and deploys `infra/lab02.yaml`. CloudFormation then provisions networking, the NAT gateway, ALB, target group, execution role, ECS cluster, task definition, two-task service and CloudWatch log group.

It outputs the endpoint and resource names. The stack can take several minutes to reach steady state. Do not assume that stack completion always means both ALB targets are healthy.

If you already have a deployed stack, running `deploy.sh` again builds a new image and updates the ECS task definition. This makes it useful for later version/rollback exercises.

## Step 4 — Verify

```bash
bash scripts/verify.sh
```

The script prints task counts and ALB target health, calls `/ready`, and checks example financial endpoints. It also calls `/v1/info` repeatedly; after two targets are healthy, record whether distinct task hostnames appear. Load balancing does not guarantee a particular distribution in a short sample.

Manual AWS Console evidence:

1. ECS > Clusters > service: **desired 2 / running 2**.
2. EC2 > Target Groups: **two healthy IP targets**.
3. ECS > Tasks: task IDs and subnet placement across AZs.
4. CloudWatch Logs: HTTP adapter request records.
5. ECR: pushed image tag.

## Step 5 — Failure exercise (instructor-approved sandbox)

1. Save a screenshot of both healthy targets.
2. Stop one *running* service task from the ECS console (do **not** delete the service).
3. Observe the stopped task reason and ECS service event history.
4. Observe replacement task creation and target registration.
5. Wait until desired 2 / running 2 and both target group entries are healthy again.
6. Query `/ready` and `/v1/interest` again.
7. Write a 5–10 sentence incident report explaining **desired state reconciliation**, ALB health and recovery.

**Extra failure:** The instructor can deploy a controlled broken image in a separate feature branch where the COBOL binary cannot execute. `/health` still responds but `/ready` returns 503, causing the ALB to mark the target unhealthy. Students then restore the known-good image. Don't intentionally compromise IAM roles or change shared infrastructure in a class account.

## Step 6 — Cleanup (required)

```bash
bash scripts/cleanup.sh
```

This deletes the CloudFormation stack **and** the ECR repository, including images in that lab repository. Do not reuse the same ECR repository for unrelated modules; the cleanup uses `--force`. It doesn't remove any resources not owned by the stack/repository.

### Student submission checklist

- [ ] Local Docker and GnuCOBOL application responds successfully.
- [ ] Image present in Amazon ECR.
- [ ] ECS desired and running count show 2.
- [ ] Two healthy target-group IPs across AZs.
- [ ] Interest, loan and transfer validation responses documented.
- [ ] Screenshots of one intentionally stopped task and its replacement.
- [ ] CloudWatch log evidence and 5–10 sentence incident report.
- [ ] Cleanup confirmation.

## Troubleshooting

| Symptom | Investigation |
|---|---|
| `CannotPullContainerError` | ECR image URI, execution role permissions, NAT route, repository/account/region |
| ECS tasks stuck `PENDING` | Fargate quotas, subnet IPs, execution-role permission, ECS service events |
| ALB says `unhealthy` | Check `/ready`, container port 8080, source ALB SG, target type `ip`, CloudWatch logs |
| Browser cannot reach ALB | Verify your *current* external IPv4 matches `ALLOWED_CIDR`; verify HTTP port 80 |
| `/health` works but `/ready` fails | COBOL executable or libcob runtime, subprocess timeout, build output |
| Docker fails on Apple Silicon | Confirm Docker Linux containers and `--platform linux/amd64` |
| Stack deletion blocked | ECS service and ENI removal may take time; inspect CloudFormation events |
| Costs persist | Confirm NAT gateway, ALB, ECS service and Elastic IP are gone; check other stacks/regions |

## Architectural discussion

- Why does an ECS **service** replace failed tasks but a one-off `run-task` does not automatically maintain a desired count?
- Why does ALB target type need to be `ip` for Fargate `awsvpc` tasks?
- Why do private Fargate tasks require NAT or suitable VPC endpoints to retrieve images and report logs?
- How does `/ready` test more than a process health check?
- What would need to change before using real financial data or persistent ledger transactions?

### Suggested AWS references

- [ECS with ALB](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html)
- [Fargate task networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html)
- [ECS IAM roles](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-iam-roles.html)
