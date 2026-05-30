# 3. Admin, Teacher & Student — Setup and Usage

How to **create accounts**, **assign roles**, and **use the platform** after installation.

**App URL (local):** http://localhost:3000

---

## 3.1 Three roles

| Role | Who | Main tasks |
|------|-----|------------|
| **Super Admin** | IT / institute head | All users, audit logs, system settings, same as teacher plus global control |
| **Teacher** | Faculty | Create exams, questions, enroll students, grade, publish results |
| **Student** | Learners | Take exams, view results, use AI assistant |

---

## 3.2 Demo accounts (after `seed_demo_data`)

Run once on the server laptop:

```powershell
cd C:\d\Online_Test_website\backend
.\.venv\Scripts\Activate.ps1
python manage.py seed_demo_data
```

Optional: more students:

```powershell
python manage.py seed_demo_data --students 30
```

### Default logins

| Role | Email | Password |
|------|-------|----------|
| Super Admin | `admin@mewatitech.edu` | `Admin@12345` |
| Teacher | `teacher@mewatitech.edu` | `Teacher@12345` |
| Student 1 | `student1@mewatitech.edu` | `Student@12345` |
| Student 2…15 | `student2@mewatitech.edu` … `student15@mewatitech.edu` | `Student@12345` |

> **Security:** Change these passwords before any public deployment. Never use demo passwords on the internet.

---

## 3.3 How to create a Super Admin

### Method A — Management command (recommended)

