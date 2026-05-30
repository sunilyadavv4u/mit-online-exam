# 2. Installation on a New Laptop

Step-by-step setup for **Windows**. Mac/Linux commands are noted where they differ.

**Prerequisite:** Complete [01-downloads-and-versions.md](./01-downloads-and-versions.md) first.

**Assumed project path:** `C:\d\Online_Test_website`

---

## 2.1 Overview

You will run **two programs** at the same time:

```
┌─────────────────────────┐         ┌─────────────────────────┐
│  Frontend (React/Vite)  │  /api   │  Backend (Django API)   │
│  http://localhost:3000  │ ──────► │  http://127.0.0.1:8000  │
└─────────────────────────┘         └─────────────────────────┘
```

Students and teachers always open **http://localhost:3000** in the browser.

---

## 2.2 Backend installation (Django API)

### Step 1 — Open terminal in backend folder

**PowerShell or CMD:**

```powershell
cd C:\d\Online_Test_website\backend
```

### Step 2 — Create Python virtual environment

```powershell
py -m venv .venv
```

If `py` is not found, try:

```powershell
python -m venv .venv
```

### Step 3 — Activate virtual environment

**PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If you see “running scripts is disabled”, run once (as your user):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**CMD (Command Prompt):**

```cmd
.\.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the start of your prompt.

### Step 4 — Install Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Optional** (only if you will use PostgreSQL locally):

```powershell
pip install -r requirements-postgres.txt
```

### Step 5 — Create environment file

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**CMD:**

```cmd
copy .env.example .env
```

For a first install on a lab laptop, the defaults in `.env` are fine:

- SQLite database (no PostgreSQL needed)
- `CELERY_TASK_ALWAYS_EAGER=True` (no Redis needed)
- Email prints to the console

Edit `.env` only if you need Databricks AI or real email — see `backend/.env.example` comments.

### Step 6 — Database setup

```powershell
python manage.py migrate
```

### Step 7 — Demo data (recommended for first run)

```powershell
python manage.py seed_demo_data
```

This creates admin, teacher, 15 students, subjects, and sample exams. Credentials are in [03-admin-teacher-student-guidance.md](./03-admin-teacher-student-guidance.md).

**Alternative:** create only a super admin manually:

```powershell
python manage.py createsuperuser
```

Follow prompts (use **email** as login, not username).

### Step 8 — Start backend server

```powershell
python manage.py runserver 0.0.0.0:8000
```

Leave this terminal **open**. You should see:

```
Starting development server at http://127.0.0.1:8000/
```

**Verify:**

- Health: http://127.0.0.1:8000/health/
- API docs: http://127.0.0.1:8000/api/docs/

> Port 8000 alone does **not** show the full student/teacher UI — that is on port 3000.

---

## 2.3 Frontend installation (React app)

Open a **second** terminal (backend keeps running in the first).

### Step 1 — Go to frontend folder

```powershell
cd C:\d\Online_Test_website\frontend
```

### Step 2 — Environment file

```powershell
Copy-Item .env.example .env
```

Default content:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_INSTITUTE_NAME=Mewati Institute of Technology
```

### Step 3 — Install Node packages

```powershell
npm install
```

First run may take several minutes.

### Step 4 — Start development server

```powershell
npm run dev
```

You should see:

```
Local:   http://localhost:3000/
```

**Verify:** Open http://localhost:3000 — you should see the landing page.

---

## 2.4 Daily usage (start / stop)

### Every time you use the platform

1. **Terminal 1** — backend:
   ```powershell
   cd C:\d\Online_Test_website\backend
   .\.venv\Scripts\Activate.ps1
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Terminal 2** — frontend:
   ```powershell
   cd C:\d\Online_Test_website\frontend
   npm run dev
   ```

3. Browser → **http://localhost:3000**

### Stop

Press `Ctrl+C` in each terminal.

---

## 2.5 Optional: Celery + Redis (background tasks)

**Not required** for normal teaching and exams in development. Email and async jobs run in-process when `CELERY_TASK_ALWAYS_EAGER=True`.

If you install Redis locally:

1. Set in `backend/.env`:
   ```env
   REDIS_URL=redis://127.0.0.1:6379/0
   CELERY_TASK_ALWAYS_EAGER=False
   ```
2. Start Redis, then in a third terminal (venv activated):
   ```powershell
   celery -A config worker --loglevel=info --pool=solo
   ```
   (`--pool=solo` is required on Windows.)

---

## 2.6 Optional: Docker (all-in-one)

If **Docker Desktop** is installed:

```powershell
cd C:\d\Online_Test_website
Copy-Item backend\.env.example backend\.env
docker compose up -d --build
docker compose exec backend python manage.py seed_demo_data
```

Open **http://localhost/** (port 80, not 3000).

---

## 2.7 Run tests (verify install)

With backend venv activated:

```powershell
cd C:\d\Online_Test_website\backend
pytest -v
```

All tests should pass (authentication, exams, grading, etc.).

---

## 2.8 Common problems on a new laptop

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'django'` | Activate `.venv` or use `.\.venv\Scripts\python.exe manage.py ...` |
| `npm` not recognized | Reinstall Node.js LTS; restart terminal |
| Blank page on port 8000 | Normal — use **http://localhost:3000** |
| Frontend cannot reach API | Ensure backend is running on 8000; check `frontend/.env` |
| `slug required` when saving exam | Use latest code; slug auto-generates from title |
| Students page search empty for teacher | Log in as **teacher** or **admin**; run latest backend (teachers can list students) |
| Port already in use | Stop old server or use `runserver 8001` and update `VITE_API_BASE_URL` |

---

## 2.9 Production build on one machine (without Docker)

For a simple LAN demo without `npm run dev`:

```powershell
cd C:\d\Online_Test_website\frontend
npm run build
```

Serve `frontend/dist` with any static file server, and point API calls to your backend URL via `VITE_API_BASE_URL` at build time.

---

## Next step

Learn how to create users and use each role: **[03-admin-teacher-student-guidance.md](./03-admin-teacher-student-guidance.md)**.
