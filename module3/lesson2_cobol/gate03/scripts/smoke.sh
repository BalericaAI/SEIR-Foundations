#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8080}"
echo 'Checking /health and /ready'
curl -fsS "$BASE/health"; echo
curl -fsS "$BASE/ready"; echo
curl -fsS "$BASE/v1/info"; echo
curl -fsS -H 'Content-Type: application/json' -d '{"principal":"1000.00","annual_rate_percent":"5.00","years":2}' "$BASE/v1/interest"; echo
curl -fsS -H 'Content-Type: application/json' -d '{"principal":"1200.00","annual_rate_percent":"0.00","months":12}' "$BASE/v1/loan-payment"; echo
curl -fsS -H 'Content-Type: application/json' -d '{"amount":"250.00","available_balance":"500.00"}' "$BASE/v1/transfer/validate"; echo
