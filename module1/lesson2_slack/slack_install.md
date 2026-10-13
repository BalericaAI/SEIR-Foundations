# SEIR Foundations — Slack Installation and Balerica AI Webhook Setup

**Lab:** Balerica AI Operational Notifications  
**Supported student computers:** macOS (Homebrew) and Windows (Chocolatey)  
**Deployment target for `slack.py`:** Student's AWS EC2 instance  
**Account:** Individual Slack Free workspace

## Objective

Install Slack using a package manager, create a dedicated alert channel, configure a Slack app with an Incoming Webhook, and preserve the values required for a future `slack.py` integration. **Do not install Slack Desktop on EC2.** The desktop application is for reading alerts; Python on EC2 sends HTTPS requests to the webhook.

## 1. Install Slack on your computer

### Option A — macOS with Homebrew

Open **Terminal** and verify Homebrew:

```bash
brew --version
```

If `brew` is unavailable, follow the official installation instructions at https://brew.sh/ and then reopen Terminal. Install Slack:

```bash
brew install --cask slack
```

Verify the installed package and launch the app:

```bash
brew list --cask slack
open -a Slack
```

To update Slack later:

```bash
brew upgrade --cask slack
```

### Option B — Windows with Chocolatey

Open **PowerShell as Administrator** and verify Chocolatey:

```powershell
choco --version
```

If Chocolatey is not installed, use the official instructions at https://docs.chocolatey.org/en-us/choco/setup/ . Review the installation script and follow your organization's device policies before installing. Reopen an elevated PowerShell window when installation completes.

Install Slack:

```powershell
choco install slack -y
```

Verify installation:

```powershell
choco list --local-only
```

**Note:** If your Chocolatey version does not support `--local-only`, use `choco list` and check for the `slack` package. Launch Slack from the Windows Start menu.

To update Slack later:

```powershell
choco upgrade slack -y
```

## 2. Create your individual Slack Free workspace

1. Open Slack and sign in or create an account at https://slack.com/ .
2. Create a **new workspace** for your SEIR Foundations lab (unless you already have a workspace where you are allowed to install apps).
3. Suggested workspace name: `SEIR-Foundations-<student-alias>`.
4. Create a channel named **`#balerica-alerts`**.
5. Send a manual message to the channel to verify that it works.

Each student should have their **own workspace and webhook**, so a classmate's test incidents do not appear in their channel. Slack Free plan limitations and message history retention may change; do not treat Slack as the authoritative log archive. Keep application logs in EC2/CloudWatch.

## 3. Create a Slack app for Balerica AI

1. Open https://api.slack.com/apps .
2. Select **Create New App**, then **From scratch** if prompted.
3. App name: **Balerica AI**.
4. Choose **your student workspace** and create the app.
5. In the app settings, select **Incoming Webhooks**.
6. Turn **Activate Incoming Webhooks** **On**.
7. Select **Add New Webhook to Workspace**.
8. Select **`#balerica-alerts`**, then **Allow**.
9. If Slack asks you to install or reinstall the app, complete that step.
10. Return to **Incoming Webhooks** and copy the new webhook URL.

The URL typically begins with `https://hooks.slack.com/services/`. **Treat the entire URL as a password.** Never paste the actual URL into a class chat, screenshot, GitHub issue, or README.

Official guide: https://api.slack.com/messaging/webhooks

## 4. Preserve the information for `slack.py`

Record the following in a **private** configuration note or password manager:

| Setting | Example | Required by `slack.py`? | Secret? |
|---|---|---|---|
| Workspace name | `SEIR-Foundations-student01` | No; useful for support | No |
| Workspace URL | `https://example.slack.com` | No; useful for support | No |
| Slack app name | `Balerica AI` | No | No |
| Alert channel | `#balerica-alerts` | Useful for documentation | No |
| Incoming webhook URL | `https://hooks.slack.com/services/...` | **Yes** | **YES** |
| EC2 instance ID | `i-0123456789abcdef0` | No; useful for troubleshooting | No |
| AWS Region | `us-east-1` | No; useful for troubleshooting | No |

**For this one-way alerting lab, you do NOT need a Slack bot token, OAuth client secret, signing secret, or Slack user password.** Those belong to different integrations that may be introduced later.

## 5. Configure the EC2 application environment

SSH into **your EC2 instance**. Use the actual Balerica AI application directory assigned by your instructor; the example below assumes `/opt/balerica-bank`:

```bash
cd /opt/balerica-bank
umask 077
nano .env
```

Add these entries, substituting your **own** webhook URL:

```dotenv
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/REPLACE_WITH_YOUR_PRIVATE_WEBHOOK
SLACK_ALERT_CHANNEL=balerica-alerts
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
```

