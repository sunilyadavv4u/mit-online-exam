# Teacher Quick-Start Guide

> A 10-minute walkthrough for teachers. For the full guide, see [`user-guide.md`](./user-guide.md).

---

## 1. Login

Use the credentials provided by your admin, or self-register and pick **Teacher** as your role.

---

## 2. Create a Subject (one-time)

Sidebar → **Subjects** → **+ New subject**

Fill:
- **Name** (e.g. "Python")
- **Code** (e.g. `PY101`)
- **Icon** (an emoji works: 🐍)
- **Description**

> Demo data already includes 15 subjects (Python, PySpark, SQL, Azure Databricks, …). Skip this if you're using the seeded data.

---

## 3. Create an Exam

Sidebar → **Exams** → **+ New exam**

Fill the basics:
- **Title** — e.g. *Python Fundamentals — Mid-term*
- **Subject** — pick from the dropdown
- **Duration** — minutes
- **Total marks** / **Passing marks**
- **Negative marking** — optional, e.g. `0.25`
- **Start time** / **End time** — define the exam window
- **Description / Instructions** — shown before students start

Toggle as desired:
- **Randomize questions / options**
- **Show objective score immediately**
- **Allow retake**
- **Enable proctoring** (recommended for graded exams)

Click **Save**. You'll stay on the exam editor with a new **Questions** section unlocked.

---

## 4. Add Questions

Click **+ Add question**. The modal opens.

### Common fields
- Question text
- Type (Single / Multi MCQ, True/False, Fill blank, Descriptive, Coding)
- Difficulty (Easy / Medium / Hard)
- Marks + Negative marks

### Type-specific fields

#### MCQs (single / multi / true-false)
Add 2+ options. Mark which one(s) are correct.

#### Fill in the blank
Type the **expected answer** in the *Correct answer (text)* box. Match is case-insensitive, trims whitespace.

#### Descriptive
No extra config — you'll grade these manually after submission.

#### Coding
- **Language** — Python / SQL / PySpark / Java
- **Starter code** — shown in the student's editor
- **Test cases** — at least one. Mark some as **Hidden** so students can't see them. Each test case has a `weight` for partial credit.

Click **Save**. Repeat for as many questions as you need.

---

## 5. Enroll students

In the exam editor, click **Enroll students** (top-right).

Either:
- Tick individual students → **Enroll selected**, or
- Click **Enroll all active students** to bulk-add everyone

Only enrolled students can see and attempt your exam.

---

## 6. Publish the exam

Use the **Status** dropdown next to *Save*:
- **Draft** → invisible to students
- **Scheduled** → visible but not yet startable
- **Live** → students can attempt (within the time window)
- **Completed** → locked; no new attempts
- **Archived** → hidden from listings

A typical flow: **Draft → (final review) → Live**.

---

## 7. Evaluate descriptive / coding answers

When students submit answers that contain descriptive or coding questions, an evaluation is auto-created in **Draft**.

1. Sidebar → **Evaluations**
2. Click **Evaluate** on a row
3. For each descriptive/coding answer:
   - Read the answer (text or code)
   - Enter **Marks** (≤ max) and an optional **Comment**
   - Click **Save**
   - Or click **AI suggest marks** to get a Databricks Llama-4 suggestion (you stay in control of the final mark)
4. When done, click **Publish result** at the top.

Publishing:
- Sets the attempt status to **Published**
- Automatically computes pass/fail based on the exam's passing marks
- Sends an **email + in-app notification** to the student
- Reveals all of your comments to the student

---

## 8. Reports

Sidebar → **Reports**:
- **Export CSV** of all attempts (or filter by exam)
- **Export Excel** with separate columns for objective, descriptive, total
- **PDF result** per attempt — linked from the result page

---

## 9. Common things you'll need

| Want to | Where |
|---|---|
| See dashboard charts | Sidebar → **Dashboard** |
| Browse students | Sidebar → **Students** |
| See overall leaderboard | Sidebar → **Leaderboard** |
| Re-use an existing question | Sidebar → **Question Bank** |
| Use AI code assistant | Sidebar → **AI Assistant** |
| See the API docs | `https://<your-host>/api/docs/` |

---

## 10. Tips

- **Always preview** as a student. Login with `student1@mewatitech.edu` (`Student@12345`) in an incognito window after enrolling them.
- **Set a buffer** between exam end_time and your evaluation start — students sometimes submit at the last second.
- **Use AI suggestions sparingly.** They're great as a sanity check, but the final grade and comment are *your* call.
- **Use comments generously.** Students learn fastest when feedback is specific.

---

## Need help?

- See the full guide: [`user-guide.md`](./user-guide.md)
- Bottom-of-the-screen banner: avatar → **Profile** to update your details

> _Thank you for teaching!_
