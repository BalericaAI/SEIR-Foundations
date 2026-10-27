# Balerica Legacy Bank — Student Runbook

## SEIR Foundations — FastAPI with a COBOL core

---

```text
=========================================================
                BALERICA AI
=========================================================

Congratulations.

You are inside a real Linux server in the AWS cloud.

Today you will accidentally learn COBOL.

Objectives

✓ git (your first clone)

✓ GnuCOBOL

✓ Fixed-width records

✓ FastAPI as a legacy modernization layer

✓ SWIFT MT103 messages

✓ Return codes (the mainframe way)

✓ Agentic AI as a platform helper

If at any point you think:

"I'm going to break something."

Remember...

You cannot break anything in this lab that
re-running one install script will not fix.

Type bravely.
```

---

## Before you start — how to use this runbook

1. **Copy and paste one command at a time.** Do not paste five
   commands at once. Run one, read what comes back, then move on.
2. Every command in this runbook shows the output you should
   expect underneath it. Your output will not match *exactly*
   (your IP address and timestamps are your own) — it just needs
   to look *similar*.
3. If something looks wrong: **stop, read the message on the
   screen, and check the Troubleshooting table** at the bottom.
   Error messages are not insults. They are instructions.
4. The `$` at the start of a line means "type this at the
   prompt." Do not type the `$` itself.

You have already done the hard part: you launched an EC2 instance
and SSH'd into it. Everything below happens inside that SSH
window.

---

## Step 0 — Prove you are really there

Type this:

```bash
whoami
```

Expected output:

```text
ec2-user
```

That is you. You are logged into a computer in an Amazon data
center. Now ask the server where you are standing:

```bash
pwd
```

Expected output:

```text
/home/ec2-user
```

`pwd` means "print working directory" — it shows which folder you
are currently in. You will use it whenever you feel lost. Feeling
lost is normal. `pwd` is the cure.

---

## Step 1 — Get the course code with git

`git` is the tool engineers use to copy and track code.
"Cloning" means downloading a project **and its entire history**
onto your machine. This is your first clone. There will be
thousands more in your career.

First, make sure git is installed:

```bash
sudo dnf install -y git
```

Expected output (the last lines):

```text
Complete!
```

(If it says `Nothing to do`, git was already installed. Also
fine. Moving on.)

Now clone the course repository:

```bash
git clone https://github.com/BalericaAI/SEIR-Foundations.git
```

Expected output:

```text
Cloning into 'SEIR-Foundations'...
remote: Enumerating objects: ...
Receiving objects: 100% ...
Resolving deltas: 100% ..., done.
```

Look at what you just downloaded:

```bash
ls SEIR-Foundations
```

Expected output:

```text
README.md  module1  module2  module3  module4  playbook.md  podcasts.md  python
```

That is the whole course, sitting in your home directory on your
own server. You did that.

---

## Step 2 — Run the installer

The installer builds the entire lab for you: it installs the
COBOL compiler, creates the bank, seeds the accounts, and
compiles the legacy programs. You only run it once.

```bash
bash SEIR-Foundations/module1/lesson1_ec2/API/install/install.sh
```

This takes a few minutes. You will see a lot of text scroll by.
That is normal — read the numbered steps as they go past:

```text
======================================
 BALERICA LEGACY BANK INSTALLER
======================================

[1/9] Updating packages...
[2/9] Installing dependencies...
[3/9] Creating directories...
[4/9] Copying Balerica Bank sources...
[5/9] Creating Python virtual environment...
[6/9] Installing Python packages...
[7/9] Creating database...
[8/9] Compiling COBOL programs...
[9/9] Exporting the ledger for the COBOL core...
  exported 3 account(s) to data/accounts.dat

Installation complete.
```

The two lines that matter are `[8/9] Compiling COBOL programs...`
(with no errors after it) and `Installation complete.`

If the installer stops with an error, run it again — it is safe
to re-run. If it stops twice in the same place, go to
Troubleshooting.

---

## Step 3 — Meet the COBOL core

The installer built your bank at `/opt/balerica-bank`. Go there:

```bash
cd /opt/balerica-bank
```

Look around:

```bash
ls
```

Expected output:

```text
agents  app  cobol  data  logs  swift  venv
```

Now run your first COBOL program. It looks up account `100001`
in the bank's ledger:

```bash
./cobol/bin/account_lookup 100001
```

Expected output:

```text
ACCOUNT=100001
NAME=Alice Johnson
STATUS=ACTIVE
BALANCE=5000.00
CURRENCY=USD
```

You just executed a program written in a language from 1959.
It read a fixed-width ledger file and found Alice.

### Return codes — how mainframes say "how it went"

Every program leaves behind a number when it finishes. Ask for
the last one:

```bash
echo $?
```

Expected output:

```text
0
```

`0` means success. Now look up an account that does not exist,
and check the number again:

