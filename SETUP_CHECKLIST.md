# ✅ Setup Checklist - Django Online Test Website

## Prerequisites Check

- [ ] Python 3.11+ installed
  ```powershell
  py --version
  ```

- [ ] Node.js 20.x LTS installed
  ```powershell
  node --version
  npm --version
  ```

- [ ] Git installed (optional)
  ```powershell
  git --version
  ```

---

## Backend Setup

- [ ] Navigate to backend folder
  ```powershell
  cd backend
  ```

- [ ] Check if `.venv` exists, if not create it
  ```powershell
  py -m venv .venv
  ```

- [ ] Activate virtual environment
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- [ ] Install dependencies
  ```powershell
  pip install -r requirements.txt
  ```
  > Note: This may take 10-15 minutes on first run (includes PySpark)
  > Or use minimal install: `pip install -r requirements-basic.txt`

- [ ] Copy environment file if needed
  ```powershell
  Copy-Item .env.example .env
  ```

- [ ] Run migrations
  ```powershell
  python manage.py migrate
  ```

- [ ] Create superuser (admin account)
  ```powershell
  python manage.py createsuperuser
  ```
  > Use email as username. Example: admin@example.com

- [ ] (Optional) Create demo data
  ```powershell
  python manage.py seed_demo_data
  ```

- [ ] Start Django server
  ```powershell
  python manage.py runserver 0.0.0.0:8000
  ```

- [ ] Verify backend is running
  - API: http://127.0.0.1:8000/
  - API Docs: http://127.0.0.1:8000/api/docs/
  - Admin: http://127.0.0.1:8000/admin/

---

## Frontend Setup

- [ ] Open NEW terminal (keep backend running)

- [ ] Navigate to frontend folder
  ```powershell
  cd frontend
  ```

- [ ] Copy environment file if needed
  ```powershell
  Copy-Item .env.example .env
  ```

- [ ] Install dependencies
  ```powershell
  npm install
  ```
  > Takes 2-5 minutes on first run

- [ ] Start development server
  ```powershell
  npm run dev
  ```

- [ ] Verify frontend is running
  - URL: http://localhost:3000

---

## Test the Application

- [ ] Backend API is accessible
  ```
  GET http://127.0.0.1:8000/health/
  ```

- [ ] Frontend loads
  ```
  Open http://localhost:3000 in browser
  ```

- [ ] Try to login
  - If using seed data: Email from `03-admin-teacher-student-guidance.md`
  - If manual setup: Use the superuser created above

- [ ] API documentation loads
  ```
  Open http://127.0.0.1:8000/api/docs/
  ```

---

## Database Setup Options

### Option 1: SQLite (Default for Development)
✅ **Recommended for initial setup**
- File-based database
- No external dependencies
- Good for single-user development

### Option 2: PostgreSQL (Production)
- For multi-user deployments
- Install PostgreSQL
- Update `DATABASE_URL` in `.env`

---

## Troubleshooting Checklist

### Backend Issues

- [ ] Django won't start?
  ```powershell
  python manage.py check
  ```

- [ ] Database issues?
  ```powershell
  python manage.py migrate --fake-initial
  ```

- [ ] Port 8000 in use?
  ```powershell
  python manage.py runserver 8001
  ```

- [ ] Import errors?
  ```powershell
  pip install --upgrade pip
  pip install -r requirements.txt --force-reinstall
  ```

### Frontend Issues

- [ ] npm install fails?
  ```powershell
  npm cache clean --force
  npm install
  ```

- [ ] Port 3000 in use?
  ```powershell
  npm run dev -- --port 3001
  ```

- [ ] Module not found?
  ```powershell
  rm -r node_modules
  npm install
  ```

### Connection Issues

- [ ] Can't connect backend from frontend?
  ```
  Check: frontend/.env has VITE_API_BASE_URL=http://127.0.0.1:8000
  ```

- [ ] CORS errors?
  ```
  Check: backend/.env has CORS_ALLOWED_ORIGINS=http://localhost:3000
  ```

---

## Common Commands Reference

| Task | Command |
|------|---------|
| Activate venv | `.\.venv\Scripts\Activate.ps1` |
| Install packages | `pip install -r requirements.txt` |
| Run migrations | `python manage.py migrate` |
| Make migrations | `python manage.py makemigrations` |
| Create superuser | `python manage.py createsuperuser` |
| Seed demo data | `python manage.py seed_demo_data` |
| Start backend | `python manage.py runserver` |
| Start frontend | `npm run dev` |
| Build frontend | `npm run build` |
| Run tests | `pytest` |

---

## Environment Variables

### `.env.example` Locations
- `backend/.env.example` - Backend configuration
- `frontend/.env.example` - Frontend configuration

### Key Backend Variables
```
DEBUG=True
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=config.settings.development
DATABASE_URL=  (leave empty for SQLite)
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:3000
```

### Key Frontend Variables
```
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_INSTITUTE_NAME=Mewati Institute of Technology
```

---

## Next Steps After First-Time Setup

1. **Create Test Data**
   - Use admin panel: http://127.0.0.1:8000/admin/
   - Or use seed_demo_data command

2. **Configure Email (Optional)**
   - Update EMAIL_* variables in `.env`
   - Default uses console (prints to terminal)

3. **Setup Production**
   - See: `docs/deployment.md`
   - Configure PostgreSQL
   - Setup Celery + Redis
   - Configure email service

4. **Read Documentation**
   - `docs/user-guide.md` - Feature overview
   - `docs/architecture.md` - System design
   - `docs/quickstart-*.md` - Role-based guides

---

## Performance Notes

- **First pip install:** 10-15 minutes (includes PySpark build)
- **First npm install:** 2-5 minutes
- **Subsequent starts:** < 30 seconds
- **Database migrations:** Usually < 10 seconds

---

## Files Created for Easy Setup

- `run_backend.ps1` - PowerShell script to start backend
- `run_backend.bat` - Batch script to start backend
- `QUICK_START.md` - Quick reference guide
- `SETUP_STATUS.md` - Current setup status
- `SETUP_CHECKLIST.md` - This file

---

**Last Updated:** May 30, 2026  
**Status:** ✅ Backend Ready | ⏳ Frontend Requires Node.js
