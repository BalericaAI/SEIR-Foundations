# SEIR Foundations — Balerica AI Jira Integration Runbook

**Lab:** Jira Cloud incident tickets from Balerica AI on EC2
**Audience:** Students using individual Jira Cloud Free sites
**Goal:** Run `jira.py` on EC2 so it creates an incident ticket that you can open **and find on your own Jira board**, then connect the full alert pipeline (`incident.py` → Jira ticket → Slack alert with the ticket link).

> **YO STUDENT!** This runbook assumes `jira_install.md` is done: you have your own `*.atlassian.net` site, a Balerica AI project, and you know your **actual** project key. If any of that is missing, go back now. Chewbacca checks prerequisites first.

## Prerequisites — complete these FIRST

- [ ] **`jira_install.md`** — your own Jira Cloud Free site and the Balerica AI project exist, and you recorded your real project key (it may not be `BAI`).
- [ ] **Slack lab complete** — `python3 slack.py --test` posts to `#balerica-alerts` (see `slack_runbook.md`). You will need it for Step 6.
- [ ] `jira.py` is on your EC2 instance in the same directory as your existing `.env`.
- [ ] You can SSH into EC2 and have Python 3, `pip`, and your virtual environment from the Slack lab.

## Step 1 — Create the RIGHT kind of Atlassian API token

This step is where most students go wrong. Read it twice.

1. Sign in at **https://id.atlassian.com/manage-profile/security/api-tokens** using the **same email** you use for your Jira site. (Atlassian may email you a one-time passcode to verify your identity first.)
2. You will see **two** buttons: **Create API token** and **Create API token with scopes**.
3. Select **Create API token** — the plain one. **Do NOT select "Create API token with scopes."**
4. Name it something descriptive, such as `balerica-seir-ec2`.
5. Choose an expiration date. Atlassian requires between 1 day and 1 year. Pick the end of the course and **write the expiry date in your private notes** — when it expires, `jira.py` starts failing with 401 and nothing else changes.
6. Select **Create**, then **Copy to clipboard** immediately. **The token is shown exactly once** and cannot be recovered — only revoked and recreated.
7. Store it in a password manager or private note. Never in GitHub, screenshots, class chat, or Claude Code prompts.

> **Why the plain token?** `jira.py` talks directly to `https://YOUR-SITE.atlassian.net`. A token created **with scopes** only works against a different Atlassian gateway URL (`api.atlassian.com/ex/jira/...`), so it is **guaranteed to fail with `Jira HTTP 401`** in this lab — even though you copied it perfectly and your email is correct. If you already created a scoped token, create a new plain one.

**Success check:** You have a plain (unscoped) API token saved privately, and you know its expiry date.

## Step 2 — Add the Jira settings to your EXISTING `.env`

Your `.env` already contains your Slack settings. **Merge — do not replace.**

> **Do NOT run `cp jira.env.example .env`** — that overwrites the file and erases your Slack webhook. This exact mistake broke Slack for half of last cohort. Chewbacca remembers.

1. On EC2, change into the directory containing `jira.py` and `.env`.
2. Open the existing file: `nano .env` (or `vi .env`).
3. Add these lines at the bottom, keeping every existing Slack line untouched:

   ```dotenv
   # JIRA — added for lesson 3; do not remove the Slack lines above
   JIRA_SITE_URL=https://YOUR-SITE.atlassian.net
   JIRA_EMAIL=the-email-you-log-into-Atlassian-with@example.com
   JIRA_API_TOKEN=paste-your-plain-api-token-here
   JIRA_PROJECT_KEY=BAI
   JIRA_ISSUE_TYPE=Task
   JIRA_ENABLED=true
   INCIDENT_STATE_DB=data/incident_state.db
   ```

