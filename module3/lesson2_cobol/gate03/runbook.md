# Gate 03 Runbook — Break one task on purpose, watch ECS heal it, prove it

**Lab:** SEIR Foundations — Module 3, Lab 02, Gate 03
**Audience:** Students with a healthy Gate 02 stack deployed (this runbook is self-contained — you do not need to have read any other document first, but you DO need the Gate 02 stack running)
**Goal:** Stop exactly **one** ECS Fargate task, observe the service controller replace it, prove the replacement with task IDs and ALB target health, demonstrate the `/health`-vs-`/ready` contract locally, and write an incident report.

> **COSTS.** Your Gate 02 stack (NAT gateway, ALB, EIP, two Fargate tasks, logs) **bills hourly the whole time it exists** — including while you do this gate. Finish and clean up the same day.

> **Guardrails — non-negotiable.**
> - Run only against **your own disposable Gate 02 stack**, never a shared or production cluster, and only in an **instructor-approved window** (capacity briefly drops during the exercise).
> - Stop **exactly one** task, **once**. Do not repeat the stop until the first recovery is fully investigated.
> - Never change `desiredCount`, IAM, security groups, or health-check settings as part of this exercise.

**Verification status:** Step 5 (local readiness) and every refusal/guardrail message below were executed and captured verbatim. Steps marked **[LIVE AWS — dry-run verified]** need your real Gate 02 stack; their logic, refusal paths, and pass/fail decisions were validated by dry run and fixture tests, but could not be executed against live AWS by this runbook's author.

## The idea in three sentences

An ECS **service** is a desired-state controller: you told it "keep 2 tasks running", so killing one should make it launch a replacement. But `runningCount=2`, "2 healthy ALB targets", and "the API answers correctly" are **three different observations** that can disagree during recovery. This gate makes you prove recovery with task identities and API checks instead of assuming it.

## Prerequisites — check these FIRST

- [ ] Gate 02 stack deployed and verified: `verify.sh` printed `PASS: desired=2, running=2, 2 healthy IP targets`.
- [ ] `AWS_REGION` and `STACK_NAME` match that deployment; AWS CLI v2 authenticated.
- [ ] IAM: read access to CloudFormation/ECS/ELB/CloudWatch Logs **plus `ecs:StopTask`**.
- [ ] `python3`, `curl`, `bash`; **Docker** for Step 5 (local experiment only).
- [ ] Instructor-approved maintenance window.

## Step 0 — Point at the right account and stack

```bash
cd module3/lesson2_cobol/gate03   # from the root of your SEIR-Foundations clone
export AWS_REGION=us-east-1        # your Gate 02 region
export STACK_NAME=seir-lab02-cobol # your Gate 02 stack name
aws sts get-caller-identity
```

**Success check:** the account/ARN is your disposable lab account. Everything destructive below is scoped to this stack — verify before proceeding.

## Step 1 — Capture the baseline (read-only)  [LIVE AWS — dry-run verified]

```bash
bash scripts/gate03_baseline.sh
```

This makes only read calls and writes JSON evidence into `evidence/gate03/baseline-<UTC-timestamp>/` (service state, `task-arns.json`, task details, ALB target health, recent service events). Expected output shape:

```text
Baseline evidence directory: evidence/gate03/baseline-20260101T120000Z (read-only AWS calls)
desired=2 running=2 pending=0
ALB targets: 2 total, 2 healthy
RUNNING task: ...<12-char suffix>  (arn:aws:ecs:...:task/<cluster>/<id>)
RUNNING task: ...<12-char suffix>  (arn:aws:ecs:...:task/<cluster>/<id>)
BASELINE PASS
Keep this directory. gate03_compare.sh needs: export BASELINE_TASKS_FILE='evidence/gate03/baseline-.../task-arns.json'
```

If the service is not at 2/2/0 with two healthy targets, the script exits with `BASELINE FAIL` and tells you not to proceed — **fix the deployment first**.

