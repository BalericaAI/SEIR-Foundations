# SEIR Foundations — Module 1, Lesson 4 Homework

## VPC: Draw the Map Before You Build the City

**Course:** SEIR Foundations  
**Lesson:** Module 1 / Lesson 4 — VPC networking (Week 7)  
**Difficulty:** Beginner  
**Format:** Individual homework + optional "Be A Man" extra credit (including Jira and a classmate change-request review)  
**Homework deadline:** **Tuesday, December 1, 2026, at 12:00 PM Eastern Time** (11:00 AM Central / 9:00 AM Pacific / 5:00 PM London)  
**Submission methods:** Send to Theo via FB DM or email  
**Reference course:** Stéphane Maarek's AWS Certified Solutions Architect – Associate (Udemy)  
**Lab runbook:** [Download and Run `create_balerica_vpc.sh`](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/readme.md)  
**Background reading:** [RFC 1918, Private IPv4 and Subnetting](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/RFC_1918_Explanation.md)

> **Chewbacca's message:** RRRRAAAWWWRRR! Anyone can click "Create VPC." An engineer can tell you why the subnet is a /24, which addresses AWS keeps, and where every packet goes. This week, you learn the math behind the map.

---

## 1. Purpose

In class, we built the Balerica Bank network **by hand in the AWS console** ("click-ops"): one VPC, an Internet Gateway, route tables, and public and private subnets. We have **not started** the script runbook (`readme.md`) yet. That comes next.

Clicking through the console is easy. **Knowing what you clicked** is the skill. This week is about the fundamentals underneath every VPC: **binary**, **IP addresses**, **subnet masks**, **CIDR**, and **public vs. private subnets**.

This week you will:

- **Read** Bahga section 2.6 and Theo's `RFC_1918_Explanation.md`.
- **Watch** Maarek SAA Section 27 and **complete its section quiz**, then watch a subnet mask explainer and Professor Messer Network+ sections 1.6 and 1.7.
- **Design** your own VPC from Theo's template, with **1 + your birth year's last two digits** as its second octet: **3 public** and **6 private** subnets across 3 AZs. Everything this week stays in the Class A private range, **10.0.0.0/8**.
- **Build** your VPC and complete the **class EC2 lab** inside it: one instance in **each** of your 3 public subnets, serving the class page on **port 80**.
- **Practice** binary until it is boring, using the Cisco Binary Game.
- **Solve** 20 subnetting questions by hand, showing your work: Theo's 7 plus 13 more, from easy to hard.
- **(Optional)** Work like a real infrastructure team: check your math with Python, plan the build in **Jira**, get a **change request** approved by a classmate, build and roll back your design, schedule your **teardown**, create your Jira backlog with code, and get ready for next week's script runbook.

**Why this matters:** every cloud job interview has a subnetting question, and every real network outage eventually comes down to an address, a mask, or a route. And on a real team, nobody builds a network because they felt like it: the work is **planned in tickets**, **approved through a change request**, and **cleaned up on schedule**. Next week we automate this network with a script. If you don't understand the network, you are just running someone else's code and hoping. Chewbacca does not hope. Chewbacca subnets.

**There are no automatic failure conditions this week.** Read the requirements carefully anyway.

 

> ⚠️⚠️⚠️ **WARNING: YOUR VPC USES YOUR BIRTH YEAR, NOT THEO'S 20** ⚠️⚠️⚠️
>
> 🚨 Your VPC is `10.1<last two digits of your birth year>.0.0/16` (born 1984 → `10.184.0.0/16`). A network architecture file — or EC2 screenshots — still using Theo's `10.20.x.x` **gets no credit.** 🚨
>
> 📅 Start from Theo's template in Section 4.2 and replace **every** `20` in the second octet.

 

---

## 2. Folder structure (required)

