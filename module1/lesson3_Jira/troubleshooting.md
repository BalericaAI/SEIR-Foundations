# SEIR Foundations — Slack + Jira Incident Integration Troubleshooting

**Audience:** Students using `slack.py`, `jira.py`, and `incident.py` on their EC2 instance, with Claude Code available for assistance.

> **CHEWBACCA SAYS:** RRRRAAAWWWRRR! Before blaming AWS, Python, Jira, Slack, or the professor, **DID YOU READ THE INSTRUCTIONS?**

## 0. Stop. Answer these questions first.

Check every box **before** asking for help:

- [ ] Did you complete `slack_install.md` and the Slack lab runbook?
- [ ] Did you complete `jira_install.md` and the Jira runbook?
- [ ] **Did you sign in to your own Slack workspace?** Can you open `#balerica-alerts` and see messages?
- [ ] **Did you sign in to your own Jira Cloud site?** Can you open your Balerica AI project and its issues?
- [ ] Did you edit the student workspace URL in `slack.py`? (Not the instructor's example URL!)
- [ ] Did you configure a Slack **Incoming Webhook** for your own workspace/channel?
- [ ] Did you generate your own Atlassian API token and configure your Jira project key?
- [ ] **Did you accidentally erase your Slack configuration while adding Jira to `.env`?** You must **merge** the settings, not replace the file.
- [ ] Are `slack.py`, `jira.py`, and `incident.py` available in the same project directory?
- [ ] Are you running Python commands on the **EC2 instance** where the code and `.env` are located, rather than in a different terminal on your laptop?
- [ ] Did you activate the intended Python virtual environment and install the dependencies there?
- [ ] Did each individual integration work **before** testing the combined workflow?

**Instructor rule:** A screenshot saying “it doesn't work” is not a diagnostic report. Provide the failing command, sanitized error, and which checks passed.

## 1. Variables: do you have ALL of them?

The following names match the lab's actual Python modules. Values below are examples, **not working credentials**.

| Variable or setting | Where it belongs | Example | Required? |
|---|---|---|---|
| `SLACK_WORKSPACE_URL` | Near the top of `slack.py` | `https://your-workspace.slack.com` | Yes; identifies workspace in messages |
| `SLACK_WEBHOOK_URL` | `.env` | `https://hooks.slack.com/services/...` | Yes; **secret**, controls delivery |
| `SLACK_ALERTS_ENABLED` | `.env` | `true` | Recommended; must be enabled for testing |
| `SLACK_ALERT_SEVERITY` | `.env` | `ERROR` | Recommended; `ERROR` allows the integration test |
| `SLACK_ALERT_CHANNEL` | `.env` | `balerica-alerts` | Optional documentation; **does not** change the webhook destination |
| `JIRA_SITE_URL` | `.env` | `https://your-site.atlassian.net` | Yes |
| `JIRA_EMAIL` | `.env` | `student@example.com` | Yes; Atlassian account email |
| `JIRA_API_TOKEN` | `.env` | *(private token)* | Yes; **secret** |
| `JIRA_PROJECT_KEY` | `.env` | `BAI` | Yes; must match an existing project |
| `JIRA_ISSUE_TYPE` | `.env` | `Task` | Recommended; must be valid in your project |
| `JIRA_ENABLED` | `.env` | `true` | Recommended; must be enabled for testing |
| `INCIDENT_STATE_DB` | `.env`, optional | `data/incident_state.db` | Optional; local incident tracking database |

**Two URLs, two different jobs:** `https://your-workspace.slack.com` is the Slack **workspace**; `https://hooks.slack.com/services/...` is the **secret webhook**. Changing the workspace URL in Python does **not** change where messages are delivered. The webhook determines the destination.

### Safe combined `.env` template

Copy the variable **names** below into the existing `.env`, fill in your own values, and **keep the Slack entries when adding Jira**:

```dotenv
# SLACK — preserve these from the previous lab
SLACK_WEBHOOK_URL=REPLACE_WITH_YOUR_PRIVATE_WEBHOOK
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
SLACK_ALERT_CHANNEL=balerica-alerts

# JIRA — add these; do not overwrite Slack
JIRA_SITE_URL=https://YOUR-SITE.atlassian.net
JIRA_EMAIL=YOUR_EMAIL
JIRA_API_TOKEN=REPLACE_WITH_YOUR_PRIVATE_TOKEN
JIRA_PROJECT_KEY=BAI
JIRA_ISSUE_TYPE=Task
JIRA_ENABLED=true

# OPTIONAL
INCIDENT_STATE_DB=data/incident_state.db
```

The Slack workspace URL is set in `slack.py`, not in this `.env` template. **Do not paste real credentials into GitHub, screenshots, shared notes, Slack messages, or Claude Code prompts.** Store secrets in `.env` with restrictive file permissions; save only nonsecret site names, project keys, and setup notes in your ordinary notepad. Keep webhook/token recovery information in a password manager or another secure secret store. If exposed, revoke/rotate immediately.

## 2. Confirm your location and files

Run on the EC2 instance:

```bash
pwd
ls -la slack.py jira.py incident.py .env
python3 --version
python3 -m pip --version
```

If a file is missing, you are probably in the wrong directory or did not copy it to EC2. `ModuleNotFoundError: No module named 'jira'` can also mean `jira.py` is absent or incorrectly named. Watch for `jira.py.txt`, `Slack.py`, or files saved in another directory. Linux filenames are case-sensitive.

**Do not run `cat .env` or paste its contents into chat.**

## 3. Confirm your Python dependencies

Activate the virtual environment used for this lab, if applicable:

```bash
source venv/bin/activate
python -m pip install requests python-dotenv
python -m pip show requests python-dotenv
python -m py_compile slack.py jira.py incident.py
```

If your environment is named `.venv`, activate `.venv/bin/activate` instead. A syntax check validates Python parsing; it does **not** validate credentials, connectivity, or permissions.

**Common errors:**

- `ModuleNotFoundError: requests` or `dotenv`: install dependencies with the **same Python interpreter** that runs the lab.
- `externally-managed-environment`: use a virtual environment instead of forcing system-wide pip installation.
- `Permission denied`: check ownership and permissions; don't reflexively run the entire app as root.
- `SyntaxError`: inspect the exact file and line, including accidental edits to quotes or indentation.

## 4. Test Slack by itself FIRST

```bash
python slack.py --test
```

Then **open Slack** and inspect `#balerica-alerts` (or the channel actually selected when you authorized the webhook).

| Symptom | First checks |
|---|---|
| No Slack message | Signed into the correct workspace? Correct channel? Webhook still active? |
| `SLACK_WEBHOOK_URL` missing | Does `.env` exist beside the code? Did the Jira lab overwrite it? |
| Workspace URL warning | Edit `SLACK_WORKSPACE_URL` in `slack.py` and include `https://` |
| HTTP 403/404/410 or webhook rejected | Verify the webhook was created/authorized; regenerate if revoked; do not print the URL |
| Script says alert was filtered | Check `SLACK_ALERTS_ENABLED=true` and `SLACK_ALERT_SEVERITY=ERROR` |
| Message arrives in wrong channel | Reconfigure the webhook's destination in Slack; `SLACK_ALERT_CHANNEL` is informational |
| Network timeout | Verify EC2 outbound HTTPS connectivity, DNS, routing, and security controls |

**Important:** Being logged into the Slack desktop app is helpful for *seeing* the message, but the Python webhook itself does not use your desktop login session.

## 5. Test Jira by itself SECOND

```bash
python jira.py --verify
python jira.py --test
```

`--verify` checks Jira access without creating an issue. `--test` creates a real test issue; confirm it appears in the expected Jira project.

| Symptom | First checks |
|---|---|
| 401 Unauthorized | Atlassian account email/token pair; revoked or mistyped token |
| 403 Forbidden | Account/project permissions; token scope or access restrictions |
| 404 Not Found | Wrong `.atlassian.net` site, project key, or endpoint; check actual project |
| 400 Bad Request | Issue type `Task` unavailable, required project fields missing, or invalid issue data |
| Test issue appears in wrong project | Confirm `JIRA_PROJECT_KEY` in `.env` |
| Cannot see test issue | Logged into the same Jira site/account? Board filters hiding the issue? |
| Token copied with spaces/quotes | Carefully re-enter into `.env`; never display it in terminal output |

**Reminder:** Jira account password and Jira API token are not interchangeable.

## 6. Test the combined incident workflow LAST

```bash
python incident.py --dry-run
python incident.py --test
```

- `--dry-run` only describes the workflow; it **does not contact Jira or Slack**.
- `--test` creates a Jira issue and then attempts to post a Slack message with the Jira ticket URL.
- Success means **both** the Jira ticket exists **and** the Slack alert arrives with the correct Jira link.
- Each explicit `--test` uses a new incident ID and can create another ticket. Don't repeat it endlessly.

The integration output includes `jira_created`, `jira_key`, `jira_url`, and `slack_status`. Read these fields before changing anything.

| Result | Interpretation / next action |
|---|---|
| `jira_created: true`, `slack_status: sent` | Expected successful first run |
| `jira_created: false` | Existing incident ID was found in the local state DB; normal for repeated IDs |
| `slack_status: filtered_or_disabled` | Check Slack enable flag and severity threshold |
| `slack_status: failed_...` | Jira may have succeeded but Slack failed; troubleshoot Slack alone |
| Jira succeeds but Slack absent | Check webhook, channel, filtering, and `slack_status`; don't delete the Jira issue |
| Jira fails before Slack | Fix Jira first: this workflow intentionally creates Jira **before** Slack |
| `sqlite3.OperationalError` | Check write permissions and the directory for `INCIDENT_STATE_DB` |
| Jira ticket duplicated after an interrupted run | A crash between Jira creation and local state commit can produce duplicates; report it rather than repeatedly retrying |

**Do not delete `data/incident_state.db` to “fix” duplicates.** It stores local incident-to-ticket associations. Deleting it can cause repeat ticket creation for previously reported IDs. This classroom deduplication is sequential, not a production-grade exactly-once guarantee.

## 7. Tiny problems that ruin an otherwise good afternoon

- **Wrong machine:** You edited `.env` on your Mac/Windows laptop but are running `incident.py` on EC2.
- **Wrong folder:** Your shell is in `~/agents` but the files are in `/opt/balerica-bank/agents`.
- **Wrong Python:** `pip` installed packages globally while `python` uses a virtual environment.
- **Wrong `.env`:** A new Jira template replaced the Slack settings rather than being merged.
- **Wrong site:** Student copied the professor's `chewbacca.slack.com` or sample Jira site instead of their own.
- **Wrong Slack channel:** The webhook is connected to `#general`, while the student watches `#balerica-alerts`.
- **Wrong Jira project:** The project key is `SEIR`, but `.env` still says `BAI`.
- **Wrong issue type:** The project accepts `Bug`, but `.env` requests `Task` (or vice versa).
- **Forgot to save:** The student edited `.env` or `slack.py` but didn't save the file.
- **Accidental spaces:** `JIRA_PROJECT_KEY= BAI` may be parsed unexpectedly; remove accidental whitespace.
- **Old token:** A revoked/expired API token is still present in `.env`.
- **Unapproved Slack app:** The student created a workspace but never enabled/authorized Incoming Webhooks.
- **No outbound Internet:** EC2 can run Python but cannot reach Slack/Jira over HTTPS.
- **Threshold mismatch:** The event is `WARNING` but the Slack minimum is `ERROR`.
- **Over-testing:** Running `jira.py --test` and `incident.py --test` repeatedly generates real test issues.
- **Confusing UI and API:** A successful desktop login does not configure Python API credentials.
- **Hardcoded secret:** The student pasted a webhook/token directly into Python. Move it to `.env`, rotate the exposed secret, and keep it out of Git.

## 8. Safe diagnostics — prove configuration exists without showing secrets

Run this on EC2 from the lab directory:

```bash
python - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv()
required = [
    'SLACK_WEBHOOK_URL', 'SLACK_ALERTS_ENABLED', 'SLACK_ALERT_SEVERITY',
    'JIRA_SITE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN',
    'JIRA_PROJECT_KEY', 'JIRA_ISSUE_TYPE', 'JIRA_ENABLED',
]
for key in required:
    print(f'{key}: {"SET" if os.getenv(key, "").strip() else "MISSING"}')
PY
```

This confirms **presence**, not correctness. Never print the actual webhook or API token. Inspect `SLACK_WORKSPACE_URL` in `slack.py` separately; it is a Python setting, not an environment variable in this lab.

## 9. Questions to ask Claude Code

Claude Code should help you reason about the lab, **not invent credentials or expose them**. Try:

> Read `troubleshooting.md`, `slack.py`, `jira.py`, and `incident.py`. Give me a step-by-step diagnostic plan for why the Jira ticket is created but no Slack notification arrives. Do not print `.env` values, send secrets to any model, or modify files without my approval.

> Compare the required environment variable **names** used by these Python modules with my `.env` variable **names only**. Tell me what is missing, without displaying values.

> Explain why `python incident.py --dry-run` succeeds but `python incident.py --test` fails. Identify which external API call occurs first.

> My Slack alert says `filtered_or_disabled`. Explain which flags and severity thresholds to inspect. Do not change anything yet.

> I see a Jira issue but `slack_status` reports a failure. Explain how local incident deduplication affects a retry with the same incident ID.

## 10. What to submit

- [ ] Slack screenshot showing a test alert in the intended channel, with no secrets visible.
- [ ] Jira screenshot showing a created test incident and its issue key.
- [ ] Sanitized terminal output of `python incident.py --test` showing the Jira issue key and `slack_status: sent`.
- [ ] One sentence explaining the difference between the Slack workspace URL and the webhook URL.
- [ ] One sentence explaining why Jira is created **before** Slack in this lab.
- [ ] Confirmation that `.env` is excluded from Git and credentials were not shared.

**Final Chewbacca inspection:** If Slack worked yesterday and stopped working right after Jira setup, ask yourself one last question: **DID YOU ERASE YOUR SLACK VARIABLES?** RRRRAAAWWWRRR!
