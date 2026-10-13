# SEIR Foundations — Module 1, Lab 0: Your First EC2 Dashboard

**Instructor-led lab | Amazon EC2 | Amazon Linux 2023 | Estimated time: 20–35 minutes**

Welcome to SEIR Foundations! This introductory lab complements Stephane Maarek's Udemy AWS training. Today you will launch an EC2 instance, see a live Linux system dashboard, connect by SSH, share your success with classmates, and then **terminate the instance**. The goal is a quick, visible first win.

> **CHEWBACCA SAYS:** RRRRAAAWWWRRR! Read the instructions *before* asking whether AWS charges $1,000 per hour for a launch template.

## Learning outcomes

By the end of this lab you should be able to:

1. Identify your AWS Region and an EC2 instance type eligible for **your account's** Free Tier or credits.
2. Create and save an EC2 **launch template** containing a Bash User Data script.
3. Launch an EC2 instance from that template and connect to it using EC2 Instance Connect or SSH.
4. Identify CPU, memory, disk, uptime, and instance metadata on the login dashboard.
5. Share a screenshot of the dashboard in Zoom and terminate the instance without deleting the launch template.

## Before class: credits and costs

Every student should have AWS promotional credits or an applicable Free Tier allowance available for this class. **Check your own AWS Billing and Cost Management console** to confirm your credit balance, expiration, and Free Tier eligibility. AWS account creation dates and offers vary; a particular instance is **not automatically free** just because the console labels it Free Tier eligible.

For today's short lab, do not let cost anxiety stop you from learning: choose a Free Tier-eligible instance for **your account and Region**, keep the lab brief, and **terminate it at the end**. Be aware that charges can still arise from public IPv4 addresses, EBS storage, extra resources, or usage outside your allowance. The launch template itself has no EC2 instance-hour charge. You can keep it for Module 1.

**Important:** Terminating an instance stops its compute charges, but independently retained EBS volumes, snapshots, Elastic IPs, and other resources may continue to incur charges. Check the cleanup section.

## Step 1 — Get the Lab 0 startup script

If you have already cloned the class repository, go to the Lab 0 directory:

```bash
git clone https://github.com/BalericaAI/SEIR-Foundations.git
cd SEIR-Foundations/module1/lab0_basics
```

If the repository is already cloned, do not clone it again; navigate to your existing local copy and update it as instructed by your instructor.

**If you have not cloned the repository**, open the script directly in GitHub:

[seir_ec2_userdata.sh — Lab 0 startup script](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lab0_basics/seir_ec2_userdata.sh)

Click **Raw** (or open the raw file), select all of the script, and copy it. **Copy the script contents, not the GitHub URL.** You will paste the contents into the EC2 launch template's **User data** field.

## Step 2 — Choose your AWS Region and instance

1. Sign in to the **AWS Management Console**.
2. In the upper-right Region selector, choose the Region your instructor is using, or a Region where your account's eligible instance type is available.
3. Open **EC2 → Instances → Launch instances** to review the launch options.
4. Choose **Amazon Linux 2023** as the Amazon Machine Image (AMI).
5. Choose a small instance type shown as **Free Tier eligible for your account**, where available. Confirm the specific instance type, offer, and applicable limits in the console. Do not assume `t2.micro` or `t3.micro` is universally free.
6. Use an existing SSH key pair or create one if needed. Keep the private key secure. For browser-based EC2 Instance Connect, the instance must meet the applicable networking and access prerequisites.
7. Configure networking to allow **SSH (TCP 22) only from your IP address**, where possible. Do not open SSH to the entire internet merely for convenience.

**Instructor note:** Students can inspect these settings first, then save the configuration as a launch template rather than launching a one-off instance.

## Step 3 — Create and SAVE your EC2 launch template

1. In the EC2 console, go to **Launch Templates → Create launch template**. (Alternatively, use **Save as launch template** from the instance launch workflow if offered.)
2. Give it a recognizable name, for example `seir-foundations-lab0`.
3. Select the **Amazon Linux 2023 AMI**, eligible instance type, key pair, and appropriate network/security group settings.
4. Expand **Advanced details** and find **User data**.
5. Paste the **entire contents** of `seir_ec2_userdata.sh` into the User data box, starting with `#!/bin/bash`.
6. Save the launch template.
7. Verify that the template exists in **EC2 → Launch Templates**.

> **DO NOT DELETE YOUR LAUNCH TEMPLATE.** We will reuse it throughout Module 1. A saved launch template is configuration, not a running EC2 instance. It does **not** incur an EC2 compute charge simply by existing. Resources launched *from* it can incur charges.

## Step 4 — Launch an EC2 instance from your template

1. Select your saved template in **EC2 → Launch Templates**.
2. Choose **Actions → Launch instance from template** (wording may vary).
3. Verify the Region, AMI, instance type, network, security group, key pair, and User data configuration.
4. Launch **one** instance.
5. Go to **EC2 → Instances** and wait until it is running and the relevant status checks pass.
6. Record the **Instance ID** and **instance type** for your lab notes.

