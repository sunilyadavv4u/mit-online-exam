<<<<<<< HEAD
# Mewati Institute of Technology — Online Examination Platform

A production-ready, role-based, scalable online examination web application built with **Django + Django REST Framework + djangorestframework-simplejwt** on the backend and **React + Vite + Tailwind CSS** on the frontend, with optional **Celery + Redis** for async work and a built-in **Databricks Llama-4 Maverick** AI code assistant.

> Built as a free NGO platform for teaching Python, PySpark, SQL, Azure Databricks, SQL Server, Azure Data Factory, Microsoft Fabric, Azure Synapse Analytics, Azure Data Lake Gen2, Azure Event Hubs, Spark Streaming, Data Engineering, Architect Designing, DSA, and Java.

---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Project structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Local setup (no Docker)](#local-setup-no-docker)
6. [Local setup (Docker)](#local-setup-docker)
7. [Default demo credentials](#default-demo-credentials)
8. [User guides](#user-guides)
9. [API documentation](#api-documentation)
10. [AI Assistant (Databricks)](#ai-assistant-databricks)
11. [Anti-cheating](#anti-cheating)
12. [Architecture](#architecture)
13. [Deployment](#deployment)
14. [Tests](#tests)
15. [Roadmap](#roadmap)

---

## Features

### Roles
- **Super Admin** — full system access, user management, audit logs, analytics
- **Teacher / Admin** — create subjects, exams, question banks, evaluate descriptive answers, publish results, generate reports
- **Student** — register, take exams, submit answers, see published results, track performance

### Core
- JWT auth (access + refresh + blacklist) via `djangorestframework-simplejwt`
- Email verification, forgot/reset password
- 6 question types: Single MCQ, Multiple MCQ, True/False, Fill-blank, Descriptive, Coding
- Auto-graded objective answers with negative marking
- Manual grading workflow for descriptive/coding answers
- Coding questions with **Monaco editor**, hidden test cases, sample run on Python
- AI code assistant: **SQL → Spark SQL / PySpark**, Python → PySpark, code explanation, AI-suggested marks
- Random question and option ordering
- Anti-cheating: fullscreen monitoring, tab-switch detection, auto-submit on timeout, audit logging
- Email + in-app notifications
- Reports: CSV / Excel / PDF
- Leaderboards & dashboards (student, teacher, admin)
- Cloudinary support (toggle via env)
- Swagger/Redoc API docs out-of-the-box
- Audit log middleware (every state-changing API call)
- Docker + docker-compose with Nginx, Postgres, Redis, Celery worker, Celery beat
- GitHub Actions CI + deploy templates (Render / Railway / Vercel / Netlify)

---

## Tech stack

### Backend
- Python 3.11+ (tested on 3.12 & 3.14)
- Django 5
- Django REST Framework
- djangorestframework-simplejwt (JWT)
- drf-spectacular (Swagger / OpenAPI)
- Celery + Redis
- PostgreSQL (production) / SQLite (default for dev)
- Whitenoise + Gunicorn
- ReportLab + openpyxl (PDF / Excel)
- Pillow, Cloudinary (optional)
- Databricks Model Serving (Llama-4 Maverick endpoint)

### Frontend
- React 18 + Vite
- Tailwind CSS 3
- Axios + react-router-dom v6
- @monaco-editor/react (in-browser code editor)
- recharts (charts)
- lucide-react (icons)
- react-hot-toast (notifications)
- jwt-decode

---

## Project structure

```
Online_Test_website/
├── backend/
│   ├── apps/
│   │   ├── ai_assistant/    # Databricks Llama-4 integration
│   │   ├── analytics/       # Dashboards, leaderboards, exports
│   │   ├── audit/           # Audit log middleware + viewer
│   │   ├── authentication/  # JWT, register, reset password
│   │   ├── evaluations/     # Manual grading + publish results
│   │   ├── exams/           # Subjects + Exams + Enrollments
│   │   ├── notifications/   # In-app + email notifications
│   │   ├── questions/       # Question bank, options, test cases
│   │   ├── submissions/     # Attempts, answers, proctor events
│   │   └── users/           # Custom User + role-aware profiles
│   ├── config/              # settings, urls, wsgi/asgi, celery
│   ├── tests/               # pytest test suite
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-postgres.txt
│   ├── pytest.ini
│   ├── .env.example
│   ├── .dockerignore
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/             # axios client + endpoint wrappers
│   │   ├── components/      # Layout + common reusable components
│   │   ├── contexts/        # AuthContext (JWT in localStorage)
│   │   ├── hooks/           # useFetch
│   │   ├── pages/           # Per-role pages + landing/auth
│   │   ├── styles/          # Tailwind layer
│   │   ├── utils/           # helpers (date, downloads, ...)
│   │   ├── App.jsx          # Routes
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
│
├── docs/
│   ├── architecture.md
│   ├── er-diagram.md
│   ├── deployment.md
│   └── api-overview.md
│
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
│
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

Install on your machine:

| Tool         | Version (recommended) | Why                                      |
|--------------|-----------------------|------------------------------------------|
| Python       | 3.11+                 | Backend                                  |
| pip / venv   | latest                | Backend deps                             |
| Node.js      | 18+ (20 LTS preferred)| Frontend                                 |
| npm / pnpm   | latest                | Frontend deps                            |
| Redis        | 7 (optional in dev)   | Caching + Celery broker                  |
| PostgreSQL   | 14+ (optional in dev) | Production DB. SQLite is the default.    |
| Docker       | 24+ (optional)        | One-command full stack                   |

> **Tip:** SQLite is used by default. You only need PostgreSQL if you set `DATABASE_URL`.

---

## Local setup (no Docker)

### 1. Clone and enter the repo

```bash
git clone <your repo url> Online_Test_website
cd Online_Test_website
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
# Optional: pip install -r requirements-postgres.txt

cp .env.example .env
# (Edit .env if needed - DATABRICKS_TOKEN comes pre-filled with the demo token)

python manage.py migrate
python manage.py createsuperuser            # OR
python manage.py seed_demo_data             # creates a teacher + 15 students

python manage.py runserver 0.0.0.0:8000
```

Server is now at: **http://127.0.0.1:8000**

- Swagger UI:    http://127.0.0.1:8000/api/docs/
- Redoc:         http://127.0.0.1:8000/api/redoc/
- Django admin:  http://127.0.0.1:8000/admin/
- Health check:  http://127.0.0.1:8000/health/

### 3. Frontend

In a **new terminal**:

```bash
cd frontend
cp .env.example .env

npm install
npm run dev
```

App is now at: **http://localhost:3000**.
The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

### 4. (Optional) Celery worker + beat

In two extra terminals (with the Python virtualenv activated):

```bash
# terminal A
celery -A config worker --loglevel=info --pool=solo   # --pool=solo on Windows

# terminal B
celery -A config beat --loglevel=info
```

> If Redis is not running, the system still works - tasks just run synchronously in the request thread.

---

## Local setup (Docker)

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
```

That brings up:
- `postgres` (port 5432)
- `redis` (6379)
- `backend` (gunicorn, internal 8000)
- `celery-worker`
- `celery-beat`
- `frontend` (Nginx → React, exposes **port 80**)

The frontend container's Nginx proxies `/api/`, `/admin/`, `/static/`, `/media/` to the backend.

Open: **http://localhost/**

To create demo data:

```bash
docker compose exec backend python manage.py seed_demo_data
docker compose exec backend python manage.py createsuperuser
```

---

## Default demo credentials

After running `python manage.py seed_demo_data`:

| Role         | Email                          | Password         |
|--------------|--------------------------------|------------------|
| Super Admin  | `admin@mewatitech.edu`         | `Admin@12345`    |
| Teacher      | `teacher@mewatitech.edu`       | `Teacher@12345`  |
| Student #1   | `student1@mewatitech.edu`      | `Student@12345`  |
| Student #2…N | `studentN@mewatitech.edu`      | `Student@12345`  |

3 demo exams are created (Python, SQL, PySpark) with all 6 question types and full enrollment.

### DSA question bank (LeetCode / HackerRank style)

After `seed_demo_data`, load **30+ Python DSA coding problems** with **sample + hidden test cases**:

```bash
cd backend
python manage.py seed_dsa_questions --exams
```

- Questions go into the **DSA** subject question bank (`DSA101`).
- `--exams` creates four live assessments: Easy, Medium, Hard, and Full (all problems).
- Students use **Run sample tests** for visible cases; **hidden tests run on final exam submit**.
- Problems are **MIT-original** practice items inspired by common patterns (not copied from external sites).

To re-seed from scratch: `python manage.py seed_dsa_questions --reset --exams`

---

## Install on another laptop / deploy online

Full step-by-step guides for IT staff and new machines:

**[`installation_guidance_anduserage/`](./installation_guidance_anduserage/README.md)**

1. Downloads & versions  
2. Installation on a new laptop  
3. Admin, teacher & student setup and usage  
4. Deploy online  

---

## User guides

End-user documentation — start with the role that fits you:

- **[Student Quick-Start](./docs/quickstart-student.md)** — login → take an exam → see results
- **[Teacher Quick-Start](./docs/quickstart-teacher.md)** — create exams → grade descriptive answers → publish results
- **[Super Admin Quick-Start](./docs/quickstart-admin.md)** — user management, audit logs, system overview
- **[Full User Guide](./docs/user-guide.md)** — every feature for every role + FAQs + troubleshooting + glossary

A clickable index lives at [`docs/README.md`](./docs/README.md).

---

## API documentation

- **Swagger / Try-it-out:** `/api/docs/`
- **Redoc:** `/api/redoc/`
- **Raw OpenAPI schema:** `/api/schema/`

A summary of grouped endpoints lives in [`docs/api-overview.md`](./docs/api-overview.md).

To export a Postman collection:

```bash
curl -o postman.json http://127.0.0.1:8000/api/schema/
# import the JSON into Postman as an OpenAPI 3.0 spec
```

---

## AI Assistant (Databricks)

The platform integrates with **Databricks Model Serving** to provide:

- SQL → Databricks Spark SQL (`spark.sql('''...''')`)
- SQL → PySpark DataFrame API
- Python (pandas) → PySpark
- Code explanation
- AI-suggested marks during manual evaluation (Teacher only)
- Generic chat endpoint

Configuration (in `backend/.env`):

```env
DATABRICKS_URL=xxxx
DATABRICKS_TOKEN=xxx
DATABRICKS_ENDPOINT=xxxx
```

> ⚠️ The token above is the one you provided. **Do not commit it to a public repository.** Rotate it via Databricks if needed.

The integration code lives in [`backend/apps/ai_assistant/databricks_client.py`](./backend/apps/ai_assistant/databricks_client.py) and is fully unit tested with mocks.

---

## Anti-cheating

The student exam page enforces:

- **Fullscreen** mode (auto-prompted on start, exits are reported)
- **Tab switching** detection (counter + audit event)
- **Right-click / DevTools / clipboard** events recorded as proctor events
- **Auto-submit** when the duration expires
- **Per-attempt question ordering** (random when enabled)
- **Hidden test cases** for coding questions
- **Audit logs** for every state-changing API call (super-admin viewable)

All proctor events are persisted server-side under `apps/submissions/models.py::ProctorEvent` for forensic review.

---

## Architecture

See [`docs/architecture.md`](./docs/architecture.md) for the full diagram. High-level overview:

```
┌────────────────────┐       HTTPS / JSON      ┌────────────────────┐
│  React + Vite app  │ ──────────────────────► │  Nginx (reverse    │
│  (Tailwind, Monaco)│ ◄────────────────────── │   proxy)           │
└────────────────────┘                          └─────────┬──────────┘
                                                          │
                                                          ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                     Django + DRF (gunicorn)                     │
   │  apps/ ┬─ users / authentication                                │
   │        ├─ exams / questions                                     │
   │        ├─ submissions / evaluations                             │
   │        ├─ analytics / notifications                             │
   │        ├─ ai_assistant ─► Databricks Llama-4 Maverick (REST)    │
   │        └─ audit (middleware)                                    │
   │                       ▲             ▲                           │
   │                       │             │                           │
   │                  Redis (cache)   Celery worker / beat           │
   │                       │             │                           │
   └───────────────────────┴─────────────┴───────────────────────────┘
                           │
                           ▼
                   PostgreSQL / SQLite
```

ER diagram lives in [`docs/er-diagram.md`](./docs/er-diagram.md).

---

## Deployment

Step-by-step instructions for free-tier deployments:

- **Frontend:** Vercel or Netlify
- **Backend:** Render or Railway
- **Database:** Supabase Postgres
- **Media:** Cloudinary or Azure Blob

Read the full guide: [`docs/deployment.md`](./docs/deployment.md).

GitHub Actions templates live in `.github/workflows/`.

---

## Tests

```bash
cd backend
.\.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate     # macOS/Linux
pytest -v
```

Coverage:

```bash
pytest --cov=apps --cov-report=html
# open htmlcov/index.html
```

There are 11 tests covering authentication, role-based access, full exam-attempt flow, MCQ auto-grading, proctor events, and the Databricks AI client (mocked).

---

## Roadmap

Things we'd add next given more time:

- Webcam-based proctoring with face detection
- Sandboxed multi-language code execution (Judge0 / Docker per submission)
- Realtime invigilator dashboard via Django Channels (WebSockets)
- Plagiarism detection across coding submissions
- Mobile native app
- More granular per-role admin permissions

---

## License

This codebase is provided for the **Mewati Institute of Technology** NGO. Free to use and modify for educational purposes.

> Built with care for teachers, students, and learners. ❤️
=======
# mit-online-exam
>>>>>>> 6ef7f59dc67b1e6595a0bb7ebe49dc85e6aa47a4
