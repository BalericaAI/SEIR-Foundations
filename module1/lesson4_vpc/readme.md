# SEIR Foundations — Module 1, Lab 4
## Runbook: Download and Run `create_balerica_vpc.sh` from Your Own Computer

**Jira:** [M1-6](https://theowaf.atlassian.net/browse/M1-6)
**Region:** us-east-1 | **Level:** beginner
**Audience:** Students on Windows (PowerShell or Git Bash), macOS, or Ubuntu
**Goal:** Get the automation script onto *your* machine, understand every command it will run, and run it once against your lab AWS account to build the Balerica Bank network.

> This runbook is about running the **automation script**. If your instructor assigned the manual, command-by-command build, use `VPC_cli_runbook.md` instead — and never run **both** against the same account, or you will create duplicate networks. Background reading: `RFC_1918_Explanation.md` (why 10.20.x.x) and `balerica_vpc_explanation.md` (a line-by-line tour of the script).

### What the script builds

One VPC (`10.20.0.0/16`) in us-east-1, one Internet Gateway, three route tables, and nine subnets — and nothing else. No EC2, no database, no NAT. The network resources themselves have no hourly charge.

| Tier | us-east-1a | us-east-1b | us-east-1c | Internet route? |
|---|---|---|---|---|
| Public | 10.20.1.0/24 | 10.20.2.0/24 | 10.20.3.0/24 | Yes (via IGW) |
| Private 1 | 10.20.11.0/24 | 10.20.12.0/24 | 10.20.13.0/24 | No |
| Private 2 | 10.20.21.0/24 | 10.20.22.0/24 | 10.20.23.0/24 | No |

It also writes a file called `balerica-network.env` in the folder you run it from, recording every resource ID for later labs. Keep that file; do not commit it to GitHub.

---

## Part 1 — Every command this lab runs

Read this section first so nothing the script does is a surprise. There are two groups of commands: the ones **you type**, and the ones **the script runs for you**.

### 1a. Commands you type (the whole lab, end to end)

```bash
# Check your tools
aws --version                          # AWS CLI v2 must be installed
aws sts get-caller-identity            # proves your credentials work, shows WHICH account
bash --version                         # must be Bash 4 or newer (see Step 1)

# Get the script (full options in Step 2)
curl -fsSL -o create_balerica_vpc.sh \
  https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/create_balerica_vpc.sh

# Check it before running it
bash -n create_balerica_vpc.sh         # syntax check only; talks to nothing, creates nothing

# Run it (ONCE)
chmod +x create_balerica_vpc.sh        # optional — see Step 4
bash create_balerica_vpc.sh

# Verify afterwards
cat balerica-network.env
aws ec2 describe-subnets --filters "Name=vpc-id,Values=YOUR-VPC-ID" \
  --query 'length(Subnets)' --output text   # expect: 9
```

### 1b. Commands the script runs for you, in order

The script makes **52 AWS CLI calls** in total. Here is the exact sequence (the script fills in the IDs and loops over tiers and AZs for you):

**Safety checks first — stops before creating anything if these fail:**

```bash
aws sts get-caller-identity                                     # who and which account am I?
# stops if balerica-network.env already exists in this folder
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=balerica-vpc" \
  --query 'length(Vpcs)' --output text                          # stops unless this is 0
aws ec2 describe-availability-zones --zone-names us-east-1a ... # run for a, b and c (3 calls)
```

**Create the VPC (4 calls):**

```bash
aws ec2 create-vpc --cidr-block 10.20.0.0/16 \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=balerica-vpc}]" \
  --query Vpc.VpcId --output text
aws ec2 wait vpc-available --vpc-ids $VPC_ID
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support '{"Value":true}'
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames '{"Value":true}'
```

**Create and attach the Internet Gateway (2 calls):**

```bash
aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=balerica-igw}]" \
  --query InternetGateway.InternetGatewayId --output text
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
```

**For each tier — public, private1, private2 — create a route table (3 calls, plus 1 route):**

```bash
aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=balerica-TIER-rt}]" \
  --query RouteTable.RouteTableId --output text
# public tier only — this one route is what makes the public subnets "public":
aws ec2 create-route --route-table-id $PUBLIC_RT_ID \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
```

**For each of the nine subnets — tier × AZ a/b/c — four calls each (36 calls):**

```bash
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.20.N.0/24 \
  --availability-zone us-east-1X \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=balerica-TIER-X}]" \
  --query Subnet.SubnetId --output text
aws ec2 wait subnet-available --subnet-ids $SUBNET_ID
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_ID --map-public-ip-on-launch
                                           # public tier; private tiers get --no-map-public-ip-on-launch
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_ID \
  --query AssociationId --output text
```

**Final inventory (1 call):**

```bash
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[].{Name:Tags[?Key==`Name`]|[0].Value,CIDR:CidrBlock,AZ:AvailabilityZone,PublicIP:MapPublicIpOnLaunch}' \
  --output table
```

After every `create` call the script appends the new resource ID to `balerica-network.env`. If the script stops partway, that file tells you exactly how far it got.

---

## Part 2 — Download, configure, and run: step by step

### Step 0 — Know which shell you are in

The script is **Bash**. It cannot run inside PowerShell or CMD. Find your row:

| You have | Where you RUN the script | Notes |
|---|---|---|
| Windows + Git Bash | Git Bash window | Recommended on Windows. Installed with [Git for Windows](https://git-scm.com/download/win) |
| Windows + PowerShell only | You can **download** with PowerShell, but must run in Git Bash, WSL, or AWS CloudShell | PowerShell cannot execute `.sh` files |
| macOS | Terminal — but check your Bash version in Step 1 first | Apple ships an ancient Bash 3.2 that breaks this script |
| Ubuntu / other Linux | Any terminal | Works out of the box |
| Any of the above | [AWS CloudShell](https://console.aws.amazon.com/cloudshell) in us-east-1 | Easiest fallback: Bash 5, AWS CLI, and credentials are already there |

> **Windows tip:** you can tell which shell you are in by the prompt. PowerShell shows `PS C:\Users\you>`. Git Bash shows `you@MACHINE MINGW64 ~` with a `$`. If you see `PS`, you are in the wrong place to run Bash commands.

### Step 1 — Check your tools (creates nothing)

In the shell you will run the script from:

```bash
aws --version
aws sts get-caller-identity
bash --version
```

Expected:

- `aws --version` prints something like `aws-cli/2.x.x ...`. If you get `command not found` (or `aws : The term 'aws' is not recognized` in PowerShell), install [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). The Windows installer makes `aws` available in both PowerShell *and* Git Bash.
- `aws sts get-caller-identity` prints JSON with your `Account` and `Arn`:

  ```json
  {
      "UserId": "AIDAEXAMPLE...",
      "Account": "111122223333",
      "Arn": "arn:aws:iam::111122223333:user/student"
  }
  ```

  **Read the `Account` number.** It must be your lab/sandbox account, not a work or personal production account. If this command fails, run `aws configure` with your lab credentials first — nothing else in this runbook will work until it succeeds.
- `bash --version` must report **4.0 or newer**.
  - Ubuntu and Git Bash: you will see 5.x — fine.
  - **macOS: the default is 3.2** and the script will crash halfway through with `bad substitution` — *after* creating some resources. Do not skip this check. Fix with `brew install bash`, then run the script as `/opt/homebrew/bin/bash create_balerica_vpc.sh` (Apple Silicon) or `/usr/local/bin/bash create_balerica_vpc.sh` (Intel) — or just use CloudShell.

**Success check:** all three commands print versions/identity, the account number is your lab account, and Bash is ≥ 4.

### Step 2 — Download the script

Pick **one** option.

**Option A — clone the whole class repo (recommended if you haven't already):**

```bash
git clone https://github.com/BalericaAI/SEIR-Foundations.git
cd SEIR-Foundations/module1/lesson4_vpc
```

Works identically in Git Bash, macOS Terminal, and Ubuntu. Already cloned it? Don't clone again — `cd` into it and `git pull origin main`.

> **Windows cloning warning (Git Bash):** if Git is configured with `core.autocrlf=true`, cloning converts the script to Windows line endings (CRLF) and Bash will refuse to run it. Before cloning, run `git config --global core.autocrlf input` — or just use Option B, which never converts anything. Step 3 shows how to detect and repair the damage.

**Option B — download just the script.**

macOS, Ubuntu, and Git Bash (all the same command):

```bash
curl -fsSL -o create_balerica_vpc.sh \
  https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/create_balerica_vpc.sh
```

Windows PowerShell:

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/create_balerica_vpc.sh -OutFile create_balerica_vpc.sh
```

Note that it is the **raw.githubusercontent.com** address. If you download from the normal github.com page without clicking **Raw**, you get a web page full of HTML, not a script. (Browser alternative: open the file on GitHub, click **Raw**, then save the page as `create_balerica_vpc.sh`.)

**Success check:** `ls -l create_balerica_vpc.sh` (Bash) or `dir create_balerica_vpc.sh` (PowerShell) shows the file, roughly 3.5 KB. The first line of the file must be `#!/usr/bin/env bash` — if you see `<!DOCTYPE html>`, you saved the web page; delete it and use the raw URL.

### Step 3 — Syntax-check the script (catches Windows line-ending damage too)

In your **Bash** shell (Git Bash / macOS / Ubuntu / CloudShell), from the folder containing the file:

```bash
bash -n create_balerica_vpc.sh
```

- **No output at all = pass.** `bash -n` reads the script without executing anything — no AWS calls, nothing created.
- Output like this means the file has Windows (CRLF) line endings:

  ```text
  create_balerica_vpc.sh: line 15: syntax error near unexpected token `$'do\r''
  ```

  The `\r` is the giveaway. This happens when `core.autocrlf=true` converted the file during a clone, or an editor (Notepad, some Windows editors) re-saved it. Repair it:

  ```bash
  # Git Bash and Ubuntu:
  sed -i 's/\r$//' create_balerica_vpc.sh
  # macOS (note the extra ''):
  sed -i '' 's/\r$//' create_balerica_vpc.sh
  ```

  Then run `bash -n` again — it must be silent before you continue.

Optional extra credit if you have [shellcheck](https://www.shellcheck.net/) installed: `shellcheck create_balerica_vpc.sh` reports one info-level note (SC2016, about backticks inside single quotes) which is a false alarm — those backticks are AWS query syntax, not shell commands.

**Success check:** `bash -n create_balerica_vpc.sh` prints nothing.

### Step 4 — Make it executable (or don't — here's the difference)

Two equally valid ways to start a script:

```bash
bash create_balerica_vpc.sh     # way 1: hand the file to bash — no permissions needed
./create_balerica_vpc.sh        # way 2: run the file itself — needs the executable bit
```

If you prefer way 2 on macOS or Ubuntu, add the executable bit first:

```bash
chmod +x create_balerica_vpc.sh
```

Platform notes:

- **Git Bash:** `chmod +x` quietly does nothing useful on Windows drives, but `./create_balerica_vpc.sh` works anyway because Git Bash sees the `#!/usr/bin/env bash` first line. Either way is fine.
- **PowerShell:** there is no `chmod`, and neither way works — `.\create_balerica_vpc.sh` will just try to open the file in an editor. This is your reminder to switch to Git Bash, WSL, or CloudShell.
- **macOS (way 2 caveat):** `./create_balerica_vpc.sh` uses whichever `bash` is first in your PATH. If you installed Bash 5 with Homebrew, confirm with `bash --version` that the new one wins; otherwise call it explicitly as shown in Step 1.

This runbook uses `bash create_balerica_vpc.sh` everywhere since it works on every platform.

### Step 5 — Configure it

There is nothing to edit inside the file. The script reads three optional environment variables and has class-correct defaults for all of them:

| Variable | Default | Meaning |
|---|---|---|
| `AWS_REGION` | `us-east-1` | Region to build in — keep it |
| `PROJECT` | `balerica` | Prefix for every Name tag and the state file |
| `NETWORK_PREFIX` | `10.20` | First two octets of every address |

**For this class, change nothing** — the defaults ARE the configuration. You would only override them (e.g. `NETWORK_PREFIX=10.30 PROJECT=balerica-dev`) with instructor approval, for a second non-overlapping deployment.

If you do override, the syntax is Bash's "variables before the command on the same line" form:

```bash
AWS_REGION=us-east-1 PROJECT=balerica NETWORK_PREFIX=10.20 bash create_balerica_vpc.sh
```

(For comparison, PowerShell would use `$env:AWS_REGION="us-east-1"` — but remember, you are not running this from PowerShell.)

The script also sets `AWS_DEFAULT_REGION` and turns the CLI pager off by itself, so you don't need any `export` lines first.

### Step 6 — Run it (once)

From the folder containing the script, in your Bash shell, with Step 1 all green:

```bash
bash create_balerica_vpc.sh
```

It takes roughly one to two minutes. Expected output (your IDs will differ — anything shaped `vpc-0...`, `subnet-0...` is right):

```text
{
    "UserId": "AIDAEXAMPLE...",
    "Account": "111122223333",
    "Arn": "arn:aws:iam::111122223333:user/student"
}
public-a: 10.20.1.0/24 (subnet-0a1b2c3d4e5f67890)
public-b: 10.20.2.0/24 (subnet-0b2c3d4e5f6789012)
public-c: 10.20.3.0/24 (subnet-0c3d4e5f678901234)
private1-a: 10.20.11.0/24 (subnet-0d4e5f6789012345a)
private1-b: 10.20.12.0/24 (subnet-0e5f6789012345ab6)
private1-c: 10.20.13.0/24 (subnet-0f6789012345abc78)
private2-a: 10.20.21.0/24 (subnet-0a789012345abcd89)
private2-b: 10.20.22.0/24 (subnet-0b89012345abcde90)
private2-c: 10.20.23.0/24 (subnet-0c9012345abcdef01)
--------------------------------------------------------------------------
|                             DescribeSubnets                            |
+------------+---------------+----------------------+-------------------+
|     AZ     |     CIDR      |        Name          |     PublicIP      |
+------------+---------------+----------------------+-------------------+
|  us-east-1a|  10.20.1.0/24 |  balerica-public-a   |  True             |
   ... nine rows total; the three public rows say True, the six private rows say False ...
+------------+---------------+----------------------+-------------------+
Created VPC vpc-0abc1234def567890. Resource IDs saved in balerica-network.env.
```

**Run it once.** The script is deliberately *not* rerunnable: on a second run it stops immediately with `State file already exists: balerica-network.env`, and if it finds a VPC already named `balerica-vpc` it stops with `Named VPC already exists.` Those guards protect you from building a duplicate network — never delete the state file just to get past them.

**If it stops partway** (expired credentials, missing permission), it prints `Deployment stopped at line N...`. Resources created before that line are real and remain in AWS. Do **not** immediately rerun. Open `balerica-network.env` to see what exists, fix the cause (rerun `aws sts get-caller-identity` first — expired lab credentials are the usual culprit), and ask your instructor about cleanup before any second attempt.

**Success check:** the last line names a VPC and the state file.

### Step 7 — Verify what you built

```bash
cat balerica-network.env
source ./balerica-network.env
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'length(Subnets)' --output text
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID" --output table
```

Expected: the state file lists ~25 `KEY=value` lines (region, CIDR, VPC, IGW, three route tables, nine subnets, nine associations); the subnet count prints `9`; the IGW table shows one gateway attached to your VPC. Also look at **VPC → Your VPCs → balerica-vpc → Resource map** in the AWS console — one picture of everything you just made.

**Success check:** count is `9` and the console resource map matches the table at the top of this runbook.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `aws: command not found` / `'aws' is not recognized` | AWS CLI not installed, or terminal not reopened after install. Install CLI v2, open a NEW terminal window |
| `Unable to locate credentials` or `ExpiredToken` | Run `aws configure` with your lab credentials, or refresh your session; retest with `aws sts get-caller-identity` |
| ``syntax error near unexpected token `$'do\r''`` | Windows CRLF line endings — Step 3 shows the one-line `sed` fix |
| `set: pipefail: invalid option name` as the very first output | Same CRLF problem (it fails here before touching AWS — nothing was created) |
| `bad substitution` midway through (macOS) | You ran Bash 3.2. Resources up to that point WERE created — check `balerica-network.env`, talk to your instructor, then use Bash 5 or CloudShell |
| `.\create_balerica_vpc.sh` opens an editor or errors in PowerShell | PowerShell cannot run Bash scripts — switch to Git Bash, WSL, or CloudShell (Step 0) |
| First line of the file is `<!DOCTYPE html>` | You saved the GitHub web page, not the script — re-download from the **raw** URL (Step 2) |
| `State file already exists` | The script already ran in this folder. That is a safety stop, not an error — inspect before doing anything |
| `Named VPC already exists` | A `balerica-vpc` is already in the account (maybe from the manual runbook). One network per account — inspect it, don't duplicate |
| `UnauthorizedOperation` | Your lab IAM role lacks an EC2 networking permission — show your instructor the exact message; do not grant yourself admin |
| `AZ us-east-1X unavailable` | Wrong region or restricted account — confirm `AWS_REGION` is us-east-1 and retry `aws ec2 describe-availability-zones` |

## Completion checklist

- [ ] `aws sts get-caller-identity` shows my **lab** account.
- [ ] Bash version ≥ 4 confirmed in the shell I actually used (macOS students: this means you).
- [ ] `bash -n create_balerica_vpc.sh` was silent before I ran the script.
- [ ] The script ran once and ended with `Created VPC vpc-... Resource IDs saved in balerica-network.env.`
- [ ] Subnet count query returns `9`; console resource map matches the design table.
- [ ] `balerica-network.env` is kept safe locally and is **not** committed to GitHub.
- [ ] I did not delete the default VPC, the state file, or anything I cannot explain.

Keep the VPC and the state file: Lab 5 (Aurora) uses the Private 2 subnet IDs, and the ASG lab uses Private 1. This runbook intentionally includes no deletion commands — cleanup is instructor-led.

> **CHEWBACCA SAYS:** RRRRAAAWWWRRR! "It printed green text" is not evidence. The state file, the subnet count of nine, and the console resource map are evidence.

## Companion documents

- `VPC_cli_runbook.md` — build the same network manually, one CLI command at a time (the gate-by-gate version of Part 1b).
- `balerica_vpc_explanation.md` — what every line of the script does and why.
- `RFC_1918_Explanation.md` — private addressing and the subnet math behind 10.20.

*Instructor note: the Bash syntax check, shellcheck, CRLF failure modes, rerun guards, and full command sequence in this runbook were verified by executing the script against a mocked AWS CLI (52 calls, exit 0, state file as described). Live AWS execution was not performed in this authoring session; AWS-dependent outputs are shaped from the script's commands and documentation.*
