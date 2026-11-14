# SEIR Foundations — Cursor + Jira Integration Runbook

**Lab:** Connect the Cursor editor's AI agent to your Jira Cloud site
**Audience:** Students who completed `jira_install.md` and `jira_runbook.md` (your Balerica AI project exists and `jira.py` works)
**Goal:** Let Cursor's agent read, summarize, and create Balerica AI incident tickets directly from the editor — without ever pasting an API token into a prompt.

> **YO STUDENT!** This is an *optional productivity layer*, not a replacement for the lab. `jira.py` and `incident.py` are still the graded work: they teach you what the Jira REST API actually does. Cursor's integration sits on top of the same Jira project. Chewbacca does not accept "the AI did it" as a submission.

## 1. Why integrate Cursor with Jira?

In the lab you built the pipeline: agent → `incident.py` → Jira ticket → Slack alert. The ticket is the incident record — but investigating it still means bouncing between the browser, the terminal, and your editor. Connecting Cursor to Jira closes that loop:

- **The ticket becomes context for the code.** Ask Cursor to read `BAI-7`, and it sees the severity, the evidence, and the recommendation that `incident.py` filed — then investigates the code in the same conversation. No copy-pasting ticket text into prompts.
- **Less context switching.** Triage happens where the fix happens. "Summarize the open Balerica AI incidents and tell me which ones look like duplicates" is one prompt instead of ten browser tabs.
- **Two-way: Cursor can file and update tickets too.** After fixing something, ask Cursor to comment on the ticket with what changed, or to create a follow-up Task. The incident record stays complete without you retyping anything.
- **No credentials in prompts — a security upgrade.** The connection uses **OAuth in your browser**, not your `JIRA_API_TOKEN`. You sign in on Atlassian's consent screen; Cursor never sees your password or token, and every action is limited to **your existing Jira permissions**. This is exactly the "keep secrets out of AI chats" rule from `troubleshooting.md`, enforced by design.
- **An audit trail you can explain.** Each Jira action the agent takes shows up as a tool call you approve, and the resulting tickets/comments are attributed to your Atlassian account. You can answer Chewbacca's favorite question: *how do you know?*
- **It scales into real SEIR work.** Production incident response is ticket-driven. Practicing "read the ticket → investigate → update the ticket" inside one agent loop is the workflow this course builds toward in later modules.

## 2. Two integration paths — pick the one that matches your account

| Path | What it does | Requirements | Who should use it |
|---|---|---|---|
| **A. Atlassian Remote MCP Server in Cursor** (this runbook) | Cursor's agent gets Jira tools: search, read, create, and update work items in your site | Any Cursor account; your own Jira Cloud Free site; a browser | **All students** |
| **B. Cursor's native Jira integration** (instructor note) | Assign a Jira work item to Cursor, or mention `@Cursor` in a ticket comment, and a **Cloud Agent** starts working on it in your repo, posting status back to the ticket | Cursor **Teams/Enterprise** plan, Jira Commercial Cloud **with Rovo enabled**, Jira admin + Cursor team admin, a connected repo provider | Instructor/organization setups only — set up from the Cursor dashboard's integrations page via the Atlassian Marketplace |

Path B is not possible on individual free-tier accounts, so the steps below cover Path A. If your class is on a Cursor team, the instructor can demo Path B separately.

## 3. Steps — connect Cursor to your Jira site (Path A)

### Step 1 — Prerequisites

- [ ] Cursor is installed and signed in on your own machine.
- [ ] Your Jira Cloud Free site and Balerica AI project exist (`jira_install.md`), and you know your real project key.
- [ ] Your browser is signed in to Atlassian with the **same account** that owns the site.
- [ ] You know this is a **different credential path** than the lab: do **not** put `JIRA_API_TOKEN` anywhere in Cursor. The MCP connection has its own browser sign-in.

### Step 2 — Add the Atlassian MCP server to Cursor

**Easiest:** open **Customize** in Cursor's sidebar, select **MCPs**, search for the **Atlassian** server, and click **Add to Cursor**, then follow the prompts.

**Manual alternative** (works the same): create or edit the MCP config file —

- for just this project: `.cursor/mcp.json` inside the project folder, or
- for all your projects: `~/.cursor/mcp.json`

— and add:

```json
{
  "mcpServers": {
    "atlassian": {
      "url": "https://mcp.atlassian.com/v2/mcp"
    }
  }
}
```

Save, then restart Cursor so it picks up the manual edit.

