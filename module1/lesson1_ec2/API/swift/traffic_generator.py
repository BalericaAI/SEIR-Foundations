#!/usr/bin/env python3
"""
=========================================================
                    BALERICA AI
              Balerica Legacy Bank v1.0
             SWIFT TRAFFIC GENERATOR
=========================================================

SEIR Foundations

Purpose

Prove connectivity through the whole stack:

    traffic_generator.py
            |
            v   HTTP (the modern edge)
         FastAPI
            |
            v   subprocess (the border crossing)
      payment_post.cob
            |
            v   fixed-width records (the legacy core)
       payments.dat

Each message is built as a SWIFT MT103 (single customer
credit transfer), the format banks have exchanged for
decades, then delivered to POST /payments as JSON.

Usage

    python3 traffic_generator.py
    python3 traffic_generator.py --count 25 --delay 0.2
    python3 traffic_generator.py --host 127.0.0.1 --port 8000
    python3 traffic_generator.py --show-mt103

No third-party packages required. Standard library only.

Chewbacca says:

    "RRRRRAAAAAAAAAAWWWWWRRRR!"

Translation:

    If the generator's report shows POSTED payments,
    you have connected 2026 to 1959.

    Be proud.

=========================================================
"""

import argparse
import json
import random
import time
import urllib.error
import urllib.request
from datetime import date

# Accounts seeded by install.sh. 999999 does not exist:
# a healthy core must also reject correctly.
KNOWN_ACCOUNTS = ["100001", "100002", "100003"]
BAD_ACCOUNT = "999999"

CUSTOMERS = [
    "ACME LOGISTICS LLC",
    "WOOKIEE IMPORTS LTD",
    "TATOOINE WATER CO",
    "BALERICA HOLDINGS",
]


# ---------------------------------------------------------
# Build an MT103-style message
#
# :20:  sender's reference
# :23B: bank operation code
# :32A: value date + currency + amount (comma decimal!)
# :50K: ordering customer
# :59:  beneficiary (account on the first line)
# :71A: who pays the charges
# ---------------------------------------------------------

def build_mt103(reference, account_id, amount, currency, customer):
    value_date = date.today().strftime("%y%m%d")
    swift_amount = f"{amount:.2f}".replace(".", ",")

    return (
        "{1:F01BALERICAXXXX0000000000}"
        "{2:I103SWIFTGENXXXXN}"
        "{4:\n"
        f":20:{reference}\n"
        ":23B:CRED\n"
        f":32A:{value_date}{currency}{swift_amount}\n"
        f":50K:{customer}\n"
        f":59:/{account_id}\n"
        "BALERICA BANK CUSTOMER\n"
        ":71A:SHA\n"
        "-}"
    )


def build_payment(sequence, invalid=False):
    account_id = BAD_ACCOUNT if invalid else random.choice(KNOWN_ACCOUNTS)
    # Occasionally oversized, so INSUFFICIENT FUNDS appears too.
    amount = (
        round(random.uniform(500000, 900000), 2)
        if invalid and random.random() < 0.5
        else round(random.uniform(5, 450), 2)
    )
    if invalid and amount > 500000:
        account_id = random.choice(KNOWN_ACCOUNTS)

    reference = f"SWIFT-{sequence:04d}"
    customer = random.choice(CUSTOMERS)

    payload = {
        "reference": reference,
        "account_id": account_id,
        "amount": amount,
        "currency": "USD",
        "ordering_customer": customer,
        "beneficiary": "BALERICA BANK CUSTOMER",
    }
    mt103 = build_mt103(reference, account_id, amount, "USD", customer)
    return payload, mt103


# ---------------------------------------------------------
# HTTP plumbing (standard library only)
# ---------------------------------------------------------

def http_json(method, url, payload=None, timeout=10):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read())
            return response.status, body, time.perf_counter() - started
    except urllib.error.HTTPError as error:
        body = json.loads(error.read() or b"{}")
        return error.code, body, time.perf_counter() - started


