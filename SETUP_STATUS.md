# Django Online Test Website - Setup Status

## Project Overview
This is a Django + React web application for online examinations built by Mewati Institute of Technology.

## Current Setup Status

### ✅ Completed
1. **Backend Python Environment**
   - Python 3.14 is available
   - Virtual environment created at `backend/.venv`
   - Core Django packages installed:
     - Django 5.1.15
     - Django REST Framework 3.17.1
     - djangorestframework-simplejwt (JWT authentication)
     - drf-spectacular (Swagger/OpenAPI docs)
     - Other essential packages: Celery, Redis, Gunicorn, Pillow, etc.

2. **Backend Configuration**
   - `.env` file exists with proper configuration
   - Uses SQLite by default for development (no PostgreSQL needed)
   - Celery configured to run synchronously (no Redis needed initially)
   - Console email backend enabled for testing

### ⚠️ In Progress / Issues
1. **Package Installation**
   - Some packages are still installing in background
   - PySpark (optional for now) not yet installed
   - Missing some test/optional dependencies

2. **Frontend Setup**
   - Node.js is NOT installed on this system
   - THIS IS REQUIRED for the React frontend
   - Frontend cannot run without Node.js 20.x LTS or higher

### ❌ Not Started
1. **Frontend React App**
   - Requires Node.js/npm (not installed)
   - Requires: `npm install` in frontend folder
   - Requires: `npm run dev` to start dev server

## Quick Start Instructions

### To run the backend Django server:
```powershell
# Navigate to backend folder
cd backend

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Create demo data (optional)
python manage.py seed_demo_data

# Start development server
python manage.py runserver 0.0.0.0:8000
```

**Backend URL:** `http://127.0.0.1:8000`
**API Docs:** `http://127.0.0.1:8000/api/docs/`
**Admin Panel:** `http://127.0.0.1:8000/admin/`

### To run the frontend React app:
```powershell
# FIRST, install Node.js from https://nodejs.org/ (LTS version)
# Then:

cd frontend
npm install
npm run dev
```

**Frontend URL:** `http://localhost:3000`

## Next Steps

### 1. **INSTALL NODE.JS** (CRITICAL)
   - Download from: https://nodejs.org/ 
   - Install Node.js 20.x LTS or higher
   - Restart PowerShell after installation
   - Verify with: `node --version`

### 2. **Complete Backend Setup**
   - Run: `python manage.py migrate` (if not done)
   - Run: `python manage.py seed_demo_data` (optional, creates demo logins)
   - Run: `python manage.py runserver 0.0.0.0:8000`

### 3. **Setup Frontend**
   - Navigate to `frontend` folder
   - Run: `npm install`
   - Run: `npm run dev`
   - Open: `http://localhost:3000`

## Demo Credentials (after running seed_demo_data)
See documentation in: `installation_guidance_anduserage/03-admin-teacher-student-guidance.md`

## Architecture
```
Frontend (React/Vite)         Backend (Django API)
http://localhost:3000    -->  http://127.0.0.1:8000
```

## Database
- **Development:** SQLite (default, file: `db.sqlite3`)
- **Production:** PostgreSQL (configured via DATABASE_URL env var)

## Key Configuration Files
- **Backend:** `backend/.env` - Environment variables
- **Backend:** `backend/config/settings/` - Django settings
- **Frontend:** `frontend/.env` - Frontend environment variables
- **Frontend:** `frontend/vite.config.js` - Vite build config

## Documentation
- Full guide: `docs/user-guide.md`
- Architecture: `docs/architecture.md`
- Deployment: `docs/deployment.md`
- Installation guidance: `installation_guidance_anduserage/`

---

**Last Updated:** May 30, 2026
