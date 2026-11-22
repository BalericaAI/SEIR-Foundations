# SEIR Foundations — Module 3 Lab 02 — Gate 01

> Prefer a single start-to-finish checklist with exact commands and expected outputs? Follow [`runbook.md`](runbook.md) — it is fully self-contained.

## Goal
Turn Lab 01's one-shot COBOL batch execution into a local persistent HTTP service using FastAPI, with **GnuCOBOL actually performing the calculations**. This is the application gate before Amazon ECR, ECS Fargate, and ALB deployment.

**Synthetic data only.** No real banking, deposits, customer records, ledger updates or production financial use. This is an instructional sample, not a certified financial engine.

## Architecture

`curl -> FastAPI :8080 -> subprocess.run(GnuCOBOL executable) -> result -> JSON`

- Validation and JSON are handled by FastAPI/Pydantic.
- Simple interest, amortized loan payment, and transfer eligibility are computed in GnuCOBOL.
- Each request launches the COBOL binary with validated arguments. This is suitable for demonstrating a language boundary, not a high-throughput production design.
- `/health` probes the HTTP application; `/ready` executes a COBOL PING and returns 503 if unavailable.
- Application logs are structured JSON lines suitable for later CloudWatch capture.

## Prerequisites

- Docker Engine/Desktop with Linux containers and permission to run `docker build`.
- `curl`; optional Python 3.11+ and packages from `requirements-dev.txt` for host-side mocked tests.
- AWS account is **not required** for Gate 01.

## Gate 01 execution (student)

```bash
cd module3/lesson2_cobol/gate01   # from the root of your SEIR-Foundations clone
# Optional contract tests (mocked COBOL runner; do not prove COBOL compilation):
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v

# Mandatory: compile the actual GnuCOBOL executable during Docker build
# --platform linux/amd64 matches the planned ECS task architecture.
docker build --platform linux/amd64 -t seir-cobol-lab02:gate01 .

docker run --rm --platform linux/amd64 --name seir-lab02 \
  -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate01
```

In a second terminal:

```bash
bash scripts/smoke.sh
```

Expected interest `100.00`, total `1100.00`; zero-interest loan payment `100.00`; transfer decision `APPROVED` and `posted:false`.

### Verify COBOL is genuinely doing the work

```bash
docker exec seir-lab02 /usr/local/bin/finance PING 0 0 0
docker exec seir-lab02 /usr/local/bin/finance INTEREST 1000.00 5.00 2
docker exec seir-lab02 /usr/local/bin/finance LOAN 1200.00 0.00 12
docker exec seir-lab02 /usr/local/bin/finance TRANSFER 250.00 500.00 0
```

Expected output lines: `OK|READY`, `OK|100.00|1100.00`, `OK|100.00`, `OK|APPROVED`.

### Failure experiment (controlled; no real AWS resources)

Stop the good container (`Ctrl-C`), then run it with an invalid executable location:

```bash
docker run --rm --platform linux/amd64 --name seir-lab02-broken \
  -e COBOL_BIN=/not/a/real/finance \
  -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate01
```

In another terminal:

```bash
curl -i http://127.0.0.1:8080/health  # HTTP 200
curl -i http://127.0.0.1:8080/ready   # HTTP 503
```

This is the core Gate 01 lesson: a live web process can be unable to do its actual job. Stop the broken container and rerun the original command to restore service.

## Student deliverables

1. Screenshot of successful `docker build` showing GnuCOBOL compilation.
2. Screenshot of successful `/health` and `/ready` on good container.
3. JSON responses from interest, loan-payment, transfer validation.
4. Screenshot showing `docker exec ... finance INTEREST ...` output.
5. Screenshot proving broken binary -> `/health` 200 and `/ready` 503.
6. Short explanation: Why must the future ALB use `/ready` rather than only `/health`?

## Troubleshooting

| Symptom | Investigation |
|---|---|
| `docker: command not found` | Install/start Docker Desktop or Docker Engine; WSL2 Docker integration on Windows |
| COBOL compilation fails during build | Check `cobol/finance.cbl`, Docker build output, and Debian GnuCOBOL package |
| HTTP 503 at `/ready` | Check `COBOL_BIN`, binary execute permission, runtime library, stderr and log events |
| HTTP 422 on financial requests | Only nonnegative decimal **strings**, at most two fractional digits; limits apply |
| Port 8080 in use | Stop other local services or use host port `8081:8080` and `BASE=http://127.0.0.1:8081` |
| Can't pull base Docker image | Check registry reachability, Docker authentication/proxy and DNS |
| `exec format error` | Build/run compatible CPU architecture; `linux/amd64` may require emulation on ARM |

## Instructor notes

- Students should confirm COBOL results directly; mocked unit tests alone do not prove binary behavior.
- This Gate includes **no AWS provisioning or costs**.
- Before Gate 02, evaluate overflow/rounding edge cases and add integration tests against the built Docker image. Finance examples are synthetic and bounded; not appropriate for actual financial decisions.
