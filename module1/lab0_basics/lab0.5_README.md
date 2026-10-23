# SEIR Foundations — Module 1, Lab 0.5

## Basics Continued: Catch Up, Find Your Team, Prove Your Work

**Course:** SEIR Foundations  
**Lab:** Module 1 / Lab 0.5 — Basics, Continued  
**Difficulty:** Beginner  
**Format:** Individual homework + group formation + optional extra credit  
**Homework deadline:** **Tuesday, October 27, 2026, at 12:00 PM Central Time** (1:00 PM Eastern / 10:00 AM Pacific / 5:00 PM London)  
**Submission methods:** Send to the SEIR Foundations FB chat, or to Theo via FB DM or email  
**Reference course:** Stéphane Maarek's AWS Udemy course

> **Chewbacca's message:** RRRRAAAWWWRRR! Fix your repo. Find your squad. Read the books. Take the quizzes. Then SSH in like you mean it.

---

## 1. Purpose

**Minimal homework is assigned this week so you can catch up.** Use the time to get your repo, your group, and your quizzes in order.

Lab 0 got you your first EC2 win. Lab 0.5 builds the foundation around it:

- **Set up your homework repo** in Theo's required format.
- **Form a team** you will work with for the rest of the course.
- **Read and watch** the core material on AWS, EC2, and Git.
- **Prove progress** with Maarek quiz screenshots uploaded to GitHub.
- **(Optional)** Earn extra credit by connecting to EC2 from your own machine, customizing a web page, and inspecting the User Data script.

&nbsp;

> ⚠️⚠️⚠️ **WARNING: THE GROUP FILE IS MANDATORY** ⚠️⚠️⚠️
>
> 🚨 No group file, or a group file with empty values, is an **AUTOMATIC FAILURE FOR THIS WEEK**. 🚨
>
> ❌ No exceptions. Finish the reading and videos all you want — without a completed `group_YourNameHere.txt`, you fail the week.

&nbsp;

## 2. General — homework repo setup (required)

Create a **homework submission GitHub repo** following Theo's given format and naming convention.