**Success check:** `BASELINE PASS`. Screenshot the ECS service page and the target group, and note both task ID suffixes.

## Step 2 — Stop exactly one task  [LIVE AWS — dry-run verified]

Copy ONE **full task ARN** from your baseline output (either one). Then:

```bash
export TASK_ARN='arn:aws:ecs:REGION:ACCOUNT:task/CLUSTER_ID/TASK_ID'   # your real ARN
export ACK_STOP_TASK=yes
bash scripts/gate03_stop_one.sh
```

The script re-checks live health, confirms the ARN is a running member of **this** service, then calls `ecs stop-task` exactly once. Expected:

```text
Pre-stop checks passed.
Stopping ONE task: arn:aws:ecs:...:task/.../...
stop-task issued once; response saved to evidence/gate03/stop-<UTC>.json
Do NOT stop another task. NEXT: bash scripts/gate03_observe.sh
```

Its refusal messages, captured verbatim (each exits with code 2 and touches nothing):

```text
STOP: This intentionally disrupts a running task. Set ACK_STOP_TASK=yes only with instructor approval.
STOP: Set TASK_ARN to one FULL task ARN from your PASS baseline (see evidence/gate03/baseline-*/task-arns.json).
STOP: 'not-an-arn' is not a full ECS task ARN (arn:aws:ecs:REGION:ACCOUNT:task/CLUSTER/ID).
```

plus refusals when the ARN is not part of this service or the live state is no longer healthy.

**Success check:** the `stop-task issued once` line. Move immediately to Step 3 — recovery starts within seconds.

## Step 3 — Watch the service heal itself  [LIVE AWS — dry-run verified]

```bash
bash scripts/gate03_observe.sh
```

Polls every **10 s**, up to **48 times** (override with `POLL_INTERVAL` / `MAX_POLLS`), writing a CSV timeline to `evidence/gate03/observe-<UTC>/timeline.csv` with this header:

```text
utc_timestamp,desired,running,pending,targets_total,targets_healthy,target_states
```

During recovery you will see `running` dip, `pending` rise, and target states like `draining` and `initial` — **no exact ordering or timing is guaranteed**. The script requires `running=2` AND `2 healthy targets`, waits for ECS stability, then runs the six-endpoint smoke suite against the ALB and ends with:

```text
RECOVERY CONFIRMED. Evidence: evidence/gate03/observe-<UTC>
```

Then prove **which** task was replaced:

```bash
export BASELINE_TASKS_FILE='evidence/gate03/baseline-<YOUR-TIMESTAMP>/task-arns.json'
bash scripts/gate03_compare.sh
```

Expected shape (verified against fixtures; your suffixes differ):

```text
RETAINED : ...aaaaaaaaaaaa  (arn:aws:ecs:...)
STOPPED  : ...bbbbbbbbbbbb  (arn:aws:ecs:...)
NEW      : ...cccccccccccc  (arn:aws:ecs:...)
PASS: exactly one task was replaced and one survived.
```

If **both** tasks changed, the script FAILS on purpose — something besides your one stop disturbed the service; investigate the events before grading. Its refusals when misconfigured (captured verbatim):

```text
STOP: export BASELINE_TASKS_FILE='evidence/gate03/baseline-YYYYMMDDTHHMMSSZ/task-arns.json' (your actual baseline directory).
STOP: <path> does not exist. Use the task-arns.json from YOUR baseline evidence directory.
```

**Success check:** `RECOVERY CONFIRMED` and compare's `PASS` with one RETAINED, one STOPPED, one NEW.

## Step 4 — Collect the diagnostics  [LIVE AWS — dry-run verified]

```bash
bash scripts/gate03_collect.sh
```

Saves service details, target health, running **and recently stopped** task metadata, 50 service events, and CloudWatch log-stream metadata to `evidence/gate03/collect-<UTC>/`, then prints the exact `aws logs tail` command for the application logs. Look for: the service event explaining why a replacement launched, and the stopped task's `stoppedReason`.