```bash
./cobol/bin/account_lookup 999999
echo $?
```

Expected output:

```text
ERROR=ACCOUNT NOT FOUND
ACCOUNT=999999
4
```

The program did not crash. It **told you what happened** with a
return code. This is the mainframe convention, and you will meet
it everywhere in banking:

| Code | Meaning                                              |
|------|------------------------------------------------------|
| 0    | success — account found / payment POSTED             |
| 4    | warning — account not found                          |
| 8    | business rejection — not ACTIVE, zero amount, funds  |
| 12   | environment failure — missing file, malformed args   |

### Post your first payment

```bash
./cobol/bin/payment_post TXN0001 100001 125.50 USD INV-1001
```

Expected output:

```text
TXN=TXN0001
ACCOUNT=100001
AMOUNT=125.50
CURRENCY=USD
STATUS=POSTED
REASON=APPROVED
```

Look at the journal the COBOL program just wrote:

```bash
cat data/payments.dat
```

Expected output:

```text
TXN0001             100001000000012550USDPOSTED  INV-1001
```

Those columns are not misaligned — they are **fixed-width**.
Every byte has an assigned seat (the layout is in the Reference
section below). Notice `000000012550` is 125.50: the decimal
point exists only in the program, never in the file. Welcome to
COBOL.

---

## Step 4 — Start the bank's web API

Now we put the modern face on the legacy core. First, activate
the Python environment the installer prepared (this just means
"use the Python packages installed for this project"):

```bash
cd /opt/balerica-bank
source venv/bin/activate
```

Your prompt will change to show `(venv)` at the front. That is
how you know it worked.

Start the web server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected output:

```text
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Important: this terminal is now busy.** The server runs here
until you stop it. Do not type anything else in this window, and
do not close it. The bank is open.

---

<img width="1603" height="1017" alt="balericalegacybank" src="https://github.com/user-attachments/assets/c8e53112-ddd3-485e-ae4b-ea6beb7f5424" />




## Step 5 — Open a second terminal

You need a second window to talk to your bank. Open a **new**
terminal tab on your laptop and SSH into the same EC2 instance
again, exactly the way you did the first time:

```bash
ssh -i your-key.pem ec2-user@YOUR-EC2-IP
```

You now have two windows into the same server:

```text
Window 1: the bank is running (leave it alone)
Window 2: you, the customer (type here from now on)
```

In the new window, check that the bank is answering:

```bash
curl http://127.0.0.1:8000/status
```

Expected output:

```text
{"platform":"Balerica Legacy Bank","environment":"Amazon EC2","api":"online","core_banking":"GnuCOBOL"}
```

And run the most sophisticated diagnostic in enterprise
computing:

```bash
curl http://127.0.0.1:8000/chewbacca
```

If you receive a Wookiee response, your platform is healthy.

---

## Step 6 — Prove connectivity with SWIFT traffic

SWIFT is the messaging network real banks use to instruct
payments. The traffic generator builds MT103 messages (a "single
customer credit transfer") and fires them at your API. In your
second window:

```bash
cd /opt/balerica-bank
python3 swift/traffic_generator.py --count 10
```

Expected output (your numbers will differ):

```text
============================================================
        BALERICA AI - SWIFT TRAFFIC GENERATOR
============================================================

[1/3] Connectivity check: http://127.0.0.1:8000/status
  OK (200) in 16 ms - core: GnuCOBOL

[2/3] Sending 10 MT103 payment(s)...

  SWIFT-0001  100001      332.63 USD  -> POSTED   APPROVED  (7 ms)
  SWIFT-0002  999999      243.30 USD  -> REJECTED ACCOUNT NOT FOUND  (7 ms)
  ...

[3/3] Traffic report
------------------------------------------------------------
  Sent     : 10
  POSTED   : 7
  REJECTED : 3  (expected - the core must reject bad payments)
  FAILED   : 0  (connectivity or server errors)
  Latency  : avg 6 ms, max 7 ms
------------------------------------------------------------

  CONNECTIVITY CONFIRMED.
  Modern edge and COBOL core are talking.
```

**Read the report carefully — REJECTED is not a failure.** About
a third of the generated traffic is intentionally bad (fake
accounts, impossible amounts), because a bank that cannot reject
a bad payment is worse than one that cannot post a good one. The
only number that must be zero is `FAILED`.

Want to see the raw SWIFT messages?

```bash
python3 swift/traffic_generator.py --count 3 --show-mt103
```

Glance back at Window 1: every payment you just sent is logged
there. That is your server doing business.

---

## Step 7 — Explore from your browser

Your API can also serve the outside world. In a web browser on
your laptop, open (replace with your instance's public IP):

```text
http://YOUR-EC2-IP:8000/docs
```

You should see the Balerica Legacy Bank API console — an
interactive page FastAPI generated for free. Click
`GET /accounts/{account_id}`, press **Try it out**, enter
`100001`, press **Execute**, and watch a COBOL program answer a
browser.

**If the page never loads**, your EC2 Security Group is not
letting port 8000 in. In the AWS Console: EC2 → your instance →
Security tab → Security group → Edit inbound rules → Add rule:
Custom TCP, port `8000`, source `My IP` → Save. Then reload.

---

## Step 8 — Ask Balerica AI for help

The platform carries its own helper agent. Ask it something, in
your second window:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What does return code 8 mean?"}'
```