- If your existing homework did **not** follow the format correctly, move it into the new repo now.
- Use this as your reference: [Aaron's example HW Repo](https://github.com/aaron-dm-mcdonald/seir-foundations-homework)

### Folder structure

```
seir-foundations-homework/
└── module1/
    ├── lab0_basics/
    └── lab0.5_basics_contd/
        ├── README.md
        ├── group_YourNameHere.txt
        └── screenshots/
            ├── Maarek_Section5_quiz.jpg
            ├── Maarek_Section6_quiz.jpg
            ├── Maarek_Section7_quiz.jpg
            ├── Maarek_Section8_quiz.jpg
            ├── BAM_1.1.jpg      (extra credit)
            ├── BAM_1.2.jpg      (extra credit)
            └── BAM_1.3.jpg      (extra credit)
```

## 3. General — find a group (required)

Verify that you have found a group and completed the other assignments below. Full details: [Lab 0.5 Readme](https://github.com/BalericaAI/SEIR-Foundations/blob/main/module1/lab0_basics/lab0.5_README.md)

Upload a file named **`group_YourNameHere.txt`** to your repo (replace `YourNameHere` with your name).

The file must contain the following, **fully completed**:

```
Spotter = ?
Teammates = ?
Days + Times when your team meets = ?
```

Example:

```
Spotter = Jane Doe
Teammates = Jane Doe, John Smith, Alex Lee
Days + Times when your team meets = Mon & Wed, 7:00–8:30 PM ET
```

| Requirement                     | Result if missing                  |
|---------------------------------|------------------------------------|
| `group_YourNameHere.txt` exists | **Automatic failure** for the week |
| All three values filled in      | **Automatic failure** for the week |

## 4. Reading

| Source                         | Assignment                    |
|--------------------------------|-------------------------------|
| Bahga (see Resources)          | Pages **25–53** and **69–80** |
| SAA Exam Guide (see Resources) | Chapters **1** and **4**      |
| AWS Developer (see Resources)  | Chapters **2** and **5**      |

## 5. Videos

### Udemy — Stéphane Maarek (see Resources)

> **Already watched these sections last week?** No need to repeat the videos — just do the quizzes.

| Section   | Deliverable                                                                            |
|-----------|----------------------------------------------------------------------------------------|
| Section 3 | **No quiz** for this section — no screenshot needed                                    |
| Section 5 | Screenshot of the **completed Section 5 quiz**, uploaded as `Maarek_Section5_quiz.jpg` |
| Section 6 | Screenshot of the **completed Section 6 quiz**, uploaded as `Maarek_Section6_quiz.jpg` |
| Section 7 | Screenshot of the **completed Section 7 quiz**, uploaded as `Maarek_Section7_quiz.jpg` |
| Section 8 | Screenshot of the **completed Section 8 quiz**, uploaded as `Maarek_Section8_quiz.jpg` |

### YouTube

**EC2**
- [EC2 Instance Types | Your Ultimate Guide for AWS Certification!](https://youtu.be/NLcWdF3x0mw?si=9LXVWc3Q1ZwiijXp)

**Git**
- [Git Bash, Bash Basics](https://www.youtube.com/watch?v=oQc-2gsjgDg&pp=ygUUZ2l0IGJhc2ggd2Fsa3Rocm91Z2g%3D)
- [Git Tutorial for Beginners: Learn Git in 1 Hour](https://www.youtube.com/watch?v=8JJ101D3knE&pp=ygUUZ2l0IGJhc2ggd2Fsa3Rocm91Z2g%3D)

## 6. "Be A Man" (BAM) extra credit

Submit a screenshot for each item below.

### BAM_1.1 — SSH from your own machine
**Submission:** `BAM_1.1.jpg`

- Successfully connect to an EC2 instance using an **SSH client on your own machine**.
- **EC2 Instance Connect does not count** for credit.
- The screenshot must show the commands **`whoami`** and **`date`** entered in the terminal.

### BAM_1.2 — Customized EC2 web page
**Submission:** `BAM_1.2.jpg`

Customize the web page served by your EC2 instance to show all of the following:

1. > I, *[Your Name]*, Thank Theo And *[Spotter's Name]*, for helping me learn about EC2s in AWS. One step closer to a new world of opportunities!
2. > "With This Class, I Will Net *[Dollar Amount]* Per Year!"
3. A **picture of the destination** you will go to after making Cloud Money and paying your bills.

### BAM_1.3 — Find the User Data script
**Submission:** `BAM_1.3.jpg`

- Using a **local SSH connection from your machine at home**, connect to the running EC2 instance from BAM_1.2.
- Locate the **`user_data`** script on the instance and display its contents in the terminal.
- To display the text in a file:

```
cat <file name>
```

### Extra credit evidence table

| Item    | Requirement                                        | Screenshot                | Done?    |
|---------|----------------------------------------------------|---------------------------|----------|
| BAM_1.1 | Local SSH client; `whoami` + `date` visible        | `screenshots/BAM_1.1.jpg` | Yes / No |
| BAM_1.2 | Custom page: thank-you line, dollar line, picture  | `screenshots/BAM_1.2.jpg` | Yes / No |
| BAM_1.3 | Local SSH; `user_data` script displayed with `cat` | `screenshots/BAM_1.3.jpg` | Yes / No |

**Screenshot guidance:** Do not expose private keys, passwords, AWS access keys, tokens, or other secrets in any screenshot.

## 7. Definition of done

&nbsp;

> ⚠️⚠️⚠️ **WARNING: THE GROUP FILE IS MANDATORY** ⚠️⚠️⚠️
>
> 🚨 No group file, or a group file with empty values, is an **AUTOMATIC FAILURE FOR THIS WEEK**. 🚨
>
> ❌ No exceptions. Finish the reading and videos all you want — without a completed `group_YourNameHere.txt`, you fail the week.

&nbsp;

**Required**
- [ ] I found a spotter and formed a group to weather the storm.
- [ ] I uploaded `group_YourNameHere.txt` with Spotter, Teammates, and meeting Days + Times all filled in.
- [ ] My homework repo follows Theo's format and naming convention, and my earlier homework has been moved into it.
- [ ] I completed the Bahga, SAA Exam Guide, and AWS Developer readings.
- [ ] I watched Maarek Section 3 (no quiz).
- [ ] I completed the Maarek Section 5, 6, 7, and 8 quizzes and uploaded `Maarek_Section5_quiz.jpg`, `Maarek_Section6_quiz.jpg`, `Maarek_Section7_quiz.jpg`, and `Maarek_Section8_quiz.jpg`.
- [ ] I watched the EC2 and Git YouTube videos.
- [ ] I committed and pushed everything to my GitHub repository by **Tuesday, October 27, 2026, 12:00 PM Central Time**.

**Extra credit**
- [ ] `BAM_1.1.jpg` — local SSH session showing `whoami` and `date`.
- [ ] `BAM_1.2.jpg` — customized EC2 web page.
- [ ] `BAM_1.3.jpg` — `user_data` script displayed over local SSH.
- [ ] I terminated unused EC2 instances and checked for leftover billable resources.

> **Chewbacca's final assessment:** RRRRAAAWWWRRR! A clean repo, a team, a stack of reading, four quizzes, and an SSH session from your own keyboard. That's how cloud careers start.
