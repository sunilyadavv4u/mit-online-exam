# Mewati Institute of Technology — Online Examination Platform
## Complete User Guide

> **Version:** 1.0  
> **Audience:** Students, Teachers, Super Admins, IT staff  
> **Platform:** Web (Chrome, Edge, Firefox, Safari) — desktop & mobile

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started — First Time Setup](#2-getting-started--first-time-setup)
3. [Logging In](#3-logging-in)
4. [Demo Accounts](#4-demo-accounts)
5. [User Guide for Students](#5-user-guide-for-students)
6. [User Guide for Teachers](#6-user-guide-for-teachers)
7. [User Guide for Super Admins](#7-user-guide-for-super-admins)
8. [The AI Code Assistant](#8-the-ai-code-assistant)
9. [Notifications & Email](#9-notifications--email)
10. [Browser & Device Requirements](#10-browser--device-requirements)
11. [Anti-Cheating Rules (For Students)](#11-anti-cheating-rules-for-students)
12. [Frequently Asked Questions](#12-frequently-asked-questions)
13. [Troubleshooting](#13-troubleshooting)
14. [Glossary](#14-glossary)
15. [Support](#15-support)

---

## 1. Introduction

The **Mewati Institute of Technology Online Examination Platform** is a free, secure, browser-based exam system for our NGO learners. It supports:

- 6 question types — single MCQ, multiple MCQ, true/false, fill-in-the-blank, descriptive, and live coding
- Auto-grading for objective questions, manual grading for descriptive answers
- Real-time anti-cheating (fullscreen, tab tracking, auto-submit on time-up)
- An AI code assistant that converts SQL ↔ PySpark ↔ Python ↔ Spark SQL
- Detailed analytics, leaderboards, downloadable reports

This guide walks each user role through every feature, step by step.

---

## 2. Getting Started — First Time Setup

You only need a modern web browser and an internet connection. Nothing to install.

### What you'll need
| Requirement | Recommended |
|---|---|
| Browser | Chrome 110+, Edge 110+, Firefox 110+, Safari 16+ |
| Screen | 1280×720 or larger (works on phones for results / dashboards) |
| Internet | Stable connection (≥ 1 Mbps) |
| Allow | JavaScript, cookies, fullscreen permission |

### Open the platform
Visit the URL provided by your institute, e.g.:
```
http://localhost:3000        (development)
https://exams.mewatitech.edu (production)
```

You'll see the public landing page with an overview and a **Login / Sign up** button at the top right.

---

## 3. Logging In

### Sign up (new students or teachers)

1. Click **Sign up** at the top right.
2. Fill in your details — name, email, password.
3. Choose your role: **Student** or **Teacher**.
4. Click **Create account**. You'll be auto-logged in.
5. (Optional) Click the verification link in your email when convenient. Some features (e.g. password reset) require a verified email.

> **Note:** Super Admin accounts are *not* created via the public sign-up. They're created by IT either through the Django admin or via the seed script.

### Login (existing user)

1. Click **Login** at the top right.
2. Enter your email + password.
3. Click **Login**.
4. You'll land on a role-specific dashboard.

### Forgot password

1. On the login page, click **Forgot password?**
2. Enter your email.
3. Open your inbox — click the reset link (valid for 1 hour).
4. Set a new password and log in.

### Logout

In the top-right header, click your **avatar / name** → **Logout**.

---

## 4. Demo Accounts

Use these for testing or training (created by `python manage.py seed_demo_data`).

| Role | Email | Password |
|---|---|---|
| Super Admin | `admin@mewatitech.edu` | `Admin@12345` |
| Teacher | `teacher@mewatitech.edu` | `Teacher@12345` |
| Student #1…#15 | `student1@mewatitech.edu` … `student15@mewatitech.edu` | `Student@12345` |

> **Important:** Change these passwords on production.

---

## 5. User Guide for Students

### 5.1 The Student Dashboard

After logging in, you land on `/dashboard`. You'll see:

- **4 stat cards** — upcoming exams, completed, passed, average score
- **Upcoming exams panel** — your next exams, click any to open
- **Recent results** — your last 5 published results

### 5.2 Browsing your exams

Click **My Exams** in the left sidebar (or `/exams`).

You see one card per exam you're enrolled in, showing:
- Subject (Python, SQL, PySpark, …)
- Title
- Status: **Live**, **Scheduled**, **Completed**
- Duration (minutes)
- Time window (start → end)
- Total marks / passing marks
- Whether the exam is **Proctored** (fullscreen + tab tracking)

### 5.3 Starting an exam

1. On a Live exam card, click **Start exam**.
2. The browser will request **fullscreen** — accept it.
3. The timer in the top-right starts counting down from the exam's duration.
4. Your questions appear one at a time, with the **question palette** in the left sidebar showing how many you've answered.

> **Once you click Start exam, the timer is running.** Even if you close the browser, the timer keeps ticking on the server.

### 5.4 Answering each question type

Each question shows:
- The question number out of total (e.g. *Question 3 of 5*)
- Question type (MCQ, descriptive, coding, …)
- Marks for the question
- The question text and (optionally) an image

#### Single Choice MCQ
- Click the radio button next to your chosen option.

#### Multiple Choice MCQ
- Click the checkbox for *every* correct option (partial credit may apply).

#### True / False
- Pick True or False.

#### Fill in the Blank
- Type your answer in the input box. Spelling matters but case doesn't.

#### Descriptive (Written)
- Use the large text area to type your answer.
- Use Enter for paragraphs.
- Your answer auto-saves when you navigate, and on **Save answer** clicks.

#### Coding
- Choose your language (preset by the teacher).
- Write code in the **Monaco editor** (same editor used by VS Code).
- Click **Run sample tests** to check your code against the visible test cases.
- Hidden test cases are evaluated only when you submit (or when teacher grades).
- Copy / paste *is* allowed inside the code editor.

### 5.5 Navigating between questions

Three ways to move between questions:

1. Click any number in the **question palette** on the left.
2. Click **Previous** / **Next** at the bottom of the question.
3. Click **Save answer** explicitly (also auto-saves on navigation).

The palette uses colors to guide you:
- **Blue** — current question
- **Green** — answered
- **Gray** — not yet answered

### 5.6 Submitting the exam

You can submit two ways:
- **Manual** — click **Submit** in the top right.
- **Automatic** — when the timer hits zero, the exam submits automatically. Don't worry, your last saved answer is captured.

After submit:
- Objective answers are auto-graded immediately.
- Descriptive and coding answers wait for teacher evaluation.
- You're redirected to a partial result page.

### 5.7 Viewing results

Click **My Results** in the sidebar.

Each row shows:
- Exam title and subject
- Submission date
- Total score (out of total marks)
- Status: **Awaiting evaluation**, **Passed**, **Not passed**

Click a row to open the **detailed result page**:
- 4 stat tiles: total / objective / descriptive / status
- Question-by-question breakdown showing your answer, the correct/wrong indicator, and the **teacher's comment** (after the teacher publishes)
- **Download PDF** button — generates a nicely formatted result certificate

### 5.8 Leaderboard

Click **Leaderboard** in the sidebar to see the top 50 performers, optionally filtered by exam. Top 3 get medal icons.

### 5.9 Updating your profile

Click your avatar → **Profile**. You can update:
- First / last name
- Phone
- Bio
- (Email is read-only — contact admin to change)

To change your password: avatar → **Settings** → enter old + new password.

---

## 6. User Guide for Teachers

### 6.1 Teacher Dashboard

`/dashboard` shows:
- 4 stat cards: total students, total exams, active exams, pending evaluations
- **Submissions in last 7 days** chart
- Pass percentage and average score
- List of upcoming exams

### 6.2 Subjects

Subjects are reusable categories (Python, SQL, PySpark, …).

#### Creating a subject

1. Sidebar → **Subjects** → **+ New subject**.
2. Fill: name, code (unique short code like `PY101`), icon (an emoji works well 🐍), description.
3. Save.

#### Editing / disabling a subject

Click the pencil icon on a subject card. Toggle **Active** off to hide it from new exams.

> The seeded data already provides 15 subjects covering Python, PySpark, SQL, Azure Databricks, SQL Server, Azure Data Factory, Microsoft Fabric, Synapse, Data Lake Gen2, Event Hubs, Spark Streaming, Data Engineering, Architect Designing, DSA, and Java.

### 6.3 Creating an exam

Sidebar → **Exams** → **+ New exam**.

#### Step 1 — Basic info
- **Title** (required)
- **Subject** (pick one)
- **Exam type**: Mixed (default), Objective, Descriptive, Coding
- **Duration** in minutes
- **Total marks** and **Passing marks**
- **Negative marking** (e.g. `0.25` for ¼ deduction per wrong objective answer)
- **Start time** and **End time**

#### Step 2 — Description & instructions

These display to students before they start. Be clear about expected behavior, allowed resources, etc.

#### Step 3 — Toggles

| Toggle | Effect |
|---|---|
| **Randomize questions** | Each student sees a different question order |
| **Randomize options** | Options inside each MCQ are shuffled per student |
| **Show objective score immediately** | Reveals the auto-graded portion right after submit |
| **Allow retake** | Students can attempt the exam more than once |
| **Enable proctoring** | Forces fullscreen + tracks tab switches and right-click |

#### Step 4 — Save

Click **Save**. The slug is auto-generated. You can now add questions.

### 6.4 Adding questions

In the exam editor, scroll to **Questions**. Click **+ Add question**.

A modal opens. Fill:
- **Question text**
- **Type** (any of the 6)
- **Difficulty** (easy / medium / hard) — used in analytics
- **Marks** and **Negative marks** (if you want per-question negative grading)
- Type-specific fields (see below)

#### MCQ (single / multiple)
Add 2 or more options. For single-choice, only one option may be marked correct. For multi-choice, mark all correct ones.

#### True / False
Auto-populated with two options. Mark the correct one.

#### Fill in the Blank
Type the **expected answer** in the *Correct answer (text)* field. Matching is case-insensitive and trims whitespace.

#### Descriptive
No extra config. Use the **comment field** during evaluation to give feedback.

#### Coding
- **Language**: Python / SQL / PySpark / Java
- **Starter code**: shown to students in the editor
- **Expected output** (reference for graders)
- **Test cases** (input + expected output, marked **Hidden** if students should not see them, with a weight)

Save. The question list updates instantly.

### 6.5 Enrolling students

In the exam editor click **Enroll students**.

Two options:
- Tick individual students → **Enroll selected (N)**
- Click **Enroll all active students** to bulk-add everyone

Only enrolled students see the exam in their dashboard.

### 6.6 Publishing the exam

In the exam editor, the **Status** dropdown next to *Save* lets you transition through:
- **Draft** — not visible to students
- **Scheduled** — visible but not yet startable
- **Live** — students can attempt it (subject to start_time / end_time)
- **Completed** — locked; no new attempts
- **Archived** — hidden from listings

Tip: keep an exam in **Scheduled** while you finalize questions, then flip to **Live** at the start time.

### 6.7 Manual evaluation workflow

When students submit descriptive or coding answers, an **Evaluation** record is auto-created in **Draft** state.

1. Sidebar → **Evaluations** to see the queue (with student name, exam, auto score).
2. Click **Evaluate** on a row.
3. The evaluation page shows every answer, grouped by question.
4. For each descriptive / coding answer:
   - Read the answer (text, code, or attached file)
   - Enter **Marks** (≤ the question's max marks)
   - Optionally write a **Comment** for the student
   - Click **Save**
   - Or click **AI suggest marks** — sends the answer + max marks to the Databricks Llama-4 model and pre-fills suggested marks (you stay in control)
5. When you're done, click **Publish result** at the top.

Publishing triggers:
- The student's status flips to **Published** with passed/failed flag
- An **email + in-app notification** to the student
- Comments and final marks become visible to the student

> Until you click **Publish**, the student only sees *Awaiting evaluation*.

### 6.8 Reusing the question bank

`/question-bank` lists every question that has `is_in_bank=True`. You can filter by type, search by text or tags. The bank is shared across all teachers — anyone can browse, but only the original creator can edit.

When creating a new exam, you can add questions from scratch, but in a future enhancement you'll also be able to clone bank questions.

### 6.9 Reports

Sidebar → **Reports** lets you export:
- **CSV** of all attempts (or filtered by exam)
- **Excel** spreadsheet with separate columns for objective, descriptive, total
- **PDF** result certificate per attempt (linked from the result detail page)

These are delivered as direct downloads from your browser.

### 6.10 Viewing students

Sidebar → **Students** lists all active students with their enrollment IDs. Search by name or email. Students with `is_active=False` (disabled by an admin) are excluded.

---

## 7. User Guide for Super Admins

A Super Admin sees everything a Teacher sees, *plus* the admin-only sections.

### 7.1 System overview

`/dashboard` shows:
- Total users, active users
- Pie chart of users by role
- Total attempts across the platform
- Live exams count
- Registrations in the last 30 days

### 7.2 User management

`/users` lets you:
- Search by name / email / role
- Change a user's role (super_admin / teacher / student) inline
- Enable / disable accounts (a disabled student cannot log in)
- See email verification status

### 7.3 Audit logs

Every state-changing API request (`POST`, `PUT`, `PATCH`, `DELETE`) is logged with:
- Timestamp
- User and IP address
- HTTP method + path
- Response status code

`/audit-logs` shows the last 100 entries (paginated). Use this for forensics during a contested exam.

### 7.4 System info

`/system` lists configured backend / frontend / DB / AI / cache and gives quick links to:
- Django admin (`/admin/`)
- Swagger UI (`/api/docs/`)
- Redoc (`/api/redoc/`)
- Raw OpenAPI schema (`/api/schema/`)

### 7.5 Django admin

For low-level data fixes (e.g., editing a single answer), open the Django admin at `/admin/`. You can manage:
- Users + profiles
- Subjects, exams, enrollments
- Questions, options, test cases
- Attempts, answers, proctor events
- Evaluations
- Notifications
- AI requests
- Audit logs
- Password reset tokens

> Use the Django admin sparingly — every action there bypasses application-level validation.

---

## 8. The AI Code Assistant

The platform integrates with **Databricks Model Serving (Llama-4 Maverick)** to help students learn faster and teachers grade smarter.

Open it from the sidebar: **AI Assistant** (`/ai-assistant`).

### 8.1 Available conversions

| Mode | What it does |
|---|---|
| **SQL → Spark SQL** | Wraps your SQL in `spark.sql('''...''')` the way Databricks notebooks expect. |
| **SQL → PySpark** | Converts SELECT/WHERE/JOIN to the equivalent PySpark DataFrame API. |
| **Python → PySpark** | Translates pandas / vanilla Python data wrangling to PySpark. |
| **Explain code** | Returns a beginner-friendly explanation in English. |

### 8.2 How to use it

1. Pick a mode card at the top.
2. Edit the input editor on the left (it ships with a sample SQL query).
3. Click **Convert**.
4. The output appears on the right within seconds.
5. Click **Copy** to copy it to your clipboard.

### 8.3 AI in evaluations (teachers only)

While grading a descriptive or coding answer, you'll see an **AI suggest marks** button. It sends the question + answer + max-marks to the Databricks endpoint and pre-fills a suggested score. **The final mark is always set by you** — the AI never publishes anything on its own.

### 8.4 History

Every AI request is logged per user. The endpoint `GET /api/v1/ai/history/` returns your last 200 calls with prompt, response, latency and success status. (No UI page yet — visible via Swagger.)

---

## 9. Notifications & Email

### In-app notifications

The bell icon in the top bar shows unread count. Click it (or open `/notifications`) to see:
- **Result published** — appears whenever a teacher publishes your result
- **Exam reminder** — sent before scheduled exams (when Celery beat is running)
- **Evaluation pending** — for teachers, when a new attempt needs grading
- **System** — global announcements

Click **Mark all read** to clear the unread badge.

### Email notifications

Email is sent on:
- New account registration (verification link)
- Forgot password (reset link, valid 1 hour)
- Result publication

In development, emails are printed to the Django console. In production, configure `EMAIL_*` settings in `backend/.env`.

---

## 10. Browser & Device Requirements

### Recommended

- **Browser:** Latest Chrome, Edge, Firefox, or Safari
- **Screen:** 1280×720 minimum for the exam page (the exam UI is laptop-first)
- **Phones / tablets:** Dashboards and results work fine; the exam attempt page is best on a laptop because of the code editor and proctoring

### Required browser features

- JavaScript enabled
- Cookies and `localStorage` enabled (used for JWT)
- Fullscreen API support
- WebSocket *not* required (the platform is REST-only today)

### Disabling browser extensions

Strongly recommended during exams:
- Ad blockers (can interfere with our security headers)
- Translation extensions (can rewrite question text)
- Auto-fill / form-filler extensions

---

## 11. Anti-Cheating Rules (For Students)

When **Enable proctoring** is on for an exam, the following are tracked **per-attempt**:

| Event | Tracked | Counted in stats |
|---|---|---|
| Tab / window switch | Yes | `tab_switch_count` |
| Exiting fullscreen | Yes | `fullscreen_exit_count` |
| Right-click | Yes | logged only |
| Copy / paste outside the code editor | Yes | logged only |
| Dev-tools shortcut attempts | Yes | logged only |
| Auto-submit on timer expiry | Yes | sets `status=auto_submitted` |

> **Cheating is logged immediately and reviewable by your teacher and the super admin.** Repeat offenders may have attempts invalidated.

### Best practices

- Close other tabs *before* clicking **Start exam**.
- Disable browser notifications (Settings → Notifications → block while testing).
- Don't unplug your laptop or let it sleep mid-exam.
- If you're disconnected, reload the page — your saved answers and remaining time are intact.

---

## 12. Frequently Asked Questions

### General

**Q. Is the platform really free?**  
Yes — it's run as part of our NGO programme. There are no fees for students or teachers.

**Q. Do I need to install anything?**  
No. Everything runs in your browser.

**Q. Can I take an exam on a phone?**  
Technically yes, but for coding questions a laptop is strongly recommended.

### For students

**Q. I lost connection mid-exam. What happens?**  
Your last saved answer is on the server, and the timer keeps running. Just reload the page within the time window and continue.

**Q. Can I retake an exam?**  
Only if your teacher enabled retakes for it.

**Q. Why don't I see my descriptive marks immediately?**  
Descriptive answers are graded by your teacher. You'll see them as soon as the result is **Published** (and you'll get a notification + email).

**Q. Can I copy / paste in the code editor?**  
Yes, inside the Monaco code editor only. Copy/paste outside the editor (into MCQ inputs, etc.) is logged.

### For teachers

**Q. Can I edit a question after some students have already attempted?**  
You can, but it's strongly discouraged — already-graded answers won't be re-graded. Prefer creating a new question.

**Q. How do I bulk-import questions?**  
The Django admin lets you import from JSON / CSV via the standard `loaddata` mechanism. A future UI tool is on the roadmap.

**Q. Can the AI auto-publish results?**  
No — the AI only *suggests* marks. You must explicitly click **Publish**.

**Q. How do I extend an exam window?**  
Open the exam editor → change **End time** → Save. Currently active attempts will respect the new end time on their next save.

### For admins

**Q. How do I create another super admin?**  
Either run `python manage.py createsuperuser` in the backend, or set an existing user's role to `super_admin` from `/users`.

**Q. Where are emails sent in development?**  
To the Django console (you'll see them in the terminal where `runserver` is running).

---

## 13. Troubleshooting

### Login

| Symptom | Likely cause | Fix |
|---|---|---|
| "Invalid credentials" on a known good password | Caps Lock, wrong env, account disabled | Check Caps Lock; ask admin to re-enable account |
| Stuck on "Logging in…" | Backend is unreachable | Check that the Django server / Render service is up |
| "User account is disabled" | `is_active=False` | Ask super-admin to re-enable in `/users` |

### Exam start

| Symptom | Likely cause | Fix |
|---|---|---|
| "Exam is not open for attempts" | Status is Draft / outside time window | Wait for live window or ask teacher |
| "You are not enrolled in this exam" | Teacher hasn't enrolled you | Ask teacher to enroll you |
| Browser blocks fullscreen | Permission denied earlier | Click the URL bar's lock → reset permission, refresh |

### During the exam

| Symptom | Cause | Fix |
|---|---|---|
| Timer disagrees with my watch | Server-authoritative timer based on `started_at` | Trust the on-screen timer |
| Code editor is blank | Slow CDN for Monaco | Wait 2–5 seconds, or refresh once |
| Can't paste into the code editor | Browser blocked clipboard read | Allow clipboard for the site; or use Ctrl+Shift+V |
| Saved my answer, then dropped | Connection blip | Reload — saved answers come back via the attempt detail |

### Results

| Symptom | Cause | Fix |
|---|---|---|
| "Awaiting evaluation" forever | Teacher hasn't published | Politely ping your teacher |
| "PDF download failed" | ReportLab error | Ask admin to check `/api/v1/analytics/reports/attempt-pdf/{id}/` directly |
| Notification email never arrived | Wrong / missing SMTP config | Admin checks `EMAIL_*` in `.env` |

### Admin

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'django'` when running `manage.py` | Wrong shell or virtualenv not activated | See the README — use `.\.venv\Scripts\activate.bat` for `cmd.exe`, `Activate.ps1` for PowerShell |
| Redis errors flooding the log | Redis is offline | Either start Redis or empty `REDIS_URL` in `.env` |
| AI returns 502 | `DATABRICKS_*` env vars missing or token rotated | Update `.env` and restart |

---

## 14. Glossary

- **Attempt** — A single instance of a student starting an exam. Multiple attempts allowed only if the exam permits retakes.
- **Auto-submit** — System submits the exam when the timer hits zero or the connection / browser is force-closed.
- **Audit log** — Server-side log of every state-changing API call (super-admin readable).
- **Descriptive question** — A free-text answer that requires manual grading.
- **Enrollment** — A teacher's assignment of a student to an exam.
- **Evaluation** — The teacher's review record (one-to-one with an attempt) where they grade descriptive/coding answers and publish the result.
- **JWT** — JSON Web Token. The platform issues a short-lived **access** token plus a longer-lived **refresh** token.
- **MCQ** — Multiple-choice question (single or multiple).
- **Negative marking** — Marks deducted for incorrect objective answers.
- **Proctoring** — Browser-side anti-cheating: fullscreen, tab tracking, etc.
- **Published** — Final result state, visible to the student with comments and final marks.
- **Question Bank** — Reusable library of questions independent of any specific exam.
- **Subject** — A teaching topic (Python, SQL, …) under which exams and questions are categorised.

---

## 15. Support

- **In-app:** Use the **Notifications** bell to receive system updates.
- **Email:** `support@mewatitech.edu` (replace with your real address)
- **Documentation:** [`/docs/`](.) folder in the repository
- **API reference:** `https://<your-host>/api/docs/`
- **Issues / feature requests:** open a GitHub issue in your fork of this repository

---

> _"Quality education, free of cost — for every learner."_  
> Built with ❤️ for **Mewati Institute of Technology**.
