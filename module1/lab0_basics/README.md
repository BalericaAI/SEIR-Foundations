# SEIR Foundations — Module 1, Lab 0
## Your First EC2 Deployment: Launch, Connect, Observe, Repeat

**Course:** SEIR Foundations  
**Lab:** Module 1 / Lab 0 — EC2 Basics  
**Difficulty:** Beginner  
**Format:** Instructor-led introduction + individual homework  
**Homework deadline:** **Tuesday, October 20, 2026, at 12:00 PM Central Time**  
**Reference course:** Stéphane Maarek's AWS Udemy course, used alongside instructor demonstrations

> **Chewbacca's message:** RRRRAAAWWWRRR! Launch it. SSH into it. Show your work. Repeat until the cloud stops looking scary.

---

## 1. Purpose: a first win

This is a **basic introductory lab**. The objective is to become comfortable launching an Amazon EC2 instance, connecting to it using SSH, and recognizing that you are operating a real Linux server in AWS.

**We are not evaluating advanced Python, AI, networking, or Linux troubleshooting skills in Lab 0.** We are establishing the deployment and SSH skills that will be used extensively in **Lab 1 and throughout Module 1**.

You will use an EC2 **launch template** and a provided Bash **User Data** script to display a friendly system dashboard after connecting to the instance.

By the end, you should be able to repeat the process without needing the instructor to perform each click for you.

## 2. Learning outcomes

After completing Lab 0, you should be able to:

1. Identify the AWS Region in which you are working.
2. Select an EC2 instance type eligible for your account's current Free Tier or credits.
3. Find the supplied User Data Bash script in the class repository.
4. Create, save, and reuse an EC2 launch template.
5. Launch an Amazon Linux 2023 instance and wait for its status checks.
6. Find the instance's **public IPv4 address**.
7. Connect through the EC2 **Connect** button (EC2 Instance Connect, when supported) or an SSH client.
8. Read the login dashboard and recognize CPU, memory, disk, and uptime information.
9. Terminate a practice instance and launch a new one from the preserved template.
10. Document deployments with screenshots and concise explanations in GitHub.

## 3. Prerequisites

- An AWS account with credits and/or applicable Free Tier eligibility.
- Permission to launch and terminate EC2 instances and create launch templates.
- Access to the class GitHub repository.
- A GitHub repository where you can submit your own homework evidence.
- An SSH-capable environment or browser access to the EC2 Connect workflow.
- An AI helper of your choice (Claude Code, Ollama, ChatGPT, etc.) if you need assistance.

**Costs:** The instructor expects students to have AWS credits for these exercises. Do not panic about ordinary small lab deployments, but **Free Tier eligibility varies by account, region, instance type, and account creation date**. EC2, public IPv4 addresses, storage, and other resources may incur charges. Choose an eligible small instance, avoid unnecessary extras, and **terminate practice instances after each exercise**. A saved launch template itself does not incur EC2 compute charges.

## 4. Lab files and references