Add this folder to your existing homework repo (same repo and format as previous weeks — see [Aaron's example HW Repo](https://github.com/aaron-dm-mcdonald/seir-foundations-homework)).

```
seir-foundations-homework/
└── module1/
    ├── lab0_basics/
    ├── lab0.5_basics_contd/
    ├── lesson1_ec2/
    ├── lesson2_slack/
    ├── lesson3_jira/
    └── lesson4_vpc/
        ├── README.md                                    (your evidence tables — Section 8)
        ├── network_architecture_YourNameHere.txt        (Section 4)
        ├── subnetting_practice_YourNameHere.txt         (Section 7)
        ├── lesson4_notes.md                             (Section 5.5, plus a BAM section if you do extra credit)
        └── screenshots/
            ├── Maarek_Section27_quiz.jpg
            ├── binary_game_high_score.jpg
            ├── public_subnet_a.jpg
            ├── public_subnet_b.jpg
            ├── public_subnet_c.jpg
            ├── BAM_7.1.jpg                              (extra credit)
            ├── BAM_7.2a.jpg                             (extra credit)
            ├── BAM_7.2b.jpg                             (extra credit)
            ├── BAM_7.3a.jpg                             (extra credit)
            ├── BAM_7.3b.jpg                             (extra credit)
            ├── BAM_7.4.jpg                              (extra credit)
            ├── BAM_7.5.jpg                              (extra credit)
            ├── BAM_7.6.jpg                              (extra credit)
            └── BAM_7.7.jpg                              (extra credit)
```

Use these file names exactly — they are how your work gets checked.

---

## 3. Required — Reading, videos, and practice

Do these **before** you start the subnetting practice (Section 7) and your network design (Section 4). Both use this vocabulary: **octet**, **subnet mask**, **CIDR**, **network address**, **usable hosts**.

### 3.1 Reading

| Source | What to read |
|--------|--------------|
| Book — Bahga | Section **2.6** |
| Theo's guide | [RFC 1918, Private IPv4 and Subnetting](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/RFC_1918_Explanation.md), all of it. Its 7 practice questions are part of Section 7. |

### 3.2 Videos

| Source | What to watch |
|--------|---------------|
| Udemy — Maarek SAA | **Section 27**, including its **section quiz** — screenshot required (below) |
| YouTube | [Subnet Mask - Explained](https://youtu.be/s_Ntt6eTn94?si=4WBd3L1nZxc1kIMQ) |
| YouTube — Professor Messer | [Network+ videos](https://youtube.com/playlist?list=PLG49S3nxzAnl_tQe3kvnmeMid0mjF8Le8&si=joBbZ78PYI4pv2XH), sections **1.6** and **1.7** |

### 3.3 Evidence — Maarek Section 27

**Submission:** `Maarek_Section27_quiz.jpg`

Watch Section 27, then take its **section quiz**. Your screenshot must show:

1. The **completed Section 27 quiz** — the results page with your **score**.
2. Your **computer's clock with the date** (taskbar or menu bar) in the same image.

No file is required for the other reading or videos.

---

## 4. Required — Design your own network architecture

**Submission:** `network_architecture_YourNameHere.txt`

You are the network engineer. Start from **Theo's Balerica plan** (Section 4.2) and make it yours: replace the **`20`** in the second octet with a **`1` followed by the last two digits of the year you were born**. Everything this week stays inside the **Class A private range, `10.0.0.0/8`**. (Class B and C private ranges are still fair game in the subnetting practice — Theo's Question 5 — and in the Deep dive, Topic 6.)

| Born in | Your VPC CIDR | Your Public Subnet A |
|---------|---------------|----------------------|
| 1984 | `10.184.0.0/16` | `10.184.1.0/24` |
| 1999 | `10.199.0.0/16` | `10.199.1.0/24` |
| 2003 | `10.103.0.0/16` | `10.103.1.0/24` |

The test: **someone else could open the AWS console and build your VPC using only your file.** If they would have to guess anything, it is missing.

### 4.1 Requirements

| # | Your plan must… |
|---|-----------------|
| 1 | Name the **AWS region** and its **3 Availability Zones**. You can keep Theo's `us-east-1`, or pick another region — then use **real AZ names** from it (for example `us-west-2a`, `us-west-2b`, `us-west-2c`). |
| 2 | Use the VPC CIDR **`10.1<your two digits>.0.0/16`**, with a VPC **name**. |
| 3 | Keep Theo's layout: **3 public subnets** (`.1`, `.2`, `.3`) and **6 private subnets** (`.11`–`.13` and `.21`–`.23`), one per tier in each AZ (A, B, C). |
| 4 | Replace the `20` in **every** subnet, so every subnet is inside **your** VPC. |
| 5 | End with a **"Why I designed it this way"** section: at least **5 sentences** explaining your addressing — what the `/16` and `/24` mean, how many AWS usable addresses each subnet has, and how someone can tell the **tier** and **AZ** from an IP address alone. |

### 4.2 Template (copy it, then make it yours)

This is **Theo's** plan. Copy it, put your name at the top, and replace **every `20` in the second octet** with **`1` + your two digits** (for example `184`). Change the region and AZ names only if you chose a different region.

```text
NETWORK ARCHITECTURE — YourNameHere
Designed for region: us-east-1
Availability Zones:  us-east-1a, us-east-1b, us-east-1c

VPC
  Name:        balerica-vpc
  CIDR:        10.20.0.0/16

Public Subnet
A: 10.20.1.0/24
B: 10.20.2.0/24
C: 10.20.3.0/24


Private Subnet 1
A: 10.20.11.0/24
B: 10.20.12.0/24
C: 10.20.13.0/24

Private Subnet 2
A: 10.20.21.0/24
B: 10.20.22.0/24
C: 10.20.23.0/24


WHY I DESIGNED IT THIS WAY
(at least 5 sentences)
```

`A`, `B`, and `C` are the three AZs you listed at the top, in that order.

> 🏛️ **Well-Architected check:** AWS's own best practice for this step is [REL02-BP03 — Ensure IP subnet allocation accounts for expansion and availability](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_planning_network_topology_ip_subnet_allocation.html): use an RFC 1918 range, leave room for subnets in multiple AZs, and keep unused space for growth. Your **"Why I designed it this way"** section is a good place to say how your design does that.

### 4.3 Validity rules

| Rule | Result |
|------|--------|
| VPC CIDR is still `10.20.0.0/16`, isn't `10.1<your birth-year digits>.0.0/16`, or isn't in `10.0.0.0/8` | No credit for Section 4 |
| Fewer than 3 public or 6 private subnets | No credit for Section 4 |
| No region, or AZ names that don't exist in that region | Not buildable — partial credit at most |
| A subnet still says `10.20.x.x` (outside your VPC) | AWS would reject it — partial credit at most |

> 🔒 Writing this file is pure planning. **Do not** paste AWS account numbers, access keys, or anything secret into it.

---

## 5. Required — The class EC2 lab, in YOUR VPC

**Submissions:** `public_subnet_a.jpg`, `public_subnet_b.jpg`, `public_subnet_c.jpg`, and the **Section 5.5** notes in `lesson4_notes.md`

Your design file (Section 4) is a plan. Now **build it and use it.** Complete the **class EC2 lab** — the same instance, the same [User Data script](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lab0_basics/seir_ec2_userdata.sh), the same web page on **port 80** — but this time inside **your own VPC**, with **one instance in each of your three public subnets**. The page (Part 5 of the script) shows each instance's **private IP address**, **Availability Zone**, and **VPC ID**, so it proves exactly where the instance landed.

| Screenshot | AZ | Public subnet | The instance's private IPv4 must be inside |
|------------|----|---------------|---------------------------------------|
| `public_subnet_a.jpg` | your AZ **A** | your **Public Subnet A** | your Public A CIDR |
| `public_subnet_b.jpg` | your AZ **B** | your **Public Subnet B** | your Public B CIDR |
| `public_subnet_c.jpg` | your AZ **C** | your **Public Subnet C** | your Public C CIDR |

✅ Born in 1984: your design says `Public Subnet A: 10.184.1.0/24` in `us-east-1a`, and instance A's private IPv4 is `10.184.1.57`.  
❌ Instance A's private IPv4 is `10.184.2.40` — that's Public Subnet **B**.  
❌ Instance A's private IPv4 is `10.20.1.57` — that's Theo's VPC, not yours.

### 5.1 Build your VPC from your design

In **your region** from Section 4, build by hand (click-ops, like class):

1. The **VPC**, with **your** name and CIDR.
2. An **Internet Gateway**, attached to your VPC.
3. Your **three public subnets** (A, B, C), each in the AZ your file says.
4. A **public route table** with `0.0.0.0/0 → your IGW`, associated with all three public subnets.

Your six private subnets aren't needed for this section (they're BAM_7.4).

> ⚠️ Turn on **DNS hostnames** for your VPC (**VPC → Your VPCs → select it → Actions → Edit VPC settings**) **before** you launch. Without it, your instances get no **Public IPv4 DNS** name — and your screenshots need one.

### 5.2 Launch the three instances

- Launch each instance the **same way as the class lab**: Amazon Linux 2023, the same instance type, and the full [`seir_ec2_userdata.sh`](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lab0_basics/seir_ec2_userdata.sh) pasted into **User data**. If you saved a launch template in class, you can use it — but check its network settings.
- Your security group must live **in your VPC** — security groups from the default VPC or from Theo's VPC can't be used. Allow **HTTP (port 80) from My IP**. Add SSH (port 22) from My IP only if you need it.
- Each instance must land in a **different** public subnet and get a **public IPv4 address**.

How you get each instance into the right subnet is up to you to figure out. You will explain it in your notes (5.5). **Hint:** look closely at **Network settings** when you launch.

### 5.3 What each screenshot must show

Find the instance's **Public IPv4 DNS** in **EC2 → Instances → (your instance) → Details**. Open the class lab page in your browser at **`http://<Public IPv4 DNS>`** (port 80). For example: `http://ec2-54-201-0-10.compute-1.amazonaws.com`

- Type `http://` yourself — if your browser switches to `https://`, the page won't load.
- Give a new instance a minute or two: the page appears only after the User Data script finishes.

Each screenshot must show, in **one image**:

1. The browser's **address bar**, with `http://<Public IPv4 DNS>`
2. The **class lab page**, showing **Instance Private Ip Address**, **Availability Zone**, and **Virtual Private Cloud (VPC)**
3. Your **computer's clock with the date** (taskbar or menu bar)

The **private IP** on the page must be inside the matching public subnet from your design, and the **Availability Zone** must be that subnet's AZ.

| Rule | Result |
|------|--------|
| The private IP on the page isn't inside the matching public subnet in **your** `network_architecture_YourNameHere.txt` | That screenshot does not count |
| The Availability Zone on the page isn't the AZ your design gives that subnet | That screenshot does not count |
| The three screenshots show **different VPC IDs**, or a VPC ID that doesn't match your table | Those screenshots do not count — all three must be in **your** one VPC |
| The private IP is in Theo's `10.20.0.0/16` range | That screenshot does not count |
| The address bar shows a raw IP or `https://` instead of `http://<Public IPv4 DNS>`, or a DNS name that doesn't match your table | That screenshot does not count |
| Two screenshots show the same private IP or the same subnet | Only one of them counts |

### 5.4 Evidence table (put this in your `lesson4_vpc/README.md`)

Copy the **private IP**, **AZ**, and **VPC ID** from the class lab page, and the **Instance ID** and **Public IPv4 DNS** from **EC2 → Instances → (your instance) → Details**.

| Instance | Date (local) | Time zone | AZ | Public subnet (from my design) | Private IPv4 | VPC ID | Instance ID | Public IPv4 DNS | Screenshot | Terminated? |
|----------|--------------|-----------|----|--------------------------------|--------------|--------|-------------|-----------------|------------|-------------|
| A | 2026-11-28 | America/Chicago | us-east-1a | 10.184.1.0/24 | 10.184.1.57 | vpc-0abc123example | i-0abc123example | ec2-54-201-0-10.compute-1.amazonaws.com | `screenshots/public_subnet_a.jpg` | Yes |
| B | | | | | | | | | `screenshots/public_subnet_b.jpg` | |
| C | | | | | | | | | `screenshots/public_subnet_c.jpg` | |

(Row A is an example — replace it with your real values. The private IP, AZ, VPC ID, and Public IPv4 DNS must match your screenshot exactly. All three rows have the **same** VPC ID.)

### 5.5 Notes — `lesson4_notes.md`

Start the file with a section called **How I put each EC2 in a different public subnet**. In **at least 5 sentences**, explain:

- **Where** in the launch steps you chose the VPC and the subnet, and **what** you selected for each of the three instances.
- How you made sure each instance got a **public IPv4 address**.
- What you had to set up **before** the port 80 page would load at the Public IPv4 DNS name (route table, security group, DNS hostnames, anything else).
- Anything that **went wrong** on the way, and how you fixed it.

> 💸 **Cleanup:** as soon as your three screenshots are done, **terminate all three instances**, then check **EC2 → Volumes** and **Elastic IPs** for leftovers. Public IPv4 addresses bill by the hour while an instance is running. Then delete your VPC — unless you're doing BAM_7.4 right away, in which case delete it when that's done.

> 🔒 Never show your private key (`.pem`) or its contents in a screenshot, README, or commit.

> 🏛️ **Well-Architected check:** you just put the same server in **three Availability Zones**. That's the AWS Well-Architected **Reliability** best practice [REL10-BP01 — Deploy the workload to multiple locations](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_fault_isolation_multiaz_region_system.html). And opening only port 80 from **your** IP, in **public** subnets only, is the **Security** practice [SEC05-BP01 — Create network layers](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_network_protection_create_layers.html). See Topic 5 in the Deep dive.

---

## 6. Required — Cisco Binary Game

**Submission:** `binary_game_high_score.jpg`

Play the [Cisco Binary Game](https://learningcontent.cisco.com/games/binary/index.html). Play it more than once. The goal is to convert any number from 0 to 255 to binary **without thinking about it**, because every IP address is four of those numbers.

Your screenshot must show:

1. Your **high score** on the game screen.
2. Your **computer's clock with the date** (taskbar or menu bar) in the same image.

> **Tip:** memorize the eight bit weights: **128, 64, 32, 16, 8, 4, 2, 1**. Every subnet mask you will ever see is built from them: 128, 192, 224, 240, 248, 252, 254, 255.

---

## 7. Required — Subnetting practice

**Submission:** `subnetting_practice_YourNameHere.txt`

Twenty questions: the **7 practice questions** from Theo's `RFC_1918_Explanation.md`, plus **13 more** (5 easy, 5 medium, 3 hard). Work them **by hand**: paper, a whiteboard, or a text editor. No subnet calculator.

> ⚠️⚠️⚠️ **WARNING: NO WORK SHOWN, NO CREDIT** ⚠️⚠️⚠️
>
> 🚨 An answer without its work gets **no credit**, even if it's right. Questions 1–7 have an answer key in Theo's guide. Copying it earns nothing — **your work** is what's graded. 🚨
>
> 📅 Do every question **before** you check any answer. Then check, and fix what you got wrong. Leave both your first answer and the fix in the file.

 

**Showing your work means:**

- **Binary conversions:** write out the bit weights (`128 64 32 16 8 4 2 1`), the bits, and the sum.
- **Calculations:** write each step — the formula, the numbers you put in, and the result.
- **Yes/no or "which ones" questions:** give the reason in one sentence, not just the answer.

### 7.1 File format

```text
SUBNETTING PRACTICE — YourNameHere

Q1:
Answer:
Work:

Q2:
Answer:
Work:
...
```

If you got one wrong on the first try, add `Fixed:` under it with the correct answer and what you missed.

### 7.2 Questions 1–7 — from `RFC_1918_Explanation.md`

1. Convert 21 and 23 to binary.
2. Identify the tier and AZ for 10.20.12.50.
3. Calculate the mask, total addresses and AWS assignable addresses for /26.
4. Does 10.20.13.0/24 overlap 10.20.0.0/20?
5. Is 172.31.255.254 RFC 1918? What about 172.32.0.1?
6. Why can an EC2 instance in a public subnet connect to a private Aurora instance without a NAT gateway?
7. Divide 10.20.50.0/24 into four /26 networks.

### 7.3 Easy (8–12)

8. Convert **192** to binary.
9. Convert **00101101** to decimal.
10. How many **total** addresses are in a **/28**? How many can you actually use in an **AWS** subnet that size?
11. The Class A private range is **10.0.0.0/8**. What are its **first** and **last** addresses? Is **10.255.255.254** a private address? Is **11.0.0.1**? Why or why not?
12. Write the **/20** subnet mask in dotted decimal. Show the mask in binary first.

### 7.4 Medium (13–17)

13. An instance has the address **10.20.37.200/22**. What is the **network address** of its subnet, the **last address**, and the **AWS usable range**? How many AWS usable addresses is that?

    > 💡 **Hint:** A `/22` mask is `255.255.252.0`. In the third octet, the block size is `256 − 252 = 4`, so subnets start at 0, 4, 8, 12… Which multiple of 4 is the closest one **at or below** 37? That's where this subnet starts.

14. Your VPC is **10.84.0.0/16**. Which of these could be a subnet in it: **a)** 10.84.4.0/22, **b)** 10.84.6.0/23, **c)** 10.84.5.0/23, **d)** 10.85.0.0/24? For each one that **can't**, say why. Then: do any of the valid ones **overlap** each other?

    > 💡 **Hint:** Two checks for each option. **1)** Is it inside the VPC? Compare the first two octets. **2)** Does it start on a valid boundary? A `/22` must start on a third octet that's a multiple of **4**; a `/23` on a multiple of **2**. For overlap, write the **first and last address** of each valid one.

