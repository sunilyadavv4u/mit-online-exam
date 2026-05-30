# 1. Downloads and Versions

Everything you need **before** installing the application on a new laptop.

---

## 1.1 Copy the project to the new laptop

You do **not** need the old laptop once you have the project files. Use **one** of these methods:

| Method | Steps |
|--------|--------|
| **USB / external drive** | Copy the entire `Online_Test_website` folder to the new PC |
| **ZIP file** | Zip the folder, transfer, unzip on the new PC |
| **Git** | Push to GitHub/GitLab, then `git clone <url>` on the new PC |
| **OneDrive / Google Drive** | Sync or upload the folder (exclude `node_modules` and `.venv` to save space — reinstall those on the new PC) |

**Folders you can skip when copying** (recreated during install):

- `backend\.venv\`
- `frontend\node_modules\`
- `backend\__pycache__\` and `*.pyc` files
- `backend\db.sqlite3` (optional — omit if you want a fresh database on the new laptop)

**Folders you must keep:**

- `backend\` (all source code, `requirements.txt`, `.env.example`)
- `frontend\` (all source code, `package.json`)
- `docs\`, `docker-compose.yml`, `installation_guidance_anduserage\`

---

## 1.2 Required software (download & versions)

| Software | Minimum version | Recommended | Download |
|----------|-----------------|-------------|----------|
| **Python** | 3.11 | **3.12** or 3.14 (tested) | https://www.python.org/downloads/ |
| **Node.js** | 18.x | **20.x LTS** or 22.x | https://nodejs.org/ (LTS installer) |
| **npm** | Comes with Node | Latest bundled with Node | (no separate install) |
| **Git** (optional) | 2.x | Latest | https://git-scm.com/download/win |

### Python install tips (Windows)

- During setup, check **“Add python.exe to PATH”**.
- Verify in a new terminal:
  ```powershell
  py --version
  # or
  python --version
  ```

### Node.js install tips (Windows)

- Use the **LTS** Windows installer (.msi).
- Close and reopen PowerShell/CMD after install.
- Verify:
  ```powershell
  node --version
  npm --version
  ```

**Example of good version output:**

```
Python 3.12.x  (or 3.14.x)
Node v20.x.x or v22.x.x
npm 10.x.x
```

---

## 1.3 Optional software (production / advanced)

| Software | Version | When you need it |
|----------|---------|------------------|
| **PostgreSQL** | 14+ (Docker uses 16) | Production database instead of SQLite |
| **Redis** | 7.x | Background jobs (Celery), caching in production |
| **Docker Desktop** | 24+ | Run entire stack with one command |
| **Visual Studio Code** | Latest | Editing code (optional) |
| **Postman** | Latest | Testing API manually (optional) |

> **For classroom / lab use on one laptop:** Python + Node.js are enough. The app uses **SQLite** by default (no PostgreSQL install required).

---

## 1.4 Application stack versions (inside the project)

These are defined in the repo — you install them via `pip` and `npm`, not manually.

### Backend (`backend/requirements.txt`)

| Package | Version constraint |
|---------|-------------------|
| Django | 5.0 – 5.1.x |
| Django REST Framework | 3.15+ |
| djangorestframework-simplejwt | 5.3+ |
| Celery | 5.4+ |
| Gunicorn | 22+ (production server) |
| pytest | 8.2+ (testing) |

Full list: see `backend/requirements.txt` and `backend/requirements-postgres.txt` (PostgreSQL driver).

### Frontend (`frontend/package.json`)

| Package | Version |
|---------|---------|
| React | 18.3.x |
| Vite | 5.3.x |
| Tailwind CSS | 3.4.x |
| react-router-dom | 6.26.x |
| @monaco-editor/react | 4.6.x |

---

## 1.5 External services (only for online / AI features)

| Service | Purpose | Required locally? |
|---------|---------|-------------------|
| **Databricks** | AI code assistant (SQL→PySpark, etc.) | No — works if `DATABRICKS_*` set in `.env` |
| **SMTP (Gmail, etc.)** | Password reset & email notifications | No in dev — console email is default |
| **Cloudinary** | Cloud image/file storage | No — local `media/` folder in dev |
| **Supabase / Render / Vercel** | Online hosting | Only when deploying (see doc 04) |

---

## 1.6 Disk space estimate

| Item | Approximate size |
|------|------------------|
| Project source (without deps) | ~5–15 MB |
| Python venv + pip packages | ~200–400 MB |
| `node_modules` | ~300–500 MB |
| SQLite database (with demo data) | &lt; 5 MB |

**Total:** plan for **~1 GB** free disk space on the new laptop.

---

## Next step

Continue with **[02-installation-on-new-laptop.md](./02-installation-on-new-laptop.md)**.
