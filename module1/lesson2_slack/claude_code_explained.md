# Why Claude Code? The AI Assistant in Your Terminal, Explained

This lab required Claude Code, and some of you wondered why an AI tool is
mandatory in a foundations class. Short answer: because AI-assisted
engineering is now how the industry works, and learning to use it **well** —
as an assistant, not a replacement — is itself a foundational skill.

## 1. What Claude Code is

Claude Code is an AI coding agent that runs **in your terminal, inside your
project folder**. Unlike a chatbot in a browser tab, it can:

- **Read your actual files** — when you ask about `slack.py`, it reads the
  real `slack.py` on your machine, not a guess about what it might contain.
- **Explain real errors** — paste the exact failure and it reasons about
  your code, your runbook, and your setup together.
- **Propose changes as diffs** — it shows you exactly what it wants to edit,
  and you approve or reject before anything happens.
- **Run commands with your permission** — and you should read them first.

That "inside your project" part is the difference. A browser chatbot answers
from memory and guesses about your setup. Claude Code looks at the truth.

## 2. Why it matters for your career

The industry has already moved. Engineers at most companies now work with an
AI assistant in the loop — Claude Code, Cursor, GitHub Copilot, or similar.
Employers increasingly expect you to be productive **with** these tools: to
know what to ask, what to verify, and what to refuse. There are two failure
modes, and both are career-limiting:

1. **Refusing the tool.** You'll be outpaced by engineers who use it well,
   the same way the engineer who refused Google was outpaced in 2005.
2. **Trusting the tool blindly.** AI output is a hypothesis, not a fact. It
   is confidently wrong often enough that blind trust ships outages. The
   engineer who pastes AI code they don't understand into production is a
   danger, and interviewers can smell it.

The skill employers want is the middle path, and it's exactly what this lab
drilled: **ask well, read the answer, verify against reality, stay in
charge.** That's why the lab had you run the test and SEE the Slack message
instead of believing any explanation — yours or the AI's.

## 3. What Claude Code did for you in this lab (the benefits, concretely)

- **A patient tutor at 11 PM.** "Explain the difference between a workspace
  URL and a webhook URL like I'm new" — it answers instantly, as many times
  as you need, with zero judgment. That compresses weeks of confusion.
- **A faster debugger.** `ModuleNotFoundError`? Instead of 40 minutes of
  forum archaeology, you asked, got the likely cause (wrong interpreter /
  venv not active), got one verification command, and moved on.
- **A reading companion for real code.** It walked you through `send_alert()`
  line by line: the severity filter, the URL validation, the timeout.
  Reading code with a guide is how juniors become mid-levels.
- **A checklist thinker.** "Help me design a checklist proving the alert
  was delivered" — it helps you think like an engineer, not just type like one.

## 4. The rules exist because the tool is powerful

The lab's rules for Claude Code are not ceremony; each blocks a real accident:

| Rule | The accident it prevents |
|---|---|
| Never paste the webhook or `.env` into a prompt | Your secret ends up in a chat log/screenshot and must be rotated |
| Ask it to *read* files before answering | Answers based on guesses about code it hasn't seen |
| Review every diff before accepting | A "helpful" rewrite that breaks the `send_alert()` interface your homework depends on |
| Explain before executing | Running a command neither of you actually checked |
| Prove, don't believe | "It should work now" is not an alert in `#balerica-alerts` |

Notice these are the same habits you'd want with a talented but brand-new
intern. That's the right mental model: **Claude Code is a tireless intern
with an enormous memory. You are the engineer of record.**

## 5. How this grows through the course

Today Claude Code explained a 70-line script. In coming labs it will help you
read FastAPI routes, COBOL return codes, and monitoring agents like
`health.py` and `analyze_logs.py` — systems too large to hold in your head at
once. The students who practice the ask-verify loop now will handle the
banking monolith later without fear. That is the plan.

> **Chewbacca's assessment:** RRRRAAAWWWRRR. The droid is clever. The Wookiee
> still flies the ship. Never confuse the two.
