# Gate 03 Incident Report — ECS desired-state recovery exercise

> Fill in every field. Attach the referenced evidence files and screenshots
> from your `evidence/gate03/` directories. Redact account IDs where your
> instructor requires it. Use UTC timestamps exactly as they appear in the
> evidence JSON/CSV.

## 1. Identification

| Field | Value |
|---|---|
| Student name | |
| Date of exercise (UTC) | |
| AWS region | |
| CloudFormation stack name | |
| ECS cluster / service | |
| Instructor-approved window | yes / no |

## 2. Baseline (before the controlled stop)

| Field | Value |
|---|---|
| Baseline evidence directory | `evidence/gate03/baseline-________` |
| Baseline result | PASS / FAIL |
| Desired / running / pending counts | / / |
| ALB targets (total / healthy) | / |
| Task A ID suffix (last 12 chars) | |
| Task B ID suffix (last 12 chars) | |

Attach: screenshot of the ECS service page showing desired/running/pending, and of the target group showing two healthy targets.

## 3. Controlled failure injection

| Field | Value |
|---|---|
| Full ARN of the task you stopped | |
| UTC time `stop-task` was issued | |
| Stop reason recorded by the script | |
| Stop evidence file | `evidence/gate03/stop-________.json` |

## 4. Observed recovery timeline

| Field | Value |
|---|---|
| Observe evidence directory | `evidence/gate03/observe-________` |
| UTC time counts first dropped below 2 running / 2 healthy | |
| UTC time running returned to 2 | |
| UTC time ALB reported two healthy targets again | |
| Total polls / poll interval used | |
| Any `initial` / `draining` target states seen? | |

Attach: `timeline.csv` and at least one ECS **service event** line explaining why a replacement task started.

## 5. Replacement proof

| Field | Value |
|---|---|
| Retained task ID suffix | |
| Stopped task ID suffix | |
| New (replacement) task ID suffix | |
| `gate03_compare.sh` result | PASS / FAIL |

## 6. Post-recovery verification

Paste the exact output (status codes and JSON bodies) for:

- `GET /health`:
- `GET /ready`:
- `GET /v1/info`:
- `POST /v1/interest` (1000.00 @ 5.00% × 2 years):
- `POST /v1/loan-payment` (1200.00 @ 0.00% × 12 months):
- `POST /v1/transfer/validate` (250.00 against 500.00):

## 7. Local readiness-contract demonstration (Step 5)

| Field | Value |
|---|---|
| `/health` HTTP code with broken `COBOL_BIN` | (expected 200) |
| `/ready` HTTP code with broken `COBOL_BIN` | (expected 503) |

In 2–3 sentences: how would an ALB target group configured with `/ready` interpret this container, and why would `/health` alone be insufficient?

## 8. Engineering explanation (5–10 sentences)

Explain, in your own words: what ECS observed after the stop, why the service launched a replacement, how the ALB's view (target health) differed from ECS's view (running count) during recovery, what the CloudWatch logs and service events contributed, and what this implies about choosing health check endpoints.

## 9. Cleanup

| Field | Value |
|---|---|
| Cleanup performed (UTC time) | |
| `ACK_DELETE=yes bash scripts/cleanup.sh` output attached | yes / no |
| Console check: no stack / ALB / NAT / EIP / ECS service / ECR repo remains | yes / no |
| If the environment was intentionally kept: instructor approval reference | |