The **only field Slack requires to deliver an Incoming Webhook message is `SLACK_WEBHOOK_URL`**. The other settings are Balerica AI configuration conventions for our forthcoming `slack.py`; they do not alter the webhook's authorized destination channel.

Protect the file:

```bash
chmod 600 .env
```

Add `.env` to your project's `.gitignore`:

```bash
printf '\n.env\n' >> .gitignore
```

**Never commit `.env` or webhook URLs to GitHub.** A `.gitignore` entry does not remove secrets already committed. If a webhook leaks, revoke/regenerate it in Slack and update EC2.

For the class repository, preserve a non-secret `.env.example` instead:

```dotenv
SLACK_WEBHOOK_URL=REPLACE_ME
SLACK_ALERT_CHANNEL=balerica-alerts
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
```

## 6. Test the webhook from EC2 without displaying the secret

Run the following from the application directory. It loads the webhook from `.env` and sends one harmless test message:

```bash
python3 - <<'PY'
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

settings = {}
for line in Path('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        settings[key.strip()] = value.strip().strip('"').strip("'")

url = settings.get('SLACK_WEBHOOK_URL', '')
if not url.startswith('https://hooks.slack.com/services/'):
    raise SystemExit('SLACK_WEBHOOK_URL is missing or invalid')

payload = json.dumps({'text': 'Balerica AI: Slack connectivity test from EC2 successful.'}).encode()
request = Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urlopen(request, timeout=10) as response:
        print('HTTP status:', response.status)
except Exception as exc:
    raise SystemExit(f'Webhook test failed: {type(exc).__name__}. Check configuration, permissions, and outbound HTTPS connectivity.')
PY
```

Check `#balerica-alerts` in Slack. You should see:

> Balerica AI: Slack connectivity test from EC2 successful.

The EC2 instance needs **outbound HTTPS (TCP 443)** to reach Slack. An EC2 instance in a private subnet needs appropriate egress, such as NAT or another approved network path. You do **not** need to open an inbound EC2 security-group port for Incoming Webhooks.

## 7. Student completion checklist

- [ ] Installed Slack with `brew` (Mac) or `choco` (Windows).
- [ ] Created or selected an individual Slack workspace.
- [ ] Created `#balerica-alerts`.
- [ ] Created the `Balerica AI` Slack app.
- [ ] Enabled Incoming Webhooks and authorized the alert channel.
- [ ] Stored the webhook URL privately.
- [ ] Created the EC2 `.env` configuration and protected it with `chmod 600`.
- [ ] Added `.env` to `.gitignore` and created a safe `.env.example`.
- [ ] Received the test message from EC2 in Slack.

## 8. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `brew: command not found` | Homebrew missing or not on PATH | Install/configure Homebrew using official instructions |
| `choco` not recognized | Chocolatey missing or shell PATH not refreshed | Install Chocolatey; reopen PowerShell |
| Cannot create webhook | App installation restricted by workspace | Use your own workspace or ask its admin for permission |
| HTTP 400 | Invalid message payload | Ensure JSON includes a nonempty `text` field |
| HTTP 403 or 404 | Revoked/invalid webhook or app restrictions | Review app's Incoming Webhooks settings; generate a new webhook if needed |
| Timeout / network error | EC2 cannot reach Slack over HTTPS | Check route tables, NAT/egress, DNS, and outbound TCP 443 |
| Message appears in wrong channel | Webhook was authorized for a different channel | Create a new webhook authorized for `#balerica-alerts` |
| Test works, but agent doesn't send alerts | `slack.py` not implemented or agent not wired to it | Complete the next Balerica AI integration lab |

## 9. What comes next: `slack.py`

The next lab will implement a Python module that reads `SLACK_WEBHOOK_URL` from `.env`, formats structured incident messages, and delivers them to Slack. Other agents (`health.py`, `telemetry.py`, `analyze_logs.py`, and later `cobol.py`) will call this module when they detect an actionable problem.

```text
EC2 / COBOL / FastAPI
         |
         v
health.py / telemetry.py / analyze_logs.py
         |
         v
      slack.py
         |
         v
Slack Incoming Webhook (HTTPS)
         |
         v
Student's #balerica-alerts channel
```

**Engineering rule:** Slack alerts notify engineers; logs and telemetry supply the evidence. An AI-generated diagnosis is a hypothesis until the student verifies it.

---

### References

- Homebrew Slack cask: https://formulae.brew.sh/cask/slack
- Chocolatey Slack package: https://community.chocolatey.org/packages/slack
- Chocolatey installation: https://docs.chocolatey.org/en-us/choco/setup/
- Slack Incoming Webhooks: https://api.slack.com/messaging/webhooks