15. A team needs a subnet with **at least 500 usable addresses** in AWS. What is the **smallest** subnet (largest prefix number) that works? Show why one size smaller doesn't.

    > 💡 **Hint:** AWS takes **5** addresses from every subnet, so you need `500 + 5` total. Subnet sizes are powers of 2 (256, 512, 1024…). Find the smallest one that's big enough, then turn it into a prefix: `/32 − (number of host bits)`.

16. Split **10.84.10.0/24** into **8 equal subnets**. What prefix do they use? List all eight.

    > 💡 **Hint:** 8 subnets = `2³`, so you **borrow 3 bits**: `/24 + 3`. Each subnet's size is `256 ÷ 8`. Start at `.0` and keep adding that size.

17. A subnet mask is **255.255.255.224**. What is the prefix (`/?`)? How many total addresses, and how many AWS usable?

    > 💡 **Hint:** Write `224` in binary. Count the `1`s. The first three octets (`255.255.255`) are already 24 ones.

### 7.5 Hard (18–20)

18. **Design under constraints.** Your VPC is **10.50.0.0/16**. You need **3 public subnets** with at least **200** usable addresses each, and **6 private subnets** with at least **1,000** usable addresses each, spread across 3 AZs. Give a CIDR for all nine. None may overlap, and each must start on a valid boundary for its size. Explain how you chose the sizes and the starting addresses.

    > 💡 **Hint:** Pick the **sizes** first: the smallest subnet with at least 200 usable (+5 for AWS), and the smallest with at least 1,000 usable. Then pick **starting addresses**: a `/22` must start on a third octet that's a multiple of 4. Keep the small public subnets and the big private ones in **separate areas** of the VPC so they can't collide. (If you did BAM_7.1, `check_my_vpc.py` can check your answer.)

19. **Which way does the packet go?** A subnet's route table has three routes:

    ```text
    Destination      Target
    10.20.0.0/16     local
    10.30.0.0/16     pcx-0abc   (a VPC peering connection)
    0.0.0.0/0        igw-0abc   (the Internet Gateway)
    ```

    For each destination, which route is used: **a)** 10.20.22.81, **b)** 10.30.4.4, **c)** 8.8.8.8, **d)** 10.99.0.5? Then answer: `0.0.0.0/0` matches **every** address, so why doesn't 10.20.22.81 go to the Internet Gateway? And what really happens to the packet in **d)**?

    > 💡 **Hint:** A router compares the destination with **every** route and picks the **most specific** match — the one with the **longest prefix** (`/16` beats `/0`). For **d)**, think about whether routers on the public internet know where to send an RFC 1918 address.

20. **Don't collide with the office.** Your company's on-premises network uses **10.0.0.0/12**, and you're about to connect a new VPC to it over a VPN. Which of these VPC CIDRs are **safe** (no overlap): **a)** 10.20.0.0/16, **b)** 10.8.0.0/16, **c)** 10.15.0.0/16, **d)** 10.16.0.0/12? Prove every answer in binary, using the second octet.

    > 💡 **Hint:** A `/12` fixes the first **12 bits**: all 8 bits of the first octet, plus the **first 4 bits of the second octet**. For `10.0.0.0/12`, those 4 bits are `0000`. Write each option's second octet in binary and compare its first 4 bits.

---

## 8. Evidence tables (put these in your `lesson4_vpc/README.md`)