**Success check:** the collect directory exists and the stopped task's reason mentions your Gate 03 stop. (ECS ages stopped tasks out of visibility quickly — if `stopped-tasks.json` is empty, rely on the service events and your Step 3 evidence.)

## Step 5 — Local proof of the readiness contract (NO AWS — fully verified)

This step runs entirely on your machine and changes nothing in AWS. It runs the application container with a deliberately broken COBOL path:

```bash
bash scripts/gate03_local_readiness.sh
```

Expected (exact; captured from a real run):

```text
/health -> HTTP 200 (expected 200: the web process is alive)
/ready  -> HTTP 503 (expected 503: the COBOL dependency is broken)
PASS: an ALB health check on /ready would mark this target unhealthy; /health alone would not.
```

(The script builds the image from the sibling `../gate02` folder and uses local port **8099**, so it will not clash with a Gate 01 container.)

**Success check:** the `PASS` line. In your report, explain how an ALB using `/ready` would treat this target and why `/health` alone is insufficient.

## Step 6 — Write the incident report

Fill in **every** field of `INCIDENT_REPORT_TEMPLATE.md` (same folder): baseline evidence, the stop, the timeline CSV, retained/stopped/new task suffixes, post-recovery endpoint outputs, the local readiness result, a 5–10 sentence engineering explanation, and cleanup evidence.

## Step 7 — Cleanup (after the instructor confirms nothing else needs the stack)  [LIVE AWS — dry-run verified]

```bash
export ECR_REPO=seir-lab02-cobol   # the repo your Gate 02 deploy used
ACK_DELETE=yes bash scripts/cleanup.sh
```

Without the acknowledgement it refuses (captured verbatim):

```text
STOP: cleanup deletes the stack and ENTIRE ECR_REPO. Set ACK_DELETE=yes after confirming names.
```

> **WARNING:** this is Gate 02's cleanup — it deletes the CloudFormation stack **and the entire named ECR repository with every image in it**. Afterwards, confirm in the console that CloudFormation, ECS, NAT gateways, Elastic IPs, load balancers, and ECR show nothing left, and screenshot it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `BASELINE FAIL` | The service is not at desired=2/running=2 with two healthy targets. Fix Gate 02 first (`../gate02/runbook.md` troubleshooting); never inject failure into an already-unhealthy service |
| `STOP: ... not a RUNNING task of this ECS service` | You pasted an ARN from another cluster/account or a stale baseline. Re-run the baseline and copy a fresh full ARN |
| `AccessDenied` on `ecs:StopTask` | Your sandbox role lacks that one permission; ask the instructor — do not widen IAM yourself |
| Observe hits `NOT RECOVERED after 48 polls` | Recovery may just be slow: check `service-events.json` for image-pull or capacity errors, then rerun observe with `MAX_POLLS=96`. No replacement at all → check quotas, subnet IPs, execution role, ECR access |
| Target shows `initial` for a long time | Health checks are warming (20 s interval × 2 required passes + 60 s grace). Observe, don't guess |
| Compare FAILS with two changed tasks | A deployment, scaling event, or second stop happened during the window. Read the service events, restore a clean 2/2 baseline, and redo the exercise with exactly one stop |
| `stopped-tasks.json` empty in collect | ECS keeps stopped tasks visible only briefly — use the service events and the observe timeline as your evidence |
| Step 5: `permission denied ... docker.sock` | Add yourself to the `docker` group or run with `sudo` |
| Step 5: `STOP: cannot find the Gate 02 application` | Run the script from the `gate03` folder of a full repo clone (it builds from `../gate02`), or point `APP_DIR` at the folder containing the Gate 02 `Dockerfile` |

**Done.** Submit the completed incident report with all evidence attached, plus the cleanup screenshots.
