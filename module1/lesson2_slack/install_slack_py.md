# Installing `slack.py` on Your EC2 Instance — Step by Step

This guide takes you from "I just SSHed in" to "`slack.py` is installed,
configured, and tested," using the same bank directory you built in Lesson 1.
Every step shows the command AND what you should see. Do not skip steps.

**Where things live (from Lesson 1):**

```text
/home/ec2-user/SEIR-Foundations    ← the course repo you cloned (Lesson 1, Step 1)
/opt/balerica-bank                 ← your bank, built by the installer
    ├── app/  cobol/  data/  venv/ ← from Lesson 1
    ├── slack.py                   ← you are adding this today
    └── .env                       ← and this (hidden! see env_explained.md)
```

## Step 0 — SSH in and prove you are really there

```bash
whoami && TZ='America/Chicago' date && ec2-metadata -i
```

Expected output: `ec2-user`, today's date in your zone, and your Instance ID.
(Use your own time zone, same as Lesson 1.)

## Step 1 — Get the Lesson 2 files onto the instance

If this instance still has the course repo from Lesson 1, update it:

```bash
cd ~/SEIR-Foundations
git pull
```

Expected output: either a list of updated files or `Already up to date.`
Both are fine.

If this is a **fresh instance** without the repo, clone it (just like
Lesson 1, Step 1):

```bash
cd ~
sudo dnf install -y git
git clone https://github.com/BalericaAI/SEIR-Foundations.git
```

Expected output ends with `Resolving deltas: 100% ..., done.`

Confirm the Lesson 2 files exist:

```bash
ls ./module1/lesson2_slack
```

Expected output:

```text
README.md                 homework             runbook.md         slack_install.md
claude_code_explained.md  install_slack_py.md  slack.env.example  why_slack_matters.md
env_explained.md          nano_basics.md       slack.py
```

(The exact layout varies with your terminal width — what matters is that
`slack.py`, `slack.env.example`, and the `homework` folder are all there.)

## Step 2 — Copy `slack.py` into the bank

`slack.py` must live in `/opt/balerica-bank`, next to the other agents, so
future scripts (and your homework) can import it.

```bash
cp ./module1/lesson2_slack/slack.py /opt/balerica-bank/
cd /opt/balerica-bank
ls slack.py
```

Expected output:

```text
slack.py
```

If you get `Permission denied`, check who owns the folder with
`ls -ld /opt/balerica-bank` — on a Lesson 1 instance it belongs to
`ec2-user` and the copy just works.

## Step 3 — Put YOUR workspace URL into `slack.py`

Open the file with nano (see `nano_basics.md` if nano is new to you):

```bash
nano slack.py
```

Near the top, find:

```python
SLACK_WORKSPACE_URL = "https://chewbacca.slack.com"
```

Change `chewbacca` to **your own workspace name** — the URL you see in your
browser when you open your Slack workspace. Then save and exit:
**`Ctrl+O`, `Enter`, `Ctrl+X`**.

> This is not optional. `slack.py` refuses to run while the placeholder is in
> place. If you skip this step, the test fails with `CHOMP!!!` — Chewbacca
> bites regardless of validation.

## Step 4 — Create your `.env` with the webhook

Copy the template, lock it down, and edit it:

```bash
cp -n ./module1/lesson2_slack/slack.env.example /opt/balerica-bank/.env
chmod 600 .env
nano .env
```

(`cp -n` means "no overwrite" — if you already have a `.env` from an earlier
lab, it is left alone; just add the Slack lines to the existing file instead.)

In nano, replace the placeholder with your **real Incoming Webhook URL** from
the Slack app you created in `runbook.md`:

```dotenv
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/REAL/WEBHOOK
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
SLACK_ALERT_CHANNEL=balerica-alerts
```

Save and exit: **`Ctrl+O`, `Enter`, `Ctrl+X`**.

Remember: `.env` is hidden. `ls` won't show it; `ls -a` will. Why this file
exists at all is explained in `env_explained.md`. Make sure `.env` is ignored
by git:

```bash
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

## Step 5 — Activate the venv and install the two dependencies

Your bank already has a virtual environment from Lesson 1. Use it:

```bash
cd /opt/balerica-bank
source venv/bin/activate
```

Your prompt now starts with `(venv)` — same as Lesson 1, Step 4. Install
what `slack.py` needs:

```bash
python -m pip install requests python-dotenv
```

Expected output ends with `Successfully installed ...` (or says the
packages are already satisfied — also fine). Verify:

```bash
python -c "import requests; import dotenv; print('Dependencies OK')"
```

Expected output:

```text
Dependencies OK
```

## Step 6 — Run the test

```bash
python slack.py --test
```

Expected output:

```text
SUCCESS: Chewbacca approves!
```

Now open Slack on your computer and check `#balerica-alerts`. You must SEE
the alert. A success message in the terminal without a message in Slack is
not done (check you're looking at the workspace the webhook belongs to).

## If something went wrong

| You see | Go fix |
|---|---|
| `FAILED: CHOMP!!! Chewbacca bit you...` | Step 3 — you left the placeholder URL |
| `FAILED: Configure SLACK_WEBHOOK_URL in .env...` | Step 4 — `.env` missing, wrong folder, or placeholder webhook |
| `ModuleNotFoundError: No module named 'requests'` | Step 5 — venv not active or packages not installed |
| `No such file or directory: slack.py` | Step 2 — you are not in `/opt/balerica-bank`, run `pwd` |
| Terminal success but nothing in Slack | Wrong workspace/channel open — the webhook decides where it goes |

Full troubleshooting lives in `runbook.md`, section 4.

> **Chewbacca's checkpoint:** RRRRAAAWWWRRR! Repo pulled, file copied, URL
> changed, webhook hidden in `.env`, venv on, test green, alert SEEN in Slack.
> That is an installation. That is engineering.
