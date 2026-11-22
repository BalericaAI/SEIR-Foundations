# SEIR Foundations — Module 3, Lab 02 — Gate 03
## ECS desired-state recovery, health signals, and incident response

> Prefer a single start-to-finish checklist with exact commands and expected outputs? Follow [`runbook.md`](runbook.md) — it is fully self-contained.

**Status:** Lab materials prepared; AWS execution must be performed in the instructor/student sandbox. Gate 01 and Gate 02 were reported successful with cosmetic changes. This ZIP preserves the prior Gate 02 application and CloudFormation template; Gate 03 adds controlled-failure tools and evidence templates.

**Jira reference:** M3-1. Do not automatically sync this lab to Jira until instructed.

### Architecture and scope
The Gate 02 AWS stack runs an ALB behind a public IPv4 /32 allowlist, with two private ECS Fargate tasks (FastAPI -> GnuCOBOL), CloudWatch logs, and NAT egress. ECS maintains `DesiredCount: 2` and the ALB checks `/ready` to exercise the COBOL dependency. Gate 03 does not introduce RDS, authentication, AI agents, or real banking transactions.

### Why this matters
A service is a desired-state controller. Stopping one task should prompt ECS to replace it. The service `runningCount`, target group's `healthy` status, and FastAPI `/health` are different observations. A service can report running tasks while the load balancer reports unhealthy targets. Recovery must be proven with task identity and API checks, not assumed.

### Prerequisites
- Gate 01 Docker application verified and Gate 02 stack successfully deployed **in a disposable student sandbox**.
- `AWS_REGION`, `STACK_NAME` match your Gate 02 deployment; AWS CLI v2 is authenticated.
- AWS CLI, Python 3, curl; Docker for optional local broken-backend experiment.
- IAM permission to view CloudFormation outputs, ECS services/tasks/events, ELB target health, CloudWatch logs; `ecs:StopTask` for the controlled stop.
- Known-good baseline: `desired=2`, `running=2`, `pending=0`, two healthy ALB targets.
- Instructor-approved maintenance window. The exercise may briefly reduce available capacity.
- This stack incurs ALB, Fargate and NAT charges while deployed. Do not leave it running needlessly.

### Step 0 — Identify the sandbox
```bash
export AWS_REGION=us-east-1
export STACK_NAME=seir-lab02-cobol
aws sts get-caller-identity
```
Verify account and region before doing anything destructive. The default stack name is the previous lab's name; edit it if the instructor used a different name.

### Step 1 — Capture the baseline (read-only)
```bash
bash scripts/gate03_baseline.sh
```
This creates timestamped JSON under `evidence/gate03/baseline-...` containing ECS service data, task ARNs, task details, ALB target health and recent service events. **Baseline must PASS** before touching tasks. Inspect it, screenshot ECS service desired/running/pending, two ALB targets, and the two task ID suffixes.

### Step 2 — Stop exactly one task (intentional disruption)
Use one **full task ARN** shown in the baseline. Never paste an ARN from another account, cluster or environment.
```bash
export TASK_ARN='arn:aws:ecs:REGION:ACCOUNT:task/CLUSTER_ID/TASK_ID'
export ACK_STOP_TASK=yes
bash scripts/gate03_stop_one.sh
```
The script rejects missing acknowledgements, a selected task outside this ECS service, and an unhealthy baseline. It calls `ecs stop-task` **once**. Do not repeat the stop until the first recovery has been investigated.

### Step 3 — Observe service reconciliation
```bash
bash scripts/gate03_observe.sh
```
The observer polls service count and target states, records a CSV timeline, captures scheduler events and runs smoke tests after stability. It requires both `2 running` and `2 healthy ALB targets` before reporting recovery. Compare the baseline with the current service task IDs using:
```bash
export BASELINE_TASKS_FILE='evidence/gate03/baseline-YYYYMMDDTHHMMSSZ/task-arns.json'
bash scripts/gate03_compare.sh
```
Replace the timestamp with the actual evidence directory. This comparison requires **exactly one changed task ARN** and one unchanged ARN. Default observation is up to 48 polls with 10-second intervals; CLI waiters may extend this. To shorten or lengthen the sample, set `POLL_INTERVAL` and `MAX_POLLS`.

Expected behavior: ECS replaces a stopped service task. During recovery, `runningCount`, ALB target states, and pendingCount may vary. New targets can be `initial`; old ones can show `draining`. **No exact ordering, timing, or absence of HTTP failures is guaranteed.**

### Step 4 — Collect diagnostics
```bash
bash scripts/gate03_collect.sh
```
This stores service details, target health, running and recently stopped task metadata, events, and CloudWatch log stream metadata. Read application logs with:
```bash
aws logs tail "$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`LogGroupName`].OutputValue | [0]' --output text)" --since 30m --region "$AWS_REGION"
```
Service events can explain why a replacement launched. Stopped reason explains why the original task ended. Access logs and `/ready` status help distinguish app-level failure from load-balancer routing.

### Step 5 — Broken COBOL readiness (LOCAL, not ECS)
The following intentionally runs a container where the configured COBOL executable path doesn't exist; FastAPI is still alive. It does not alter ECS resources.
```bash
bash scripts/gate03_local_readiness.sh
```
Expected: `/health` is HTTP `200` and `/ready` is HTTP `503`. Explain how an ALB target group using `/ready` would interpret this, and why `/health` alone would be insufficient. This does **not** demonstrate a live ALB unhealthy state; it demonstrates the health signaling contract locally.

### Step 6 — Produce the incident report
Complete `INCIDENT_REPORT_TEMPLATE.md` with timestamps, desired/running counts, ALB states, original/replacement task ID suffixes, screenshots, logs, a 5–10 sentence engineering explanation, and the exact endpoint results.

### Step 7 — Cleanup (after your instructor confirms further testing is complete)
```bash
ACK_DELETE=yes bash scripts/cleanup.sh
```
**Important:** The inherited Gate 02 cleanup deletes the **entire named ECR repository** in addition to the stack. Only use it with a dedicated disposable lab repository. Confirm in CloudFormation, ECS, NAT, ALB and ECR that billable resources are gone.

### Submission checklist
- [ ] Correct AWS account/region and read-only PASS baseline
- [ ] ECS 2 desired/2 running and two healthy ALB targets before stop
- [ ] Task selection and one controlled stop recorded
- [ ] Poll timeline CSV and ECS service event evidence
- [ ] New task ARN compared to pre-stop ARN
- [ ] ECS stabilizes at 2/2; ALB has two healthy targets
- [ ] Functional interest, loan and transfer requests still pass
- [ ] Local `/health=200`, `/ready=503` demonstrated
- [ ] Incident report completed with screenshot evidence
- [ ] Cleanup evidence or instructor-approved reason to keep environment active

### Instructor notes
See `GATE03_INSTRUCTOR.md` for grading rubric, limitations, safety controls and troubleshooting.

### Official AWS references
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-event-messages.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/troubleshoot-service-load-balancers.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/load-balancer-healthcheck.html
