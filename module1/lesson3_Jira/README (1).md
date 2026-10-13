# SEIR Foundations — Balerica AI Incident Integration Lab

**Lab:** Slack + Jira Incident Reporting  
**Platform:** Student EC2, Python, Slack Free, Jira Cloud Free  
**AI assistant:** Claude Code (required)  
**Goal:** Detect or simulate an operational incident, create a Jira issue, and notify the engineer through Slack with a link to the issue.

> **CHEWBACCA'S PRE-FLIGHT INSPECTION:** RRRRAAAWWWRRR! If you skip the instructions and then announce that you are confused, Chewbacca will inspect your `.env` file first. He is especially interested in students who deleted yesterday's Slack settings.

## 1. What you are building

```text
EC2 / Balerica AI monitoring agent
              |
              v
          incident.py
              |
       +------+------+
       |             |
       v             v
    jira.py        slack.py
       |             |
       v             v
 Jira Cloud       Slack channel
 incident issue   alert + Jira link
```

`incident.py` calls Jira first to obtain an issue URL, then sends a Slack alert. Its local SQLite state database tracks incident IDs to reduce duplicate Jira issues. **Jira is the incident record; Slack is the notification channel.**

This is a controlled classroom lab, not an unattended production incident-response service.

## 2. Prerequisites — finish these BEFORE starting

- [ ] Complete `slack_install.md`; create and sign in to your own Slack Free workspace.
- [ ] Configure `slack.py` and its `SLACK_WORKSPACE_URL` variable. Your workspace URL must begin with `https://`.
- [ ] Complete the Slack runbook and confirm `python3 slack.py --test` posts a message.
- [ ] Complete `jira_install.md`; create and sign in to your own Jira Cloud Free site and project.
- [ ] Configure `jira.py` and complete the Jira runbook.
- [ ] Confirm `python3 jira.py --verify` succeeds.
- [ ] Have access to your EC2 instance, Python 3, pip, and Claude Code.
- [ ] Read `incident_integration.md` and keep `troubleshooting.md` available.

**Stop here if either individual integration does not work.** Combining two broken integrations will not repair either one.

## 3. Files and responsibilities

| File | Responsibility |
|---|---|
| `slack_install.md` | Slack account, workspace, and webhook setup |
| `slack.py` | Send notifications using the Slack Incoming Webhook |
| `jira_install.md` | Jira Cloud account, site, and project setup |
| `jira.py` | Verify Jira connectivity and create incident issues |
| `incident.py` | Coordinate Jira issue creation and Slack notification |
| `incident_integration.md` | Integration installation and invocation details |
| `troubleshooting.md` | Common failures and diagnostic questions |
| `.env` | **Private** credentials and configuration; never commit |
| `data/incident_state.db` | Locally persisted incident state, created as needed |

Run commands from the directory containing the three Python modules and your `.env` file. Do not replace your existing `.env` when adding Jira settings.

## 4. Student configuration checklist

Verify the following **exact names**. The sample values below are examples, not credentials.

| Variable | Location | Required behavior |
|---|---|---|
| `SLACK_WORKSPACE_URL` | At top of `slack.py` | Your actual workspace URL, not the webhook |
| `SLACK_WEBHOOK_URL` | `.env` | Secret Slack Incoming Webhook URL |
| `SLACK_ALERTS_ENABLED` | `.env` | `true` for testing |
| `SLACK_ALERT_SEVERITY` | `.env` | `ERROR` for testing |
| `SLACK_ALERT_CHANNEL` | `.env`, optional | Informational only; webhook controls actual channel |
| `JIRA_SITE_URL` | `.env` | Your `https://...atlassian.net` site URL |
| `JIRA_EMAIL` | `.env` | Email used for your Atlassian account |
| `JIRA_API_TOKEN` | `.env` | Secret Atlassian API token |
| `JIRA_PROJECT_KEY` | `.env` | Existing Jira project key, e.g. `BAI` |
| `JIRA_ISSUE_TYPE` | `.env` | Valid issue type in your project, e.g. `Task` |
| `JIRA_ENABLED` | `.env` | `true` for testing |
| `INCIDENT_STATE_DB` | `.env`, optional | `data/incident_state.db` |

**Critical:** `SLACK_WORKSPACE_URL` and `SLACK_WEBHOOK_URL` are different. A workspace URL cannot deliver messages. Keep the webhook and Jira API token out of screenshots, GitHub, Claude Code prompts, and class chat. Store a secure private backup of your configuration for later modules.

## 5. Installation and execution

On your EC2 instance, activate the class Python virtual environment if one is in use. Then run:

```bash
python3 -m pip install requests python-dotenv
mkdir -p data
python3 slack.py --test
python3 jira.py --verify
python3 incident.py --dry-run
python3 incident.py --test
```

**What each command proves:**

1. `pip install` makes the required Python libraries available to the active interpreter.
2. `slack.py --test` sends an actual test alert to your Slack channel.
3. `jira.py --verify` checks Jira project access **without creating a ticket**.
4. `incident.py --dry-run` previews the integrated workflow **without calling the external services**.
5. `incident.py --test` creates an actual Jira issue and sends a real Slack alert with its issue URL.

Do not repeatedly run `--test` because of impatience: new test incident IDs may create additional Jira issues. Confirm the first test's result before retrying.

## 6. Required end-to-end verification