User Data normally runs during the instance's initial boot. Give the system a minute or two to complete initialization before testing the dashboard.

## Step 5 — Connect using the EC2 Connect button

1. In **EC2 → Instances**, select your running instance.
2. Click **Connect**.
3. Review the connection methods presented by AWS:
   - **EC2 Instance Connect:** use the browser-based connection option when supported and properly configured.
   - **SSH client:** follow the console's instructions for your operating system and your key pair.
4. For Amazon Linux 2023, the default SSH username is usually `ec2-user`.
5. Connect to your instance.

**Example for a local SSH client** (replace the placeholders with values from the EC2 **Connect → SSH client** instructions):

```bash
chmod 400 ~/Downloads/YOUR-KEY.pem
ssh -i ~/Downloads/YOUR-KEY.pem ec2-user@YOUR-PUBLIC-DNS
```

On Windows, key-file permissions and command syntax may differ depending on whether you use PowerShell, Windows OpenSSH, Git Bash, or WSL. Follow the instructions shown by the AWS Connect screen.

## Step 6 — Inspect your dashboard

After SSH login, look for the **SEIR Foundations / Chewbacca Operations Center** terminal dashboard. Depending on the script's login-shell setup, you may see it automatically or need to run:

```bash
seir-dashboard
```

Find these items and explain what they mean:

| Dashboard item | What it tells you |
| --- | --- |
| Hostname / instance ID | Which EC2 machine you are connected to |
| Instance type / Availability Zone | Where and on what type of compute the instance runs |
| CPU usage / vCPUs | Current processor activity and available logical CPUs |
| Memory | RAM in use and available |
| Disk usage | Space consumed on the root filesystem |
| Uptime | How long Linux has been running |
| Load average | Recent runnable or waiting workload; not the same as CPU percentage |

**Remember:** The dashboard displays operating-system metrics. It does **not** prove that your AWS bill is zero. Check AWS Billing for charges and credits.

## Step 7 — Show the class!

**Required:** Take a screenshot showing your SSH session and the dashboard. **Paste the screenshot into the Zoom chat** so classmates can see your successful deployment.

Before sharing, check the screenshot for passwords, private keys, tokens, or other secrets. Instance IDs and hostnames are usually not secrets, but you can crop them if you prefer.

Then answer in Zoom or aloud:

- What instance type did you launch?
- How many vCPUs and how much RAM does your dashboard show?
- What is the current CPU utilization?
- Did the dashboard appear automatically after SSH login?

## Step 8 — Tear down the EC2 instance (keep the template)

1. Return to **EC2 → Instances**.
2. Select the Lab 0 instance.
3. Choose **Instance state → Terminate instance** and confirm.
4. Verify the instance transitions to **Terminated**.
5. Review **EC2 → Volumes**, **Elastic IPs**, and any other resources you created. Remove unneeded billable resources, but do not delete anything you did not create or still need.
6. Go to **EC2 → Launch Templates** and confirm `seir-foundations-lab0` still exists.

**Terminate the running instance. Keep the reusable launch template.** Those are two different things.

## If something doesn't work

| Symptom | First thing to check |
| --- | --- |
| No dashboard after SSH login | Run `seir-dashboard`; check whether User Data finished |
| `seir-dashboard: command not found` | Confirm the full script was pasted into the launch template before the instance was launched |
| Can't SSH | Confirm instance is running, key pair, username, public connectivity, security group port 22, and Connect instructions |
| No public address | Check subnet/public IP assignment and your chosen connection method |
| User Data appears not to run | On the instance, inspect `sudo tail -n 100 /var/log/cloud-init-output.log` |
| Metrics look different from the instructor's | That is expected: instances have different live utilization and hardware configurations |
| Worried about charges | Check Billing, credits/Free Tier usage, instance type, and whether the instance was terminated |

If you use Claude Code for assistance, ask it to read the script and explain the exact failing step. **Do not paste private keys, tokens, or account credentials into AI prompts.**

## Completion checklist

- [ ] I checked my AWS Region, credits, and Free Tier eligibility.
- [ ] I obtained `seir_ec2_userdata.sh` from the class repository or GitHub.
- [ ] I created and **saved** my EC2 launch template.
- [ ] I launched one Amazon Linux 2023 instance from the template.
- [ ] I connected using the **Connect** button's browser or SSH instructions.
- [ ] I saw the dashboard and identified CPU, memory, disk, and uptime.
- [ ] I posted a screenshot in the Zoom chat.
- [ ] I terminated the instance and checked for leftover resources.
- [ ] I **kept** my launch template for future Module 1 labs.

### Definition of done

You are finished when the instructor can see your working dashboard screenshot, you can explain at least two of its metrics, your instance has been terminated, and your launch template is saved for reuse.

> **CHEWBACCA'S FINAL ASSESSMENT:** RRRRAAAWWWRRR! Your first EC2 is operational. The template survives. The instance does not. Excellent engineering.
