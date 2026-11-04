# Why Slack? Why This Lab Matters to Your Career

If today's lab felt like being shown electricity for the first time — good.
This page explains, in plain language, what Slack is, why companies run on it,
and why "my code just messaged a human" is a skill employers pay for.

## 1. What Slack actually is

Slack is a messaging app for workplaces. Think of it as group chat, organized
into **channels** — one channel per team or per topic. `#payments-team`,
`#new-hires`, `#balerica-alerts`. Companies use it instead of endless email
chains because conversation is instant, searchable, and organized by topic.

Slack is one of the standard tools of the modern workplace, alongside
Microsoft Teams and Discord-style tools. Walk into almost any tech company
and some version of this is open on every engineer's screen all day. Learning
it is like learning email was in 1998: not optional for long.

## 2. The big idea you proved today: machines can talk to people

Here is what you actually built, in one sentence:

> **A program on a server in an Amazon datacenter detected something and told
> a human about it, instantly, on the phone in their pocket.**

Before today, the only way you knew what your EC2 instance was doing was to
SSH in and look. That doesn't scale. A real company has hundreds or thousands
of servers. Nobody is logged into them watching. So how does anyone know when
something breaks at 3 AM?

**This. Exactly this.** A monitoring script notices a problem, and a message
appears in a channel like `#balerica-alerts`. An on-call engineer's phone
buzzes. They open Slack, read "disk 91% full on payment server," and fix it
before customers ever notice. The pattern you built today — detect, format,
notify — is called **alerting**, and it is how the entire industry stays
awake so humans can sleep.

## 3. "But it's just a chat message" — no, it's a career skill

The specific thing you did — **sending an HTTP POST with a JSON payload to a
webhook URL** — is one of the most reused patterns in all of software:

- **Alerting and on-call:** Tools like PagerDuty, Opsgenie, and Datadog all
  deliver into Slack channels exactly like your script does. You built the
  core of what those billion-dollar products do.
- **ChatOps:** Many teams deploy code, check system status, and run
  operations from inside Slack. The chat channel becomes the control room.
- **Integrations everywhere:** "When a customer pays, post to `#sales`."
  "When a build fails, post to `#ci`." "When a server dies, post to
  `#alerts`." Every one of those is your `send_alert()` with different words.
- **Webhooks generally:** The webhook idea (a secret URL you POST to) is how
  Stripe reports payments, how GitHub triggers builds, how most of the
  internet's services talk to each other. You now know it from the inside.

When a job posting says "experience with monitoring, alerting, and
incident response" — you started that experience today.

## 4. Why alerts and not just logs?

Lesson 1 gave the bank logs. Logs are the **evidence**: detailed, complete,
and nobody reads them until something is wrong. Alerts are the **doorbell**:
short, loud, and impossible to miss. Real systems need both:

| | Logs | Slack alerts |
|---|---|---|
| Who reads it | Engineers investigating | Everyone on the team, instantly |
| When | After you know there's a problem | The moment the problem starts |
| Detail | Everything | One or two lines + severity |
| Lives in | Files / CloudWatch | A channel on your phone |

That's also why `slack.py` has severity filtering. If every INFO message
pinged the team, people would mute the channel and miss the real emergency.
Knowing **what deserves an alert** is a mark of a senior engineer.

## 5. The 12th-century peasant speech

You are not wrong to feel like this is magic. Here's the honest version:

A free chat account, a free-tier server, 70 lines of Python, and one secret
URL — and you assembled the same notification pipeline that banks, hospitals,
and airlines pay teams to maintain. It is not magic; it is **plumbing you can
now build**. The senior students in class were happy because they've seen
companies pay real money for exactly this skill. The peasant who learns how
the lightning works stops being a peasant.

You did not "just send a chat message." You wired a machine to a human.
Everything in operations — monitoring, on-call, incident response, ChatOps —
is that wire, repeated.

> **Chewbacca's perspective:** RRRRAAAWWWRRR. A Wookiee howls and the whole
> ship knows. Today your server learned to howl. That is not small.
