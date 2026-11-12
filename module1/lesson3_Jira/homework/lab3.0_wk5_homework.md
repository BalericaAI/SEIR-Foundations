# SEIR Foundations — Module 1, Lesson 3 Homework

## Jira: A Day in My Shoes

**Course:** SEIR Foundations  
**Lesson:** Module 1 / Lesson 3 — Jira Cloud + Agile (Week 5)  
**Difficulty:** Beginner  
**Format:** Individual homework + optional "Be A Man" extra credit  
**Homework deadline:** **Tuesday, November 17, 2026, at 12:00 PM Eastern Time** (11:00 AM Central / 9:00 AM Pacific / 5:00 PM London)  
**Extra credit deadlines:** BAM_5.1–5.3 by **Saturday, November 14, 2026, at 2:00 PM Eastern Time** (1:00 PM Central / 11:00 AM Pacific / 7:00 PM London); BAM_5.4 and up by the Tuesday homework deadline — see Section 6  
**Submission methods:** Send to Theo via FB DM or email  
**Lab runbook:** [Jira Cloud Free Installation](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson3_Jira/jira_install.md)  
**Integration lab (extra credit):** [Balerica AI Incident Integration Lab](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson3_Jira/readme.md)

> **Chewbacca's message:** RRRRAAAWWWRRR! You brush your teeth every day without a ticket. This week, you write the ticket. Every bite, every step, every bathroom break. Chewbacca estimates his own naps in story points.

---

## 1. Purpose

In class, most of you reached **Step 3** of `jira_install.md`: your Jira site exists, your Balerica AI project exists, and you created a test incident. This week you will:

- **Read** the first three chapters of *Head First Agile* (in the MEGA repository).
- **Break down one ordinary day of your life** into an epic, stories, and tasks in Jira, with a **story point estimate** on every story and task.
- **Explore** (optional reading, no submission) the politics, metrics, and real-world fit of Agile and Scrum.
- **(Optional)** Finish `jira_install.md` from Step 4 onward, then connect Jira and Slack with the integration lab. BAM_5.1–5.3 are due **Saturday at 2:00 PM Eastern**; the rest are due with the homework on Tuesday.

**Why this matters:** every engineering team you join will hand you work as Jira tickets. Breaking work into small, estimated pieces is a skill, and the easiest place to practice it is the thing you know best: your own day. If you can describe "make breakfast" clearly enough that a stranger could do it, you can describe "patch the EC2 fleet."

**There are no automatic failure conditions this week.** Read the requirements carefully anyway.

---

## 2. Folder structure (required)

