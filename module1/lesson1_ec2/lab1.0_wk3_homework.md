# SEIR Foundations — Module 1, Lesson 1 Homework

## Balerica Legacy Bank: Repeat It, Break It (Safely), Research It

**Course:** SEIR Foundations  
**Lesson:** Module 1 / Lesson 1 — EC2 + Balerica Legacy Bank (FastAPI with a COBOL core)  
**Difficulty:** Beginner  
**Format:** Individual homework + spotter check-in + optional "Be A Man" extra credit  
**Homework deadline:** **Tuesday, November 3, 2026, at 12:00 PM Central Time** (1:00 PM Eastern / 10:00 AM Pacific / 6:00 PM London)  
**Submission methods:** Send to the SEIR Foundations FB chat, or to Theo via FB DM or email  
**Reference course:** Stéphane Maarek's AWS Udemy course  
**Lab runbook:** [Balerica Legacy Bank — Student Runbook](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson1_ec2/API/runbook.md)

> **Chewbacca's message:** RRRRAAAWWWRRR! Once is luck. Seven times is skill. Run the bank until your fingers know the way.

---

## 1. Purpose

In class, most of you reached **Step 4** of the runbook: the COBOL core is compiled and the FastAPI server is running. This week you will:

- **Repeat** Steps 0–4 seven times, on seven fresh EC2 instances, across at least three days, until the process is muscle memory.
- **Practice** talking directly to the COBOL core and reading its return codes.
- **Clone your own homework repo** onto an EC2 instance.
- **Research** databases, COBOL, SWIFT, and APIs — the four building blocks of the bank you just ran — using reading, video, and AI.
- **(Optional)** Explore beyond Step 4: connect Bedrock, bake the lab into your launch template, and build a golden AMI.

**Why this matters for next week:** the next lab turns Balerica AI into a platform with FastAPI (`app.py`). You will see `GET` vs `POST`, JSON request bodies, Pydantic validation, and the `/docs` console. The API research below prepares you for that.

&nbsp;

> ⚠️⚠️⚠️ **WARNING: THE SCREENSHOT DAILY LIMIT IS STRICT** ⚠️⚠️⚠️
>
> 🚨 **No more than 3** of your 7 lab-run screenshots may show the same date (your local time). **4 or more on the same date is an AUTOMATIC FAILURE FOR THIS WEEK.** 🚨
>
> 📅 That means you need **at least 3 separate days**. Start early. Waiting until Monday night means you cannot pass.

&nbsp;

---

## 2. Folder structure (required)

