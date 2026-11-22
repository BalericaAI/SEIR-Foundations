# Gate 01 Runbook — Local COBOL + FastAPI service in Docker

**Lab:** SEIR Foundations — Module 3, Lab 02, Gate 01
**Audience:** Students starting Lab 02 (this runbook is self-contained — you do not need to have read any other document first)
**Goal:** Build a Docker image where **GnuCOBOL** performs financial calculations behind a **FastAPI** HTTP service, prove the COBOL binary is really doing the work, and demonstrate why `/ready` and `/health` are different signals.
**AWS needed:** No. Gate 01 is entirely local and incurs **zero cost**.

> Every command and expected output below was executed and captured on a clean Linux machine. Where an output contains a value unique to your machine (container IDs, hostnames), the runbook says so.

## What you are building

```text
curl → FastAPI :8080 → subprocess(GnuCOBOL binary) → result → JSON
```

FastAPI validates the input; a compiled COBOL program (`cobol/finance.cbl`) computes simple interest, amortized loan payments, and transfer eligibility. All data is synthetic — no real banking.

## Prerequisites — check these FIRST

- [ ] **Docker** Engine or Docker Desktop installed, Linux containers, daemon running. Verify: `docker version` prints both a Client and a Server section. (Windows: use WSL2 integration.)
- [ ] **curl** installed: `curl --version` works.
- [ ] **Python 3.11+ and pip** (only for the optional unit tests in Step 2): `python3 --version`.
- [ ] This repository cloned locally.

## Step 1 — Go to the Gate 01 folder

```bash
cd module3/lesson2_cobol/gate01   # from the root of your SEIR-Foundations clone
```

**Success check:** `ls` shows `app`, `cobol`, `Dockerfile`, `scripts`, `tests`, `requirements.txt`.

## Step 2 (optional but recommended) — Run the mocked unit tests

These test the HTTP contract with the COBOL runner mocked; they do **not** prove COBOL compiles — that is Step 3's job.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

Expected (exact, apart from timing):

```text
tests/test_api.py::test_health_does_not_depend_on_cobol PASSED           [ 11%]
tests/test_api.py::test_ready_calls_cobol PASSED                         [ 22%]
tests/test_api.py::test_interest_contract PASSED                         [ 33%]
tests/test_api.py::test_loan_contract PASSED                             [ 44%]
tests/test_api.py::test_transfer_never_posts_money PASSED                [ 55%]
tests/test_api.py::test_bad_amount_rejected_before_cobol PASSED          [ 66%]
tests/test_api.py::test_negative_amount_rejected PASSED                  [ 77%]
tests/test_api.py::test_readiness_degrades_when_binary_missing PASSED    [ 88%]
tests/test_api.py::test_info_has_hostname PASSED                         [100%]
========================= 9 passed, 1 warning in 0.29s =========================
```

**Success check:** `9 passed`. (One `DeprecationWarning` from the test client is normal.)

## Step 3 — Build the image (compiles the real COBOL)

```bash
docker build --platform linux/amd64 -t seir-cobol-lab02:gate01 .
```

The build installs GnuCOBOL in a builder stage and runs `cobc -x -free -o /build/finance finance.cbl`. Expected final lines:

```text
Successfully built <image-id>
Successfully tagged seir-cobol-lab02:gate01
```

**Success check:** `Successfully tagged seir-cobol-lab02:gate01`. If the build fails at the `cobc` step, the COBOL source has a problem — read the compiler message in the build output.

## Step 4 — Run the service

```bash
docker run --rm --platform linux/amd64 --name seir-lab02 \
  -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate01
```

This runs in the **foreground** (keep this terminal open). Expected startup output:

```text
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**Success check:** the `Uvicorn running` line appears and the process stays up.

## Step 5 — Smoke-test all six endpoints (second terminal)

```bash
cd module3/lesson2_cobol/gate01
bash scripts/smoke.sh
```

Expected (exact; only the `hostname` value varies — it is the container ID):

```text
Checking /health and /ready
{"status":"healthy"}
{"status":"ready"}
{"hostname":"47f0fcf29c74","version":"gate01"}
{"interest":"100.00","total":"1100.00","currency":"USD","method":"simple"}
{"monthly_payment":"100.00","currency":"USD"}
{"decision":"APPROVED","posted":false}
```

**Success check:** interest `100.00`, total `1100.00`, monthly payment `100.00`, decision `APPROVED` with `"posted":false`.

## Step 6 — Prove COBOL is genuinely doing the work

Run the compiled COBOL binary directly inside the container, bypassing Python entirely:

```bash
docker exec seir-lab02 /usr/local/bin/finance PING 0 0 0
docker exec seir-lab02 /usr/local/bin/finance INTEREST 1000.00 5.00 2
docker exec seir-lab02 /usr/local/bin/finance LOAN 1200.00 0.00 12
docker exec seir-lab02 /usr/local/bin/finance TRANSFER 250.00 500.00 0
```

Expected (exact, one line per command):

```text
OK|READY
OK|100.00|1100.00
OK|100.00
OK|APPROVED
```

**Success check:** the COBOL outputs match the JSON the API returned in Step 5 — the same binary produced both.

## Step 7 — The core lesson: a live process that cannot do its job

Stop the good container (`Ctrl-C` in the Step 4 terminal), then start one whose COBOL binary path is deliberately wrong:

```bash
docker run --rm --platform linux/amd64 --name seir-lab02-broken \
  -e COBOL_BIN=/not/a/real/finance \
  -p 127.0.0.1:8080:8080 seir-cobol-lab02:gate01
```

In the second terminal:

```bash
curl -s -o /dev/null -w "health=%{http_code}\n" http://127.0.0.1:8080/health
curl -s -o /dev/null -w "ready=%{http_code}\n"  http://127.0.0.1:8080/ready
curl -s http://127.0.0.1:8080/ready
```

Expected (exact):

```text
health=200
ready=503
{"detail":"COBOL backend unavailable"}
```

**Success check:** `/health` is `200` while `/ready` is `503`. The web process is alive but cannot do its actual job — this is why the load balancer in Gate 02 must health-check `/ready`, not `/health`.

## Deliverables

1. Screenshot of the successful `docker build` (showing the COBOL compile step).
2. Screenshot of Step 5's six JSON responses.
3. Screenshot of Step 6's four direct COBOL outputs.
4. Screenshot of Step 7 (`health=200`, `ready=503`).
5. One short paragraph: why must the future ALB use `/ready` rather than only `/health`?

## Troubleshooting

| Symptom | Fix |
|---|---|
| `docker: command not found` | Install Docker Engine/Desktop; on Windows enable WSL2 integration |
| `permission denied ... docker.sock` | Add yourself to the `docker` group (then log out/in) or prefix commands with `sudo` |
| Build fails during `cobc` | Read the compiler error in the build output; `cobol/finance.cbl` must be unmodified |
| `Bind for 127.0.0.1:8080 failed: port is already allocated` | Another container or service owns 8080. Use `-p 127.0.0.1:8081:8080` and run smoke with `BASE=http://127.0.0.1:8081 bash scripts/smoke.sh` |
| `docker: ... Conflict. The container name "/seir-lab02" is already in use` | `docker rm -f seir-lab02`, then rerun |
| `exec format error` | You are on ARM (Apple Silicon) without emulation; keep `--platform linux/amd64` on both build and run, and enable Rosetta/QEMU emulation in Docker Desktop |
| HTTP 422 on POST requests | Amounts must be **nonnegative decimal strings with at most 2 decimals** (e.g. `"1000.00"`, not `1000` or `"1.234"`). The error body names the bad field, e.g. `principal must be a nonnegative decimal string with up to 2 decimal places` |
| `/ready` returns 503 on the GOOD container | Check `docker logs seir-lab02`; the COBOL binary or `libcob4` runtime is broken — rebuild the image |
| `pip install` fails in Step 2 | Use a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`, then retry. Step 2 is optional; Steps 3–7 need no Python on the host |

## Cleanup

```bash
docker stop seir-lab02 seir-lab02-broken 2>/dev/null   # if still running (they auto-remove)
docker rmi seir-cobol-lab02:gate01                     # optional: keep it if you are continuing to Gate 02
```

Nothing was created outside Docker. **Next:** Gate 02 (`../gate02/runbook.md`) deploys this exact application to AWS.