| Item | File | Done? |
|------|------|-------|
| Bahga section 2.6 | — | Yes / No |
| `RFC_1918_Explanation.md` | — | Yes / No |
| Maarek SAA Section 27 | `screenshots/Maarek_Section27_quiz.jpg` | Yes / No |
| Subnet Mask - Explained video | — | Yes / No |
| Professor Messer Network+ 1.6 and 1.7 | — | Yes / No |
| Network architecture | `network_architecture_YourNameHere.txt` | Yes / No |
| Class EC2 lab in my VPC: port 80, one per public subnet | `screenshots/public_subnet_a.jpg`, `public_subnet_b.jpg`, `public_subnet_c.jpg` | Yes / No |
| EC2 instance table (Section 5.4) | in this README | Yes / No |
| Notes: how I put each EC2 in a different subnet | `lesson4_notes.md` | Yes / No |
| Cisco Binary Game | `screenshots/binary_game_high_score.jpg` | Yes / No |
| Subnetting practice (20 questions) | `subnetting_practice_YourNameHere.txt` | Yes / No |

Under the table, add:

- **My binary game high score:**
- **Subnetting practice: how many I got right on the first try (out of 20), and the one that took me longest:**
- **My VPC CIDR and region:** (for example `10.184.0.0/16` in `us-east-1`)
- **The hardest part of the design, in 2–3 sentences:**

---

## 9. Deep dive (no submission)

Nothing to turn in for this section. These are for students who want to go further — and for anyone who wants subnetting to feel easy before next week.

### Topic 1 — IP addressing and subnetting, the long way

