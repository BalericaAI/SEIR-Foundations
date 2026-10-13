# SEIR Foundations — Balerica AI Slack Alert Lab

**Lab objective:** Connect your Balerica AI EC2 instance to your own Slack Free workspace so that Python agents can send operational alerts to `#balerica-alerts`.

**Claude Code is required for this class.** Use it as a lab assistant: ask it to explain instructions, inspect errors, and propose minimal fixes. **You** are responsible for running commands, understanding changes, protecting credentials, and proving the alert reached Slack.

> **CHEWBACCA WARNING:** YO STUDENT! INSERT YOUR SLACK WORKSPACE URL IN `slack.py` OR CHEWBACCA BITES YOU!!!!! And no, copying your neighbor's URL does not count.

## 0. Required reading and files

Complete these **in order** before attempting the test:

1. **`slack_install.md`** — Install the Slack desktop app using `brew` (macOS) or `choco` (Windows); create/sign into your individual workspace.
2. **`slack.py`** — Copy the agent to your EC2 instance and update `SLACK_WORKSPACE_URL` to your workspace URL, in **one place near the top of the file**.
3. **`runbook.md`** — Follow the webhook setup, private-notes, dependency installation, and test procedures.
4. **`slack.env.example`** — Template for the `.env` settings; do **not** put a real webhook URL in a tracked file.

If a step is unclear, **ask Claude Code to read these files before making suggestions**. Do not ask it to invent a different lab architecture.

## 1. Understand the architecture

```text
Student's Windows or Mac
  └─ Slack desktop application (installed with choco / brew)
         ▲
         │ notification appears in #balerica-alerts
         │
Slack Incoming Webhook (HTTPS)
         ▲
         │ POST JSON
         │
Student's EC2 instance
  ├─ .env                [private webhook + alert settings]
  ├─ slack.py            [notification sender]
  └─ health.py / analyze_logs.py / other agents [future integrations]
```

**Critical distinction:**

- `SLACK_WORKSPACE_URL = "https://YOUR-WORKSPACE.slack.com"` in `slack.py` identifies the workspace **for labeling and validation**.
- `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...` in `.env` is the **private delivery endpoint**. Slack chooses the channel when you authorize the webhook. Changing the workspace URL in Python **does not** redirect the webhook.
- The Slack desktop app runs on **your computer**, not EC2. `slack.py` runs on **EC2**.

## 2. Student setup checklist

- [ ] I completed `slack_install.md` using Homebrew or Chocolatey.
- [ ] I created my own Slack workspace and `#balerica-alerts` channel.
- [ ] I created a Slack app, enabled **Incoming Webhooks**, and authorized posting to `#balerica-alerts` (see `runbook.md`).
- [ ] I updated the **single** `SLACK_WORKSPACE_URL` assignment in `slack.py`.
- [ ] I recorded my workspace URL, channel name, app name, and webhook **in private notes** for later labs. I will keep the actual webhook in a password manager or secure private note, **not** in a shared classroom notepad.
- [ ] I placed the real webhook in `.env` on EC2 and excluded `.env` from Git.
- [ ] I installed Python dependencies in the intended virtual environment.
- [ ] I ran the test and confirmed the alert appeared in Slack.

### EC2 commands

From the directory containing `slack.py` and `slack.env.example`:

```bash
# If you already have a project virtual environment, activate that instead.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests python-dotenv
python -c "import requests; import dotenv; print('Dependencies OK')"

# ONLY if .env does not already exist; never overwrite existing project settings.
cp -n slack.env.example .env
chmod 600 .env
vi .env

# Ensure .env is ignored by Git.
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore

python slack.py --test
```

In `.env`, set `SLACK_WEBHOOK_URL` to your **actual private Incoming Webhook URL**, `SLACK_ALERTS_ENABLED=true`, and `SLACK_ALERT_SEVERITY=ERROR`. Never paste the actual webhook into a Claude Code chat, issue, screenshot, commit, or lab submission. If exposed, revoke/rotate it in Slack.

### Expected result

EC2 terminal:

```text
SUCCESS: Chewbacca approves!
```

Slack `#balerica-alerts` channel:

```text
BALERICA AI ALERT
Severity: ERROR
Agent: slack.py
Incident: TEST-001
Message: TEST: Slack is connected. RRRRAAAWWWRRR!
```

A success message alone is **not** sufficient: visually verify the message in the correct workspace/channel.

## 3. Using Claude Code to work through the lab

Start Claude Code **in the lab project directory**, where it can read the files. Claude Code is your assistant, **not your replacement**. Ask it to read the README, installation guide, runbook, and source before answering. Review all proposed changes before accepting them.

### Recommended first question

> Read `README.md`, `slack_install.md`, `runbook.md`, and `slack.py`. Explain the lab objective, the difference between a Slack workspace URL and an Incoming Webhook URL, and the exact steps I must complete. Do not edit any files or ask me to reveal secrets.