- [ ] `slack.py --test` sends a message to the intended Slack channel.
- [ ] `jira.py --verify` confirms access to the intended Jira project.
- [ ] `incident.py --dry-run` completes without creating an external incident.
- [ ] `incident.py --test` reports the Jira issue key and Slack delivery outcome.
- [ ] You can open the newly created Jira issue in your own project.
- [ ] The Slack alert appears in your channel and includes the **correct clickable Jira issue URL**.
- [ ] The alert and issue describe the same test incident.
- [ ] You can explain where the incident ID is stored and why duplicate detection matters.

A successful terminal command **alone** is not sufficient evidence. Verify both external systems.

## 7. Expected learning outcomes

By the end of this lab, each student should be able to:

1. Explain the distinction between an event, an alert, and an incident record.
2. Configure two independent SaaS integrations without exposing credentials.
3. Explain why the coordinator creates a Jira issue before posting the Slack notification.
4. Trace a single incident from the originating agent through `incident.py`, `jira.py`, and `slack.py`.
5. Interpret API failures such as unauthorized access, forbidden access, invalid project, and missing webhook.
6. Verify external results instead of assuming a Python function call means the workflow succeeded.
7. Explain how a stable incident ID helps prevent duplicate Jira tickets.
8. Use Claude Code to investigate a failure, evaluate its recommendation, and test a minimal correction.
9. Preserve the working Slack configuration when adding Jira or future integrations.

## 8. Expected deliverables / evidence

Submit the following to the instructor using the class submission process:

- **Screenshot A:** Slack alert showing the test incident and Jira link.
- **Screenshot B:** Jira issue showing its issue key, title, and project.
- **Screenshot C:** Terminal output showing the integrated test outcome; redact any secrets.
- **Short explanation (5–8 sentences):** Describe the flow, which component creates the ticket, which component sends the alert, and how you verified both results.
- **Troubleshooting note:** Describe one configuration check you performed, even if your first test succeeded.

Do **not** submit `.env`, webhook URLs, API tokens, or screenshots displaying them.

## 9. Before saying “I'm confused”

Answer these questions **in order**:

1. Did you finish `slack_install.md` and `jira_install.md`?
2. Did you sign in to the **correct** Slack workspace and Jira site?
3. Did Slack work by itself **before** Jira was added?
4. Did you accidentally overwrite or erase the Slack variables in `.env`?
5. Did you replace the Chewbacca placeholder `SLACK_WORKSPACE_URL` in `slack.py`?
6. Are `SLACK_WEBHOOK_URL`, `JIRA_SITE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` present and correct?
7. Are `SLACK_ALERTS_ENABLED=true` and `JIRA_ENABLED=true`?
8. Is your issue type (`JIRA_ISSUE_TYPE`) valid for your Jira project?
9. Are you in the right directory and using the Python environment where dependencies were installed?
10. Did `slack.py --test` succeed? Did `jira.py --verify` succeed?
11. Did you run `incident.py --dry-run` **before** `--test`?
12. Did you inspect the actual Jira project and Slack channel, rather than only reading terminal output?
13. Did you consult `troubleshooting.md` and ask Claude Code a **specific** question?

If you still need help, report: **command run, sanitized error, expected behavior, actual behavior, and checks already performed.** “It doesn't work” is not a diagnostic report.

## 10. Claude Code — required student assistant

Start Claude Code from the repository directory and give it the lab files. Suggested prompts:

```text
Read README.md, incident_integration.md, troubleshooting.md,
incident.py, jira.py, and slack.py. Explain the workflow and list
my next three verification steps. Do not change any files.
```

```text
I ran python3 incident.py --test. Jira succeeded but Slack failed.
Help me isolate the problem, starting with safe configuration-presence
checks. Do not display, log, or request any credentials.
Do not modify code until I approve the proposed fix.
```

```text
Compare the exact environment variable names used by jira.py,
slack.py, and incident.py against troubleshooting.md. Identify
mismatches without printing secret values.
```

Claude Code is an assistant, not a substitute for understanding the result. Students are responsible for validating every recommended change.

## 11. Common failure map

| Symptom | First check |
|---|---|
| Slack worked yesterday, not today | Did Jira setup replace `.env` and remove `SLACK_WEBHOOK_URL`? |
| No Slack alert | Webhook, channel authorization, `SLACK_ALERTS_ENABLED`, severity threshold |
| Slack alert goes to unexpected channel | Incoming Webhook's configured destination; `SLACK_ALERT_CHANNEL` does not reroute it |
| Jira 401 | Account email and API token |
| Jira 403 | Project access and issue creation permissions |
| Jira 404 | Site URL, project key, and endpoint access |
| Jira issue creation rejected | Project's available issue types and required fields |
| `ModuleNotFoundError` | Active Python environment and pip dependencies |
| SQLite state error | `data/` directory, path, and write permissions |
| Jira ticket exists but Slack failed | Investigate Slack independently; reuse the same incident ID when retrying |
| Unexpected duplicate Jira issues | Check whether the incident ID changed between runs |

See `troubleshooting.md` for the expanded diagnostic procedure.

## 12. Definition of done

**The lab is complete only when:** (1) Jira creates the intended issue, (2) Slack receives an alert linking to that issue, (3) the student provides evidence from both systems, and (4) the student can explain and troubleshoot the integration.

### Instructor extension (optional)

Have the instructor trigger a harmless synthetic health-check failure. Students must trace it through Balerica AI, confirm the Jira issue, acknowledge the Slack alert, and document the root cause. Do not use real customer data or production financial transactions.

---

**CHEWBACCA'S FINAL ASSESSMENT:** “RRRRAAAWWWRRR!” Translation: *The alert was sent. The ticket was created. Now explain how you know.*
