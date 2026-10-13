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

Choose a **stable incident ID** for the same ongoing fault. Repeating the same ID reuses the locally recorded Jira ticket instead of creating a new one; if Slack previously failed, the function tries the Slack delivery again. A different ID creates a new Jira ticket.

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
