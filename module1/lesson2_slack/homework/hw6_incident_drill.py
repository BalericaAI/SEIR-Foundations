"""HOMEWORK 6 — Incident drill: send a random (FAKE) bank incident.

You practice: lists, random.choice, building an incident id, realistic alert text.
Run it:       python hw6_incident_drill.py   (run it a few times!)
Everything here is synthetic. Never send real customer data to Slack.
"""
import random

from slack import send_alert

# All fiction. The Balerica compliance department (Chewbacca) insists.
FAKE_INCIDENTS = [
    ("WARNING",  "COBOL batch job BATCH-EOD running 12 minutes longer than usual."),
    ("ERROR",    "payment_post returned code 8: business rejection rate above 5%."),
    ("ERROR",    "FastAPI /payments endpoint responded 500 twice in one minute."),
    ("WARNING",  "SWIFT traffic generator queue depth climbing: 42 messages waiting."),
    ("CRITICAL", "account_lookup returned code 12: ledger file not reachable."),
    ("INFO",     "Nightly ledger backup completed successfully."),
]

severity, description = random.choice(FAKE_INCIDENTS)
incident_id = f"DRILL-{random.randint(1000, 9999)}"

delivered = send_alert(
    agent="hw6_incident_drill.py",
    severity=severity,
    message=f"(DRILL — not real) {description}",
    incident_id=incident_id,
)

print(f"Drew incident {incident_id}: [{severity}] {description}")
print("Delivered!" if delivered else "Skipped by threshold — note WHICH severities get through.")
print("In your notes: which of these fake incidents deserves to wake a human at 3 AM?")
