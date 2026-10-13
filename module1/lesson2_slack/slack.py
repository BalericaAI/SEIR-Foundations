"""Balerica AI Slack notification agent. Run: python slack.py --test"""
import argparse
import os
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv

# =============================================================
# YO STUDENT! INSERT YOUR SLACK WORKSPACE URL HERE OR
# CHEWBACCA BITES YOU!!!!!
# YES, YOU. NOT THE STUDENT NEXT TO YOU.
# =============================================================
SLACK_WORKSPACE_URL = "https://chewbacca.slack.com"

# The workspace URL is NOT the private Incoming Webhook URL.
# Keep SLACK_WEBHOOK_URL in .env, never in Python or GitHub.
load_dotenv()
LEVELS = {"INFO": 0, "WARNING": 1, "ERROR": 2, "CRITICAL": 3}


def send_alert(agent: str, severity: str, message: str, incident_id: str = "") -> bool:
    """Return True when Slack confirms delivery, False if filtered/disabled."""
    if os.getenv("SLACK_ALERTS_ENABLED", "true").lower() not in ("true", "1", "yes"):
        return False
    severity = severity.upper()
    minimum = os.getenv("SLACK_ALERT_SEVERITY", "ERROR").upper()
    if severity not in LEVELS or minimum not in LEVELS:
        raise ValueError("Severity must be INFO, WARNING, ERROR or CRITICAL")
    if LEVELS[severity] < LEVELS[minimum]:
        return False

    workspace = SLACK_WORKSPACE_URL.strip().rstrip("/")
    parsed_workspace = urlparse(workspace)
    if parsed_workspace.scheme != "https" or not parsed_workspace.hostname or not parsed_workspace.hostname.endswith(".slack.com"):
        raise ValueError("Fix SLACK_WORKSPACE_URL. Chewbacca is waiting.")

    webhook = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    parsed_webhook = urlparse(webhook)
    if parsed_webhook.scheme != "https" or parsed_webhook.hostname != "hooks.slack.com" or not parsed_webhook.path.startswith("/services/"):
        raise RuntimeError("Configure SLACK_WEBHOOK_URL in .env; workspace URL alone cannot deliver alerts")
    if not agent.strip() or not message.strip():
        raise ValueError("Agent and message are required")

    text = (f"*BALERICA AI ALERT*\n*Severity:* {severity}\n"
            f"*Agent:* {agent[:100]}\n*Workspace:* {workspace}\n"
            f"*Incident:* {incident_id[:100] or 'N/A'}\n"
            f"*Message:* {message[:2500]}")
    # Never pass credentials or sensitive financial/customer records as message.
    response = requests.post(webhook, json={"text": text}, timeout=10)
    response.raise_for_status()
    if response.text.strip() != "ok":
        raise RuntimeError("Slack did not confirm delivery")
    return True


def main():
    parser = argparse.ArgumentParser(description="Balerica AI Slack notifier")
    parser.add_argument("--test", action="store_true", help="Send a test alert")
    args = parser.parse_args()
    if not args.test:
        parser.print_help()
        return
    try:
        result = send_alert("slack.py", "ERROR", "TEST: Slack is connected. RRRRAAAWWWRRR!", "TEST-001")
        print("SUCCESS: Chewbacca approves!" if result else "SKIPPED: Check alert settings in .env")
    except (ValueError, RuntimeError, requests.RequestException) as exc:
        print(f"FAILED ({type(exc).__name__}). Check workspace URL, webhook, .env and network.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
