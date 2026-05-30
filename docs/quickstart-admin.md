# Super Admin Quick-Start Guide

> A 5-minute walkthrough for super admins. For the full guide, see [`user-guide.md`](./user-guide.md).

A Super Admin sees everything a Teacher sees, *plus* user management and audit logs.

---

## 1. Login

Use the credentials your IT team provided, or the seeded ones:
- `admin@mewatitech.edu` / `Admin@12345` ← **change this on production!**

---

## 2. System overview

Sidebar → **Dashboard** (`/dashboard`):
- Total users, active users
- Pie chart of users by role
- Total attempts platform-wide
- Live exams count
- Registrations in the last 30 days

---

## 3. Manage users

Sidebar → **Users** (`/users`):

For each user you can:
- **Search** by name / email
- **Filter** by role (super_admin / teacher / student)
- **Change role** inline using the dropdown
- **Enable / Disable** an account (a disabled user can't log in)
- See verification status (✅ verified / ⏳ pending)

> Tip: Only ever have a *small* number of super admins. The role bypasses many permission checks.

---

## 4. Audit logs

Sidebar → **Audit Logs** (`/audit-logs`):

Every state-changing API request (POST/PUT/PATCH/DELETE) is captured:
- Timestamp
- User + email
- HTTP method + path
- Response status
- IP address

Use this for forensic review:
- During a contested exam
- When someone reports unusual activity
- When confirming what an account changed

The middleware also strips obvious password fields before persistence.

---

## 5. System info & quick links

Sidebar → **System** (`/system`) provides:
- Backend / frontend / DB / AI / cache configuration summary
- Direct links to:
  - Django Admin → `/admin/` (low-level data ops)
  - Swagger UI → `/api/docs/`
  - Redoc → `/api/redoc/`
  - OpenAPI JSON → `/api/schema/`

---

## 6. Django Admin (advanced)

Open **`/admin/`** for low-level edits to any database row. You can manage:

| Model | Use case |
|---|---|
| Users | Force-reset email verification |
| Exams + Enrollments | Bulk enroll / un-enroll |
| Questions / Options / Test cases | Quick text fixes |
| Attempts / Answers / Proctor events | Forensics |
| Evaluations | Roll back a publication |
| Notifications | Manually push system messages |
| AI Requests | Inspect AI history |
| Audit Logs | Read-only |

> Use the Django admin sparingly — every action there bypasses the application layer's validation.

---

## 7. Common admin tasks

### Create another super admin

Two ways:

**Via the UI:**
1. Sidebar → **Users**
2. Find the user → set their role to `super_admin`

**Via the CLI (server side):**
```bash
cd backend
.\.venv\Scripts\activate.bat   # Windows cmd
python manage.py createsuperuser
```

### Reset a user's password (without email)

```bash
python manage.py changepassword someone@example.com
```

### Re-seed demo data

```bash
python manage.py seed_demo_data --students 30
```

> Idempotent — re-running creates only missing users / subjects / exams.

### Disable an account temporarily

`/users` → toggle **Disable** for the user. Their JWT remains valid until expiry, so for full effect, also blacklist their refresh tokens via Django admin → *Token blacklist* → *Outstanding Tokens*.

### Investigate cheating

1. `/audit-logs` to see what API calls the student made
2. Django admin → *Submissions › Proctor events* to see fullscreen exits / tab switches
3. Open the attempt → check `tab_switch_count` / `fullscreen_exit_count`
4. If needed, set the attempt's `status` to `auto_submitted` and add an admin note

### Generate the OpenAPI schema offline

```bash
python manage.py spectacular --color --file schema.yaml
```

---

## 8. Operational checklist

When deploying to production:

- [ ] Change all demo passwords (admin / teacher / students)
- [ ] Set a long random `SECRET_KEY` in `.env`
- [ ] `DEBUG=False`
- [ ] Restrict `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- [ ] Use HTTPS (`SECURE_SSL_REDIRECT=True` is on by default in `production.py`)
- [ ] Rotate the Databricks token
- [ ] Configure a real SMTP backend
- [ ] Set up daily DB backups (Supabase or `pg_dump` cron)
- [ ] Test password reset & email verification end-to-end
- [ ] Review audit logs weekly for anomalies

---

## Need help?

- See the full guide: [`user-guide.md`](./user-guide.md)
- Deployment specifics: [`deployment.md`](./deployment.md)
- Architecture diagrams: [`architecture.md`](./architecture.md)
- ER diagram: [`er-diagram.md`](./er-diagram.md)
- API reference: [`api-overview.md`](./api-overview.md)

> _Thank you for keeping the platform running smoothly._