4. Fix each value:
   - `JIRA_SITE_URL` — your Jira site address, beginning `https://` and ending `.atlassian.net`. **Not** your Slack workspace URL, and no trailing path.
   - `JIRA_EMAIL` — your Atlassian **account** email, exactly as you sign in with.
   - `JIRA_API_TOKEN` — the token from Step 1. No quotes, no spaces, nothing else on the line.
   - `JIRA_PROJECT_KEY` — your project's **real** key. Open your project in the browser and read the prefix of any issue key (the `BAI` in `BAI-1`), or check the project URL. Do not assume `BAI`.
   - `JIRA_ISSUE_TYPE` — a work-item type that exists in your project. `Task` exists in the standard team-managed Kanban template; if your project only offers something else, use that name.
5. Save, then lock the file down and confirm nothing was lost:

   ```bash
   chmod 600 .env
   grep -c '^SLACK_' .env   # should still be 2 or more
   grep -c '^JIRA_' .env    # should be 6
   ```

**Success check:** Both `grep` counts are correct. If the Slack count is 0, restore your Slack settings before continuing.

## Step 3 — Verify connectivity (creates nothing)

From the directory containing `jira.py` and `.env`, with your virtual environment active:

```bash
python3 jira.py --verify
```

Expected output (your key and name will differ):

```text
Connected to Jira project: BAI (Balerica AI Incident Management)
```

This proves your site URL, email, token, and project key all work — **without creating a ticket**. If you see `JIRA ERROR` instead, the message tells you which variable to check; the table in Step 7 and `troubleshooting.md` section 5 go deeper. **Do not continue until `--verify` succeeds.**

## Step 4 — Create one test ticket

```bash
python3 jira.py --test
```

Expected output:

```text
Connected to Jira project: BAI (Balerica AI Incident Management)
Test issue created: https://YOUR-SITE.atlassian.net/browse/BAI-2
```

Run it **once**. Every `--test` run creates a real new ticket in your project.

**Success check:** The command printed a `/browse/...` URL with an issue key from **your** project.

## Step 5 — Find the ticket on your board (the part everyone struggles with)

Do these in order. The printed URL is your ground truth.

