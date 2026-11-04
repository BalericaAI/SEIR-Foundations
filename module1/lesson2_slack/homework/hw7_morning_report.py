"""HOMEWORK 7 — Capstone: one combined "morning report" for the whole server.

You practice: combining everything — datetime, disk, load — into one message.
Run it:       python hw7_morning_report.py
This is the shape of a real daily status report a team reads with coffee.
"""
import os
import platform
import shutil
from datetime import datetime, timezone

from slack import send_alert

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
usage = shutil.disk_usage("/")
percent_used = usage.used / usage.total * 100
load_1, _, _ = os.getloadavg()

report = (
    "MORNING REPORT — Balerica AI server\n"
    f"- Time: {now}\n"
    f"- Host: {platform.node()} ({platform.system()} {platform.machine()})\n"
    f"- Python: {platform.python_version()}\n"
    f"- Disk on / : {percent_used:.1f}% used\n"
    f"- Load (1m): {load_1:.2f}\n"
    "- Status: all checks ran. The bank greets the day."
)

delivered = send_alert(
    agent="hw7_morning_report.py",
    severity="INFO",
    message=report,
    incident_id="HW-007",
)

print(report)
print()
print("Delivered!" if delivered else "Skipped — set SLACK_ALERT_SEVERITY=INFO to receive reports.")
print("You just wrote a monitoring report generator. Screenshot the Slack message!")
