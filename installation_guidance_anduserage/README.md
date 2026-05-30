# Installation, Usage & Deployment — MIT Online Exam Platform

This folder is the **complete guide for setting up the project on a new laptop** and putting it **online**. It is written for **Mewati Institute of Technology** staff and students who may not have the original development machine.

**Project location (example):** `C:\d\Online_Test_website`

**Application URLs after local setup:**

| What | URL |
|------|-----|
| Main app (React) | http://localhost:3000 |
| API / Swagger | http://127.0.0.1:8000/api/docs/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

---

## Documents in this folder

| # | Document | Purpose |
|---|----------|---------|
| 1 | [01-downloads-and-versions.md](./01-downloads-and-versions.md) | What to download, recommended versions, optional tools |
| 2 | [02-installation-on-new-laptop.md](./02-installation-on-new-laptop.md) | Step-by-step install backend + frontend on Windows (and notes for Mac/Linux) |
| 3 | [03-admin-teacher-student-guidance.md](./03-admin-teacher-student-guidance.md) | Create admins/teachers/students and day-to-day usage by role |
| 4 | [04-deploy-online.md](./04-deploy-online.md) | Deploy to the internet (free tier + Docker VPS) |

**Additional docs already in the repo:**

- Full feature guide: [`../docs/user-guide.md`](../docs/user-guide.md)
- Student quick-start: [`../docs/quickstart-student.md`](../docs/quickstart-student.md)
- Teacher quick-start: [`../docs/quickstart-teacher.md`](../docs/quickstart-teacher.md)
- Super admin quick-start: [`../docs/quickstart-admin.md`](../docs/quickstart-admin.md)
- Architecture: [`../docs/architecture.md`](../docs/architecture.md)

---

## Quick start (experienced users)

1. Install **Python 3.11+**, **Node.js 20 LTS**, **Git** (see doc 01).
2. Copy or clone the project folder to the new laptop.
3. Follow [02-installation-on-new-laptop.md](./02-installation-on-new-laptop.md).
4. Run `python manage.py seed_demo_data` for demo logins, or create your own admin (doc 03).
5. Open http://localhost:3000 and log in.
6. For production, follow [04-deploy-online.md](./04-deploy-online.md).

---

## Support checklist

If something fails on a new machine, check in this order:

1. **Python venv activated?** (`.\.venv\Scripts\activate` on Windows)
2. **Both servers running?** Backend on port **8000**, frontend on **3000**
3. **Migrations run?** `python manage.py migrate`
4. **Using the web app URL?** Use **localhost:3000**, not port 8000 alone
5. **Firewall** blocking Node or Python?

---

*Mewati Institute of Technology — Online Examination Platform*
