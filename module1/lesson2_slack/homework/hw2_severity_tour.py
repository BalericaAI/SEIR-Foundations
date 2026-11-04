"""HOMEWORK 2 — Tour all four severities and watch the filter work.

You practice: loops, how SLACK_ALERT_SEVERITY in .env filters alerts.
Run it:       python hw2_severity_tour.py
Experiment:   run it once with SLACK_ALERT_SEVERITY=INFO in .env, then again
              with SLACK_ALERT_SEVERITY=ERROR. Compare what reaches Slack!
"""
from slack import send_alert

SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]

for severity in SEVERITIES:
    delivered = send_alert(
        agent="hw2_severity_tour.py",
        severity=severity,
        message=f"This is what a {severity} alert looks like.",
        incident_id="HW-002",
    )
    # The filter decides: anything below your .env threshold is skipped
    # BEFORE any message is sent. That is why a team can keep INFO quiet.
    status = "DELIVERED to Slack" if delivered else "skipped by your threshold"
    print(f"{severity:8} -> {status}")

print("\nQuestion to answer in your notes: which severities arrived, and WHY those?")
