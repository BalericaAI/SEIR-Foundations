# Gate 02 Runbook — Deploy the COBOL + FastAPI service to AWS ECS Fargate

**Lab:** SEIR Foundations — Module 3, Lab 02, Gate 02
**Audience:** Students who completed Gate 01 (this runbook is self-contained — you do not need to have read any other document first, but you DO need a passing Gate 01)
**Goal:** Push the Gate 01 image to Amazon ECR and run it as a two-task **ECS Fargate service** in private subnets behind an internet-facing **Application Load Balancer**, reachable only from your own IP.

> **COSTS — READ THIS FIRST.** This gate creates a **NAT gateway, an ALB, an Elastic IP, two Fargate tasks, an ECR repository, and CloudWatch logs**. The NAT gateway and ALB bill **per hour even when idle**. Deploy, collect your evidence, and run the cleanup the same day. Never leave this running overnight. Use a disposable lab/sandbox AWS account, not anything shared or production.

> **Security guardrails.** The ALB speaks plain HTTP (no TLS) and is restricted to your single public IPv4 (`/32`). **Never widen the allowlist to `0.0.0.0/0`** — both the deploy script and the CloudFormation template reject it. Synthetic data only.

**Verification status:** every *local* command below was executed and its output captured verbatim. Steps marked **[LIVE AWS — dry-run verified]** touch a real AWS account, which this runbook's author validated by dry run (guardrails, template lint, and script logic) but could not execute end-to-end; their "expected output" comes from the scripts' own code paths.

## What you are building

```text
Your workstation (your public /32 only)
        │  HTTP :80 (no TLS — lab only)
Internet-facing ALB (2 public subnets)
        │  target group: /ready must return 200
Fargate task A (private subnet, AZ1)   Fargate task B (private subnet, AZ2)
   FastAPI :8080 → GnuCOBOL               FastAPI :8080 → GnuCOBOL
        └────────── CloudWatch Logs ──────────┘
ECR image pulls + log writes go out through ONE shared NAT gateway
```

## Prerequisites — check these FIRST

- [ ] **Gate 01 actually passed on your machine**: local build, the six endpoints, direct COBOL execution, and the broken-binary `/ready=503` experiment. Do not fake this — Step 2 makes you attest to it.
- [ ] **AWS CLI v2** authenticated: `aws sts get-caller-identity` returns your lab account (not a personal/production one).
- [ ] **IAM permissions** for CloudFormation, EC2/VPC (incl. NAT + EIP), ECR, ECS, `iam:CreateRole`/`iam:PassRole`, ELB, CloudWatch Logs.
- [ ] **Docker** running (`docker version` shows a Server), **python3**, **curl**, **bash**.
- [ ] Your **public IPv4**: `curl -s https://checkip.amazonaws.com` — note it; you need it as `<YOUR_IP>/32`. (A private address like `10.x.x.x` or `192.168.x.x` is your LAN IP, not this.)
- [ ] Instructor/budget approval for roughly a few USD of hourly charges while deployed.

## Step 1 — Re-validate locally (same machine you will deploy from)

