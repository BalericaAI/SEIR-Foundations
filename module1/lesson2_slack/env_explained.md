# What Is `.env`? (A Beginner's Guide to the Most Important File You Can't See)

You created a file called `.env` in this lab, and it probably raised questions:
Why the weird name? Why does `ls` pretend it doesn't exist? Why does everyone
keep yelling about never committing it? This page answers all of that.

## 1. What `.env` is for

`.env` is a plain text file that holds **configuration and secrets** for a
program — things like passwords, API keys, and your Slack webhook URL. Each
line is one setting in `NAME=value` form:

```dotenv
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../secret-token
SLACK_ALERTS_ENABLED=true
SLACK_ALERT_SEVERITY=ERROR
```

When `slack.py` starts, the line `load_dotenv()` reads this file and makes
every setting available to Python through `os.getenv("SLACK_WEBHOOK_URL")`.

## 2. Why not just put the webhook inside `slack.py`?

Because **code gets shared and secrets must not be**. Think about what happens
to each file:

| | `slack.py` (code) | `.env` (secrets) |
|---|---|---|
| Pushed to GitHub? | Yes — code is meant to be shared | **Never** |
| Same for every student? | Yes, identical | No — yours is unique |
| If a stranger reads it? | No harm done | They can post to your Slack |

This separation is called **"configuration lives outside the code."** It is
one of the most universal rules in software engineering. The same `slack.py`
runs on every student's EC2 instance; only the `.env` next to it is different.
That is exactly how real companies deploy one codebase to dev, staging, and
production with different passwords in each place.

## 3. Why the dot in front of the name?

On Linux (and macOS), **any file whose name starts with a dot is "hidden."**
This is an old Unix convention: dot-files are for configuration that programs
need but humans rarely browse, so the system keeps them out of the way.

You already know other dot-things without realizing it: `.gitignore`,
`.ssh` (where your EC2 key lives), `.bashrc`, and the `.venv` folder.

**Important:** hidden is not the same as secure. The dot only hides the file
from casual listing — anyone with access to the machine can still open it.
That's why we also protect it with permissions (see section 5).

## 4. Why `ls` doesn't show it (and how to see it anyway)

Plain `ls` skips hidden files on purpose. Add the `-a` flag ("all") to see them:

```bash
cd /opt/balerica-bank
ls          # no .env visible — this is normal!
ls -a       # there it is, along with . and ..
ls -la      # long form: shows permissions, owner, and size too
```

Expected output of `ls -la` (one line of it):

```text
-rw------- 1 ec2-user ec2-user  187 Nov  3 19:12 .env
```

If you ever think "my `.env` disappeared!", it didn't. You just ran plain
`ls`. This catches every beginner at least once.

## 5. The three protections around your `.env`

1. **`chmod 600 .env`** — sets permissions so only your user can read or
   write the file. That's the `-rw-------` you saw in `ls -la`. Other users
   on the machine see "Permission denied."
2. **`.gitignore`** — the line `.env` in `.gitignore` tells git to never
   track the file, so you can't accidentally push your webhook to GitHub.
3. **Your own discipline** — never paste `.env` contents into chats,
   screenshots, AI prompts, or submissions. Ask "is this variable set?"
   instead of printing its value.

## 6. Common beginner confusions, cleared up

- **`.env` is not the virtual environment.** The folder `venv` (or `.venv`)
  holds installed Python packages. The file `.env` holds settings. Similar
  names, totally different jobs.
- **`cat .env` works even though `ls` hides it.** Hidden only means "not
  listed by default," not "inaccessible." (But avoid printing it when others
  can see your screen.)
- **Editing `.env` requires being in the right folder.** `slack.py` looks for
  `.env` in the directory you run it from. If the test says the webhook is
  missing but you're sure you created `.env`, run `ls -a` and check you're in
  `/opt/balerica-bank`.
- **Changes to `.env` take effect the next time you run the script.** No
  reboot or reinstall needed.

## 7. Check your understanding

Can you answer these without looking up? (Answers are all on this page.)

1. Why does the webhook go in `.env` instead of `slack.py`?
2. What does the leading dot do, and what does it NOT do?
3. What command shows hidden files?
4. What does `chmod 600 .env` protect against, and what does `.gitignore`
   protect against?

> **Chewbacca's note:** RRRRAAAWWWRRR. The webhook in `.env`, the dot keeps it
> humble, `ls -a` reveals it, and GitHub never sees it. Learn this and no bites.
