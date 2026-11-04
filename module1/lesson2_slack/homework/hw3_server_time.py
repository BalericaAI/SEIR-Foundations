"""HOMEWORK 3 — Report the server's clock to Slack.

You practice: the datetime module, formatting timestamps, UTC awareness.
Run it:       python hw3_server_time.py
Notice:       EC2 runs on UTC. Is the reported hour the same as your watch?
"""
from datetime import datetime, timezone

from slack import send_alert

now_utc = datetime.now(timezone.utc)
pretty = now_utc.strftime("%A %B %d, %Y at %H:%M:%S %Z")

delivered = send_alert(
    agent="hw3_server_time.py",
    severity="INFO",
    message=f"Time check from EC2: it is {pretty} here. Servers speak UTC!",
    incident_id="HW-003",
)

print("Delivered!" if delivered else "Skipped — check SLACK_ALERT_SEVERITY in .env.")
print(f"Local fact: the server believes it is {pretty}.")
print("In your notes: how many hours apart are server time and YOUR wall clock?")
