"""HOMEWORK 5 — Report CPU load average, like a tiny health.py.

You practice: os.getloadavg, tuples, rounding, comparing against a limit.
Run it:       python hw5_load_check.py
Load average = roughly "how many CPUs' worth of work is queued."
"""
import os

from slack import send_alert

# Three numbers: average load over the last 1, 5, and 15 minutes.
load_1, load_5, load_15 = os.getloadavg()
cpu_count = os.cpu_count() or 1

# Rule of thumb: sustained load above the CPU count means the box is busy.
severity = "WARNING" if load_5 > cpu_count else "INFO"

delivered = send_alert(
    agent="hw5_load_check.py",
    severity=severity,
    message=(f"Load average: {load_1:.2f} (1m), {load_5:.2f} (5m), {load_15:.2f} (15m) "
             f"on {cpu_count} CPU(s)."),
    incident_id="HW-005",
)

print(f"Load: {load_1:.2f} / {load_5:.2f} / {load_15:.2f} on {cpu_count} CPU(s) -> {severity}")
print("Delivered!" if delivered else "Skipped by threshold.")
print("In your notes: what would make this number spike on the Balerica bank?")