1. **Open the printed URL directly** in the browser where you are signed in to Jira. You should see the issue: summary `[Balerica AI][INFO] jira.py: SEIR Foundations Jira integration test - no real incident`, with your project under its key. If the URL works, **the API connection is fine** — anything that remains is a board-view question, not a connectivity problem.
2. Open your project and select **Board** in the left navigation. The test ticket should be a card in the leftmost column (usually **To Do**).
3. **Card not on the board? Check the Backlog first.** In team-managed projects with the backlog feature enabled, items often land in the **Backlog** list instead of the board. Select **Backlog** in the left navigation; if the ticket is there, drag it into the board column (or move it with its status field). This is the single most common reason students think the integration "didn't work."
4. Still missing? Work through these, in order:
   - **Search box / quick filters on the board** — clear any text in the board search and turn off quick filters.
   - **Wrong project** — compare the key prefix in the printed URL (`BAI-2` → project `BAI`) with the project whose board you are viewing. If they differ, fix `JIRA_PROJECT_KEY` in `.env`.
   - **Wrong site** — you may be signed in to a different Atlassian site (the instructor's demo, a work account). The site name is in the browser address bar; it must match `JIRA_SITE_URL`.
   - **Board filter** (company-managed projects) — the board's filter query may exclude the issue type. Open board settings and check the filter, or just use the project's **Issues**/work-item list view, which always shows everything.

**Success check:** You can open the ticket from the URL **and** point to the same card on your board (or explain that it was in the backlog and you moved it).

## Step 6 — Connect the alert pipeline (alerts → Jira board → Slack)

Now wire the full flow from `incident_integration.md`. All three modules must sit in the same directory; **`slack.py` is not in this lesson's folder — copy your working copy from the Slack lab** if it is not already beside `jira.py`:

```bash
ls slack.py jira.py incident.py .env   # all four must be present
mkdir -p data
python3 incident.py --dry-run
python3 incident.py --test
```

- `--dry-run` prints the workflow and calls **no** external services.
- `--test` creates a **real** Jira ticket, then posts a **real** Slack alert containing the ticket URL. Expected output is JSON like:

  ```json
  {
    "incident_id": "SEIR-TEST-20261113T182400123456",
    "jira_key": "BAI-3",
    "jira_url": "https://YOUR-SITE.atlassian.net/browse/BAI-3",
    "jira_created": true,
    "slack_status": "sent"
  }
  ```

Then verify **all three places**, not just the terminal:

1. The new ticket is on your Jira board (repeat Step 5 for `BAI-3` — this one is severity `ERROR`).
2. The Slack alert is in `#balerica-alerts` and its Jira link opens **that same ticket**.
3. The JSON shows `jira_created: true` and `slack_status: sent`.

If `slack_status` is anything else, the Jira half still worked — troubleshoot Slack alone (`slack_runbook.md` section 4, `troubleshooting.md` section 4). Do not delete the Jira ticket.

## Step 7 — Quick troubleshooting table

| Symptom | Most likely cause and fix |
|---|---|
| `JIRA ERROR: ... replace the placeholder JIRA_SITE_URL` | `.env` missing or still has `https://YOUR-SITE.atlassian.net`; set your real site URL |
| `Jira HTTP 401` immediately after creating a token | You chose **"Create API token with scopes"** — create a plain **"Create API token"** instead (Step 1) |
| `Jira HTTP 401` after weeks of working | Token expired (they live 1–365 days) or was revoked; create a new one and update `.env` |
| `Jira HTTP 401` with a fresh plain token | `JIRA_EMAIL` is not the Atlassian sign-in email, or the token was copied with spaces/quotes/a password manager line break |
| `Jira HTTP 403` | Your account cannot create issues in that project; confirm you own the project on **your** site |
| `Jira HTTP 404` | Wrong `JIRA_SITE_URL` or `JIRA_PROJECT_KEY`; run `--verify` and fix whichever it names |
| `Jira HTTP 400` on `--test` | `JIRA_ISSUE_TYPE` does not exist in the project, or the project demands extra required fields; set a type the project has (check project settings → work item types) |
| `--test` succeeded but no card on the board | Not a connectivity problem — Step 5: open the printed URL, then check **Backlog**, filters, project, and site |
| `Cannot reach Jira: ...` | EC2 has no outbound HTTPS or DNS; same network checks as the Slack lab |
| `ModuleNotFoundError: No module named 'requests'` (or `dotenv`) | Activate the virtual environment used in the Slack lab and `python3 -m pip install requests python-dotenv` |
| `ModuleNotFoundError: No module named 'jira'` or `'slack'` | `jira.py` / `slack.py` is missing from the current directory or misnamed (`jira.py.txt`); copy `slack.py` from the Slack lab folder |

Full diagnostic procedure: `troubleshooting.md`.

## Completion checklist

- [ ] Plain (unscoped) API token created, stored privately, expiry date noted.
- [ ] Jira variables merged into the existing `.env`; Slack variables still present; `chmod 600 .env`.
- [ ] `python3 jira.py --verify` reports the correct project key and name.
- [ ] `python3 jira.py --test` printed a ticket URL; the ticket opens in the browser.
- [ ] The same ticket is visible on your board (or you found it in the Backlog and know why).
- [ ] `python3 incident.py --test` shows `jira_created: true` and `slack_status: sent`.
- [ ] The Slack alert's Jira link opens the ticket created by that same test.
- [ ] No token, webhook, or `.env` contents in screenshots, Git, or chat.

**Lab complete.** Your EC2 instance now files Jira incident tickets and announces them in Slack with a working link.

> **CHEWBACCA'S FINAL REVIEW:** RRRRAAAWWWRRR! The ticket is not "in Jira" until you can show it **on your board**. The terminal is not evidence. The board is evidence.