> **Use the `v2` URL above.** Older tutorials show `https://mcp.atlassian.com/v1/sse`; Atlassian is retiring that legacy endpoint (unsupported after June 30, 2026). If a blog post disagrees with this runbook, the blog post is older than you think.

### Step 3 — Authorize with OAuth (no tokens!)

1. Cursor opens your browser to Atlassian's consent screen.
2. Sign in with your Atlassian account, **select your own site** (the one in `JIRA_SITE_URL`), and approve.
3. That's it. Notice what you did **not** do: create a token, paste a secret, or edit `.env`. The agent now acts as *you*, with your Jira permissions and nothing more.

### Step 4 — Verify the connection

1. Open **Customize → MCPs**: the `atlassian` server should show as enabled, with a toggle.
2. In a chat, check the tools list at the top of the chat panel — Jira tools should appear under the server's available tools.
3. If anything looks wrong, open the Output panel (`Ctrl+Shift+U` / `Cmd+Shift+U`) and select **MCP Logs** to see connection and auth messages.

### Step 5 — Test with your Balerica AI project

Ask Cursor's agent (replace `BAI` with your real project key):

```text
Using the Atlassian tools, list the five most recent work items in my
Jira project BAI with their keys, summaries, and statuses.
```

Cursor will show the Jira tool call and **ask for your approval** before running it — click the arrow next to the tool name to inspect the arguments first. Approve it and compare the result against your board.

Then try a read-plus-reasoning prompt on a real lab ticket:

```text
Read Jira issue BAI-3 and summarize the incident. Based on incident.py,
jira.py, and slack.py in this repo, explain how that ticket was created
and list three things I should verify on my board and in Slack.
```

**Write test (creates a real ticket — do it once):**

```text
Create a Task in project BAI titled
"[Balerica AI][INFO] cursor: MCP integration test - no real incident"
with a one-line description saying this was filed from Cursor via MCP.
```

Approve the tool call, then confirm the new ticket on your board (remember `jira_runbook.md` Step 5: check the Backlog if it is not on the board).

### Step 6 — Classroom rules for agent-driven Jira access

- **Keep approval prompts on for write actions.** Reading issues is low risk; creating, editing, or transitioning them changes the shared record. Review each write before approving — do not blanket-auto-approve Jira tools in this course.
- **Synthetic data only**, same as the whole lab: no real customer, financial, or personal data in tickets or prompts.
- One test ticket is plenty. Chewbacca counts.
- If you are on a managed Cursor team, admins may restrict which MCP servers are allowed; ask the instructor if the Atlassian server does not appear.

## 4. Troubleshooting

| Symptom | What to check |
|---|---|
| Server missing from the MCPs list after a manual edit | JSON syntax in `mcp.json` (validate it), file in the right place (`.cursor/mcp.json` in the project or `~/.cursor/mcp.json`), then restart Cursor |
| OAuth page loops or shows the wrong site | Your browser is signed in to a different Atlassian account; sign out, sign in with the lab account, and re-authorize, selecting the site from `JIRA_SITE_URL` |
| Tools connected but the agent never uses them | Check the server's toggle in **Customize → MCPs** and the tools list in the chat panel; say "using the Atlassian tools" explicitly in the prompt |
| Jira tool calls fail with permission errors | The MCP connection has exactly your Jira permissions — confirm you can do the same action in the browser on the same site |
| Connected to the wrong/old endpoint | Use `https://mcp.atlassian.com/v2/mcp`; the `v1/sse` endpoint is being retired |
| Agent can't find your project | Give the real project key in the prompt (the `BAI` in `BAI-1`); the same wrong-key mistake from `troubleshooting.md` section 1 applies here |
| Anything else | Output panel → **MCP Logs** first; it names the failing step |

## 5. How this relates to the rest of the lesson

| Concern | `jira.py` (the lab) | Cursor + Jira (this runbook) |
|---|---|---|
| Auth | API token in `.env` (plain token, 1–365 day expiry) | OAuth in the browser; no stored token |
| Who acts | Your script, headless on EC2 | Cursor's agent, interactively, with your approval per action |
| Purpose | Automated incident pipeline (agent → ticket → Slack) | Human-in-the-loop triage, investigation, and ticket hygiene |
| Graded | **Yes** | No — productivity layer |

Both talk to the same project, so the tickets your pipeline files are the tickets Cursor helps you investigate. That is the point.

> **CHEWBACCA'S FINAL REVIEW:** RRRRAAAWWWRRR! Translation: *The agent may read the ticket for you. Understanding it is still your job.*
