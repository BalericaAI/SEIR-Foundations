# Balerica Legacy Bank — Lab Runbook

## SEIR Foundations — FastAPI with a COBOL core

---

```text
=========================================================
                BALERICA AI
=========================================================

Congratulations.

Today you will accidentally learn COBOL.

Objectives

✓ GnuCOBOL

✓ Fixed-width records

✓ FastAPI as a legacy modernization layer

✓ SWIFT MT103 messages

✓ Return codes (the mainframe way)

✓ Agentic AI as a platform helper

If at any point you think:

"Nobody uses COBOL anymore."

Remember...

Your paycheck probably cleared through it this morning.
```

---

## Architecture

```text
SWIFT Traffic Generator        (swift/traffic_generator.py)
         |
         v  HTTP / JSON
      FastAPI                  (app/main.py)
         |
         v  subprocess
   cobol_bridge.py             (app/cobol_bridge.py)
         |
         v  argv + KEY=VALUE stdout
account_lookup / payment_post  (cobol/*.cob, compiled by GnuCOBOL)
         |
         v  fixed-width records
accounts.dat / payments.dat    (data/)
         |
         v  export / ingest
       SQLite                  (data/bank.db — system of record)

Side door for confused humans:

      POST /ask  ->  Balerica AI helper  ->  Amazon Bedrock
                     (agents/balerica.py)    (offline fallback built in)
```

---

## 1. Install

From the repository, on your EC2 instance (Amazon Linux 2023):

```bash
bash module1/lesson1_ec2/API/install/install.sh
```

This installs GnuCOBOL + FastAPI, copies the sources to
`/opt/balerica-bank`, seeds the SQLite ledger, compiles both COBOL
programs, and exports the fixed-width ledger file COBOL reads.

---

## 2. Meet the COBOL core (before the web gets involved)

```bash
cd /opt/balerica-bank

./cobol/bin/account_lookup 100001
echo $?        # 0 = found

./cobol/bin/account_lookup 999999
echo $?        # 4 = not found

./cobol/bin/payment_post TXN0001 100001 125.50 USD INV-1001
echo $?        # 0 = POSTED

cat data/payments.dat
```

### Return codes (the mainframe convention)

| Code | Meaning                                              |
|------|------------------------------------------------------|
| 0    | success — account found / payment POSTED             |
| 4    | warning — account not found                          |
| 8    | business rejection — not ACTIVE, zero amount, funds  |
| 12   | environment failure — missing file, malformed args   |

### The fixed-width ledger (`data/accounts.dat`)

```text
Columns  1-6   account id       PIC X(6)
Columns  7-36  customer name    PIC X(30)
Columns 37-44  status           PIC X(8)
Columns 45-56  balance          PIC 9(10)V99   (implied decimal!)
Columns 57-59  currency         PIC X(3)
```

`000000500000` is 5000.00. The decimal point lives in the PICTURE
clause, never in the file. Welcome to COBOL.

---

## 3. Start the bank API

```bash
cd /opt/balerica-bank
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the console: `http://EC2-IP:8000/docs`

| Endpoint                | What it does                                |
|-------------------------|---------------------------------------------|
| `GET /status`           | platform heartbeat                          |
| `GET /accounts/{id}`    | runs `account_lookup` (COBOL answers)       |
| `POST /payments`        | runs `payment_post` (COBOL renders verdict) |
| `GET /transactions`     | the SQLite journal                          |
| `POST /ask`             | Balerica AI helper agent                    |
| `GET /chewbacca`        | essential enterprise diagnostics            |

---

## 4. Prove connectivity with SWIFT traffic

```bash
cd /opt/balerica-bank
python3 swift/traffic_generator.py --count 10
python3 swift/traffic_generator.py --count 5 --show-mt103
```

The generator builds MT103-style messages (`:20:` reference, `:32A:`
date/currency/amount, `:50K:` ordering customer, `:59:` beneficiary),
delivers them to `POST /payments`, and prints a traffic report.

A healthy run shows **both** POSTED and REJECTED verdicts — about 30%
of the generated traffic is intentionally bad, because a core that
cannot reject a payment is worse than one that cannot post it.

---

## 5. Ask Balerica AI for help

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What does return code 8 mean?"}'
```

The helper grounds its answers in the live ledger and recent
transactions. With an IAM role and Bedrock model access it answers
through Amazon Bedrock; without them it falls back to its built-in
knowledge base, so the lab works before the AWS portion is configured.

**Student Challenge:** set `BEDROCK_MODEL_ID` to the model you enabled
in the Bedrock console (Model Access) before starting uvicorn. Newer
Claude models require the *inference profile* id (it starts with
`us.`), not the base model id.

---

## Troubleshooting

| Symptom                              | Likely cause                                             |
|--------------------------------------|----------------------------------------------------------|
| `FILE-STATUS=35` / return code 12    | `data/accounts.dat` missing — run from `/opt/balerica-bank`, re-run install step 9 |
| Generator prints UNREACHABLE         | uvicorn not running, wrong port, or Security Group       |
| Every payment REJECTED               | check `REASON=` — the core always explains itself        |
| `/ask` answers `offline-knowledge-base` | no IAM role or Bedrock model access yet — expected early in the lab |
| `cobc: command not found`            | re-run install step 2                                    |

Only after checking all of the above are you permitted to blame AWS.