Add this folder to your existing homework repo (same repo and format as previous weeks — see [Aaron's example HW Repo](https://github.com/aaron-dm-mcdonald/seir-foundations-homework)).

```
seir-foundations-homework/
└── module1/
    ├── lab0_basics/
    ├── lab0.5_basics_contd/
    ├── lesson1_ec2/
    ├── lesson2_slack/
    └── lesson3_jira/
        ├── README.md                 (your evidence tables — Sections 4.4 and 6)
        ├── lesson3_notes.md          (only if you do extra credit)
        └── screenshots/
            ├── jira_estimation_on.jpg
            ├── jira_epic.jpg
            ├── jira_story.jpg
            ├── jira_task.jpg
            ├── jira_backlog.jpg
            ├── BAM_5.1.jpg           (extra credit)
            ├── BAM_5.2.jpg           (extra credit)
            ├── BAM_5.3.jpg           (extra credit)
            ├── BAM_5.4.jpg           (extra credit)
            ├── BAM_5.5.jpg           (extra credit)
            ├── BAM_5.6.jpg           (extra credit)
            └── BAM_5.7.jpg           (extra credit)
```

Use these file names exactly — they are how your work gets checked.

---

## 3. Required — Read *Head First Agile*, Chapters 1–3

Read chapters 1, 2, and 3 of *Head First Agile* from the MEGA repository.

No file is required for the reading. You will use its vocabulary (**epic**, **user story**, **estimate**, **sprint**) in Section 4, so read it **before** you build your Jira space.

---

## 4. Required — A Day in My Shoes (Jira)

> ⚠️⚠️⚠️ **WARNING: NO STORY POINTS, NO CREDIT** ⚠️⚠️⚠️
>
> 🚨 Every story and task screenshot **must show the "Story point estimate" field.** If the field is missing from a screenshot, **that screenshot gets no credit.** 🚨
>
> 📌 Story point estimate is a **space-wide setting** that you must turn on (4.2). Epics do **not** get points — the epic is the overarching goal, and its stories and tasks carry the points.

&nbsp;

### 4.1 Create your space

1. In Jira, choose **Spaces** (or **Projects**) → **Create space**.
2. Choose the **Scrum** template.
3. Choose **team-managed** when asked.
4. Name it **`SEIR-Saga_YourNameHere`** (for example, `SEIR-Saga_JaneDoe`).
5. Accept the key Jira suggests, and write it down.

**Do not use your `Balerica AI Incident Management` (BAI) project for this.** `jira.py` will create incident tickets there later. Keep it clean.

### 4.2 Turn on Story point estimate (space-wide)

1. In your new space, next to the space name in the sidebar, select **More actions (•••)** → **Space settings**.
2. Select **Features**.
3. Turn **Estimation** **ON**, and choose **Story points**.

Story points are now on every **story** and **task**. Screenshot this page as `jira_estimation_on.jpg`.

### 4.3 Break down your day

**The epic is one full day of your life.** The stories are the big blocks of that day. The tasks are the individual things you do inside each block, **including the mundane ones**: waking up, brushing your teeth, eating, walking, talking, driving, bathroom breaks, checking your phone, scrolling, waiting in line. If you did it, it is a task.

**Build this structure:**

| Level | How many | What it is | Example |
|-------|----------|------------|---------|
| **Epic** | 1 | `A day in my shoes` — one single day, start to finish | `A day in my shoes` |
| **Story** | at least 5 | A block of your day, written as a user story | `As a parent, I get my kids out the door so they are on time for school` |
| **Task** | at least 20 | One specific action inside a block | `[Morning] Brush teeth — 2 min, upstairs bathroom` |

**Rules:**

- Every story and every task must have the epic as its **Parent**.
- **Suggested (you have creative liberty):** start every task name with its block in square brackets, such as `[Morning]`, `[Commute]`, `[Work]`, `[Lunch]`, `[Evening]`, `[Bedtime]`, so it is clear which story it belongs to.
- **Every story and task gets a Story point estimate.** The epic does not — it is the overarching goal, and the work underneath it carries the points. Points measure effort compared with your other items, not minutes. You decide the values, but be consistent. Examples:
  - Driving to or from work = **3**
  - Healthy meal = **2**
  - Unhealthy meal = **1**
  - Work = **5**
- **Every story and task gets a Description of at least 2 sentences.** Be as descriptive as possible: when, where, how long, with whom, and what "done" looks like.
  - ✅ `[Commute] Drive to work — 35 min on I-90 in stop-and-go traffic. Podcast on. Done when I'm parked in the garage, level 2.`
  - ❌ `drive`
- Cover the **whole** day, from the alarm to falling asleep. Gaps count against you.

**Story ideas (use your own life):** waking up and getting ready, commute, work or school, meals, errands, exercise, family time, studying for SEIR, evening wind-down, bedtime.

> **Tip:** Subtasks are allowed if you want more detail. Subtasks do not get the Story point estimate field by default — add it under **Space settings → Work types → Subtask** and give each subtask points. Subtasks do not count toward your 20 tasks.

### 4.4 Evidence table (put this in your `lesson3_jira/README.md`)

List **every** item you created:

| Key | Type | Summary | Story points |
|-----|------|---------|--------------|
| SAGA-1 | Epic | A day in my shoes | — |
| SAGA-2 | Story | As a commuter, I get to work on time so I can start my day calm | 3 |
| SAGA-3 | Task | [Commute] Drive to work — 35 min on I-90 | 3 |
| | | | |

(The first rows are examples. Replace them with your real keys and values.)

Under the table, add:

- **Space name and key:** `SEIR-Saga_YourNameHere` / `YOURKEY`
- **Total story points of all stories and tasks:**
- **Your biggest task, and why you estimated it that way (2–3 sentences):**

### 4.5 Screenshots

Every story and task screenshot must show the **Story point estimate** field. Blur anything personal you do not want to share.

| Screenshot | It must show |
|------------|--------------|
| `jira_estimation_on.jpg` | Space settings → Features, with **Estimation ON** and **Story points** selected |
| `jira_epic.jpg` | Your `A day in my shoes` epic opened, with its child work items and their story points visible |
| `jira_story.jpg` | One story opened, showing its **Parent** (the epic), description, and **Story point estimate** |
| `jira_task.jpg` | One task opened, showing its **Parent** (the epic), description, and **Story point estimate** |
| `jira_backlog.jpg` | The backlog (or list view) showing your stories and tasks with their story point values |

---

## 5. Further reading, watching, and discussion (no submission)

Nothing to turn in for this section. These links are for your understanding. Read them **after** *Head First Agile* chapters 1–3, and compare the book's version of Agile with what working engineers say about it.

### Topic 1 — Interoffice politics surrounding Agile

| Read | Reddit | Watch |
|------|--------|-------|
| [DZone: Resistance to Agile Transformations (Stefan Wolpers)](https://dzone.com/articles/resistance-to-agile-transformations) | [r/cscareerquestionsEU: Does anyone else hate Scrum?](https://www.reddit.com/r/cscareerquestionsEU/comments/spuwqi/does_anyone_else_hate_scrum/) | [GOTO 2015: Agile is Dead — Pragmatic Dave Thomas](https://www.youtube.com/watch?v=a-BOSpxYJ9M) |

Think about: who loses power when a team becomes self-organizing? Why would a manager resist that?

### Topic 2 — Hitting your story points during a sprint

| Read | Reddit | Watch |
|------|--------|-------|
| [Mountain Goat Software: Finish Everything Every Sprint?](https://www.mountaingoatsoftware.com/agile/agile-leadership/finish-everything-every-sprint) | [Is it normal for your boss to get mad at your team for finishing sprint tasks early?](https://redd.it/1sxe108) | [Sprint Planning with Jira, Part 2: Story Points and Velocity — Pros and Cons](https://www.youtube.com/watch?v=bvKDldShE8A) |

Think about: if a team finishes 100% of its points every sprint, is that good news or a warning sign?

### Topic 3 — Why Agile is used for DevOps work

| Read | Reddit | Watch |
|------|--------|-------|
| [Coveros: The Relationship between Agile and DevOps](https://www.coveros.com/blog/the-relationship-between-agile-and-devops/) | [r/devops: Sprints/Agile/Scrum? What to use when not really doing Programming?](https://redd.it/1raz8zq) | [Agile, Explained: DevOps](https://www.youtube.com/watch?v=qr0eaVUbduM) |

Think about: a Slack alert fires at 3 AM in the middle of a sprint. Where does that work go? Why do so many ops teams prefer Kanban?

### Topic 4 — The impact of Scrum on asynchronous work

| Read | Reddit | Watch |
|------|--------|-------|
| [Scrum.org: How Async Scrum Teams Self-Manage Without Daily Scrums](https://www.scrum.org/resources/blog/how-async-scrum-teams-self-manage-without-daily-scrums) | [Required standups every morning — is there an alternative?](https://redd.it/1psjfqi) | [Async Daily Scrum: Pros and Cons, with Ed Martin](https://www.youtube.com/watch?v=BAdfoMDOEjY) |

Think about: this class is spread across time zones. Which Scrum events would survive if we never met live?

---

## 6. "Be A Man" (BAM) extra credit

> ⏰⏰⏰ **EXTRA CREDIT HAS TWO DEADLINES** ⏰⏰⏰
>
> 🚨 **BAM_5.1, 5.2, and 5.3** only count if their screenshot timestamps are before **Saturday, November 14, 2026, 2:00 PM Eastern** (1:00 PM Central / 11:00 AM Pacific / 7:00 PM London). Late screenshots for these get no credit, even if your main homework is on time. 🚨
>
> 📅 **BAM_5.4 and up** are due with the main homework: **Tuesday, November 17, 2026, 12:00 PM Eastern**.

&nbsp;

Steps 4 and beyond of `jira_install.md`, plus the full Jira + Slack integration lab, are now fair game.

**Every BAM screenshot must prove its time:**

- **Terminal screenshots** must show the **ID line** (same as Lesson 1):

  ```bash
  whoami && TZ='America/New_York' date && ec2-metadata -i && uptime -s
  ```

  Use your own zone. If `ec2-metadata` is missing, run `sudo dnf install -y ec2-utils` first.

- **Browser and Slack screenshots** must show your **computer's clock with the date** (taskbar or menu bar) in the same image.

Add a **BAM** section to `lesson3_notes.md` with the Instance ID from each terminal screenshot.

> 🔒 **Never show your Jira API token, your Slack webhook URL, or your `.env` file in any screenshot, README, GitHub commit, Slack message, or AI prompt.**

### BAM_5.1 — Finish `jira_install.md` (Steps 4–5)

**Submission:** `BAM_5.1.jpg`

1. Complete **Step 4** of `jira_install.md`: save `JIRA_SITE_URL`, `JIRA_EMAIL`, `JIRA_PROJECT_KEY`, `JIRA_TEST_ISSUE_KEY`, and `JIRA_DEFAULT_ISSUE_TYPE` in a **private note**.
2. Complete the **Step 5** checklist, and copy it into `lesson3_notes.md` with every box checked.

Your screenshot must show your private note with **your email blurred**, next to your test incident (for example `BAI-1`) opened in Jira, with your computer's clock visible.

### BAM_5.2 — Verify Jira from EC2

**Submission:** `BAM_5.2.jpg`

1. Create an Atlassian API token ([Manage API tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)). Treat it like a password.
2. Copy the Jira files next to `slack.py`:

   ```bash
   cd ~/SEIR-Foundations && git pull
   cp ~/SEIR-Foundations/module1/lesson3_Jira/jira.py ~/SEIR-Foundations/module1/lesson3_Jira/incident.py /opt/balerica-bank/
   cd /opt/balerica-bank
   source venv/bin/activate
   ```

3. **Add** the Jira variables to your existing `.env` with `nano .env` (see `jira.env.example`). **Do not replace your Slack settings.**
4. Run:

   ```bash
   whoami && TZ='Your/Zone' date && ec2-metadata -i && uptime -s
   python3 -m pip install requests python-dotenv
   python3 jira.py --verify
   ```

Your screenshot must show the ID line and `jira.py --verify` succeeding. `--verify` checks access **without creating a ticket**.

### BAM_5.3 — Integration dry run, then the real test

**Submission:** `BAM_5.3.jpg`

Follow Section 5 of the [integration lab](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson3_Jira/readme.md):

```bash
whoami && TZ='Your/Zone' date && ec2-metadata -i && uptime -s
mkdir -p data
python3 slack.py --test
python3 jira.py --verify
python3 incident.py --dry-run
python3 incident.py --test
```

Your screenshot must show the ID line and the `incident.py --test` output, including the **Jira issue key** and the **Slack delivery outcome**.

**Run `--test` once.** Do not rerun it out of impatience: every new test can create another Jira issue. Check Slack and Jira first.

### BAM_5.4 — The Slack alert links to Jira

**Submission:** `BAM_5.4.jpg`

Screenshot `#balerica-alerts` showing the test incident alert with a **clickable Jira issue URL**, with your computer's clock visible. Click the link and make sure it opens the right issue.

### BAM_5.5 — The Jira issue exists

**Submission:** `BAM_5.5.jpg`

Screenshot the Jira issue that `incident.py --test` created, opened in your **BAI** project, showing its **issue key**, **title**, and **project**, with your computer's clock visible.

In `lesson3_notes.md`, write:

- **A short explanation (5–8 sentences):** describe the flow, which component creates the ticket, which component sends the alert, why Jira is called **before** Slack, and how you verified both results.
- **A troubleshooting note:** describe one configuration check you performed, even if your first test succeeded.

### BAM_5.6 — No duplicate tickets

**Submission:** `BAM_5.6.jpg`

`incident.py` uses a **stable incident ID** to avoid creating the same Jira ticket twice. Prove it.

Create `bam_dup_check.py` in `/opt/balerica-bank`:

```python
from incident import report_incident

result = report_incident(
    agent="bam_dup_check.py",
    severity="CRITICAL",
    message="Synthetic test: duplicate detection check (DRILL — not real)",
    incident_id="BAM-DUP-YOURINITIALS-001",
    evidence="Manual BAM test",
    recommendation="Confirm only one Jira issue exists for this ID",
)
print(result)
```

Replace `YOURINITIALS` with your initials. Run it **twice**:

```bash
whoami && TZ='Your/Zone' date && ec2-metadata -i && uptime -s
python3 bam_dup_check.py
python3 bam_dup_check.py
```

Your screenshot must show the ID line and both runs returning the **same Jira issue key**. In `lesson3_notes.md`, explain where the incident ID is stored and what would happen with a **different** ID.

### BAM_5.7 — Live your day as a sprint

**Submission:** `BAM_5.7.jpg`

Turn Section 4 into a real sprint.

1. In your `SEIR-Saga_YourNameHere` space, create a sprint named `Day Sprint — YYYY-MM-DD` that lasts **one day**.
2. Move your stories and tasks into it, and **start the sprint** in the morning.
3. As you actually do each thing during the day, move it to **Done**.
4. At the end of the day, **complete the sprint**. Anything unfinished goes back to the backlog.

Your screenshot must show the sprint's **burndown chart** or **sprint report** (from **Reports**), with your computer's clock visible.

In `lesson3_notes.md`, answer:

- How many story points did you commit to, and how many did you complete?
- Which tasks did not get done, and why?
- Was anything you did that day **missing** from your backlog? (That is unplanned work. How does it connect to the DevOps reading in Section 5?)

### Extra credit evidence table

| Item | Requirement | Due | Screenshot | Done? |
|------|-------------|-----|------------|-------|
| BAM_5.1 | `jira_install.md` Steps 4–5: private note (email blurred) + test incident open | Sat 11/14, 2 PM ET | `screenshots/BAM_5.1.jpg` | Yes / No |
| BAM_5.2 | `jira.py --verify` succeeds on EC2 | Sat 11/14, 2 PM ET | `screenshots/BAM_5.2.jpg` | Yes / No |
| BAM_5.3 | `incident.py --test` shows Jira key + Slack delivery | Sat 11/14, 2 PM ET | `screenshots/BAM_5.3.jpg` | Yes / No |
| BAM_5.4 | Slack alert with clickable Jira link | Tue 11/17, 12 PM ET | `screenshots/BAM_5.4.jpg` | Yes / No |
| BAM_5.5 | Jira issue created by `incident.py` | Tue 11/17, 12 PM ET | `screenshots/BAM_5.5.jpg` | Yes / No |
| BAM_5.6 | Same incident ID twice → same Jira key | Tue 11/17, 12 PM ET | `screenshots/BAM_5.6.jpg` | Yes / No |
| BAM_5.7 | One-day sprint completed; burndown or sprint report | Tue 11/17, 12 PM ET | `screenshots/BAM_5.7.jpg` | Yes / No |

**Screenshot guidance:** Do not expose private keys, passwords, AWS access keys, Jira API tokens, Slack webhook URLs, or other secrets in any screenshot.

---

## 7. Definition of done

&nbsp;

> ⏰⏰⏰ **TWO DEADLINES THIS WEEK** ⏰⏰⏰
>
> 🟢 **Extra credit BAM_5.1–5.3:** screenshots timestamped before **Saturday, November 14, 2026, 2:00 PM Eastern**.
>
> 🔵 **Everything else (including BAM_5.4 and up):** pushed to GitHub by **Tuesday, November 17, 2026, 12:00 PM Eastern**.

&nbsp;

**Required**
- [ ] I read chapters 1–3 of *Head First Agile*.
- [ ] I created a **team-managed Scrum** space named `SEIR-Saga_YourNameHere` (not my BAI project).
- [ ] I turned on **Estimation → Story points** for the space and screenshotted it.
- [ ] I created **1 epic** (`A day in my shoes`), **at least 5 stories**, and **at least 20 tasks**, all with the epic as their Parent.
- [ ] My tasks cover my **whole day**, including the mundane things (eating, walking, talking, driving, bathroom breaks).
- [ ] **Every** story and task has a Story point estimate and a description of at least 2 sentences. (The epic has no points.)
- [ ] Every story and task screenshot shows the **Story point estimate** field.
- [ ] My `lesson3_jira/README.md` lists every item with its key, type, summary, and story points.
- [ ] I uploaded `jira_estimation_on.jpg`, `jira_epic.jpg`, `jira_story.jpg`, `jira_task.jpg`, and `jira_backlog.jpg`.
- [ ] I committed and pushed everything to my GitHub repository by **Tuesday, November 17, 2026, 12:00 PM Eastern Time**.

**Extra credit** (BAM_5.1–5.3 timestamped before **Saturday, November 14, 2026, 2:00 PM Eastern**; BAM_5.4 and up by **Tuesday, November 17, 2026, 12:00 PM Eastern**)
- [ ] `BAM_5.1.jpg` — `jira_install.md` Steps 4–5 complete.
- [ ] `BAM_5.2.jpg` — `jira.py --verify` succeeds.
- [ ] `BAM_5.3.jpg` — `incident.py --test` succeeds.
- [ ] `BAM_5.4.jpg` — Slack alert with a working Jira link.
- [ ] `BAM_5.5.jpg` — Jira issue created by the integration.
- [ ] `BAM_5.6.jpg` — duplicate detection proven.
- [ ] `BAM_5.7.jpg` — one-day sprint completed.
- [ ] My `lesson3_notes.md` has the BAM section, with Instance IDs, the 5–8 sentence explanation, and the troubleshooting note.
- [ ] No API token, webhook URL, or `.env` contents appear anywhere in my repo or screenshots.

> **Chewbacca's final assessment:** RRRRAAAWWWRRR! You turned a whole day into tickets. Breakfast has a key. Your commute has a story point. The bathroom break was estimated, scheduled, and closed. Next week, the bank writes its own tickets.
