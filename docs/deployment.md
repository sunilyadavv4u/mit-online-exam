# Deployment Guide

This document walks through deploying **Mewati Institute of Technology - Online Examination Platform** for **free** using Render / Railway / Supabase / Vercel / Cloudinary, then how to scale up to enterprise infra.

> If you only want a self-hosted setup, jump straight to the [Docker section](#docker-self-hosted).

---

## 1. Free-tier deployment

### Architecture

```
┌──────────────┐     HTTPS     ┌──────────────────┐
│ Vercel /     │ ────────────► │ Render / Railway │
│ Netlify      │               │ Django + DRF     │
│ (React app)  │ ◄──────────── │  + Celery        │
└──────────────┘               └──────────┬───────┘
                                          │
                              ┌───────────┼───────────┐
                              │                       │
                         Supabase                 Upstash
                         Postgres                 Redis (free)
                              │
                          Cloudinary
                          (images / files)
```

### 1.1 Database — Supabase Postgres

1. Sign up at [https://supabase.com](https://supabase.com) (free tier: 500MB DB).
2. Create a new project. Set a strong password.
3. Go to **Project Settings → Database → Connection string → URI**.
4. Copy the value. It looks like:
   ```
   postgres://postgres.[ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```
5. Save it as `DATABASE_URL` later.

### 1.2 Redis — Upstash (free)

1. Sign up at [https://upstash.com](https://upstash.com).
2. Create a new Redis database (the free tier is enough for caching + Celery).
3. Copy the **Redis URL** (`rediss://default:<password>@<host>:6379`).
4. Save as `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.

### 1.3 Media — Cloudinary (optional)

1. Sign up at [https://cloudinary.com](https://cloudinary.com) (free tier: 25 credits / month).
2. Copy `Cloud name`, `API key`, `API secret`.
3. In your backend `.env` set:
   ```
   USE_CLOUDINARY=True
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```

### 1.4 Backend — Render (recommended) or Railway

**Render — Web Service**

1. Push your repo to GitHub.
2. On [https://render.com](https://render.com), click **New → Web Service** and connect the repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt && pip install -r requirements-postgres.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2`
4. Add environment variables:
   ```
   DJANGO_SETTINGS_MODULE=config.settings.production
   SECRET_KEY=<long random string>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com,your-domain.com
   DATABASE_URL=<supabase connection string>
   REDIS_URL=<upstash url>
   CELERY_BROKER_URL=<upstash url>
   CELERY_RESULT_BACKEND=<upstash url>/1
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
   DATABRICKS_URL=https://dbc-xxx.cloud.databricks.com
   DATABRICKS_TOKEN=<rotated token>
   DATABRICKS_ENDPOINT=databricks-llama-4-maverick
   USE_CLOUDINARY=True
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=...
   EMAIL_HOST_PASSWORD=<gmail app password>
   ```
5. After first deploy, run a one-off shell:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo_data    # optional - for demo accounts
   ```

**Render — Background Worker (Celery)**

1. New → Background Worker
2. Same repo, same root directory `backend`
3. Build Command: `pip install -r requirements.txt && pip install -r requirements-postgres.txt`
4. Start Command: `celery -A config worker --loglevel=info --concurrency=2`
5. Same env vars as the web service.

**Railway** is similar — use [https://railway.app](https://railway.app), pick **Deploy from GitHub** and follow the same env var setup. Railway automatically provisions PostgreSQL & Redis if you don't want to use Supabase/Upstash.

### 1.5 Frontend — Vercel (recommended)

1. Push your repo to GitHub.
2. On [https://vercel.com](https://vercel.com), click **New Project** and import.
3. **Root Directory:** `frontend`
4. **Framework Preset:** Vite (auto-detected)
5. **Environment variables:**
   ```
   VITE_API_BASE_URL=https://your-backend.onrender.com
   VITE_INSTITUTE_NAME=Mewati Institute of Technology
   ```
6. Deploy.
7. Go back to your backend env vars and set `CORS_ALLOWED_ORIGINS` and `FRONTEND_URL` to the Vercel URL.

### 1.6 SSL & custom domain

- Vercel and Render both terminate TLS automatically. Just point your domain's DNS to them.
- For Vercel: Project → Settings → Domains → add your domain → follow DNS instructions.
- For Render: Service → Settings → Custom Domain → add and verify.

---

## 2. Docker (self-hosted)

If you have a single VPS (DigitalOcean, AWS Lightsail, Hetzner, etc.):

```bash
git clone <repo> Online_Test_website
cd Online_Test_website
cp backend/.env.example backend/.env
# edit backend/.env (set SECRET_KEY, DATABASE_URL, REDIS_URL, DATABRICKS_*, etc.)

docker compose up -d --build
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo_data   # optional
```

Open http://your-server-ip/ — Nginx serves the built React app and proxies `/api`, `/admin`, `/static`, `/media` to the Django container.

For HTTPS, place a Caddy or Traefik container in front of nginx, or terminate TLS via Cloudflare.

---

## 3. Production checklist

Before going live:

- [ ] Set `DEBUG=False`
- [ ] Set a long random `SECRET_KEY`
- [ ] Whitelist exact hosts in `ALLOWED_HOSTS`
- [ ] Whitelist exact origins in `CORS_ALLOWED_ORIGINS`
- [ ] Use HTTPS only (production settings already enforce HSTS + secure cookies)
- [ ] Rotate the Databricks token
- [ ] Use a real SMTP (Gmail App Password, SES, Mailgun, …)
- [ ] Run `python manage.py collectstatic` (Docker compose does this automatically)
- [ ] Configure a CDN for static / media (Cloudinary handles media; Vercel/Netlify CDN for the React bundle)
- [ ] Take a daily DB backup (`pg_dump` cron, or use Supabase scheduled backups)
- [ ] Review the audit logs regularly (`/admin/` → audit logs, or `/api/v1/audit/logs/`)

---

## 4. Scaling up

- **Run multiple backend replicas** behind Render's autoscaling, or use Kubernetes (GKE / EKS / AKS).
- **Read replicas:** Add a read-replica DB and route reads via `DATABASE_ROUTERS`.
- **Caching:** Use Redis for view-level caching of leaderboards / dashboards (`@cache_page` on read endpoints).
- **Celery scaling:** Add more workers; split queues per priority.
- **CDN:** Cloudflare / Akamai in front of static + media.
- **Object storage:** Switch from Cloudinary to Azure Blob / S3 with `django-storages`.
- **Observability:** Sentry for errors, OpenTelemetry for traces, Grafana + Prometheus for metrics, Loki for logs.
- **Code execution sandbox:** Replace the simple subprocess Python runner with Judge0 or per-submission Docker / Firecracker microVMs.

---

## 5. Useful management commands

```bash
python manage.py seed_demo_data --students 30
python manage.py createsuperuser
python manage.py changepassword <email>
python manage.py shell_plus              # django-extensions REPL
python manage.py show_urls               # list every URL pattern
python manage.py runserver_plus 0:8000   # django-extensions enhanced server
python manage.py spectacular --color --file schema.yaml   # offline OpenAPI dump
```
