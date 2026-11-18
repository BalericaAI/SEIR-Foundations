# SEIR Foundations — Jira + Slack Incident Integration

## Prerequisites

Complete `slack_install.md`, configure `slack.py`, complete `jira_install.md`, configure `jira.py`, and follow both runbooks. Both integrations must work separately **before** running this lab.

## Architecture

```text
health.py / analyze_logs.py / cobol.py
                 |
                 v
             incident.py
                 |
                 +--> jira.py --> Jira issue
                 |
                 +--> slack.py --> Slack alert containing Jira issue URL
```

**Jira records the incident; Slack notifies the engineer.** Jira is called first so Slack can link to the created issue.

## Installation on student EC2

Place `incident.py`, `jira.py`, and `slack.py` together in the Balerica AI agents directory. Use the same `.env` file for both integrations. From that directory:

```bash
python3 -m pip install requests python-dotenv
mkdir -p data
python3 slack.py --test
python3 jira.py --verify
python3 incident.py --dry-run
python3 incident.py --test
```

`--test` **creates a real test Jira ticket and sends a real Slack notification**. Confirm the Slack alert includes a clickable Jira ticket URL. Jira must have permissions to create issues and Slack must have an authorized Incoming Webhook.

Example `.env` (replace placeholders; never commit the populated file):

```dotenv
JIRA_SITE_URL=https://YOUR-SITE.atlassian.net
JIRA_EMAIL=student@example.com
JIRA_API_TOKEN=YOUR_PRIVATE_TOKEN
JIRA_PROJECT_KEY=BAI
JIRA_ISSUE_TYPE=Task
JIRA_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/REPLACE/ME/PRIVATELY
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
INCIDENT_STATE_DB=data/incident_state.db
```

Also edit the student-facing `SLACK_WORKSPACE_URL` in `slack.py` as instructed. The workspace URL is **not** the webhook URL.

## Call from a monitoring agent

So far you have run `incident.py` as a command with `--test`. In real use, a monitoring agent (a program such as `health.py` that watches your application) calls the `report_incident` **function** from inside its own Python code when it detects a problem. The block below is that function call — it is **Python code, not a shell command**, so typing it at the Linux `$` prompt will not work. Here is how to execute it yourself, step by step.

**Before you start:** this is a *real* run, not a drill. Executing it creates one actual Jira ticket and sends one actual Slack alert. That is the point — do it once, then verify both.

**Step 1 — Go to the lab directory and activate your environment.** The code must run from the directory that contains `incident.py`, `jira.py`, `slack.py`, and your `.env`, with the same virtual environment you used for the earlier tests:

```bash
cd ~/your-lab-directory        # wherever those four files live — `ls` to confirm
source .venv/bin/activate      # or venv/bin/activate, whichever you created
ls incident.py jira.py slack.py .env
```

**Step 2 — Create a small Python file for the call.** Open a new file in the same directory:

```bash
nano my_first_incident.py
```

Paste in exactly this, then save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano):

```python
from incident import report_incident

result = report_incident(
    agent='health.py',
    severity='CRITICAL',
    message='Synthetic test: application process is unavailable',
    incident_id='EC2-PROCESS-DOWN-001',
    evidence='Health check returned unhealthy',
    recommendation='Inspect process status and service logs'
)
print(result)
```

Line by line: the `import` loads the `report_incident` function from `incident.py` (that is why the files must be in the same directory). The call then hands it five pieces of information — which agent noticed the problem, how severe it is, what happened, a **stable ID** for this particular fault, plus the evidence and a suggested next step. The function creates the Jira ticket, sends the Slack alert, and hands back a Python dictionary describing what it did, which `print(result)` shows you.

**Step 3 — Run it:**

```bash
python3 my_first_incident.py
```

Expected output (your key and site will differ):

```python
{'incident_id': 'EC2-PROCESS-DOWN-001', 'jira_key': 'BAI-4', 'jira_url': 'https://YOUR-SITE.atlassian.net/browse/BAI-4', 'jira_created': True, 'slack_status': 'sent'}
```

Read the dictionary before celebrating: `jira_created: True` means a new ticket was filed, `jira_url` is the ticket, and `slack_status: 'sent'` means the alert went out. Now verify like an engineer — open the `jira_url` in your browser, find the ticket on your board (`jira_runbook.md` Step 5 if it hides in the Backlog), and check `#balerica-alerts` for the alert containing that same link.

**Step 4 — Run it a second time, on purpose:**

```bash
python3 my_first_incident.py
```

This time you should see `'jira_created': False` and `'slack_status': 'already_sent'` — and **no new ticket** on your board. That is the deduplication working: the incident ID `EC2-PROCESS-DOWN-001` was already recorded in the local state database (`data/incident_state.db`), so the same ongoing fault does not flood Jira with duplicates. This two-run exercise is the fastest way to *see* why stable incident IDs matter.

Choose a **stable incident ID** for the same ongoing fault. Repeating the same ID reuses the locally recorded Jira ticket instead of creating a new one; if Slack previously failed, the function tries the Slack delivery again. A different ID creates a new Jira ticket.

When you are done experimenting, you can delete `my_first_incident.py`; a real monitoring agent would simply contain the same `import` and function call inside its detection logic.

## Claude Code student prompts

- "Read `incident_integration.md`, `incident.py`, `jira.py`, and `slack.py`. Explain the end-to-end data flow without changing any files."
- "My Jira ticket exists but Slack did not receive the alert. Diagnose using configuration and return statuses. Never print secrets."
- "Explain why stable incident IDs matter and show me how to verify that a second call doesn't create another Jira ticket."
- "Review the incident payload for secrets and customer information before we send it."

## Limitations and safety

- This starter workflow is **single-process classroom code**, not a production-grade distributed incident service. Simultaneous writers, crashes between Jira creation and local persistence, and state database deletion can still cause duplicates. Production needs a durable queue, distributed idempotency, retries, and reconciliation.
- `slack.py` filters notifications below `SLACK_ALERT_SEVERITY`. Use `ERROR` or `CRITICAL` for this lab.
- Keep `.env` and `data/incident_state.db` out of Git (`.gitignore`). Never paste tokens, webhook URLs, or real financial/customer data into Slack, Jira, GitHub, or Claude Code.
- A Slack delivery failure does **not** delete the Jira issue. Repeat the same incident ID after correcting the problem to retry Slack.
- Do not automatically remediate production systems from LLM recommendations; require engineer verification.

**Chewbacca's final assessment:** RRRRAAAWWWRRR! If your Slack alert has no Jira link, go read the runbook again.