### Questions students should ask

**Installation and prerequisites**

> I am using [macOS/Windows]. Based on `slack_install.md`, which Homebrew/Chocolatey command do I use, and how do I verify Slack installed? Explain; don't run installation commands without my approval.

**Webhook configuration**

> Based on `runbook.md`, guide me through creating the Slack app, enabling Incoming Webhooks, and authorizing `#balerica-alerts`. Tell me what information I should preserve privately. Do not ask for my actual webhook token.

**Understanding the code**

> Read `slack.py`. Explain `SLACK_WORKSPACE_URL`, `SLACK_WEBHOOK_URL`, `send_alert()`, severity filtering, and what `--test` does. Identify which values are safe to share and which are secrets.

**Dependency installation**

> Explain how to create or activate a Python virtual environment on my Linux EC2 and install `requests` and `python-dotenv`. Tell me how to verify that I am using the same Python interpreter for installation and testing.

**Debugging**

> My `python slack.py --test` output is [paste the error with tokens/URLs redacted]. Inspect `slack.py` and `runbook.md`, propose the smallest likely fix, and give me one verification command. Do not rewrite the module or print `.env`.

**Engineering verification**

> Help me design a checklist proving an ERROR alert was delivered to the intended Slack channel, and explain why an INFO alert may be skipped when the threshold is ERROR. Do not send extra alerts without my approval.

### Rules for Claude Code use

1. **Read before editing.** Use the supplied project files as the source of truth; do not invent modules or commands.
2. **Explain before executing.** Ask Claude Code for a plan, then inspect the proposed commands and diffs.
3. **Protect secrets.** Do not paste the webhook URL or `.env` contents into prompts. Ask Claude Code to check whether a variable is **present**, not to print its value. Avoid `cat .env`, `env`, verbose HTTP logs, or `git diff` containing secrets.
4. **Make minimal changes.** Preserve the public `send_alert(agent, severity, message, incident_id="")` interface and the `python slack.py --test` command.
5. **Prove your answer.** A plausible explanation is not evidence of a working integration. Run the test and check Slack.
6. **Understand the boundary.** Claude Code does not magically configure your Slack workspace; you must authorize the webhook in Slack.

## 4. Troubleshooting guide

| Symptom | First investigation | Suggested Claude Code question |
|---|---|---|
| `ModuleNotFoundError` | Confirm active venv and `python -m pip install requests python-dotenv` | “Which interpreter is running this script?” |
| `SKIPPED` | Check `SLACK_ALERTS_ENABLED` and severity threshold **without printing secrets** | “Why would an ERROR alert be filtered?” |
| Invalid workspace URL | Check the single assignment in `slack.py` | “Show me the expected workspace URL format.” |
| Missing/invalid webhook | Confirm `.env` is in the working directory and the URL was authorized | “How can I safely test whether the webhook variable is set?” |
| HTTP 403/404 | Check Slack authorization and whether the webhook was revoked | “What does this HTTP status suggest for an Incoming Webhook?” |
| Timeout/network error | Check EC2 outbound HTTPS and DNS | “Which nonsecret connectivity checks should I run?” |
| Test says success, no message visible | Check you opened the workspace/channel associated with the **webhook** | “Explain why the workspace label does not route delivery.” |

**Do not** use a public webhook-testing website, share credentials with classmates, or repeatedly send test alerts while troubleshooting.

## 5. Integrating with other Balerica AI agents (after the initial test)

`slack.py` exposes this function:

```python
from slack import send_alert

send_alert(
    agent="health.py",
    severity="ERROR",
    message="Test incident: simulated disk threshold exceeded",
    incident_id="LAB-001"
)
```

Use **synthetic** messages in class. Never send actual passwords, tokens, private account records, or sensitive logs to Slack. In a later exercise, `health.py`, `analyze_logs.py`, and the banking monolith will call this same function for real detected conditions. Add rate limiting/deduplication before enabling recurring production-style monitoring.

## 6. Submission / evidence of completion

Provide your instructor:

- Your **workspace URL** (not the webhook URL) and alert channel name.
- A screenshot of the **test alert in Slack**, with sensitive information hidden.
- The terminal line `SUCCESS: Chewbacca approves!`.
- A short explanation (2–3 sentences) of the difference between `SLACK_WORKSPACE_URL` and `SLACK_WEBHOOK_URL`.
- One example of a question you asked Claude Code, and how you independently verified its answer.

**Never submit your `.env`, real webhook URL, or secret tokens.**

## 7. Exit criteria

You are finished when your EC2 sends an ERROR-level test alert, your own Slack workspace receives it in `#balerica-alerts`, and you can explain the flow from `slack.py` to the Incoming Webhook to Slack.

> **Chewbacca's review:** RRRRAAAWWWRRR! The alert arrived. The student has demonstrated basic reading comprehension. The investigation continues.
