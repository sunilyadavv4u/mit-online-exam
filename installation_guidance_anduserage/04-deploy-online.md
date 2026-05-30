# 4. Deploy Online (Internet)

How to host the **Mewati Institute of Technology Online Exam Platform** so students and teachers can access it from anywhere.

**Prerequisites:** Working local install ([02-installation-on-new-laptop.md](./02-installation-on-new-laptop.md)) and changed demo passwords ([03-admin-teacher-student-guidance.md](./03-admin-teacher-student-guidance.md)).

---

## 4.1 Deployment options

| Option | Cost | Difficulty | Best for |
|--------|------|------------|----------|
| **A. Free cloud** (Vercel + Render + Supabase) | Free tier limits | Medium | NGO / pilot, &lt; 100 concurrent users |
| **B. Docker on VPS** | ~$5–20/month | Medium | Full control, one server |
| **C. Institute LAN only** | Free | Easy | Single building, no internet |

---

## 4.2 Architecture (online)

```
  Users (browser)
        │
        ▼
┌───────────────────┐
│  Vercel / Netlify │  ← React static site (HTTPS)
│  (frontend)       │
└─────────┬─────────┘
          │  HTTPS API calls
          ▼
┌───────────────────┐
│  Render / Railway │  ← Django + Gunicorn (HTTPS)
│  (backend)        │
└─────────┬─────────┘
          │
    ┌─────┴─────┬─────────────┐
    ▼           ▼             ▼
 Supabase    Upstash      Cloudinary
 Postgres     Redis        (media, optional)
```

---

## 4.3 Option A — Free cloud deployment (step by step)

### Step 1 — Put code on GitHub

1. Create a GitHub account and repository.
2. Push the `Online_Test_website` folder (do **not** commit `.env`, `.venv`, `node_modules`, or `db.sqlite3`).
3. Use `.gitignore` already in the project if present; otherwise exclude:
   - `backend/.env`
   - `backend/.venv/`
   - `frontend/node_modules/`
   - `**/db.sqlite3`

### Step 2 — Database (Supabase PostgreSQL)

1. Sign up: https://supabase.com
2. **New project** → choose region close to India if possible.
3. **Settings → Database → Connection string (URI)**.
4. Copy the URI → you will set it as `DATABASE_URL` on the backend.

Example shape:

```
postgresql://postgres.[ref]:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

### Step 3 — Redis (Upstash) — optional but recommended

1. Sign up: https://upstash.com
2. Create Redis database → copy **Redis URL**.
3. Use the same URL for:
   - `REDIS_URL`
   - `CELERY_BROKER_URL`
   - `CELERY_RESULT_BACKEND` (can append `/1` for results DB)

Set `CELERY_TASK_ALWAYS_EAGER=False` in production.

### Step 4 — Backend on Render

1. Sign up: https://render.com
2. **New → Web Service** → connect GitHub repo.
3. Settings:

   | Field | Value |
   |-------|--------|
   | Root Directory | `backend` |
   | Environment | Python 3 |
   | Build Command | `pip install -r requirements.txt && pip install -r requirements-postgres.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput` |
   | Start Command | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2` |

4. **Environment variables** (minimum):

   ```env
   DJANGO_SETTINGS_MODULE=config.settings.production
   SECRET_KEY=<generate-a-long-random-string-50-chars>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com,yourdomain.com
   DATABASE_URL=<supabase-uri>
   REDIS_URL=<upstash-url>
   CELERY_BROKER_URL=<upstash-url>
   CELERY_RESULT_BACKEND=<upstash-url>/1
   CELERY_TASK_ALWAYS_EAGER=False
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

5. Optional (AI, email, media):

   ```env
   DATABRICKS_URL=https://dbc-xxx.cloud.databricks.com
   DATABRICKS_TOKEN=<your-token>
   DATABRICKS_ENDPOINT=databricks-llama-4-maverick
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your@gmail.com
   EMAIL_HOST_PASSWORD=<gmail-app-password>
   USE_CLOUDINARY=True
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```

6. Deploy → note backend URL, e.g. `https://mit-exam-api.onrender.com`

7. **One-off shell** on Render (first time):

   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo_data   # optional — remove demo passwords after!
   ```

### Step 5 — Celery worker on Render (optional)

1. **New → Background Worker**
2. Same repo, root `backend`
3. Build: `pip install -r requirements.txt && pip install -r requirements-postgres.txt`
4. Start: `celery -A config worker --loglevel=info --concurrency=2`
5. Copy **all** backend env vars from the web service.

### Step 6 — Frontend on Vercel

1. Sign up: https://vercel.com
2. **New Project** → import GitHub repo.
3. Settings:

   | Field | Value |
   |-------|--------|
   | Root Directory | `frontend` |
   | Framework | Vite |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |

4. Environment variables:

   ```env
   VITE_API_BASE_URL=https://mit-exam-api.onrender.com
   VITE_INSTITUTE_NAME=Mewati Institute of Technology
   ```

5. Deploy → note URL, e.g. `https://mit-exam.vercel.app`

