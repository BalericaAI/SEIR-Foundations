"""HOMEWORK 1 — Your first custom Slack alert.

You practice: calling a function with your own arguments, f-strings.
Run it:       python hw1_hello_slack.py
You should see: your greeting appear in #balerica-alerts.
"""
from slack import send_alert

# Put YOUR name here. Yes, yours. Chewbacca is watching.
MY_NAME = "REPLACE WITH YOUR NAME"

if "REPLACE" in MY_NAME:
    raise SystemExit("CHOMP! Edit MY_NAME in this file first (nano hw1_hello_slack.py).")

delivered = send_alert(
    agent="hw1_hello_slack.py",
    severity="INFO",
    message=f"Hello from {MY_NAME}! I sent this alert myself, from my own EC2 instance.",
    incident_id="HW-001",
)

if delivered:
    print("Delivered! Go look at #balerica-alerts. That message is yours.")
else:
    print("Skipped. Check .env: SLACK_ALERTS_ENABLED must be true and "
          "SLACK_ALERT_SEVERITY=INFO (see homework README).")