```bash
cd module3/lesson2_cobol/gate02   # from the root of your SEIR-Foundations clone
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

Expected: the same 9 tests as Gate 01, ending in:

```text
========================= 9 passed, 1 warning in 0.29s =========================
```

Then build and smoke-test the Gate 02 image locally (it is the same application):

```bash
docker build --platform linux/amd64 -t seir-cobol-lab02:gate02-local .
docker run --rm --platform linux/amd64 --name seir-lab02-g2 -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate02-local
# Second terminal:
BASE=http://127.0.0.1:8080 bash scripts/smoke.sh
```

Expected smoke output (exact; `hostname` and the `version` field — `gate02` here — vary):

```text
Checking /health and /ready
{"status":"healthy"}
{"status":"ready"}
{"hostname":"<container-id>","version":"gate02"}
{"interest":"100.00","total":"1100.00","currency":"USD","method":"simple"}
{"monthly_payment":"100.00","currency":"USD"}
{"decision":"APPROVED","posted":false}
```

Stop the local container (`Ctrl-C`). **Success check:** 9 tests passed and the six smoke lines match.

## Step 2 — Set context and explicit acknowledgements

```bash
export AWS_REGION=us-east-1            # use your assigned classroom region
export STACK_NAME=seir-lab02-cobol
export ECR_REPO=seir-lab02-cobol       # cleanup will DELETE this whole repository — keep it lab-only
export ALLOWED_CIDR='<YOUR_IP>/32'     # from the prerequisites, e.g. 198.51.100.7 → your real one
export GATE01_VALIDATED=yes            # ONLY if Step 1 and Gate 01 truly passed
export ACK_COSTS=yes                   # ONLY after reading the cost warning above
aws sts get-caller-identity
```

The deploy script refuses to run otherwise. The refusal messages (captured verbatim):

```text
STOP: Validate Gate 01 local integration, then set GATE01_VALIDATED=yes
STOP: NAT Gateway, ALB, Fargate, EIP and logs incur charges. Set ACK_COSTS=yes only after review.
```

And if `ALLOWED_CIDR` is private, not `/32`, or a reserved/documentation address, it exits with:

```text
ALLOWED_CIDR must be a valid global public IPv4 /32, e.g. 203.0.113.1/32 is documentation-only and NOT valid
```

**Success check:** `aws sts get-caller-identity` shows your lab account, and all five variables are exported in THIS terminal (exports do not survive new terminals).

## Step 3 — Deploy  [LIVE AWS — dry-run verified]

```bash
bash scripts/deploy.sh
```

What it does, in order: verifies identity and acknowledgements → creates the immutable-tag ECR repository if missing → builds and pushes a `linux/amd64` image under a unique timestamp tag → resolves the image **digest** → deploys `infra/lab02.yaml` with `ImageUri=<repo>@sha256:...`. Expected final lines:

```text
Deployment requested. Do not assume stack success implies healthy containers.
NEXT: bash scripts/verify.sh
CLEANUP: ACK_DELETE=yes bash scripts/cleanup.sh
ECR REPOSITORY: seir-lab02-cobol (cleanup deletes the entire repository)
```

Expect the CloudFormation deploy to take **5–10 minutes** (the NAT gateway is the slow part). **Success check:** the script prints the stack outputs table (including `AlbUrl`) with no error.

## Step 4 — Verify the deployment  [LIVE AWS — dry-run verified]

```bash
bash scripts/verify.sh
```

The script waits for service stability (the `aws ecs wait services-stable` step can sit silently for **up to ~10 minutes** — it is not hung), then checks. The pass line (exact string from the script):

```text
PASS: desired=2, running=2, 2 healthy IP targets
```

followed by the same six smoke-test lines as Step 1 (now served through the ALB) and a table of the two running tasks with their private subnets. **Success check:** the `PASS` line, two `healthy` targets in the table, and the smoke outputs.

Manual spot-check from your allowed IP:

```bash
curl -s "$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`AlbUrl`].OutputValue | [0]' --output text)/v1/info"
```

Expected: `{"hostname":"<task-id>","version":"gate02"}` — repeat it a few times and the hostname should alternate between the two tasks.

## Step 5 — Collect evidence

- `aws sts get-caller-identity` output (redact as instructed).
- ECR image digest (`sha256:...`) from the deploy output.
- CloudFormation `CREATE_COMPLETE` screenshot with outputs.
- ECS service: desired `2`, running `2`; tasks in **different** subnets (from verify's table).
- Target group: **two healthy** IP targets.
- The six endpoint responses through the ALB.
- A CloudWatch log line showing a JSON request log.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `STOP: ...` from deploy.sh | Reread Step 2 — a required export is missing in this terminal |
| `ALLOWED_CIDR must be a valid global public IPv4 /32...` | Use `curl -s https://checkip.amazonaws.com`; append `/32`; never a private/VPN-internal address |
| `CannotPullContainerError` in ECS events | Wrong region, missing NAT route, or execution role problem — check CloudFormation created `PrivateInternetRoute` and the stack is in the SAME region as the ECR repo |
| Targets stuck `initial` then `unhealthy` | Give the 60 s grace period + 2 health checks; then check `/ready` via logs: `/health=200` but `/ready=503` means the COBOL binary is broken in the image — rebuild and redeploy |
| ALB URL times out from your machine | Your public IP changed (VPN, café Wi-Fi). Re-run `curl -s https://checkip.amazonaws.com`; if different, redeploy with the new `ALLOWED_CIDR` — do **not** open `0.0.0.0/0` |
| `AccessDenied` on `iam:PassRole` | Your lab role lacks permission; ask the instructor — do not attach admin policies yourself |
| CloudFormation `ROLLBACK_COMPLETE` | Open the stack's **Events** tab, find the FIRST `CREATE_FAILED`, fix that cause, delete the stack, redeploy |
| `verify.sh` seems frozen | `aws ecs wait services-stable` polls up to ~10 min; watch the ECS console meanwhile |
| Charges after cleanup | See Cleanup below — confirm NAT, ALB, EIP, ECS service, ECR repo, and the log group are all gone in the console |

## Cleanup — MANDATORY, same day  [LIVE AWS — dry-run verified]

```bash
ACK_DELETE=yes bash scripts/cleanup.sh
```

Without the acknowledgement it refuses (captured verbatim):

```text
STOP: cleanup deletes the stack and ENTIRE ECR_REPO. Set ACK_DELETE=yes after confirming names.
```

> **WARNING:** cleanup deletes the CloudFormation stack **and the entire ECR repository named in `ECR_REPO`, including every image in it** — never point `ECR_REPO` at a shared repository.

Afterwards, confirm in the AWS console that **CloudFormation, ECS, EC2 → NAT gateways, EC2 → Elastic IPs, EC2 → Load balancers, and ECR** show nothing left from this lab, and screenshot it for your evidence.

**Next:** Gate 03 (`../gate03/runbook.md`) deliberately breaks this deployment to study ECS recovery — do **not** run Gate 03 experiments as part of Gate 02, and do not clean up yet if you are continuing to Gate 03 today.
