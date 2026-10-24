#!/usr/bin/env python3
"""
=========================================================
                    BALERICA AI
              Balerica Legacy Bank v1.0
                   COBOL BRIDGE
=========================================================

SEIR Foundations

Purpose

This module is the border crossing between two worlds:

    Modern world            Legacy world
    ------------            ------------
    FastAPI                 GnuCOBOL
    JSON                    fixed-width records
    SQLite                  flat files
    Python                  PIC 9(10)V99

Responsibilities

- Export the SQLite accounts table to data/accounts.dat
  (the fixed-width ledger COBOL reads)
- Execute the COBOL binaries and parse their KEY=VALUE output
- Record POSTED payments back into SQLite

This is not a toy pattern. Real mainframe integration is
built on exactly this kind of batch file handoff.

=========================================================
"""

import os
import sqlite3
import subprocess
import time
from pathlib import Path

# ---------------------------------------------------------
# BANK_HOME is where install.sh placed the bank.
# Override it with an environment variable for local labs.
# ---------------------------------------------------------

BANK_HOME = Path(os.environ.get("BANK_HOME", "/opt/balerica-bank"))

DB_PATH = BANK_HOME / "data" / "bank.db"
ACCOUNTS_DAT = BANK_HOME / "data" / "accounts.dat"


# ---------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# Chewbacca says:
#
# "Rrrrrrrgh..."
#
# Translation:
#
# COBOL does not read SQLite.
#
# COBOL reads records where every byte
# has an assigned seat.
#
# This function writes those records.
#
# Layout (59 bytes per record):
#
#   account id    X(6)
#   customer name X(30)
#   status        X(8)
#   balance       9(10)V99   <- 12 digits, implied decimal
#   currency      X(3)
# ---------------------------------------------------------

def export_accounts():
    conn = connect()
    rows = conn.execute(
        "SELECT account_id, customer_name, status, balance, currency "
        "FROM accounts ORDER BY account_id"
    ).fetchall()
    conn.close()

    lines = []
    for row in rows:
        cents = int(round(row["balance"] * 100))
        lines.append(
            f"{row['account_id']:<6.6}"
            f"{row['customer_name']:<30.30}"
            f"{row['status']:<8.8}"
            f"{cents:012d}"
            f"{row['currency']:<3.3}"
        )

    ACCOUNTS_DAT.write_text("\n".join(lines) + "\n")
    return len(lines)


# ---------------------------------------------------------
# Chewbacca says:
#
# "RAAWR!"
#
# Translation:
#
# subprocess.run() is how Python knocks
# on COBOL's door.
#
# cwd=BANK_HOME matters: the COBOL programs
# open data/accounts.dat relative to it.
# ---------------------------------------------------------

def run_cobol(program, *args):
    binary = BANK_HOME / "cobol" / "bin" / program

    if not binary.exists():
        raise FileNotFoundError(
            f"{binary} not found. Did you run install.sh?"
        )

    result = subprocess.run(
        [str(binary), *args],
        cwd=BANK_HOME,
        capture_output=True,
        text=True,
        timeout=10,
    )

    # COBOL speaks KEY=VALUE lines. Parse them into a dict.
    fields = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip().lower()] = value.strip()

    fields["return_code"] = result.returncode
    return fields


# ---------------------------------------------------------
# Account lookup
#
#   HTTP GET /accounts/100001
#        |
#        v
#   ./cobol/bin/account_lookup 100001
# ---------------------------------------------------------

def account_lookup(account_id):
    export_accounts()
    return run_cobol("account_lookup", account_id)


# ---------------------------------------------------------
# Payment posting
#
#   1. refresh the ledger file COBOL validates against
#   2. let COBOL render its verdict (and write the journal)
#   3. if POSTED: debit the account in SQLite
#
# SQLite is the system of record.
# accounts.dat is the legacy interface to it.
# ---------------------------------------------------------

def new_txn_id():
    # 17 digits of the nanosecond clock: unique even under
    # burst traffic, and exactly fills PIC X(20) with "TXN".
    return f"TXN{time.time_ns() % 10 ** 17:017d}"


def post_payment(account_id, amount, currency, reference):
    export_accounts()

    # GnuCOBOL OPEN EXTEND fails with file status 35 when the
    # journal does not exist yet. An empty file is a valid journal.
    payments = BANK_HOME / "data" / "payments.dat"
    payments.parent.mkdir(parents=True, exist_ok=True)
    payments.touch(exist_ok=True)

    txn_id = new_txn_id()

    # COBOL argument parsing splits on spaces.
    # References travel with dashes instead.
    safe_reference = reference.replace(" ", "-")[:16] or "NONE"

    verdict = run_cobol(
        "payment_post",
        txn_id,
        account_id,
        f"{amount:.2f}",
        currency,
        safe_reference,
    )

    conn = connect()
    conn.execute(
        "INSERT INTO transactions "
        "(transaction_id, account_id, amount, currency, status, reference) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            txn_id,
            account_id,
            amount,
            currency,
            verdict.get("status", "UNKNOWN"),
            safe_reference,
        ),
    )

    if verdict.get("status") == "POSTED":
        conn.execute(
            "UPDATE accounts SET balance = balance - ? "
            "WHERE account_id = ?",
            (amount, account_id),
        )

    conn.commit()
    conn.close()

    if verdict.get("status") == "POSTED":
        export_accounts()

    return verdict


def list_transactions(limit=50):
    conn = connect()
    rows = conn.execute(
        "SELECT transaction_id, account_id, amount, currency, "
        "status, reference, created_at "
        "FROM transactions ORDER BY created_at DESC, transaction_id DESC "
        "LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
