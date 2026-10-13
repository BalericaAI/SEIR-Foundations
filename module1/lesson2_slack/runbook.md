# SEIR Foundations — Balerica AI Slack Integration Runbook

**Lab:** Slack Incoming Webhook notifications from Balerica AI on EC2  
**Audience:** Students using individual Slack Free workspaces  
**Goal:** Successfully deliver a test incident from `slack.py` on EC2 to `#balerica-alerts` in your own Slack workspace.

## Prerequisites — complete these FIRST

Before starting this runbook, you **must** complete:

- [ ] **`slack_install.md`** — install Slack Desktop using **Homebrew (`brew`) on macOS** or **Chocolatey (`choco`) on Windows**; create and sign in to your Slack workspace.
- [ ] **`slack.py`** — place the Balerica AI notification module on your EC2 instance and change the `SLACK_WORKSPACE_URL` assignment near the top of the file to **your own** workspace URL.
- [ ] Confirm you can SSH into your student EC2 and have Python 3 and `pip` available.

> **YO STUDENT! INSERT YOUR SLACK WORKSPACE URL IN `slack.py` OR CHEWBACCA BITES YOU!!!!!**  
> `https://chewbacca.slack.com` is an **example**, not your workspace. And no, the workspace URL is **not** the Incoming Webhook URL.

## 1. Create and configure your Incoming Webhook

1. Sign in to **your** Slack workspace.
2. Create a channel named **`#balerica-alerts`**.
3. Open **https://api.slack.com/apps** and select **Create New App** → **From scratch**.
4. Name it **`Balerica AI`** and select **your own Slack workspace**.
5. In the app configuration, open **Incoming Webhooks**.
6. Turn **Activate Incoming Webhooks** **On**.
7. Select **Add New Webhook to Workspace**.
8. Choose **`#balerica-alerts`**, then select **Allow** to authorize posting.
9. Return to **Incoming Webhooks** and copy the webhook URL. It should resemble:

   ```text
   https://hooks.slack.com/services/T.../B.../YOUR-PRIVATE-TOKEN
   ```

**Important:** The webhook URL is a **secret**. Never paste your real webhook into class chat, screenshots, GitHub, tickets, or submissions. If it leaks, revoke/rotate it in Slack and update `.env`.

## 2. Preserve your configuration for later labs

Open a **private notepad or secure notes application** on your own computer and record the following. This will be needed for future Balerica AI configuration and incident-response labs.

| Setting | What to record | Secret? |
|---|---|---|
| Workspace name | Your Slack workspace name | No |
| Workspace URL | `https://YOUR-WORKSPACE.slack.com` | No |
| Alert channel | `#balerica-alerts` | No |
| Slack app name | `Balerica AI` | No |
| Incoming Webhook URL | Your full `https://hooks.slack.com/services/...` URL | **YES** |
| Alert threshold | `ERROR` (initial lab setting) | No |

**Preservation rule:** Store the full webhook URL only in a **secure/private note or password manager**, not in a shared/plaintext classroom note. Do not submit it to the instructor. Save the other nonsecret values in your lab notes.

On EC2, keep the webhook in `.env` alongside `slack.py`:

```dotenv
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/PASTE-YOUR-REAL-WEBHOOK-HERE
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
SLACK_ALERT_CHANNEL=balerica-alerts
```

You can use the provided `slack.env.example` as your template:

```bash
cp slack.env.example .env
chmod 600 .env
vi .env
```

If you already have a `.env`, **do not overwrite it**; add these settings to the existing file instead. Ensure `.env` is in `.gitignore`. The `SLACK_ALERT_CHANNEL` value documents the channel; the actual delivery destination is chosen when you authorize the webhook in Slack.

In `slack.py`, update this one line:

```python
SLACK_WORKSPACE_URL = "https://YOUR-WORKSPACE.slack.com"
```

**Do not paste the webhook URL into `SLACK_WORKSPACE_URL`.** The webhook remains in `.env`.

## 3. Install Python dependencies on EC2

From the directory containing `slack.py`, activate your existing project virtual environment if one is available. Otherwise create one:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies used by `slack.py`:

```bash
python -m pip install requests python-dotenv
```

Verify imports:

```bash
python -c "import requests; import dotenv; print('Dependencies OK')"
```

If you are using the full Balerica AI project `requirements.txt`, these packages can also be added there for repeatable installation.

## 4. Test your Slack connection

Make sure you are in the directory containing both `slack.py` and `.env` and that your virtual environment is active. Run:

```bash
python slack.py --test
```

Expected terminal output:

```text
SUCCESS: Chewbacca approves!
```

Now open your Slack desktop application and look in **`#balerica-alerts`**. You should see a **BALERICA AI ALERT** with:

```text
Severity: ERROR
Agent: slack.py
Incident: TEST-001
Message: TEST: Slack is connected. RRRRAAAWWWRRR!
```

The test uses `ERROR` severity so it passes the default `SLACK_ALERT_SEVERITY=ERROR` filter.

### Troubleshooting

| Symptom | What to check |
|---|---|
| `SKIPPED: Check alert settings in .env` | Set `SLACK_ALERTS_ENABLED=true` and `SLACK_ALERT_SEVERITY=ERROR` (or lower). |
| `FAILED` and missing webhook | Check `SLACK_WEBHOOK_URL` is set in `.env` and begins with `https://hooks.slack.com/services/`. |
| `FAILED` and workspace validation | Correct `SLACK_WORKSPACE_URL` in `slack.py`; include `https://` and your `.slack.com` hostname. |
| HTTP 403/404 or revoked webhook | Revisit Slack app → Incoming Webhooks, check authorization, and rotate/recreate the webhook if necessary. |
| `ModuleNotFoundError` | Activate the correct virtual environment and reinstall dependencies. |
| Terminal says success, no visible message | Verify you are looking in the **same workspace and channel** authorized for that webhook. |
| Network/timeout error | Confirm EC2 has outbound HTTPS (TCP 443) access and appropriate DNS resolution. |

## 5. Completion checklist

- [ ] `slack_install.md` completed (Slack installed via `brew` or `choco`).
- [ ] `slack.py` present on EC2; student workspace URL updated.
- [ ] `#balerica-alerts` created.
- [ ] Slack app created; Incoming Webhook activated and authorized.
- [ ] Workspace details and webhook recorded privately for future labs.
- [ ] `.env` configured, permission-restricted, and excluded from Git.
- [ ] `requests` and `python-dotenv` installed.
- [ ] `python slack.py --test` reports success.
- [ ] Test alert appears in the correct Slack channel.

**Lab complete.** Your EC2 instance can now send Balerica AI incident notifications to your Slack workspace. Next, we will call `send_alert()` from monitoring agents such as `health.py` and `analyze_logs.py`.

> **CHEWBACCA'S FINAL REVIEW:** RRRRAAAWWWRRR! If you see the alert, you passed. If you don't, check the configuration before blaming the Wookiee.
