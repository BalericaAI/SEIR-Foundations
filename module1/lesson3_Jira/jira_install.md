# SEIR Foundations — Jira Cloud Free Installation

**Lab:** Balerica AI — Jira Incident Management  
**Goal:** Create your own free Jira Cloud site and a project that Balerica AI can use later to track incidents.  
**Prerequisites:** An email address, a web browser, and a place to save *non-secret* configuration details.

> **YO STUDENT!** Create your **own** Jira site. Do not use the instructor's site or your neighbor's project. Chewbacca is monitoring your reading comprehension. 🐶

## 1. Register for Jira Cloud Free

1. Visit [Atlassian Jira](https://www.atlassian.com/software/jira/free) and select **Get it free** (or the current equivalent).
2. Create an Atlassian account or sign in with an available identity provider.
3. Verify your email address if prompted.
4. Choose **Jira** on the **Free** plan. If onboarding offers a time-limited premium trial, check the plan selection carefully; this course does not require paid features.
5. Follow the prompts to create your Jira Cloud site. Choose a unique site name such as `studentname-seir`; your URL will typically look like `https://studentname-seir.atlassian.net`.
6. Finish the onboarding prompts. The labels and screen order may vary.

**Success check:** You can sign in and open your own `*.atlassian.net` Jira site.

## 2. Create the Balerica AI project

1. In Jira, choose **Projects** or **Spaces**, then **Create project** / **Create space** (wording varies).
2. Choose a simple **Kanban** template if available.
3. Name the project **Balerica AI Incident Management**.
4. Set the project key to **BAI** if Jira permits it. If that key is unavailable or assigned automatically, record the actual key.
5. Use a straightforward team-managed project when offered; avoid complicated workflows and permission customization for this introductory lab.
6. Open the new project and confirm you can see its work-item list or board.

**Success check:** Your project exists and you can create a work item.

## 3. Create a manual test incident

1. Click **Create** or **Create work item**.
2. Select your Balerica AI project.
3. Select **Task** or **Bug** (whichever is available).
4. Enter:

   - **Summary:** `TEST — EC2 application error`
   - **Description:** `Manual SEIR Foundations verification. Later, Balerica AI will create incidents automatically from application and infrastructure errors.`
   - **Priority:** Default value is fine.

5. Save the work item and note its issue key, such as `BAI-1`.
6. Open it to verify that its summary and description are visible.

**Success check:** A test work item appears in the project and has an issue key.

## 4. Preserve your configuration for jira.py

Save the following in a **private note** so you can configure the later Python integration. These values are examples; use your own.

```text
JIRA_SITE_URL=https://studentname-seir.atlassian.net
JIRA_EMAIL=student@example.com
JIRA_PROJECT_KEY=BAI
JIRA_TEST_ISSUE_KEY=BAI-1
JIRA_DEFAULT_ISSUE_TYPE=Task
```

**Important:** `JIRA_SITE_URL` is your Jira site address, **not** an API token. Do not assume your project key is `BAI` unless you verified it.

### API token — later lab

For the future `jira.py` integration, you'll generate an Atlassian API token from your Atlassian account's security settings and store it securely as `JIRA_API_TOKEN` in an EC2 `.env` file. **Do not generate or submit a token for this account-creation exercise unless the instructor explicitly requests it.** Never paste tokens into a README, screenshots, GitHub, Slack, or AI chat prompts.

When that step arrives, use Atlassian's current instructions: [Manage API tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/). API-token scopes and authentication requirements may vary; follow the later `jira.py` lab instructions.

## 5. Verify completion

- [ ] I created my own Atlassian account.
- [ ] I can open my Jira Cloud site.
- [ ] I selected or confirmed the Free plan.
- [ ] I created the Balerica AI Incident Management project.
- [ ] I know my **actual** project key.
- [ ] I created and opened a manual test incident.
- [ ] I saved the site URL, email, project key, and test issue key privately.
- [ ] I have **not** shared any passwords or API tokens.

## 6. Troubleshooting and Claude Code guidance

**Can't find “Projects”?** Look for **Spaces** or the **Create** menu; Atlassian's interface changes over time.

**My site name is unavailable.** Choose a different unique name and save the exact resulting URL.

**I don't see “Bug.”** Use **Task** and record the work-item type that exists in your project.

**I'm being asked for payment.** Return to Jira's Free-plan page and confirm the edition before continuing. Do not enter payment details for this lab.

**Want to ask Claude Code?** Give it this file and ask: *“Read jira_install.md. Walk me through the next step, explain what information I need to preserve for jira.py, and do not ask me to disclose credentials.”* Claude Code cannot necessarily see your browser or Atlassian account, so verify the actual UI yourself.

## 7. What comes next

In a later lab, `jira.py` will use the Jira Cloud REST API to create work items for errors detected by Balerica AI. `slack.py` will notify you; `jira.py` will track the investigation. **No Jira software needs to be installed on your EC2 for this account setup.**

**Official references:** [Jira Free](https://www.atlassian.com/software/jira/free) · [Jira Cloud documentation](https://support.atlassian.com/jira-software-cloud/) · [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
