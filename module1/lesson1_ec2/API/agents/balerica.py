#!/usr/bin/env python3
"""
=========================================================
                    BALERICA AI
              Balerica Legacy Bank v1.0
                  HELPER AGENT
=========================================================

SEIR Foundations

Purpose

This is the first Balerica AI agent embedded inside a
running platform instead of a terminal.

It answers questions about the Legacy Bank lab:

- COBOL return codes and file-status errors
- what POSTED / REJECTED verdicts mean
- what the SWIFT traffic generator is doing
- the state of the ledger

How it thinks

1. Gather context from the live system
   (recent transactions, account summary).

2. Ask Amazon Bedrock, grounding the model
   with that context.

3. If Bedrock is unreachable (no IAM role, no model
   access, no internet), fall back to the built-in
   knowledge base. The lab keeps working either way.

Chewbacca says:

    "Rrrrrrrgh..."

Translation:

    A helper that dies when the cloud blinks
    is not a helper.

    Always have a fallback.

=========================================================
"""

import json
import os
import sqlite3
from pathlib import Path

AGENT = True
NAME = "Balerica Bank Helper"
DESCRIPTION = "Explains the Legacy Bank lab: COBOL, SWIFT, verdicts."

BANK_HOME = Path(os.environ.get("BANK_HOME", "/opt/balerica-bank"))
DB_PATH = BANK_HOME / "data" / "bank.db"

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-sonnet-4.X",  # Student Challenge: set the real one
)
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1000"))


# ---------------------------------------------------------
# Context gathering
#
# An agent that cannot see the system
# can only answer in generalities.
# ---------------------------------------------------------

def gather_context():
    context = {"accounts": [], "recent_transactions": []}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        context["accounts"] = [
            dict(row) for row in conn.execute(
                "SELECT account_id, customer_name, status, balance, "
                "currency FROM accounts ORDER BY account_id"
            )
        ]
        context["recent_transactions"] = [
            dict(row) for row in conn.execute(
                "SELECT transaction_id, account_id, amount, status, "
                "reference FROM transactions "
                "ORDER BY created_at DESC LIMIT 10"
            )
        ]
        conn.close()
    except Exception:
        pass

    return context


# ---------------------------------------------------------
# The built-in knowledge base (offline fallback)
# ---------------------------------------------------------

RETURN_CODES = """COBOL return codes in this lab (the mainframe convention):
  0  = success (account found / payment POSTED)
  4  = warning (account not found)
  8  = business rejection (not ACTIVE, zero amount, insufficient funds)
  12 = environment failure (missing file, malformed arguments)
Check them in the shell with: echo $?"""

TOPICS = {
    "return code": RETURN_CODES,
    "rc": RETURN_CODES,
    "rejected": (
        "A REJECTED verdict comes from payment_post.cob with a REASON:\n"
        "  ACCOUNT NOT FOUND    - the id is not in data/accounts.dat\n"
        "  ACCOUNT NOT ACTIVE   - the ledger status is not ACTIVE\n"
        "  AMOUNT MUST BE GREATER THAN ZERO\n"
        "  INSUFFICIENT FUNDS   - amount exceeds the ledger balance\n"
        "Rejections are still written to the journal. Banks append; "
        "they never erase."
    ),
    "swift": (
        "SWIFT is the messaging network banks use to instruct payments. "
        "An MT103 is a single customer credit transfer. The traffic "
        "generator builds MT103-style messages (fields :20: reference, "
        ":32A: date/currency/amount, :50K: ordering customer, :59: "
        "beneficiary) and delivers them to POST /payments to prove "
        "connectivity between the modern edge and the COBOL core."
    ),
    "mt103": (
        "MT103 is the SWIFT message type for a single customer credit "
        "transfer. Key fields: :20: sender reference, :32A: value date + "
        "currency + amount, :50K: ordering customer, :59: beneficiary."
    ),
    "cobol": (
        "The bank core is two GnuCOBOL programs:\n"
        "  account_lookup.cob - scans data/accounts.dat (fixed-width, "
        "59 bytes per record) for one account\n"
        "  payment_post.cob   - validates a payment and appends the "
        "verdict to data/payments.dat (OPEN EXTEND = append only)\n"
        "Recompile after editing: cobc -x -o cobol/bin/<name> "
        "cobol/<name>.cob"
    ),
    "file status": (
        "COBOL FILE STATUS '35' means the file does not exist; '37' or "
        "'39' usually mean a mode or attribute mismatch. In this lab a "
        "failed OPEN surfaces as return code 12. Make sure you run the "
        "binaries from BANK_HOME so data/accounts.dat resolves."
    ),
    "fixed width": (
        "accounts.dat layout (59 bytes): id X(6), name X(30), status "
        "X(8), balance 9(10)V99 (12 digits, implied decimal point), "
        "currency X(3). '000000500000' means 5000.00 - the decimal "
        "point exists only in the PICTURE clause, never in the file."
    ),
}


def offline_answer(question, context):
    lowered = question.lower()

    matched = [text for key, text in TOPICS.items() if key in lowered]
    # Deduplicate while keeping order (aliases share answers).
    seen = set()
    unique = []
    for text in matched:
        if text not in seen:
            seen.add(text)
            unique.append(text)

    parts = unique or [
        "I could not reach Amazon Bedrock, and that question is outside "
        "my built-in notes. Topics I can explain offline: return codes, "
        "rejected payments, SWIFT, MT103, COBOL, file status, fixed "
        "width records."
    ]

    if context["accounts"]:
        ledger = ", ".join(
            f"{a['account_id']} ({a['status']}, {a['balance']:.2f} "
            f"{a['currency']})"
            for a in context["accounts"]
        )
        parts.append(f"Current ledger: {ledger}.")

    if context["recent_transactions"]:
        posted = sum(
            1 for t in context["recent_transactions"]
            if t["status"] == "POSTED"
        )
        parts.append(
            f"Last {len(context['recent_transactions'])} transactions: "
            f"{posted} POSTED, "
            f"{len(context['recent_transactions']) - posted} other."
        )

    return "\n\n".join(parts)


# ---------------------------------------------------------
# Bedrock path
# ---------------------------------------------------------

def bedrock_answer(question, context):
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)

    system_prompt = (
        "You are Balerica AI, the helper agent inside the SEIR "
        "Foundations 'Legacy Bank' lab: a FastAPI front end over a "
        "GnuCOBOL core (account_lookup.cob, payment_post.cob) with "
        "fixed-width flat files and a SQLite system of record, tested "
        "by a SWIFT MT103 traffic generator. Return codes: 0 ok, 4 not "
        "found, 8 business rejection, 12 environment failure. Answer "
        "the student's question concisely and concretely. Live system "
        f"context: {json.dumps(context, default=str)}"
    )

    request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": question}],
    }

    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request),
    )

    body = json.loads(response["body"].read())
    return body["content"][0]["text"]


# ---------------------------------------------------------
# Public entry point
# ---------------------------------------------------------

def ask(question):
    context = gather_context()

    try:
        return {
            "response": bedrock_answer(question, context),
            "source": "amazon-bedrock",
        }
    except Exception:
        return {
            "response": offline_answer(question, context),
            "source": "offline-knowledge-base",
        }


def run(question):
    """CLI entry point, same contract as the other Balerica agents."""
    answer = ask(question)
    print()
    print("=" * 60)
    print(f"Balerica AI ({answer['source']})")
    print("=" * 60)
    print()
    print(answer["response"])
    print()


if __name__ == "__main__":
    run(input("Ask Balerica AI about the Legacy Bank lab:\n\n> "))