| Read | Watch |
|------|-------|
| [Microsoft Learn: TCP/IP addressing and subnetting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/tcpip-addressing-and-subnetting) | [what is an IP Address? // You SUCK at Subnetting // EP 1](https://youtu.be/5WfiTHiU4x8?si=ih5UdeCyc-hEA8DV) |
| [IP addressing & troubleshooting guide](http://penta2.ufrgs.br/trouble/ts_ip.htm) | [16. How to Find the Number of Subnets, Valid Hosts](https://youtu.be/uyRtYUg6bnw?si=9IFsgX4GY4x5Nf0I) |

**Think about:** the classic formula says a /24 has 254 usable hosts. AWS says 251. Who is right, and why do they disagree?

### Topic 2 — Networking fundamentals, end to end

| Read | Watch |
|------|-------|
| [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html), sections 2–5 | [Professor Messer Network+ playlist](https://youtube.com/playlist?list=PLG49S3nxzAnl_tQe3kvnmeMid0mjF8Le8&si=joBbZ78PYI4pv2XH) (the whole thing) |

**Lab hook:** both public and private subnets in our VPC use private `10.x` addresses. So what actually makes a subnet "public"? (Hint: it's one route.)

### Topic 3 — PowerCert Animated Videos (short, animated, beginner-friendly)

[PowerCert](https://www.youtube.com/@PowerCertAnimatedVideos) covers the same ground as Professor Messer sections 1.6 and 1.7 in short animated videos. *Subnet Mask - Explained*, from the required list, is one of theirs. Watch these in this order:

| # | Watch | Ties to this week |
|---|-------|-------------------|
| 1 | [IP Address - IPv4 vs IPv6 Tutorial](https://www.youtube.com/watch?v=ThdO9beHhpA) | Octets and binary, the base of every question in Section 7 |
| 2 | [Public vs Private IP Address](https://www.youtube.com/watch?v=po8ZFG0Xc4Q) | Why our VPC uses RFC 1918 addresses |
| 3 | [LAN, WAN, SUBNET - EXPLAINED](https://www.youtube.com/watch?v=NyZWSvSj8ek) | What a subnet actually is |
| 4 | [Default Gateway Explained](https://www.youtube.com/watch?v=pCcJFdYNamc) | The `.1` address AWS reserves for the VPC router |
| 5 | [DHCP Explained](https://www.youtube.com/watch?v=e6-TaH5bkjo) | How your EC2s got their private addresses in Section 5 |
| 6 | [NAT Explained](https://www.youtube.com/watch?v=FTUV0t6JaDA) | How private addresses reach the internet (and why our private subnets can't, yet) |
| 7 | [ARP Explained](https://www.youtube.com/watch?v=cn8Zxh9bPio) | How a device finds its neighbor inside a subnet |
| 8 | [Subnets vs VLANs](https://www.youtube.com/watch?v=6_giEv20En0) | Two ways to split up a network |

### Topic 4 — Ad-free reading

| Read | Why |
|------|-----|
| [AWS: Subnet CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html) | The official list of the 5 addresses AWS reserves in every subnet |
| [AWS: VPC CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html) | Why a VPC must be between /16 and /28 |
| [AWS Networking Best Practices: IP Address Planning with CIDR Blocks](https://aws.github.io/aws-networking-best-practices/foundation/cidr/) | How to choose a VPC CIDR you won't regret, with a size table |
| [Cloudflare: What is a subnet?](https://www.cloudflare.com/learning/network-layer/what-is-a-subnet/) | A plain-English explanation of subnets and subnet masks |

**Think about:** in Section 5, instance A got a private address in your Public Subnet A. Using the AWS subnet page, which addresses in that subnet could it **never** have gotten, and why?

### Topic 5 — The AWS Well-Architected Framework

The **Well-Architected Framework** is AWS's official set of best practices, organized into **six pillars**: operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability. Every AWS certification, including the SAA, expects you to think this way. This week's work maps straight onto it:

| Read | Pillar | What it says | Where you did it this week |
|------|--------|--------------|----------------------------|
| [Well-Architected overview](https://aws.amazon.com/architecture/well-architected/) and [the six pillars](https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html) | All | What the framework is and what each pillar covers | — |
| [REL02-BP03 — IP subnet allocation for expansion and availability](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_planning_network_topology_ip_subnet_allocation.html) | Reliability | Use RFC 1918 ranges, plan subnets across AZs, and leave room to grow | Section 4 (your design) |
| [REL10-BP01 — Deploy the workload to multiple locations](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_fault_isolation_multiaz_region_system.html) | Reliability | Spread workloads across Availability Zones; running in only one AZ is an anti-pattern | Section 5 (one EC2 per AZ) |
| [SEC05 — Protecting networks](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec05.html) and [SEC05-BP01 — Create network layers](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_network_protection_create_layers.html) | Security | Keep internet-facing parts apart from internal-only parts; putting everything in one subnet is an anti-pattern | Public vs. private tiers; port 80 open to your IP only |

**Think about:** your design puts web servers in public subnets and keeps two private tiers. Which part of SEC05-BP01 does that follow? And what would REL10-BP01 say about a design with all nine subnets in **one** AZ?


### Topic 6 — Beyond Class A: the Class B and C private ranges

The homework stays in **10.0.0.0/8** (Class A). RFC 1918 sets aside **two more** private ranges, and you'll meet both at work — `192.168.x.x` on almost every home router, and `172.16.0.0/12` inside many companies (including every **AWS default VPC**, which uses `172.31.0.0/16`).

| Range | Old class | Addresses | Where you'll see it |
|-------|-----------|-----------|---------------------|
| `10.0.0.0/8` | A | 16,777,216 | This homework; most large company and cloud networks |
| `172.16.0.0/12` (172.16.0.0 – 172.31.255.255) | B | 1,048,576 | AWS default VPCs (`172.31.0.0/16`), Docker, corporate networks |
| `192.168.0.0/16` | C | 65,536 | Home and small-office routers |

| Read | Watch |
|------|-------|
| [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html), section 3 | [Public vs Private IP Address](https://www.youtube.com/watch?v=po8ZFG0Xc4Q) (PowerCert) |
| [AWS: VPC CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html) | |

**Optional practice** (no submission — same rules: show your work). Theo's Question 5 in Section 7 is required Class B practice; these go further:

- **B1.** Which RFC 1918 block does **192.168.40.7** belong to? Is **192.169.1.1** a private address? Why or why not?
- **B2.** A VPC is **172.16.0.0/16**. Which of these could be a subnet in it: **a)** 172.16.4.0/22, **b)** 172.16.6.0/23, **c)** 172.16.5.0/23, **d)** 172.17.0.0/24? Do any of the valid ones overlap? *Hint: same method as Question 14.*
- **B3.** Split **192.168.10.0/24** into **8 equal subnets**. What prefix do they use? List all eight. *Hint: same method as Question 16 — only the first two octets change.*
- **B4.** Your office uses **10.0.0.0/12**. Is a VPC at **172.16.0.0/16** safe to connect? Why? *Hint: compare the first octets.*
- **B5.** Why is `172.31.0.0/16` — the default VPC range — a **bad** choice for a VPC you'll connect to another AWS account's default VPC? *Hint: what range does the other account's default VPC use?*

---

## 10. "Be A Man" (BAM) extra credit

Everything in this section is optional, and everything is due with the homework: **Tuesday, December 1, 2026, 12:00 PM Eastern Time.**

The BAM items are built to be done **in order**, the way a real infrastructure team works: **check** the plan (7.1) → **ticket** it (7.2) → **get approval** (7.3) → **build and roll back** (7.4) → **schedule cleanup** (7.5) → **automate the tickets** (7.6) → **prep the next lab** (7.7). You can do any of them on their own, except where an item says it needs another.

Steps 0–3 of [`readme.md`](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/readme.md) are now fair game. **Do not run Step 6 (the script itself) yet** — we run it together in the next lab.

**Every BAM screenshot must prove its time:**

- **Terminal screenshots** must show the **ID line**. On your EC2 instance:

  ```bash
  whoami && TZ='America/New_York' date && ec2-metadata -i && uptime -s
  ```

  Use your own zone. If `ec2-metadata` is missing, run `sudo dnf install -y ec2-utils` first. On **your own computer** or **CloudShell** (no instance ID there), run `whoami && date` and make sure your **computer's clock with the date** is visible in the same image.

- **Browser, AWS console, Jira, and Slack screenshots** must show your **computer's clock with the date** (taskbar or menu bar) in the same image.

Add a **BAM** section to `lesson4_notes.md`, with the Instance ID from any EC2 terminal screenshot.

> 🔒 **Never show AWS access keys, secret keys, session tokens, your `~/.aws/credentials` file, your Jira API token, or your `.env` file in any screenshot, README, GitHub commit, or AI prompt.** Blur your AWS account number if you prefer.

### BAM_7.1 — Check your math with Python

**Submission:** `BAM_7.1.jpg`

Engineers don't trust their own arithmetic. They test it. Create `check_my_vpc.py` (on your EC2 instance, your own computer, or CloudShell — anywhere with Python 3):

```python
#!/usr/bin/env python3
"""BAM_7.1 — check your VPC plan before you build it.
Edit VPC_CIDR and SUBNETS to match YOUR network_architecture file, then run:
    python3 check_my_vpc.py
Names must start with "public" or "private" so the script can count tiers.
"""
import ipaddress

VPC_CIDR = "10.20.0.0/16"           # <-- replace with YOUR VPC CIDR
SUBNETS = {                          # <-- replace with YOUR subnets (name: CIDR)
    "public-a":   "10.20.1.0/24",
    "public-b":   "10.20.2.0/24",
    "public-c":   "10.20.3.0/24",
    "private1-a": "10.20.11.0/24",
    "private1-b": "10.20.12.0/24",
    "private1-c": "10.20.13.0/24",
    "private2-a": "10.20.21.0/24",
    "private2-b": "10.20.22.0/24",
    "private2-c": "10.20.23.0/24",
}

RFC1918 = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
problems = []

vpc = ipaddress.ip_network(VPC_CIDR)          # raises an error if host bits are set
if not any(vpc.subnet_of(block) for block in RFC1918):
    problems.append(f"VPC {vpc} is not inside an RFC 1918 block")
if not 16 <= vpc.prefixlen <= 28:
    problems.append(f"VPC prefix /{vpc.prefixlen} is outside AWS's /16-/28 limit")

nets = {}
print(f"{'Name':<14}{'CIDR':<18}{'Mask':<17}{'Total':>7}{'AWS usable':>12}  Usable range")
for name, cidr in SUBNETS.items():
    net = ipaddress.ip_network(cidr)
    nets[name] = net
    total = net.num_addresses
    usable = total - 5                         # AWS reserves 5 per subnet
    first, last = net[4], net[-2]              # .0-.3 and the last address are reserved
    print(f"{name:<14}{str(net):<18}{str(net.netmask):<17}{total:>7}{usable:>12}  {first} - {last}")
    if not net.subnet_of(vpc):
        problems.append(f"{name} {net} is NOT inside the VPC {vpc}")
    if not 16 <= net.prefixlen <= 28:
        problems.append(f"{name} prefix /{net.prefixlen} is outside AWS's /16-/28 limit")

names = list(nets)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if nets[a].overlaps(nets[b]):
            problems.append(f"{a} {nets[a]} OVERLAPS {b} {nets[b]}")

public = sum(n.lower().startswith("public") for n in names)
private = sum(n.lower().startswith("private") for n in names)
if public < 3:
    problems.append(f"only {public} public subnets (need at least 3)")
if private < 6:
    problems.append(f"only {private} private subnets (need at least 6)")

print(f"\nPublic: {public}  Private: {private}  Total AWS-usable: {sum(n.num_addresses - 5 for n in nets.values()):,}")
if problems:
    print("\nPLAN FAILED:")
    for p in problems:
        print("  -", p)
    raise SystemExit(1)
print("\nPLAN OK — Chewbacca approves. RRRRAAAWWWRRR!")
```

1. Run it **once as-is** with Theo's values. It should print `PLAN OK`.
2. Replace `VPC_CIDR` and `SUBNETS` with **your** plan, then run:

   ```bash
   whoami && date
   python3 check_my_vpc.py
   ```

Your screenshot must show the time proof and your plan's table ending in `PLAN OK`, with your computer's clock visible.

In `lesson4_notes.md`, answer:

- Before you run it, work out the **mask** and **AWS usable addresses** for two of your subnets by hand. Did the script agree? If not, which one was wrong — you or the script — and why?
- **Break it on purpose:** change one subnet so it overlaps another. Paste the exact `OVERLAPS` line it printed. Then put it back.

### BAM_7.2 — Plan the build in Jira

**Submissions:** `BAM_7.2a.jpg` (backlog) and `BAM_7.2b.jpg` (one subnet task)

Your network design is a plan. In a real job, a plan becomes **tickets** before anyone touches the console. Turn yours into a Jira backlog, using the same skills as Lesson 3's "A Day in My Shoes."

> ⚠️ **No story points, no credit** — same rule as Lesson 3. Every story and task screenshot must show the **Story point estimate** field. The epic does not get points.

**Create your space:**

1. In Jira, choose **Spaces** (or **Projects**) → **Create space** → **Scrum** template → **team-managed**.
2. Name it **`SEIR-Net_YourNameHere`** (for example, `SEIR-Net_JaneDoe`). Accept the key Jira suggests, and write it down.
3. Turn on **Estimation → Story points**, exactly as in Lesson 3 Section 4.2 (**Space settings → Features**).

**Do not** use your `SEIR-Saga` space or your `Balerica AI Incident Management` (BAI) project. Keep each one clean.

**Build the backlog:**

| Level | How many | What it is | Example (Theo's plan — use yours) |
|-------|----------|------------|---------|
| **Epic** | 1 | Building your whole network | `Build us-east-1 VPC (10.20.0.0/16)` |
| **Story** | 1 per tier (at least 2) | One tier of your design, written as a user story | `As the application tier, I need 3 private subnets in 3 AZs so the app survives an AZ outage` |
| **Task** | 1 per resource (at least 13) | One resource you would create in the console: the VPC, the IGW, **each** route table, **each** subnet | `[Public] Subnet balerica-public-a — 10.20.1.0/24 — us-east-1a` |

**Rules:**

- Every story and task has the **epic as its Parent**.
- Start every task name with its tier in square brackets, such as `[Public]`, `[Private1]`, `[Private2]`, or `[Shared]` for the VPC and IGW.
- **Every subnet task's description** must include its **CIDR**, **subnet mask**, **AZ**, **total addresses**, **AWS usable addresses**, its **route table**, and **auto-assign public IP** on or off. The CIDR and AZ must match your `network_architecture_YourNameHere.txt` exactly; work out the rest yourself (BAM_7.1's script can check it).
  - ✅ `CIDR 10.20.1.0/24, mask 255.255.255.0, AZ us-east-1a. 256 total, 251 AWS usable (10.20.1.4–10.20.1.254). Route table balerica-public-rt. Auto-assign public IP ON. Done when the subnet shows Available with this route table.`
  - ❌ `make subnet`
- Every story and task gets a **Story point estimate** and a description of **at least 2 sentences**, ending with what "done" looks like.

| Screenshot | It must show |
|------------|--------------|
| `BAM_7.2a.jpg` | The backlog (or list view) showing every story and task with its story points, with your computer's clock visible |
| `BAM_7.2b.jpg` | One **subnet** task opened, showing its **Parent**, the full description (CIDR, mask, AZ, usable addresses…), and **Story point estimate**, with your computer's clock visible |

In `lesson4_notes.md`, add a **Jira items** table listing **every** item in the space (the CR from BAM_7.3 and the teardown ticket from BAM_7.5 too, if you do them):

| Key | Type | Summary | Story points |
|-----|------|---------|--------------|
| NET-1 | Epic | Build us-east-1 VPC (10.20.0.0/16) | — |
| NET-2 | Story | As the public tier, I need 3 public subnets in 3 AZs so the load balancer can reach the internet | 3 |
| NET-5 | Task | [Public] Subnet balerica-public-a — 10.20.1.0/24 — us-east-1a | 1 |
| | | | |

(The first rows are examples. Replace them with your real keys and values.) Under it, write your **space name and key**.

### BAM_7.3 — Change request, reviewed by a classmate

**Submissions:** `BAM_7.3a.jpg` (the CR) and `BAM_7.3b.jpg` (the approval)

**Needs BAM_7.2** (the CR links to your backlog).

On a real team, you don't change a production network without an approved **change request (CR)**. A CR answers four questions: **what** are you changing, **how** will you check it worked, **how** do you undo it, and **who** approved it.

**Write the CR.** In your `SEIR-Net_YourNameHere` space, create a **Task**:

- **Summary:** `CR: Build <region> VPC <your CIDR>` (for example `CR: Build us-east-1 VPC 10.184.0.0/16`)
- **Parent:** your epic
- **Label:** `change-request`
- **Link:** open the CR, choose **Link work item → blocks**, and link it to your `[Shared] VPC` task. That says "nobody builds the VPC until this CR is approved."
- **Story point estimate:** yes, like every task.
- **Description** — use these exact headings:

```text
WHAT IS CHANGING
(1–2 sentences: the VPC, region, CIDR, number of subnets per tier)

WHY
(1–2 sentences: what this network is for)

IMPLEMENTATION PLAN
(the order you would build in, using your Jira task keys, e.g. NET-3 VPC, NET-4 IGW, NET-5..NET-7 route tables, NET-8..NET-16 subnets)

VALIDATION PLAN
(how you will prove it worked: e.g. console Resource map matches the plan, subnet count, IGW attached, public route 0.0.0.0/0 -> IGW only on the public route table)

ROLLBACK PLAN
(how to undo it completely: which resources to delete, in what order, and how you confirm nothing is left)

RISK AND COST
(what could go wrong, what costs money and what doesn't — e.g. "No NAT gateway or Elastic IP, so no hourly charge")

APPROVER
(your classmate's name)
```

**Get it reviewed.** Pick a classmate as your **reviewer**. You review theirs too.

1. **Share the CR with your reviewer.** Either:
   - **(Preferred)** invite them to your Jira site (**Settings (⚙) → User management → Invite users**; the Free plan allows up to 10 users), **or**
   - send them a screenshot of the whole CR in Slack.
2. Your reviewer must leave **at least one real question or requested change**. "Looks good" doesn't count.
   - ✅ `Your rollback deletes the VPC before the subnets — won't AWS block that?`
   - ✅ `private2-b is /25 but the others are /24. Intentional?`
   - ❌ `nice`
3. **You answer** the question, or fix the CR and say what you changed.
4. Your reviewer then writes: **`APPROVED — <their name> — <date>`**.

If you used Slack, paste the reviewer's question, your answer, and their approval into **comments on the CR** in Jira, with their name, so the approval lives with the ticket.

| Screenshot | It must show |
|------------|--------------|
| `BAM_7.3a.jpg` | The CR opened, showing all seven description headings, the `change-request` label, the **blocks** link to your VPC task, and the **Story point estimate**, with your computer's clock visible |
| `BAM_7.3b.jpg` | The CR's comments (or the Slack thread) showing the reviewer's question, your answer, and `APPROVED — <name> — <date>`, with your computer's clock visible |

In `lesson4_notes.md`, write:

- Your **CR key** and your **reviewer's name**.
- The reviewer's question, and how you answered it (2–3 sentences).
- The CR **you** reviewed (classmate's name and CR key), and the question you asked.

### BAM_7.4 — Finish your design: the private tiers, then roll it all back

**Submission:** `BAM_7.4.jpg`

Section 5 built the **public** half of your design. Now finish it, so your VPC matches your `network_architecture_YourNameHere.txt` exactly.

**If you did BAM_7.3, only start once your CR says `APPROVED`.** Building before approval is exactly what a CR exists to stop. (Your CR covers the Section 5 build too.)

1. In your Section 5 VPC, add your **six private subnets** (Private Subnet 1 and 2, A/B/C), each in the AZ your file says.
2. Add a **private route table** with only the `local` route — **no** `0.0.0.0/0 → IGW` — and associate it with all six private subnets.
3. If you did BAM_7.2, move each Jira task to **Done** as you finish that resource. If you did BAM_7.3, build in the order of your CR's implementation plan.
4. Open **VPC → Your VPCs → (your VPC) → Resource map**, and take your screenshot.
5. **Delete everything** — instances first, then the VPC (your CR's rollback plan, if you wrote one). Confirm in **VPC → Your VPCs** that it's gone.

Your screenshot must show the **Resource map** with all **nine** subnets, both route tables, and the IGW, with your computer's clock visible.

In `lesson4_notes.md`, record:

- Anything in your plan that turned out to be **wrong or missing** when you actually built it. (If nothing: say what you double-checked.)
- Your VPC ID.
- How you deleted it, and in what order. If AWS refused to delete something, what did it say, and what did you delete first?

> 💸 **Cost and cleanup:** an empty VPC, its subnets, route tables, and IGW have no hourly charge. **Do not** create a NAT gateway or Elastic IP for this — those bill by the hour. Delete the VPC as soon as your screenshot is done. Just like the class network, **nothing stays up between labs.**

### BAM_7.5 — Schedule your teardown in Jira

**Submission:** `BAM_7.5.jpg`

We tear the class network down **at the end of every lab**, and the [readme](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/readme.md) warns that forgotten labs are the #1 cause of surprise bills. A calendar reminder is easy to ignore. On a real team, the reminder is a **ticket with a due date and a definition of done**.

In your `SEIR-Net_YourNameHere` space (or `SEIR-Saga` if you skipped BAM_7.2), create a **Task**:

- **Summary:** `Teardown: no lab VPCs left in my AWS account`
- **Label:** `teardown`
- **Due date:** **Tuesday, December 1, 2026** (the homework deadline, 12:00 PM Eastern — write the time in the description; Jira due dates have no time).
- **Story point estimate:** yes.
- **Description**, with these headings:

```text
WHY
(1–2 sentences: what keeps billing if a lab is forgotten)

STEPS
(how the class balerica-vpc is torn down — readme.md Step 8: download, bash -n, run, verify in the console —
 and how you delete your own Section 5 VPC)

DONE WHEN
- VPC -> Your VPCs shows no balerica-vpc and no VPC of my own design, in every region I used
- EC2 -> Instances shows nothing left running
- no NAT gateways or Elastic IPs exist

EVIDENCE
(what you checked, and when)
```

Before the deadline, actually **check your account** against **DONE WHEN**. Then add a comment with what you checked and when, and move the ticket to **Done**.

Your screenshot must show the teardown ticket opened, with its **due date**, `teardown` label, full description, your **comment**, **Done** status, and **Story point estimate**, with your computer's clock visible.

### BAM_7.6 — Plan as code: create your Jira backlog with Python

**Submission:** `BAM_7.6.jpg`

**Needs BAM_7.1** (it reads your plan from `check_my_vpc.py`).

In BAM_7.2 you typed a backlog by hand. Now write it **from your plan, with code** — the same way next week's script builds the network from code. This uses the **same Jira API token and `.env`** as Lesson 3's `jira.py`.

The script imports the `VPC_CIDR` and `SUBNETS` you already filled in, and runs those checks first. A plan that fails `check_my_vpc.py` never reaches Jira. Name your subnets `<tier>-<az letter>` (for example `public-a`, `private1-b`): the part before the dash becomes the route-table tier.

1. **Create a separate space** named **`SEIR-NetCode_YourNameHere`** (team-managed, Scrum, Estimation on), so the script's tickets don't mix with your BAM_7.2 backlog. Write down its key.
2. Put `vpc_to_jira.py` (below) in the **same folder** as `check_my_vpc.py`, next to the `.env` that holds your Jira settings (on EC2 that's `/opt/balerica-bank`).
3. Run it in three steps:

   ```bash
   whoami && TZ='America/New_York' date && ec2-metadata -i && uptime -s
   python3 vpc_to_jira.py --project YOURKEY --region YOUR-REGION --dry-run   # prints the tickets, creates nothing
   python3 vpc_to_jira.py --project YOURKEY --region YOUR-REGION --verify    # checks Jira access, creates nothing
   python3 vpc_to_jira.py --project YOURKEY --region YOUR-REGION             # creates the tickets — ONCE
   ```

   (Not on EC2? Use `whoami && date` and show your computer's clock instead.)

**Run the last command once.** The script saves every key it creates to `vpc-jira-import.json` and refuses to run again while that file exists — the same run-once guard as `create_balerica_vpc.sh`. **Never delete that file just to rerun.** Check Jira first.

```python
#!/usr/bin/env python3
"""BAM_7.6 — turn your VPC plan into a Jira backlog, as code.

Reads VPC_CIDR and SUBNETS from check_my_vpc.py (same folder), checks the plan,
then creates in your Jira space:
  1 Epic   "Build <region> VPC (<cidr>)"
  1 Task   for the VPC
  1 Task   for the Internet Gateway
  1 Task   per route table (one per tier: public, private1, private2, ...)
  1 Task   per subnet, with CIDR, mask, total, AWS-usable and usable range
Every Task gets the Epic as its Parent and the label "vpc-plan".

Install:   python3 -m pip install requests python-dotenv
Configure: the SAME .env you used for jira.py (JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN)
Run:
  python3 vpc_to_jira.py --project NET --region us-west-2 --dry-run   # prints only, creates nothing
  python3 vpc_to_jira.py --project NET --region us-west-2 --verify    # checks access, creates nothing
  python3 vpc_to_jira.py --project NET --region us-west-2             # creates the tickets (ONCE)

Run-once guard: every created key is saved to vpc-jira-import.json as it is
created. If that file exists, the script refuses to run again, so you can never
import the same plan twice. If it stops partway, the file shows how far it got.
"""

import argparse
import ipaddress
import json
import os
import sys
from urllib.parse import urlparse

STATE_FILE = "vpc-jira-import.json"
LABEL = "vpc-plan"
TIMEOUT_SECONDS = 15


# ---------- the plan -------------------------------------------------------

def load_plan():
    """Import the plan from check_my_vpc.py. Importing it also RUNS its checks:
    a plan that fails (overlaps, too few subnets...) stops here, before Jira."""
    try:
        import check_my_vpc  # noqa: WPS433 — prints the plan table, exits on failure
    except ModuleNotFoundError:
        sys.exit("STOP: check_my_vpc.py (BAM_7.1) must be in this folder.")
    return check_my_vpc.VPC_CIDR, check_my_vpc.SUBNETS


def tier_of(name):
    """'private1-a' -> 'private1', 'public-b' -> 'public'."""
    return name.split("-")[0].lower()


def build_items(region, vpc_cidr, subnets):
    """Return the epic and the list of child tasks, as plain dicts. No Jira calls."""
    vpc = ipaddress.ip_network(vpc_cidr)
    epic = {
        "summary": f"Build {region} VPC ({vpc})",
        "description": (
            f"Epic for my VPC plan in {region}.\n"
            f"VPC CIDR: {vpc} (mask {vpc.netmask}, {vpc.num_addresses:,} addresses).\n"
            f"Subnets: {len(subnets)}. Source: network_architecture file + check_my_vpc.py.\n"
            "Done when every child task is built in the console and verified."
        ),
    }
    tasks = [
        {"summary": f"[VPC] Create VPC {vpc} in {region}",
         "description": f"Create the VPC with CIDR {vpc} (mask {vpc.netmask}). "
                        "Enable DNS resolution and DNS hostnames. Done when it shows as Available."},
        {"summary": "[IGW] Create and attach the Internet Gateway",
         "description": "Create one Internet Gateway and attach it to the VPC. "
                        "Done when its state is Attached."},
    ]
    tiers = sorted({tier_of(n) for n in subnets})
    for tier in tiers:
        members = ", ".join(n for n in subnets if tier_of(n) == tier)
        routes = f"{vpc} -> local"
        if tier == "public":
            routes += " ; 0.0.0.0/0 -> Internet Gateway"
        tasks.append({
            "summary": f"[RT] Create {tier} route table",
            "description": f"Routes: {routes}.\nAssociate with: {members}.\n"
                           "Done when every listed subnet shows this route table.",
        })
    for name, cidr in subnets.items():
        net = ipaddress.ip_network(cidr)
        public = tier_of(name) == "public"
        tasks.append({
            "summary": f"[Subnet] {name} — {net}",
            "description": (
                f"Tier: {tier_of(name)}.\n"
                f"CIDR: {net}  Mask: {net.netmask}\n"
                f"Total addresses: {net.num_addresses}  AWS usable: {net.num_addresses - 5}\n"
                f"Usable range: {net[4]} - {net[-2]}\n"
                f"Auto-assign public IPv4: {'ON' if public else 'OFF'}.\n"
                "Pick the AZ from my network_architecture file. "
                "Done when the subnet exists with this CIDR and the right route table."
            ),
        })
    return epic, tasks


# ---------- Jira ------------------------------------------------------------

def adf(text):
    """Jira Cloud API v3 wants descriptions in Atlassian Document Format."""
    return {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", **({"content": [{"type": "text", "text": line}]} if line else {})}
        for line in str(text).splitlines() or [""]
    ]}


class Jira:
    def __init__(self, project):
        import requests  # imported here so --dry-run needs no packages
        from dotenv import load_dotenv
        load_dotenv()
        self.requests = requests
        self.site = os.getenv("JIRA_SITE_URL", "").rstrip("/")
        self.auth = (os.getenv("JIRA_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))
        self.project = project
        host = urlparse(self.site).hostname or ""
        if not host.endswith(".atlassian.net") or host.startswith("your-site"):
            sys.exit("STOP: set JIRA_SITE_URL in .env, e.g. https://your-site.atlassian.net")
        if not all(self.auth):
            sys.exit("STOP: set JIRA_EMAIL and JIRA_API_TOKEN in .env (never in this file).")

    def call(self, method, path, payload=None):
        try:
            r = self.requests.request(
                method, f"{self.site}/rest/api/3/{path}", auth=self.auth, json=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=TIMEOUT_SECONDS)
        except self.requests.RequestException as exc:
            sys.exit(f"STOP: cannot reach Jira: {exc}")
        if not r.ok:
            hint = {400: "Check the project key, and that this space has Epic and Task work types.",
                    401: "Check JIRA_EMAIL and JIRA_API_TOKEN.",
                    403: "Your token can't create work items in this space.",
                    404: "Check JIRA_SITE_URL and --project."}.get(r.status_code, "")
            # Error bodies can contain private data, so we don't print them.
            sys.exit(f"STOP: Jira HTTP {r.status_code}. {hint}")
        return r.json() if r.content else {}

    def verify(self):
        p = self.call("GET", f"project/{self.project}")
        return p.get("key"), p.get("name")

    def create(self, issue_type, item, parent=None):
        fields = {"project": {"key": self.project}, "summary": item["summary"][:255],
                  "description": adf(item["description"]),
                  "issuetype": {"name": issue_type}, "labels": [LABEL]}
        if parent:
            fields["parent"] = {"key": parent}
        key = self.call("POST", "issue", {"fields": fields}).get("key")
        if not key:
            sys.exit("STOP: Jira did not return a key.")
        return key


# ---------- main -------------------------------------------------------------

def save_state(state):
    with open(STATE_FILE, "w") as fh:
        json.dump(state, fh, indent=2)


def main():
    ap = argparse.ArgumentParser(description="Import your VPC plan into Jira (BAM_7.6)")
    ap.add_argument("--project", required=True, help="Jira space key, e.g. NET")
    ap.add_argument("--region", required=True, help="AWS region from your plan, e.g. us-west-2")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print the tickets, create nothing")
    mode.add_argument("--verify", action="store_true", help="check Jira access, create nothing")
    args = ap.parse_args()

    vpc_cidr, subnets = load_plan()
    epic, tasks = build_items(args.region, vpc_cidr, subnets)

    if args.dry_run:
        print(f"\nDRY RUN — would create in space {args.project}: 1 Epic + {len(tasks)} Tasks\n")
        print(f"EPIC  {epic['summary']}")
        for t in tasks:
            print(f"  └─ TASK  {t['summary']}")
        print("\nNothing was created.")
        return

    jira = Jira(args.project)
    if args.verify:
        key, name = jira.verify()
        print(f"\nJira OK — space {key} ({name}). Nothing was created.")
        return

    if os.path.exists(STATE_FILE):
        sys.exit(f"STOP: {STATE_FILE} already exists — this plan was already imported. "
                 "Check Jira before doing anything else. Never delete the file just to rerun.")
    jira.verify()  # fail fast before creating anything

    state = {"project": args.project, "region": args.region, "vpc_cidr": vpc_cidr,
             "epic": None, "tasks": []}
    save_state(state)
    state["epic"] = jira.create("Epic", epic)
    save_state(state)
    print(f"\nEPIC  {state['epic']}  {epic['summary']}")
    for t in tasks:
        key = jira.create("Task", t, parent=state["epic"])
        state["tasks"].append(key)
        save_state(state)
        print(f"  └─ {key}  {t['summary']}")
    print(f"\nCreated 1 Epic + {len(state['tasks'])} Tasks. Keys saved in {STATE_FILE}.")
    print(f"Open: {jira.site}/browse/{state['epic']}")


if __name__ == "__main__":
    main()
```

Your screenshot must show the time proof and the final run's output: the **epic key** and every **task key** it created, with your computer's clock visible.

In `lesson4_notes.md`, answer:

- Open one subnet task the script created. If you did BAM_7.2, compare it to the one you typed. Which is more accurate, and why?
- The script doesn't know your **AZs** or **story points**. Where in the code would you add AZs? (Name the function.)
- Why does the script save `vpc-jira-import.json` **after every ticket**, not once at the end?

> 🔒 Your Jira API token stays in `.env`. **Do not** put it in the script, commit `.env`, or paste it into an AI prompt. `vpc-jira-import.json` holds only ticket keys and is safe to commit.

### BAM_7.7 — Get ready for next week: runbook Steps 0–3

**Submission:** `BAM_7.7.jpg`

Do **Steps 0, 1, 2, and 3** of [`readme.md`](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lesson4_vpc/readme.md) on the machine you will use next week. These steps **create nothing in AWS**. They only check your tools and download and syntax-check the script.

```bash
whoami && date
aws --version
aws sts get-caller-identity
bash --version
bash -n create_balerica_vpc.sh && echo "SYNTAX OK"
```

Your screenshot must show the time proof, AWS CLI v2, your caller identity (**blur the account number** if you like), **Bash 4 or newer**, and `SYNTAX OK`, with your computer's clock visible.

**Stop after Step 3.** Do not run `bash create_balerica_vpc.sh` — we run it together in the next lab.

In `lesson4_notes.md`, write which row of the Step 0 table you are (Git Bash, macOS, Ubuntu, CloudShell…), and any problem you hit (old Mac Bash, CRLF line endings, `aws` not found) and how you fixed it.

### Extra credit evidence table

| Item | Requirement | Screenshot | Done? |
|------|-------------|------------|-------|
| BAM_7.1 | `check_my_vpc.py` prints `PLAN OK` for your plan; overlap test in notes | `screenshots/BAM_7.1.jpg` | Yes / No |
| BAM_7.2 | Jira backlog: 1 epic, 1 story per tier, 1 task per resource, all with story points | `screenshots/BAM_7.2a.jpg`, `screenshots/BAM_7.2b.jpg` | Yes / No |
| BAM_7.3 | Change request with seven headings, reviewed and approved by a classmate | `screenshots/BAM_7.3a.jpg`, `screenshots/BAM_7.3b.jpg` | Yes / No |
| BAM_7.4 | Private tiers added to your Section 5 VPC; Resource map shows all 9 subnets; deleted afterwards | `screenshots/BAM_7.4.jpg` | Yes / No |
| BAM_7.5 | Teardown ticket due 12/1, account checked, ticket Done | `screenshots/BAM_7.5.jpg` | Yes / No |
| BAM_7.6 | `vpc_to_jira.py` creates your epic + tasks in `SEIR-NetCode_YourNameHere`, run once | `screenshots/BAM_7.6.jpg` | Yes / No |
| BAM_7.7 | `readme.md` Steps 0–3: tools checked, `bash -n` passes | `screenshots/BAM_7.7.jpg` | Yes / No |

**Screenshot guidance:** Do not expose private keys, passwords, AWS access keys, secret keys, session tokens, Jira API tokens, `.env` contents, or other secrets in any screenshot.

---

## 11. Definition of done

 

> ⚠️⚠️⚠️ **WARNING: YOUR VPC USES YOUR BIRTH YEAR, NOT THEO'S 20** ⚠️⚠️⚠️
>
> 🚨 Your VPC is `10.1<last two digits of your birth year>.0.0/16` (born 1984 → `10.184.0.0/16`). A network architecture file — or EC2 screenshots — still using Theo's `10.20.x.x` **gets no credit.** 🚨
>
> 📅 Everything — required and extra credit — is due: **Tuesday, December 1, 2026, at 12:00 PM Eastern Time.**

 

**Required**
- [ ] I read Bahga section 2.6.
- [ ] I read all of `RFC_1918_Explanation.md`.
- [ ] I finished Maarek SAA Section 27 and its section quiz, and uploaded `Maarek_Section27_quiz.jpg`, showing my completed quiz results and my computer's clock with the date.
- [ ] I watched *Subnet Mask - Explained* and Professor Messer Network+ sections 1.6 and 1.7.
- [ ] My `network_architecture_YourNameHere.txt` is Theo's template with **every `20` replaced by `1` + my birth-year digits** (`10.1<YY>.0.0/16`), a **region** and **3 real AZs**, and **3 public + 6 private subnets**, one per tier in each AZ.
- [ ] My plan ends with a **"Why I designed it this way"** section of at least 5 sentences.
- [ ] I built **my** VPC from my design and completed the **class EC2 lab** in it: one instance in **each** of my three public subnets.
- [ ] I uploaded `public_subnet_a.jpg`, `public_subnet_b.jpg`, and `public_subnet_c.jpg`. Each shows `http://<Public IPv4 DNS>` in the address bar, the **class lab page on port 80** (private IP, AZ, VPC ID), and my computer's clock — with the **private IP inside the matching public subnet of my design**, and the **same VPC ID** on all three.
- [ ] My README has the **EC2 instance table** (Section 5.4) filled in, matching my screenshots.
- [ ] `lesson4_notes.md` explains, in at least 5 sentences, **how I put each EC2 in a different public subnet**.
- [ ] I **terminated all three instances**, checked Volumes and Elastic IPs, and deleted my VPC.
- [ ] I uploaded `binary_game_high_score.jpg`, showing my high score and my computer's clock with the date.
- [ ] My `subnetting_practice_YourNameHere.txt` answers **all 20 questions**, each with its **work shown**, and a `Fixed:` line for anything I got wrong on the first try.
- [ ] My `lesson4_vpc/README.md` has the evidence table, my high score, my first-try score on the practice, my CIDR and region, and the hardest part of the design.
- [ ] I committed and pushed everything to my GitHub repository by **Tuesday, December 1, 2026, 12:00 PM Eastern Time**.

**Extra credit**
- [ ] `BAM_7.1.jpg` — `check_my_vpc.py` prints `PLAN OK` for my plan.
- [ ] `BAM_7.2a.jpg` + `BAM_7.2b.jpg` — my Jira backlog, every story and task with story points; Jira items table in my notes.
- [ ] `BAM_7.3a.jpg` + `BAM_7.3b.jpg` — my CR, questioned and approved by a classmate; I reviewed a classmate's CR too.
- [ ] `BAM_7.4.jpg` — my full design (all 9 subnets) in the Resource map (after approval, if I did BAM_7.3), then deleted.
- [ ] `BAM_7.5.jpg` — teardown ticket due December 1, account checked, ticket Done.
- [ ] `BAM_7.6.jpg` — `vpc_to_jira.py` created my epic and tasks in `SEIR-NetCode_YourNameHere`, run once.
- [ ] `BAM_7.7.jpg` — `readme.md` Steps 0–3 complete; `bash -n` passes.
- [ ] No lab VPC, NAT gateway, or Elastic IP is left in my account, and no secrets (AWS keys, Jira token, `.env`) appear in any screenshot or commit.

> **Chewbacca's final assessment:** RRRRAAAWWWRRR! You turned numbers into binary, binary into masks, and masks into a network someone else could build from a text file. Extra credit crew: you also ticketed it, got it approved, built it, tore it down on schedule, and wrote the tickets with code. Next week, a script builds the network in two minutes — and you will know exactly what every line is doing.