```powershell
cd C:\d\Online_Test_website\backend
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

- Enter **email** (e.g. `principal@mewatitech.edu`)
- Enter name and a **strong password**
- Django creates a user with `is_superuser=True`

Then set role in the **web app** or Django admin:

1. Log in to http://localhost:3000 as that user, **or**
2. Open http://127.0.0.1:8000/admin/ → **Users** → edit user → set **Role** = `super_admin`

### Method B — Django Admin (`/admin/`)

1. Create superuser as above.
2. Go to http://127.0.0.1:8000/admin/
3. **Users** → Add user → set email, password, role **Super Admin**, active, email verified.

### Method C — Seed command (demo only)

`seed_demo_data` creates `admin@mewatitech.edu` automatically.

---

## 3.4 How to create a Teacher

### Option 1 — Self-registration (website)

1. Open http://localhost:3000
2. Click **Sign up** / **Register**
3. Choose role **Teacher**
4. Fill name, email, password
5. Log in after registration

### Option 2 — Super Admin creates user

1. Log in as **Super Admin**
2. Sidebar → **Users** (`/users`)
3. Create user or change an existing user’s **role** to **Teacher**

### Option 3 — Django Admin

`/admin/` → Users → add user with role `teacher` and create **Teacher profile** (employee ID, department).

---

## 3.5 How to create Students

### Option 1 — Self-registration (website)

1. Landing page → **Sign up**
2. Role **Student**
3. Complete profile (enrollment ID may be auto-generated on register — check registration form)

### Option 2 — Super Admin

1. Log in as Super Admin → **Users**
2. Add user with role **Student**

### Option 3 — Bulk demo students

```powershell
python manage.py seed_demo_data --students 50
```

Creates `student1@` … `studentN@mewatitech.edu` with password `Student@12345`.

### Enroll students in an exam (Teacher)

1. Log in as **Teacher**
2. **Exams** → open an exam → **Enrollments** section
3. Select students to allow for that exam

Without enrollment, a student may see the exam but cannot start it (depending on exam settings).

---

## 3.6 Super Admin — day-to-day guide

**Login:** Super Admin email + password → http://localhost:3000

| Task | Where in app |
|------|----------------|
| Dashboard stats | **Dashboard** |
| Manage all users | **Users** (`/users`) — search, filter by role, enable/disable |
| Audit trail | **Audit Logs** (`/audit-logs`) |
| System links (Swagger, Django admin) | **System** (`/system`) |
| Low-level DB edits | Browser → http://127.0.0.1:8000/admin/ |

**Typical workflow:**

1. Create teacher accounts (or approve self-registrations).
2. Verify student accounts are active.
3. Review audit logs after exams if cheating is reported.
4. Change default demo passwords before going live.

**Detailed guide:** [`../docs/quickstart-admin.md`](../docs/quickstart-admin.md)

---

## 3.7 Teacher — day-to-day guide

**Login:** Teacher email + password

| Task | Where in app |
|------|----------------|
| View / search students | **Students** (`/students`) — teachers and admins only |
| Manage subjects | **Subjects** |
| Create / edit exams | **Exams** → **+ New exam** |
| Add questions (MCQ, coding, etc.) | Exam editor → **Questions** |
| Enroll students | Exam editor → **Enrollments** |
| Grade descriptive / coding | **Evaluations** |
| Publish results | Evaluation detail → **Publish** |
| Reports (CSV/Excel/PDF) | **Reports** |
| AI code tools | **AI Assistant** |

**Typical workflow:**

1. Create or pick a **Subject**.
2. **New exam** → set duration, marks, start/end time, proctoring.
3. Add questions (all 6 types supported).
4. **Enroll** students who should take it.
5. Set exam status to **Live** when the window opens.
6. After submissions → **Evaluations** → grade → **Publish**.
7. Students see final marks under **My Results**.

**Detailed guide:** [`../docs/quickstart-teacher.md`](../docs/quickstart-teacher.md)

---

## 3.8 Student — day-to-day guide

**Login:** Student email + password

| Task | Where in app |
|------|----------------|
| See available exams | **Dashboard** or **My Exams** |
| Take exam | **Start exam** (only when status is **Live**) |
| View results | **My Results** |
| Leaderboard | **Leaderboard** |
| AI study help | **AI Assistant** |
| Profile | **Profile** / **Settings** |

**Taking an exam:**

1. Click **Start exam** on a live exam.
2. Allow **fullscreen** when prompted.
3. Answer questions; use **Save answer** or navigate with the question palette.
4. For **coding** questions: write code in Monaco editor → **Run sample tests** (Python).
5. Click **Submit** before time ends (or wait for auto-submit).

**Rules (proctoring):**

- Do not switch tabs — events are logged.
- Stay in fullscreen.
- Timer auto-submits at zero.

**Detailed guide:** [`../docs/quickstart-student.md`](../docs/quickstart-student.md)

---

## 3.9 Password reset and email verification

| Feature | Development (default) | Production |
|---------|----------------------|------------|
| Forgot password | Link logged in **backend terminal** (console email) | Configure SMTP in `backend/.env` |
| Email verification | May be skipped or console link | Real SMTP + `FRONTEND_URL` set |

**Change a user password (admin):**

```powershell
python manage.py changepassword user@email.com
```

---

## 3.10 Who can access which pages

| Page | Student | Teacher | Super Admin |
|------|---------|---------|-------------|
| Dashboard | ✅ | ✅ | ✅ |
| My Exams / Take exam | ✅ | — | — |
| Exams (manage) | — | ✅ | ✅ |
| Students list | — | ✅ | ✅ |
| Evaluations / Reports | — | ✅ | ✅ |
| Users / Audit / System | — | — | ✅ |

Students who try teacher URLs are blocked by the app.

---

## 3.11 Printing / sharing guides with students

Give students:

1. This section **3.8** or the PDF/print of [`../docs/quickstart-student.md`](../docs/quickstart-student.md)
2. Their **email + temporary password**
3. The **correct URL** (e.g. `https://exams.yourinstitute.org` after deployment)

Give teachers:

1. Section **3.7** or [`../docs/quickstart-teacher.md`](../docs/quickstart-teacher.md)

---

## Next step

Put the system on the internet: **[04-deploy-online.md](./04-deploy-online.md)**.