6. **Update backend** on Render:

   ```env
   FRONTEND_URL=https://mit-exam.vercel.app
   CORS_ALLOWED_ORIGINS=https://mit-exam.vercel.app
   ```

Redeploy backend if CORS was wrong on first try.

### Step 7 — Custom domain (optional)

- **Vercel:** Project → Settings → Domains → add `exams.mewatitech.edu` → follow DNS records.
- **Render:** Service → Custom Domains → add API subdomain e.g. `api.mewatitech.edu`.
- Update `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`, and `VITE_API_BASE_URL` to match.

### Step 8 — SSL

Vercel and Render provide HTTPS automatically. No extra certificate setup on free tier.

---

## 4.4 Option B — Docker on a VPS (DigitalOcean, AWS Lightsail, Hetzner)

Good when you want **one server** for institute use.

### Requirements

- Ubuntu 22.04+ (or similar) VPS with 2 GB+ RAM
- Docker + Docker Compose installed
- Domain pointing to server IP (optional)

### Steps

```bash
# On the server
git clone <your-repo-url> Online_Test_website
cd Online_Test_website
cp backend/.env.example backend/.env
nano backend/.env   # set SECRET_KEY, DATABRICKS_*, EMAIL_*, etc.

docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo_data   # optional
```

Open: **http://YOUR_SERVER_IP/** (port 80)

`docker-compose.yml` includes:

- PostgreSQL 16
- Redis 7
- Django (Gunicorn)
- Celery worker + beat
- Frontend (Nginx serving React + proxy to API)

### HTTPS on VPS

- Use **Cloudflare** in front of the server (easiest), or
- Add **Caddy** / **Traefik** reverse proxy with Let's Encrypt.

---

## 4.5 Option C — LAN only (no public internet)

1. Install on one **lab server laptop** ([02-installation-on-new-laptop.md](./02-installation-on-new-laptop.md)).
2. Start backend with:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```
3. Start frontend with:
   ```powershell
   npm run dev -- --host 0.0.0.0
   ```
4. Find server IP: `ipconfig` → e.g. `192.168.1.50`
5. Students open: **http://192.168.1.50:3000**
6. Ensure Windows Firewall allows ports **3000** and **8000**.

---

## 4.6 Production checklist (before students use it online)

- [ ] `DEBUG=False`
- [ ] Strong unique `SECRET_KEY`
- [ ] Demo passwords changed or `seed_demo_data` not used in production
- [ ] `ALLOWED_HOSTS` lists only your real domains
- [ ] `CORS_ALLOWED_ORIGINS` lists only your frontend URL
- [ ] PostgreSQL (not SQLite) for production
- [ ] SMTP configured for password reset emails
- [ ] Databricks token rotated (never commit tokens to GitHub)
- [ ] Backups scheduled for database (Supabase has backups on paid tiers; or `pg_dump` cron on VPS)
- [ ] Test full flow: register → exam → submit → teacher publish → student sees result

---

## 4.7 Environment variables reference

### Backend (production)

| Variable | Purpose |
|----------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Django secret — must be random |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Comma-separated domains |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Cache + Celery |
| `FRONTEND_URL` | For email links |
| `CORS_ALLOWED_ORIGINS` | Frontend origin(s) |
| `DATABRICKS_*` | AI assistant |
| `EMAIL_*` | Outgoing mail |

### Frontend (production build)

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | Full HTTPS URL of backend (no trailing slash) |
| `VITE_INSTITUTE_NAME` | Shown in UI header |

---

## 4.8 CI/CD (GitHub Actions)

The repo includes workflows in `.github/workflows/`:

- `ci.yml` — runs tests on push
- `deploy.yml` — template for automated deploy

Connect these after the repo is on GitHub. Details: [`../docs/deployment.md`](../docs/deployment.md)

---

## 4.9 After go-live support

| Issue | Action |
|-------|--------|
| 502 / slow API on Render free tier | Cold start — wait 30s or upgrade plan |
| CORS error in browser | Fix `CORS_ALLOWED_ORIGINS` to exact frontend URL |
| Login works locally but not online | Check `VITE_API_BASE_URL` was set **before** `npm run build` on Vercel |
| Media files missing | Enable Cloudinary or configure volume on VPS |
| Students cannot start exam | Teacher must **enroll** them and exam must be **Live** |

---

## 4.10 Summary

| Goal | Document section |
|------|------------------|
| Install on new PC | [02](./02-installation-on-new-laptop.md) |
| Create admin / teacher / student | [03](./03-admin-teacher-student-guidance.md) |
| Free internet hosting | [04.3](#43-option-a--free-cloud-deployment-step-by-step) |
| Own server hosting | [04.4](#44-option-b--docker-on-a-vps-digitalocean-aws-lightsail-hetzner) |
| Classroom Wi‑Fi only | [04.5](#45-option-c--lan-only-no-public-internet) |

For more technical depth, see [`../docs/deployment.md`](../docs/deployment.md) and [`../README.md`](../README.md).