def main():
    parser = argparse.ArgumentParser(
        description="SWIFT MT103 traffic generator for Balerica Legacy Bank"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--count", type=int, default=10,
                        help="number of payments to send (default 10)")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="seconds between payments (default 0.1)")
    parser.add_argument("--invalid-rate", type=float, default=0.3,
                        help="fraction of intentionally bad payments "
                             "(default 0.3)")
    parser.add_argument("--show-mt103", action="store_true",
                        help="print each raw MT103 message")
    args = parser.parse_args()

    base = f"http://{args.host}:{args.port}"

    print()
    print("=" * 60)
    print("        BALERICA AI - SWIFT TRAFFIC GENERATOR")
    print("=" * 60)

    # ----------------------------------------------------
    # Step 1: connectivity check before sending traffic.
    # ----------------------------------------------------
    print(f"\n[1/3] Connectivity check: {base}/status")
    try:
        status_code, body, elapsed = http_json("GET", f"{base}/status")
    except Exception as error:
        print(f"\n  UNREACHABLE: {error}")
        print("\n  Checklist (in Chewbacca-approved order):")
        print("    1. Is uvicorn running?")
        print("    2. Is it bound to 0.0.0.0?")
        print("    3. Is port 8000 open in the Security Group?")
        print("    4. Only now may you blame AWS.")
        raise SystemExit(1)

    print(f"  OK ({status_code}) in {elapsed * 1000:.0f} ms "
          f"- core: {body.get('core_banking', '?')}")

    # ----------------------------------------------------
    # Step 2: send the MT103 traffic.
    # ----------------------------------------------------
    print(f"\n[2/3] Sending {args.count} MT103 payment(s)...\n")

    results = {"POSTED": 0, "REJECTED": 0, "FAILED": 0}
    latencies = []

    for sequence in range(1, args.count + 1):
        invalid = random.random() < args.invalid_rate
        payload, mt103 = build_payment(sequence, invalid=invalid)

        if args.show_mt103:
            print(mt103)
            print()

        try:
            status_code, body, elapsed = http_json(
                "POST", f"{base}/payments", payload
            )
            latencies.append(elapsed)

            detail = body.get("detail", body)
            verdict = detail.get("status", "UNKNOWN")
            reason = detail.get("reason", "")

            results[verdict if verdict in results else "FAILED"] += 1
            print(f"  {payload['reference']}  {payload['account_id']}  "
                  f"{payload['amount']:>10.2f} USD  -> {verdict:<8} "
                  f"{reason}  ({elapsed * 1000:.0f} ms)")
        except Exception as error:
            results["FAILED"] += 1
            print(f"  {payload['reference']}  -> FAILED   {error}")

        time.sleep(args.delay)

    # ----------------------------------------------------
    # Step 3: the report.
    # ----------------------------------------------------
    print(f"\n[3/3] Traffic report")
    print("-" * 60)
    total = args.count
    print(f"  Sent     : {total}")
    print(f"  POSTED   : {results['POSTED']}")
    print(f"  REJECTED : {results['REJECTED']}  "
          "(expected - the core must reject bad payments)")
    print(f"  FAILED   : {results['FAILED']}  "
          "(connectivity or server errors)")
    if latencies:
        print(f"  Latency  : avg {sum(latencies) / len(latencies) * 1000:.0f} ms"
              f", max {max(latencies) * 1000:.0f} ms")
    print("-" * 60)

    if results["FAILED"] == 0:
        print("\n  CONNECTIVITY CONFIRMED.")
        print("  Modern edge and COBOL core are talking.")
        print("\n  Chewbacca says: \"RRRRAAAWWWRRR!\"")
        print("  Translation: 2026 and 1959 are now friends.\n")
    else:
        print("\n  Some messages failed. Ask Balerica AI:")
        print(f"    curl -X POST {base}/ask "
              "-H 'Content-Type: application/json' "
              "-d '{\"question\": \"Why did my payments fail?\"}'\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