It answers grounded in your live ledger and recent transactions.
If your instance has an IAM role with Amazon Bedrock access, the
answer comes from a foundation model; if not, the response says
`"source": "offline-knowledge-base"` and the built-in notes
answer instead. **Both are correct behavior** — the offline mode
exists so this lab works before the AWS AI portion is configured.

**Student Challenge:** in the Bedrock console, enable a Claude
model (Model Access), then set `BEDROCK_MODEL_ID` before starting
uvicorn. Newer Claude models need the *inference profile* id
(it starts with `us.`), not the base model id.

### Why `/ask` might silently stay offline

The fallback to `offline-knowledge-base` is silent — no error, no
stack trace in the `curl` output. It hides three separate
requirements, and **all three** must be true before Bedrock will
ever answer:

1. **An IAM role is attached to the instance**, with permission
   to call Bedrock. See `iam/PERMISSIONS.md` in this folder for
   the exact policy and the AWS CLI commands to create and attach
   it (instructor action — role creation needs IAM admin rights).
2. **`AWS_REGION` matches wherever you enabled model access.**
   The code defaults to `us-east-1` if `AWS_REGION` isn't set.
   Enabling Claude in a different region's Bedrock console but
   leaving `AWS_REGION` unset (or set to something else) means
   the SDK calls the wrong region and never finds it.
3. **`BEDROCK_MODEL_ID` is a real model/inference-profile ID**,
   not the shipped placeholder (see the Student Challenge above).

Any one of these being wrong looks identical from the outside:
`"source": "offline-knowledge-base"`. Check all three, in order,
before assuming something else is broken.

---

## Step 9 — Closing time

When you are done for the day: in Window 1, press `Ctrl+C` to
stop the server. The data survives — `data/bank.db` and the
journal keep everything you did. Tomorrow, Step 4 reopens the
bank exactly where you left it.

---

## Reference

### Architecture — what you just built

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

### API endpoints

| Endpoint                | What it does                                |
|-------------------------|---------------------------------------------|
| `GET /status`           | platform heartbeat                          |
| `GET /accounts/{id}`    | runs `account_lookup` (COBOL answers)       |
| `POST /payments`        | runs `payment_post` (COBOL renders verdict) |
| `GET /transactions`     | the SQLite journal                          |
| `POST /ask`             | Balerica AI helper agent                    |
| `GET /chewbacca`        | essential enterprise diagnostics            |

### The fixed-width ledger (`data/accounts.dat`)

```text
Columns  1-6   account id       PIC X(6)
Columns  7-36  customer name    PIC X(30)
Columns 37-44  status           PIC X(8)
Columns 45-56  balance          PIC 9(10)V99   (implied decimal!)
Columns 57-59  currency         PIC X(3)
```

### Troubleshooting

| Symptom                                   | What it means and what to do                                  |
|-------------------------------------------|---------------------------------------------------------------|
| `Permission denied (publickey)` on SSH    | wrong key file or wrong user — use `ec2-user@` and your `.pem` |
| `git: command not found`                  | Step 1's `sudo dnf install -y git` did not run — run it        |
| installer stops with an error             | run it again; it is safe to re-run                             |
| `cobc: command not found`                 | re-run the installer (step 2 installs GnuCOBOL)                |
| `FILE-STATUS=35` / return code 12         | you are in the wrong folder — `cd /opt/balerica-bank` first    |
| `(venv)` missing from the prompt          | run `source venv/bin/activate` again (it is per-terminal)      |
| `command not found: uvicorn`              | activate the venv first (see above)                            |
| generator prints UNREACHABLE              | the server is not running in Window 1 — redo Step 4            |
| `/docs` never loads in the browser        | Security Group — open port 8000 (see Step 7)                   |
| every payment REJECTED                    | read the `REASON=` — the core always explains itself           |
| `/ask` says `offline-knowledge-base`      | expected early in the lab; if you've done the Student Challenge and it's still happening, check all three Bedrock requirements in "Why `/ask` might silently stay offline" above (IAM role, `AWS_REGION`, `BEDROCK_MODEL_ID`) — getting any one wrong looks identical |

Only after checking all of the above are you permitted to blame
AWS.

```text
Chewbacca says:

    "RRRRAAAWWWRRR!"

Translation:

    You cloned a repository.
    You compiled COBOL.
    You ran a bank.
    You generated SWIFT traffic.

    On your first day with git.

    Walk taller.
```
