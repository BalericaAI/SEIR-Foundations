# SEIR Foundations — Module 1, Lab 4
## Runbook: Download and Run `create_balerica_vpc.sh` from Your Own Computer

**Jira:** [M1-6](https://theowaf.atlassian.net/browse/M1-6)
**Region:** us-east-1 | **Level:** beginner
**Audience:** Students on Windows (PowerShell or Git Bash), macOS, or Ubuntu
**Goal:** Get the automation script onto *your* machine, understand every command it will run, and run it once against your lab AWS account to build the Balerica Bank network.

> This runbook is about running the **automation script**. If your instructor assigned the manual, command-by-command build, use `VPC_cli_runbook.md` instead — and never run **both** against the same account, or you will create duplicate networks. Background reading: `RFC_1918_Explanation.md` (why 10.20.x.x) and `balerica_vpc_explanation.md` (a line-by-line tour of the script).

> ## ⚠️ YOU MUST TEAR THIS LAB DOWN WHEN THE COURSE IS DONE ⚠️
>
> **AWS keeps billing your account for whatever you leave behind. Forgotten labs are the #1 cause of surprise student bills.** This lab comes with a teardown script, `delete_balerica_vpc.sh`, and running it is **part of the lab, not optional**. Keep the VPC only while later labs still need it (Lab 5 Aurora, the ASG lab) — then, when your instructor announces the module is finished, run **Step 8** of this runbook the same day. Put a reminder in your calendar **right now**, before you build anything. You will forget otherwise. Everyone forgets otherwise.

### What the script builds

One VPC (`10.20.0.0/16`) in us-east-1, one Internet Gateway, three route tables, and nine subnets — and nothing else. No EC2, no database, no NAT. The empty network itself has no hourly charge — but later labs deploy billable resources into it, which is exactly why the teardown in Step 8 is mandatory once the module ends: deleting the network proves nothing billable is left hiding inside it.

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

# LATER — when the instructor says the module is done — tear it all down (Step 8)
curl -fsSL -o delete_balerica_vpc.sh \
  https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/delete_balerica_vpc.sh
bash -n delete_balerica_vpc.sh
bash delete_balerica_vpc.sh            # asks you to type DELETE vpc-... to confirm
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

### 1c. Commands the teardown script runs for you, in order

`delete_balerica_vpc.sh` makes **38 AWS CLI calls**: 13 read-only safety checks first, and the 25 deletion calls only after you type the confirmation. It reads its resource IDs from `balerica-network.env` (it parses the file as plain text — it never executes it).

**Read-only verification — nothing is deleted yet (13 calls):**

```bash
aws sts get-caller-identity --query Account --output text        # must match the VPC's owner
aws ec2 describe-vpcs --vpc-ids $VPC_ID \
  --query 'Vpcs[0].[CidrBlock,IsDefault,Tags[?Key==`Name`]|[0].Value,OwnerId]' --output text
                                 # refuses the default VPC, a wrong CIDR, or someone else's VPC
# Seven "is the VPC empty?" checks — each must count 0, or the script stops:
aws ec2 describe-instances ...            # no EC2 instances (running OR stopped)
aws ec2 describe-network-interfaces ...   # no network interfaces left behind
aws ec2 describe-nat-gateways ...         # no NAT gateways
aws ec2 describe-vpc-endpoints ...        # no VPC endpoints
aws ec2 describe-security-groups ...      # no custom security groups
aws ec2 describe-network-acls ...         # no custom network ACLs
aws rds describe-db-subnet-groups ...     # no database subnet groups (Lab 5!)
# Inventory — every live resource must match an ID recorded in the state file:
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[].SubnetId'
aws ec2 describe-route-tables ...         # run twice: custom route tables, then associations
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID" ...
```

**Then it prints the full inventory and waits for you to type `DELETE vpc-...` — only after that (25 calls):**

```bash
aws ec2 disassociate-route-table --association-id $ASSOC_ID   # × 9
aws ec2 delete-subnet --subnet-id $SUBNET_ID                  # × 9
aws ec2 delete-route-table --route-table-id $RT_ID            # × 3
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
aws ec2 delete-vpc --vpc-id $VPC_ID
aws ec2 describe-vpcs --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'length(Vpcs)' --output text                        # confirms 0 — really gone
```

Finally it renames the state file to `balerica-network.env.deleted.TIMESTAMP` so the lab cannot be torn down twice by accident.

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

### Step 5 — Configure it (and how to open it in an editor)

The script reads three optional environment variables and has class-correct defaults for all of them:

| Variable | Default | Meaning |
|---|---|---|
| `AWS_REGION` | `us-east-1` | Region to build in — keep it |
| `PROJECT` | `balerica` | Prefix for every Name tag and the state file |
| `NETWORK_PREFIX` | `10.20` | First two octets of every address |

**For this class, change nothing** — the defaults ARE the configuration. You would only change them (e.g. `NETWORK_PREFIX=10.30 PROJECT=balerica-dev`) with instructor approval, for a second non-overlapping deployment. There are two ways to change them:

**Way 1 — override at run time, no editing (preferred):** Bash's "variables before the command on the same line" form:

```bash
AWS_REGION=us-east-1 PROJECT=balerica NETWORK_PREFIX=10.20 bash create_balerica_vpc.sh
```

(For comparison, PowerShell would use `$env:AWS_REGION="us-east-1"` — but remember, you are not running this from PowerShell.)

The script also sets `AWS_DEFAULT_REGION` and turns the CLI pager off by itself, so you don't need any `export` lines first.

**Way 2 — edit the defaults inside the script.** When your instructor asks you to change the subnet values in the file itself, use **Visual Studio Code** — nano works too, but you are not stuck with it.

#### Opening the script in VS Code from your terminal

Once the `code` command works, it is the same on every platform — run it in the folder where you downloaded the script, right after the `curl`:

```bash
code create_balerica_vpc.sh            # opens the create script in VS Code
code delete_balerica_vpc.sh            # the teardown script opens the same way
```

(The delete script never needs editing — it reads everything from the state file — but you are welcome to open and read it.)

Getting `code` onto your PATH differs per platform:

- **macOS:** `code` is NOT available by default, even with VS Code installed. One-time setup: open VS Code, press **Cmd+Shift+P** to open the Command Palette, type `shell command`, and select **Shell Command: Install 'code' command in PATH**. Then open a **new** terminal window and `code create_balerica_vpc.sh` works.
- **Windows (Git Bash AND PowerShell):** the VS Code installer adds `code` to your PATH by default, so it usually just works in both shells. If you get `command not found` / `'code' is not recognized`, re-run the installer and tick the **"Add to PATH"** checkbox (it's on the Select Additional Tasks page), then open a new terminal.
- **Ubuntu:** install VS Code from the [.deb package](https://code.visualstudio.com/download) or with `sudo snap install --classic code` — both put `code` on your PATH automatically.
- **`code` still not found?** No problem: open VS Code normally (Start menu / Applications / Launchpad), then **File → Open File…** and navigate to `create_balerica_vpc.sh` in the folder where you downloaded it. Same file, same editing.

> **VS Code line-ending check (Windows students especially):** after the file is open, look at the **bottom-right of the VS Code status bar**. It must say **LF**. If it says **CRLF**, click it, choose **LF**, and save — otherwise you are re-creating the Step 3 line-ending problem with every save.

#### The quick alternative: nano

nano is already there in Git Bash, macOS, Ubuntu, and CloudShell — handy on a machine without VS Code (like CloudShell):

```bash
nano create_balerica_vpc.sh
```

Edit, then **Ctrl+O**, **Enter** to save and **Ctrl+X** to exit. Do **not** use Windows Notepad — it loves to re-save the file with CRLF line endings and break it.

#### What to actually change once the file is open

The subnet values live in these lines (only touch them with instructor approval, and change nothing else):

| Line | What you see | What it controls |
|---|---|---|
| 5 | `PROJECT="${PROJECT:-balerica}"` | The name prefix (`balerica-vpc`, `balerica-public-a`, …) and the state-file name. Change only the `balerica` after the `:-` |
| 6 | `NETWORK_PREFIX="${NETWORK_PREFIX:-10.20}"` | The first two octets of the VPC and of all nine subnets. Change only the `10.20` after the `:-` — it must stay a valid, approved, non-overlapping private /16 prefix |
| 7 | `VPC_CIDR="$NETWORK_PREFIX.0.0/16"` | Derived from line 6 automatically — do **not** edit |
| 33 | `case "$tier" in public) base=0;; private1) base=10;; private2) base=20;; esac` | The tens digit of the third octet per tier (public → .1-.3, private1 → .11-.13, private2 → .21-.23) |
| 41 | `n=$((n+1)); cidr="$NETWORK_PREFIX.$((base+n)).0/24"` | Where each subnet's /24 is assembled from the pieces above — read it, understand it, do **not** edit it |

The `:-` syntax means "use the environment variable if set, otherwise this default" — which is why Way 1 works without editing anything.

After **any** edit, before running: save, then repeat Step 3 (`bash -n create_balerica_vpc.sh` must stay silent).

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

### Step 8 — TEARDOWN (mandatory — this is how you stop being billed)

**Do not skip this step. Do not "do it later."** When your instructor announces that the module is finished (after Lab 5 and the ASG lab are done with this VPC), tear it down the same day. An AWS account is not a junk drawer: whatever you leave in it, AWS keeps billing you for — and later labs put billable resources (EC2, databases, public IPv4 addresses) *inside this VPC*. Deleting the network forces you to notice anything still alive in it, because the teardown script **refuses to run while anything else is still in the VPC**.

The teardown script needs the same environment as the create script: a **Bash 4+** shell (Git Bash, Ubuntu, macOS with Homebrew Bash, WSL, or CloudShell — PowerShell still cannot run it, see Step 0) and it must run **in the same folder as your `balerica-network.env` state file**, because that file tells it exactly which resources are yours to delete.

**8.1 — Download it** (same pattern as Step 2; skip if you cloned the repo — it is already next to the create script):

macOS, Ubuntu, and Git Bash:

```bash
curl -fsSL -o delete_balerica_vpc.sh \
  https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/delete_balerica_vpc.sh
```

Windows PowerShell (download only — run it from Git Bash/WSL/CloudShell):

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/BalericaAI/SEIR-Foundations/main/module1/lesson4_vpc/delete_balerica_vpc.sh -OutFile delete_balerica_vpc.sh
```

Using CloudShell? Upload your `balerica-network.env` there first (Actions → Upload file), or run the teardown from whatever machine still has it.

**8.2 — Check it before running it** (same drill as Step 3 — catches CRLF damage too):

```bash
bash -n delete_balerica_vpc.sh     # silence = pass
```

**8.3 — Run it.** From the folder containing both the script and `balerica-network.env`:

```bash
bash delete_balerica_vpc.sh
```

macOS Homebrew-Bash users: call it explicitly, as in Step 1 — e.g. `/opt/homebrew/bin/bash delete_balerica_vpc.sh`. (With Apple's Bash 3.2 it fails immediately at `declare -A`, before touching AWS.)

The script verifies everything first, shows you exactly what it found, and then **stops and asks you to type a confirmation**. Expected output (your IDs will differ):

```text
Account: 111122223333
Region: us-east-1
VPC: vpc-0abc1234def567890 (balerica-vpc, 10.20.0.0/16)
Subnets: subnet-0a1b... subnet-0b2c... (nine IDs)
Route tables: rtb-0a1b... rtb-0b2c... rtb-0c3d... (three IDs)
IGW: igw-0abc1234def567890
Type DELETE vpc-0abc1234def567890 to proceed:
```

Read the inventory. If it matches what you built, type `DELETE ` followed by **your** VPC ID, exactly as the prompt shows, and press Enter. Typing anything else cancels safely:

```text
STOP: Cancelled; no resources deleted
```

After a correct confirmation, the deletions run (about 30–60 seconds) and it ends with:

```text
VPC deleted and verified. State archived: balerica-network.env.deleted.20261124T212247Z
```

The state file is renamed, not deleted — that archive is your proof of cleanup (submit it with your homework notes), and it stops an accidental second run.

**8.4 — Verify with your own eyes.** The script already confirmed the VPC is gone, but check the console too: **VPC → Your VPCs** must no longer show `balerica-vpc`. While you are there, glance at **EC2 → Instances** and **Billing** — make sure nothing else is quietly running.

**What if it refuses?** That is the script protecting you, not a bug:

- `Dependencies found: ...` — something is still alive inside the VPC (an EC2 instance — even a *stopped* one — a database subnet group from Lab 5, a NAT gateway, a custom security group…). The message names the check that failed. Delete that resource first (instructor can help), then rerun.
- `Unrecorded subnet/route table/association ...` — something in the VPC was created outside the lab script, so the script won't touch the VPC. Investigate with your instructor; never delete what you cannot explain.
- `VPC identity mismatch or default VPC. Chewbacca says NO.` — the state file points at a VPC that isn't the lab's (wrong account, wrong region, renamed VPC, or the default VPC). Stop and check `aws sts get-caller-identity` first.

**Success check:** the `VPC deleted and verified` line appeared, the archived `.deleted.` file exists, and the console shows no `balerica-vpc`.

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
| `STOP: Missing balerica-network.env` (teardown) | You are not in the folder where you ran the create script — `cd` there, or pass the file's path: `bash delete_balerica_vpc.sh /path/to/balerica-network.env` |
| `STOP: Dependencies found: ...` (teardown) | The VPC is not empty — a (possibly stopped) EC2 instance, DB subnet group, NAT gateway, endpoint, custom SG/NACL is still inside. Remove it first, then rerun (Step 8) |
| `STOP: Unrecorded subnet ...` (teardown) | The VPC contains resources the lab didn't create — investigate with your instructor before deleting anything |
| `STOP: Cancelled; no resources deleted` | You didn't type `DELETE vpc-...` exactly as prompted. Nothing happened — rerun when ready |
| `declare: -A: invalid option` (teardown, macOS) | Bash 3.2 again — nothing was touched; use Homebrew Bash 5 or CloudShell (Step 1) |
| Teardown ran, but the state file is "gone" | It was archived, not lost — look for `balerica-network.env.deleted.TIMESTAMP` in the same folder |

## Completion checklist

- [ ] `aws sts get-caller-identity` shows my **lab** account.
- [ ] Bash version ≥ 4 confirmed in the shell I actually used (macOS students: this means you).
- [ ] `bash -n create_balerica_vpc.sh` was silent before I ran the script.
- [ ] The script ran once and ended with `Created VPC vpc-... Resource IDs saved in balerica-network.env.`
- [ ] Subnet count query returns `9`; console resource map matches the design table.
- [ ] `balerica-network.env` is kept safe locally and is **not** committed to GitHub.
- [ ] I did not delete the default VPC, the state file, or anything I cannot explain.
- [ ] **I have a dated reminder to run the teardown (Step 8) the day the instructor closes the module.**

And when the module ends — the part of the lab people fail by forgetting:

- [ ] `bash delete_balerica_vpc.sh` ran, I typed `DELETE vpc-...`, and it ended with `VPC deleted and verified`.
- [ ] The archived `balerica-network.env.deleted.TIMESTAMP` file exists (keep it as proof of cleanup).
- [ ] The AWS console shows **no** `balerica-vpc`, and Billing shows nothing unexpected still running.

Keep the VPC and the state file *while the course still needs them*: Lab 5 (Aurora) uses the Private 2 subnet IDs, and the ASG lab uses Private 1. The moment those labs are done, **teardown is mandatory — see Step 8**. The lab is not complete, and your bill is not safe, until the VPC is gone.

> **CHEWBACCA SAYS:** RRRRAAAWWWRRR! "It printed green text" is not evidence. The state file, the subnet count of nine, and the console resource map are evidence. And a lab you never tore down is not finished — it is a subscription you forgot to cancel.

## Companion documents

- `VPC_cli_runbook.md` — build the same network manually, one CLI command at a time (the gate-by-gate version of Part 1b).
- `balerica_vpc_explanation.md` — what every line of the script does and why.
- `RFC_1918_Explanation.md` — private addressing and the subnet math behind 10.20.

*Instructor note: the Bash syntax checks, shellcheck, CRLF failure modes, rerun/confirmation guards, and full command sequences in this runbook were verified by executing both scripts against a mocked AWS CLI — create: 52 calls, exit 0, state file as described; teardown: 38 calls, exit 0, consuming that same state file and archiving it, with the cancel path making zero destructive calls. Live AWS execution was not performed in this authoring session; AWS-dependent outputs are shaped from the scripts' commands and documentation.*
