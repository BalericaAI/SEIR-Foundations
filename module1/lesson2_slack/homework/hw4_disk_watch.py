"""HOMEWORK 4 — Your first REAL monitoring agent: disk usage.

You practice: shutil.disk_usage, math on bytes, if/else choosing a severity.
Run it:       python hw4_disk_watch.py
This is the actual pattern production monitors use: measure, decide, alert.
"""
import shutil

from slack import send_alert

usage = shutil.disk_usage("/")
percent_used = usage.used / usage.total * 100
free_gb = usage.free / (1024 ** 3)

# The engineering decision: how full is "worth waking a human for"?
if percent_used >= 90:
    severity = "ERROR"
elif percent_used >= 75:
    severity = "WARNING"
else:
    severity = "INFO"

delivered = send_alert(
    agent="hw4_disk_watch.py",
    severity=severity,
    message=(f"Disk check on / : {percent_used:.1f}% used, "
             f"{free_gb:.1f} GB free. Severity chosen by MY code."),
    incident_id="HW-004",
)

print(f"Disk is {percent_used:.1f}% used -> severity {severity}.")
print("Delivered!" if delivered else "Skipped by threshold — that can be correct behavior!")
print("In your notes: why is a quiet INFO here GOOD design, not a failure?")