- [Lab 0 runbook](runbook.md) — step-by-step instructor-led procedure.
- [EC2 User Data script](seir_ec2_userdata.sh) — script to paste into the launch template.
- [Class GitHub repository](https://github.com/BalericaAI/SEIR-Foundations).
- [Direct User Data script on GitHub](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lab0_basics/seir_ec2_userdata.sh).

Optional local setup:

```bash
git clone https://github.com/BalericaAI/SEIR-Foundations.git
cd SEIR-Foundations/module1/lab0_basics
```

If you have not cloned the repository, open the direct GitHub script link, choose **Raw**, and copy the entire Bash script into the EC2 launch template's **User data** field. Do not paste a GitHub page URL into User Data; paste the actual script contents.

## 5. Instructor-led procedure

Follow [runbook.md](runbook.md) while the instructor demonstrates:

1. Sign in to the AWS Console and select the intended Region.
2. Navigate to **EC2** and create a **launch template** using **Amazon Linux 2023** and an appropriate Free Tier-eligible or credit-covered instance type.
3. Configure an appropriate key pair and network/security group. Permit SSH (TCP 22) only from a suitable trusted source where practical; do not expose additional ports unnecessarily.
4. Paste the entire `seir_ec2_userdata.sh` file into **Advanced details → User data** and save the template.
5. Launch an instance from the saved template.
6. Wait for the instance to reach **Running** and pass its status checks.
7. Find and record the instance's public IPv4 address.
8. Select the instance and click **Connect**. Follow either the browser-based EC2 Instance Connect instructions (if supported) or the **SSH client** instructions shown by AWS.
9. After login, observe the SEIR system dashboard. If it does not appear automatically, try `seir-dashboard` and consult the runbook.
10. Take a screenshot and share the initial result in the class Zoom chat.
11. Terminate the instance when finished, but **keep the launch template** for the homework and subsequent labs.

**SSH reminder:** SSH is the critical skill here. Lab 1 will depend heavily on your ability to connect to Linux servers and work from the terminal.

## 6. Homework — three separate EC2 deployments

**Due: Tuesday, October 20, 2026, at 12:00 PM Central Time.**

Independently perform **three separate successful EC2 launches**, preferably reusing your saved launch template. For each deployment:

1. Launch a new EC2 instance.
2. Wait until it is ready.
3. Record its **public IPv4 address**.
4. Successfully connect through EC2 Instance Connect or SSH.
5. Show the SEIR dashboard or run `seir-dashboard`.
6. Capture a screenshot demonstrating your connection and dashboard.
7. Write a brief explanation of what you did, how you connected, and what the dashboard showed.
8. Terminate the instance after collecting evidence, unless the instructor specifically directs otherwise.

**You must demonstrate three different public IPv4 addresses across the three deployments.** Public IP addresses are assigned by AWS and can sometimes be reused, so do not assume a fresh launch guarantees a unique address. If an address repeats, record that observation and perform another launch until you have three distinct addresses. Do **not** purchase Elastic IP addresses to satisfy this requirement.

You may run the deployments sequentially. **Three simultaneous running instances are not required.** This reduces unnecessary costs.

### Homework evidence table

Fill in this table in your own GitHub submission:

| Deployment | Public IPv4 address | Connection method | Screenshot | Instance terminated? |
|---|---|---|---|---|
| 1 | `YOUR_IP_1` | EC2 Connect / SSH | `screenshots/deployment-1.png` | Yes / No |
| 2 | `YOUR_IP_2` | EC2 Connect / SSH | `screenshots/deployment-2.png` | Yes / No |
| 3 | `YOUR_IP_3` | EC2 Connect / SSH | `screenshots/deployment-3.png` | Yes / No |

**Screenshot guidance:** Capture the SSH terminal and dashboard; include the instance's public IPv4 in your written explanation or an accompanying AWS Console screenshot. A terminal dashboard alone may not display the public IP. Do not expose private keys, passwords, AWS access keys, tokens, or other secrets.

### Suggested GitHub submission structure

```text
seir-foundations-homework/
└── module1/
    └── lab0_basics/
        ├── README.md
        └── screenshots/
            ├── deployment-1.png
            ├── deployment-2.png
            └── deployment-3.png
```

In your submission README, include:

- The completed evidence table with **three distinct public IPv4 addresses**.
- One short paragraph per deployment describing the launch, SSH connection, and dashboard.
- What CPU, memory, disk, and uptime tell you about the instance.
- One thing that became easier after repeating the process.
- Any errors encountered and how you resolved them.
- Confirmation that you retained the launch template and cleaned up practice instances.

Commit and push your screenshots and explanation to **your GitHub repository**. Submit the repository link through the instructor's designated submission channel by the deadline. **Posting the first screenshot to Zoom during class does not replace the GitHub homework submission.**

## 7. How to use your AI helper

Your AI assistant may be **Claude Code, Ollama, ChatGPT, or another model**. This README provides the context it needs to help you.

### Instructions for the AI helper

> You are assisting a beginner student in SEIR Foundations Module 1, Lab 0. The goal is for the student to launch an Amazon Linux 2023 EC2 instance using the provided User Data script, connect by SSH or EC2 Instance Connect, inspect the dashboard, and repeat the deployment three times for homework. Prioritize simple explanations and one step at a time. Use `runbook.md` and `seir_ec2_userdata.sh` as the source of truth. Ask what step the student is on, what they expected, and what actually happened. Help diagnose issues without taking over the lab. Never request or reveal AWS credentials, private SSH keys, or secrets. Do not change infrastructure, create billable resources, or terminate instances on the student's behalf without explicit approval. Remind the student to preserve the launch template and terminate unused instances.

### Good questions to ask your AI helper

- "What is the difference between an EC2 instance and an EC2 launch template?"
- "Where do I paste the Bash User Data script in the EC2 launch template?"
- "Why do I need to select Amazon Linux 2023 for this lab?"
- "What does a public IPv4 address mean, and where can I find it?"
- "Explain the SSH instructions shown on my EC2 Connect screen."
- "I connected successfully, but the SEIR dashboard did not appear. Help me check it."
- "What do CPU, memory, disk usage, and uptime mean?"
- "How do I confirm an EC2 instance has been terminated without deleting my launch template?"
- "Review my homework README and tell me which required evidence is missing."

**AI is a tutor, not a substitute for your own three deployments.** You must execute the work and verify the results yourself.

## 8. Common issues and first checks

| Symptom | Check first |
|---|---|
| Cannot launch instance | AWS Region, permissions, instance type availability, quotas, and account eligibility |
| Cannot connect over SSH | Instance running/status checks, public IPv4, security group TCP 22 rule, correct key and user (`ec2-user` for Amazon Linux 2023) |
| EC2 Instance Connect fails | Browser connection support, instance network configuration, security group, and AWS-provided Connect instructions |
| Dashboard does not display | Verify User Data was pasted as script text; run `seir-dashboard`; check `/var/log/cloud-init-output.log` if needed |
| Script was added after launch | User Data normally runs on initial launch; use the saved corrected template for a new instance |
| New instance has the same public IP | AWS may reuse public addresses; launch another instance and record the distinct IPs |
| Worried about costs | Check AWS credits/Free Tier eligibility, inspect running resources, terminate unused instances, and review AWS Billing/Budgets |
| GitHub screenshots missing | Ensure image files were added, committed, and pushed, not merely saved locally |

When asking for help, provide: **step number, command/action, expected result, actual result, and a sanitized error message or screenshot**.

## 9. Definition of done

- [ ] I completed the instructor-led EC2 deployment.
- [ ] I connected to EC2 using the AWS Connect instructions or SSH.
- [ ] I observed the SEIR dashboard and shared a screenshot in Zoom during class.
- [ ] I preserved my launch template.
- [ ] I completed three separate EC2 deployments for homework.
- [ ] I successfully connected to each of the three instances.
- [ ] I recorded **three distinct public IPv4 addresses**.
- [ ] I uploaded three screenshots and explanations to my GitHub repository.
- [ ] I submitted my repository link by **Tuesday, October 20, 2026, noon Central Time**.
- [ ] I terminated unused EC2 instances and checked for leftover billable resources.

## 10. Why repetition matters

The objective is **confidence through repetition**. The first deployment may feel unfamiliar. The second should feel easier. By the third, the workflow should be recognizable and repeatable.

In Lab 1, you will use SSH repeatedly to edit files, run programs, inspect logs, and troubleshoot your own systems. **Lab 0 removes the uncertainty around connecting to EC2 before that work begins.**

> **Chewbacca's final assessment:** RRRRAAAWWWRRR! Three launches. Three SSH sessions. Three public IPs. Three screenshots. The Force is strong with students who actually do the homework.