Add this folder to your existing homework repo (same repo and format as Lab 0.5 — see [Aaron's example HW Repo](https://github.com/aaron-dm-mcdonald/seir-foundations-homework)).

```
seir-foundations-homework/
└── module1/
    ├── lab0_basics/
    ├── lab0.5_basics_contd/
    └── lesson1_ec2/
        ├── README.md                      (your evidence tables — Sections 3 and 9)
        ├── lab1_notes.md                  (your personal notes)
        ├── ai_review_YourNameHere.txt
        ├── spotter_YourNameHere.txt
        ├── AI_enabled_study_lab1.0.txt
        └── screenshots/
            ├── lab1_run1.jpg  …  lab1_run7.jpg
            ├── Maarek_Section21_quiz.jpg
            ├── Maarek_Section23_quiz.jpg
            ├── Maarek_Section25_quiz.jpg
            ├── cobol_rc0.jpg
            ├── cobol_rc4.jpg
            ├── cobol_rc8.jpg
            ├── cobol_rc12.jpg
            ├── cobol_ledger_decode.jpg
            ├── git_clone.jpg
            ├── BAM_2.1.jpg      (extra credit)
            ├── BAM_2.2.jpg      (extra credit)
            └── BAM_2.3.jpg      (extra credit)
```

Replace `YourNameHere` with your name. Use these file names exactly — they are how your work gets checked.

---

## 3. Required — Complete the lab seven times

### 3.1 What counts as one run

One run = **one brand-new EC2 instance** taken from launch through **Step 4** of the runbook (Steps 0, 1, 2, 3, 4), done by hand.

- Launch from your saved launch template (or the console), SSH in, and follow the runbook.
- Instances built from a baked launch template or a golden AMI (BAM_2.2 / BAM_2.3) **do not count** toward the seven. The point is to do the steps yourself.
- When the run is done: `Ctrl+C` the server, **terminate the instance**, and check **EC2 → Volumes** and **Elastic IPs** for leftovers. **Keep your launch template.**

### 3.2 What the screenshot must show

Right **before** you start uvicorn in Step 4, run `whoami` and the date **in your own time zone**. Amazon Linux shows UTC by default, so set the zone for that one command:

```bash
whoami && TZ='America/Chicago' date
```

Use your own zone: `America/New_York`, `America/Chicago`, `America/Denver`, `America/Los_Angeles`, `Europe/London`, etc.

Then start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Take the screenshot when you see `Application startup complete.` It must show, in one image:

1. `ec2-user` (from `whoami`)
2. The local date and time (from `date`)
3. The uvicorn startup lines, including `Application startup complete.`

Save as `screenshots/lab1_run1.jpg` through `screenshots/lab1_run7.jpg`.

### 3.3 Daily limit

| Rule | Result |
|------|--------|
| 1–3 lab-run screenshots on the same local date | OK |
| **4 or more** lab-run screenshots on the same local date | **Automatic failure** for the week |
| The date in the screenshot does not match the date in your table | That run does not count |
| Two runs share the same Public DNS / Instance ID | Only one of them counts |

The daily limit applies **only** to the seven `lab1_run` screenshots. COBOL practice, git clone, quiz, and BAM screenshots do not count toward it.

### 3.4 Evidence table (put this in your `lesson1_ec2/README.md`)

Find the **Public IPv4 DNS** and **Instance ID** in **EC2 → Instances → (your instance) → Details**.

| Run | Date (local) | Time zone | Instance ID | Public IPv4 DNS | Screenshot | Terminated? |
|-----|--------------|-----------|-------------|-----------------|------------|-------------|
| 1 | 2026-10-29 | America/Chicago | i-0abc123example | ec2-3-91-0-1.compute-1.amazonaws.com | `screenshots/lab1_run1.jpg` | Yes |
| 2 | | | | | `screenshots/lab1_run2.jpg` | |
| 3 | | | | | `screenshots/lab1_run3.jpg` | |
| 4 | | | | | `screenshots/lab1_run4.jpg` | |
| 5 | | | | | `screenshots/lab1_run5.jpg` | |
| 6 | | | | | `screenshots/lab1_run6.jpg` | |
| 7 | | | | | `screenshots/lab1_run7.jpg` | |

(Row 1 is an example — replace it with your real values.)

### 3.5 Personal notes — `lab1_notes.md`

For **each run**, write at least **3 sentences**:

- What went differently this time?
- What error (if any) did you hit, and what fixed it?
- What did you understand this time that you did not understand before?

End the file with a **"Mistakes I made"** list (at least 3 items) and a **"Commands I now know by heart"** list.

---

## 4. Required — Maarek quizzes

| Section | Deliverable |
|---------|-------------|
| Section 21 | Screenshot of the **completed** quiz, uploaded as `Maarek_Section21_quiz.jpg` |
| Section 23 | Screenshot of the **completed** quiz, uploaded as `Maarek_Section23_quiz.jpg` |
| Section 25 | Screenshot of the **completed** quiz, uploaded as `Maarek_Section25_quiz.jpg` |

---

## 5. Required — `ai_review_YourNameHere.txt`

Review the Lesson 1 runbook with the AI of your choice (Claude, ChatGPT, Gemini, etc.). Ask it to explain the parts you did not fully understand.

Use this format:

```
AI used = ?

Q1: (the question you asked)
AI's answer, in my own words:
How I checked it (ran a command, re-read the runbook, asked my spotter, etc.):

Q2: ...
(minimum 5 questions)

Where the AI was wrong, vague, or out of date:
(at least one example, and how you found out)
```

> 🔒 **Never paste private keys (`.pem` contents), AWS access keys, passwords, or tokens into an AI prompt.**

---

## 6. Required — `spotter_YourNameHere.txt`

```
Spotter = ?
5 things my spotter learned while working on the lab / homework:
1. ?
2. ?
3. ?
4. ?
5. ?
```

Be specific. Ask your spotter directly — these are **their** lessons, not yours.

- ✅ "Learned that return code 4 means the account was not found, and the program does not crash."
- ❌ "Learned a lot about EC2."

---

## 7. Required — Talk to the COBOL core

Do this on **any one** of your lab-run instances (before Step 4, after stopping the server, or in a second SSH window). Start in the bank folder:

```bash
cd /opt/balerica-bank
```

Each screenshot must also show `whoami && TZ='Your/Zone' date`.

### 7.1 Find your customers

```bash
cat data/accounts.dat
```

How many accounts are there? Write down every account ID.

### 7.2 Trigger every return code on purpose

Run each command, then immediately run `echo $?` to see the return code.

| Screenshot | Goal | Command to try |
|------------|------|----------------|
| `cobol_rc0.jpg` | **0** — success | `./cobol/bin/account_lookup 100001` |
| `cobol_rc4.jpg` | **4** — account not found | `./cobol/bin/account_lookup 999999` |
| `cobol_rc8.jpg` | **8** — business rejection | `./cobol/bin/payment_post TXN9001 100001 0.00 USD TEST-ZERO` (zero amount) — then try an amount bigger than the balance |
| `cobol_rc12.jpg` | **12** — environment failure | `cd ~` then `/opt/balerica-bank/cobol/bin/account_lookup 100001` (wrong folder) |

After the rc 12 test, go back with `cd /opt/balerica-bank`.

**Bonus:** if one of the accounts from 7.1 is not `ACTIVE`, try posting a payment to it. What return code and `REASON=` do you get?

### 7.3 Decode the fixed-width ledger by hand

Use the column layout from the runbook's Reference section:

```bash
cut -c1-6   data/accounts.dat    # account id
cut -c7-36  data/accounts.dat    # customer name
cut -c37-44 data/accounts.dat    # status
cut -c45-56 data/accounts.dat    # balance (implied decimal!)
cut -c57-59 data/accounts.dat    # currency
```

Screenshot as `cobol_ledger_decode.jpg`.

### 7.4 Write it up (add a "COBOL practice" section to `lab1_notes.md`)

- What each return code meant, and the `REASON=` the program gave you.
- Decode Alice's balance by hand: what are the raw 12 characters, and what dollar amount do they mean? Why is there no decimal point in the file?
- Run `cat data/payments.dat`. Find your own test transactions. Then look up account `100001` again. Did the balance change after your payments? Write down what you see and your best guess why.

**Optional:** check if the SQLite command-line tool is installed with `which sqlite3`. If it is, run `sqlite3 data/bank.db ".tables"` and `sqlite3 data/bank.db ".schema"`, and describe what tables the bank keeps.

---

## 8. Required — Clone your own homework repo onto EC2

On any lab-run instance:

```bash
cd ~
whoami && TZ='Your/Zone' date
git clone https://github.com/YOUR-GITHUB-USERNAME/seir-foundations-homework.git
ls seir-foundations-homework/module1
```

Screenshot as `git_clone.jpg`.

- Your homework repo must be **public** for this to work without logging in.
- **Clone only. Do not push from the EC2 instance**, and do not put a GitHub token or password on the server for this assignment.

---

## 9. Required — `AI_enabled_study_lab1.0.txt`

For each of the 5 topics below, you will use **three sources**:

1. **Read** the listed source.
2. **Watch** the listed video.
3. **Ask an AI** (your choice) the research points the reading and video did not answer.

Then write **one paragraph per topic, minimum 5 sentences**, in your own words.

### Rules

- **Every number needs a source and a year.** Example: "about X billion lines of COBOL (source: ___, 2022)." COBOL and banking statistics are repeated all over the internet without dates, and many disagree. If two sources disagree, say so.
- If the AI gives you a number, ask it where the number comes from, then try to find that source yourself.
- Do not paste the AI's answer. Your paragraph must be your own writing.

### File format

```
=== Topic 1: Databases ===
Read:    (title + link)
Watched: (title + link)
AI used: ?
Prompt(s) I asked the AI:
One thing the AI said that I double-checked, and what I found:

Paragraph (minimum 5 sentences):

Numbers + sources:
- (number) — (source, year)

=== Topic 2: COBOL ===
...
```

### Topic 1 — Database basics

| Read | Watch |
|------|-------|
| [AWS: What's the Difference Between Relational and Non-relational Databases?](https://aws.amazon.com/compare/the-difference-between-relational-and-non-relational-databases/) | [IBM Technology: SQL vs. NoSQL — What's the difference?](https://www.youtube.com/watch?v=Q5aTUc7c4jg) (6 min) |

Research points:

- What is a database, and why does nearly every application need one?
- Types of databases (relational, key-value, document, graph, etc.).
- How do you choose one database over another?
- What do SQL and NoSQL mean? How are they represented in the cloud? (Example: Amazon RDS / Aurora vs. DynamoDB.)
- Which databases are the de facto standards? Compare SQLite, Microsoft SQL Server, MariaDB/MySQL, and PostgreSQL.
- Strengths and weaknesses of PostgreSQL.
- **Lab hook:** Balerica's system of record is SQLite (`data/bank.db`). Why might a teaching lab choose SQLite, and why would a real bank probably not?

### Topic 2 — COBOL basics

| Read | Watch |
|------|-------|
| [Wikipedia: COBOL](https://en.wikipedia.org/wiki/COBOL) | [Fireship: COBOL in 100 Seconds](https://www.youtube.com/watch?v=7d7-etf-wNI) (2 min) |

Research points:

- What is COBOL, and who introduced it?
- How was it first integrated into infrastructure (mainframes, government, banks)?
- How many systems use COBOL today?
- What is the value of the systems that run on COBOL (transactions, money, records)?
- What is the average age of COBOL engineers, and why does it matter?
- How much effort would replacing COBOL take, and why have so many replacement projects struggled?
- **Lab hook:** In `payments.dat`, 125.50 is stored as `000000012550`. Why would a 1959 business language store money with an *implied* decimal instead of a decimal point?

### Topic 3 — SWIFT basics (the financial payment messaging network)

> **Note:** This is **SWIFT, the Society for Worldwide Interbank Financial Telecommunication** — the network banks use to send payment instructions. It is **not** Apple's Swift programming language.

| Read | Watch |
|------|-------|
| [Wikipedia: SWIFT](https://en.wikipedia.org/wiki/SWIFT) | [a16z: Foreign Exchange 101 — What Happens When You Send Money Abroad?](https://www.youtube.com/watch?v=eoXdyO9oGJc) (6 min) |

Research points:

- What is SWIFT, who introduced it, and when?
- Does SWIFT actually move money, or does it move *messages* about money? What are correspondent banks?
- How is SWIFT used day to day? Who uses it?
- Close competitors and alternatives (for example: CIPS, SPFS, Ripple, real-time payment systems).
- How much effort would replacing SWIFT take?
- **ISO 20022 deep dive:**
  - What is ISO 20022, and how is it different from the older MT message format?
  - What is an **MT103**? What is an **MT202**? How are they different?
  - What replaced them? (Look up **pacs.008** and **pacs.009**.)
  - When did the MT/ISO 20022 "coexistence period" end for cross-border payment instructions? Confirm the date on Swift's own FAQ: [Swift ISO 20022 FAQs — Implementation](https://www.swift.com/standards/iso-20022/iso-20022-faqs/implementation).
  - Which MT messages are still in use after that date, and why do old formats survive so long?
- **Lab hook:** Your traffic generator sends **MT103** messages — a format that is now retired for cross-border payment instructions. Why might a training lab still teach MT103? What would change if Balerica switched to pacs.008?

### Topic 4 — API basics

| Read | Watch |
|------|-------|
| [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) | [IBM Technology: What is a REST API?](https://www.youtube.com/watch?v=lsMQRaeKNDk) (9 min) |

Research points:

- What is an API, and who introduced the idea (and the REST style)?
- How many systems use APIs today? How are they used?
- Close competitors and alternatives: REST vs. SOAP vs. GraphQL vs. gRPC.
- Why are APIs important for AI adoption? (Hint: how does your EC2 talk to Amazon Bedrock?)
- Why is securing API communications difficult? (Look up authentication, TLS, input validation, and the OWASP API Security Top 10.)
- **Next-lab prep:**
  - What is the difference between `GET` and `POST`?
  - What is JSON, and why do APIs use it?
  - Why should an API never trust incoming data, even from a "friendly" client?
- **Lab hook:** Look at the runbook's API endpoints table. Which Balerica endpoints are `GET` and which are `POST`? Why does `/payments` need to be `POST`?

### Topic 5 — Where COBOL, SWIFT, APIs, and databases meet

| Read | Watch |
|------|-------|
| [US GAO (2025): Agencies Need to Plan for Modernizing Critical Decades-Old Legacy Systems](https://files.gao.gov/reports/GAO-25-107795/index.html) | [Modernizing COBOL: From Mainframe to API](https://www.youtube.com/watch?v=-CI8hb-077E) (6 min) |

Research points:

- Trace one payment through Balerica in your own words: SWIFT message → FastAPI → COBOL program → fixed-width file → SQLite. Which piece is old, which is new, and why keep both?
- Why do organizations often **wrap** legacy systems with APIs instead of replacing them?
- How do these four technologies matter to different industries: **financial, medical/healthcare, academic, and government**? Give at least one real example per industry.
- What risks does the GAO report describe for systems that are decades old?
- How is AI being used today to understand or modernize COBOL systems, and what are its limits?

---

## 10. "Be A Man" (BAM) extra credit

Steps 5–8 of the runbook are now fair game. Each screenshot must show `whoami` and the local `date`.

### BAM_2.1 — Make `/ask` answer with Bedrock

**Submission:** `BAM_2.1.jpg`

**Student Challenge:** make the Balerica AI helper answer from a real Claude model instead of `offline-knowledge-base`.

> 📢 **Updated instructions:** AWS retired the Bedrock **Model Access** page. Serverless models are now available automatically in your Region. **Anthropic (Claude) models still require a one-time usage form** the first time you use them in your account.

All three requirements from the runbook's "Why `/ask` might silently stay offline" section must be true:

1. **IAM role:** create an IAM role with Bedrock invoke permission and attach it to your instance. Use `iam/PERMISSIONS.md` in the lab's `API` folder as your guide. (In your own AWS account, you are the admin.) **Do not put AWS access keys on the instance.**
2. **Region:** `AWS_REGION` must match the Region where you will call Bedrock.
3. **Model ID:** `BEDROCK_MODEL_ID` must be a real **inference profile ID**. Newer Claude models need the inference profile ID (it starts with `us.`), not the base model ID. Find it in the Bedrock console.

Set the variables in **Window 1**, in the same terminal, **before** starting uvicorn:

```bash
cd /opt/balerica-bank
source venv/bin/activate
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=us.YOUR-INFERENCE-PROFILE-ID
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then in **Window 2**, ask a question with `curl` (Step 8). Your screenshot must show a response whose `source` is **not** `offline-knowledge-base`.

Bedrock calls are billed per use. A few test questions cost very little, but do not loop it.

### BAM_2.2 — Bake it in (launch template User Data)

**Submission:** `BAM_2.2.jpg`

Create a **new** launch template (for example `seir-lesson1-baked`) whose User Data installs the whole lab at boot, so a new instance is ready for Step 3 without you typing the install steps. **Do not overwrite your Lab 0 template.**

Starting point (you may need to debug it — that is the challenge):

```bash
#!/bin/bash
dnf install -y git
cd /home/ec2-user
sudo -u ec2-user git clone https://github.com/BalericaAI/SEIR-Foundations.git
sudo -u ec2-user bash SEIR-Foundations/module1/lesson1_ec2/API/install/install.sh
```

Launch an instance from it, wait a few minutes, then SSH in. Your screenshot must show:

- `sudo tail -n 20 /var/log/cloud-init-output.log` showing `Installation complete.`
- `cd /opt/balerica-bank && ./cobol/bin/account_lookup 100001` working — without you running the installer.

In `lab1_notes.md`, explain: what did you have to fix (if anything), and why does User Data run as `root` by default?

### BAM_2.3 — Build a golden AMI

**Submission:** `BAM_2.3.jpg`

Turn a successfully configured instance into a reusable image.

1. On an instance where Steps 0–4 worked, stop the server (`Ctrl+C`).
2. **EC2 → Instances → (your instance) → Actions → Image and templates → Create image.** Name it something like `seir-balerica-golden-v1`. (By default AWS reboots the instance to take a clean image.)
3. Wait until the AMI shows **Available** under **EC2 → AMIs**.
4. Launch a **new** instance from your AMI, SSH in, and go straight to Step 4:

```bash
cd /opt/balerica-bank
source venv/bin/activate
whoami && TZ='Your/Zone' date
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Your screenshot must show `Application startup complete.` on the AMI-launched instance, with no installer run.

In `lab1_notes.md`, record the AMI ID and answer:

- Were your earlier test payments still in `data/payments.dat` on the new instance? Why?
- What is the difference between a launch template (BAM_2.2) and an AMI (BAM_2.3)? When would you use each?

**Cost warning:** an AMI keeps an **EBS snapshot**, and snapshots are billed while they exist. Unless Theo tells you to keep it, **deregister the AMI** when you are done, then delete its snapshot under **EC2 → Snapshots**. Deregistering does not delete the snapshot for you.

### Extra credit evidence table

| Item | Requirement | Screenshot | Done? |
|------|-------------|------------|-------|
| BAM_2.1 | `/ask` answered by Bedrock (not `offline-knowledge-base`) | `screenshots/BAM_2.1.jpg` | Yes / No |
| BAM_2.2 | Baked launch template; cloud-init log + COBOL lookup with no manual install | `screenshots/BAM_2.2.jpg` | Yes / No |
| BAM_2.3 | Golden AMI; uvicorn starts on AMI instance with no installer | `screenshots/BAM_2.3.jpg` | Yes / No |

**Screenshot guidance:** Do not expose private keys, passwords, AWS access keys, tokens, or other secrets in any screenshot.

---

## 11. Definition of done

&nbsp;

> ⚠️⚠️⚠️ **WARNING: THE SCREENSHOT DAILY LIMIT IS STRICT** ⚠️⚠️⚠️
>
> 🚨 **4 or more** lab-run screenshots on the same local date is an **AUTOMATIC FAILURE FOR THIS WEEK.** 🚨
>
> ❌ No exceptions. Spread your seven runs over at least three days.

&nbsp;

**Required**
- [ ] I completed Steps 0–4 on **seven** fresh EC2 instances, with **no more than 3** on any one local date.
- [ ] Each `lab1_run` screenshot shows `whoami`, the local `date`, and `Application startup complete.`
- [ ] My `lesson1_ec2/README.md` has the run table with seven unique Instance IDs and Public DNS names.
- [ ] I terminated every lab instance and checked for leftover volumes and Elastic IPs. My launch template still exists.
- [ ] I uploaded `lab1_notes.md` with notes for every run, a "Mistakes I made" list, and a "COBOL practice" section.
- [ ] I completed the Maarek Section 21, 23, and 25 quizzes and uploaded the screenshots.
- [ ] I uploaded `ai_review_YourNameHere.txt` with at least 5 questions and one place the AI was wrong or vague.
- [ ] I uploaded `spotter_YourNameHere.txt` with my spotter's name and 5 specific things they learned.
- [ ] I triggered return codes 0, 4, 8, and 12 and decoded the ledger, with screenshots.
- [ ] I cloned my own homework repo onto EC2 (clone only, no push) and uploaded `git_clone.jpg`.
- [ ] I uploaded `AI_enabled_study_lab1.0.txt` with one paragraph (minimum 5 sentences) for each of the 5 topics, using all three sources per topic, with a source and year for every number.
- [ ] I committed and pushed everything to my GitHub repository by **Tuesday, November 3, 2026, 12:00 PM Central Time**.

**Extra credit**
- [ ] `BAM_2.1.jpg` — `/ask` answered by Bedrock.
- [ ] `BAM_2.2.jpg` — baked launch template works.
- [ ] `BAM_2.3.jpg` — golden AMI works.
- [ ] I deregistered unused AMIs, deleted their snapshots, and checked for leftover billable resources.

> **Chewbacca's final assessment:** RRRRAAAWWWRRR! Seven banks opened. Four return codes triggered on purpose. A legacy core you can read by hand. Next week, it becomes a platform.
