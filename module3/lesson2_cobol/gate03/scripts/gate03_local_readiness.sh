#!/usr/bin/env bash
# Gate 03 Step 5 - LOCAL broken-COBOL readiness demonstration. No AWS calls,
# no ECS changes. Builds the Gate 02 application image, runs it with an
# invalid COBOL_BIN, and proves /health stays 200 while /ready returns 503.
set -euo pipefail
for cmd in docker curl; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done

# Gate 03 ships no application code; the image comes from the sibling Gate 02
# folder (same app the stack runs). Override APP_DIR if your layout differs.
DEFAULT_APP_DIR="$(cd "$(dirname "$0")/../../gate02" 2>/dev/null && pwd)" || DEFAULT_APP_DIR=""
APP_DIR="${APP_DIR:-$DEFAULT_APP_DIR}"
[[ -n "$APP_DIR" && -f "$APP_DIR/Dockerfile" ]] || { echo 'STOP: cannot find the Gate 02 application (expected ../gate02 next to gate03). Set APP_DIR to the folder containing its Dockerfile.' >&2; exit 2; }

HOST_PORT="${HOST_PORT:-8099}"   # avoid clashing with a Gate 01 container on 8080
IMAGE=seir-cobol-lab02:gate03-readiness
CONTAINER=seir-lab02-gate03-readiness
cleanup() { docker rm -f "$CONTAINER" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "Building $IMAGE from $APP_DIR"
docker build --platform linux/amd64 -t "$IMAGE" "$APP_DIR"
cleanup
docker run -d --platform linux/amd64 --name "$CONTAINER" \
  -e COBOL_BIN=/not/a/real/finance \
  -p "127.0.0.1:$HOST_PORT:8080" "$IMAGE" >/dev/null

BASE="http://127.0.0.1:$HOST_PORT"
echo "Waiting for FastAPI on $BASE ..."
for _ in $(seq 1 15); do
  curl -fsS -o /dev/null "$BASE/health" 2>/dev/null && break
  sleep 1
done

HEALTH="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health")"
READY="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/ready")"
echo "/health -> HTTP $HEALTH (expected 200: the web process is alive)"
echo "/ready  -> HTTP $READY (expected 503: the COBOL dependency is broken)"
if [[ "$HEALTH" == "200" && "$READY" == "503" ]]; then
  echo 'PASS: an ALB health check on /ready would mark this target unhealthy; /health alone would not.'
else
  echo 'FAIL: expected /health=200 and /ready=503. Check docker logs for the container.' >&2
  docker logs "$CONTAINER" >&2 || true
  exit 1
fi
