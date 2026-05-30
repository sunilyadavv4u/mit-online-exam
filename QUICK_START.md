# 🚀 Quick Start Guide - Django Online Test Website

> **MIT Online Examination Platform** - A production-ready online exam system with Django backend and React frontend

---

## 📋 Prerequisites

### Required (must install first)
- **Python 3.11+** (tested with 3.12, 3.14) → [Download](https://www.python.org/downloads/)
- **Node.js 20.x LTS** → [Download](https://nodejs.org/) (REQUIRED for frontend)

### Optional (for production)
- PostgreSQL 14+
- Redis 7.x
- Docker Desktop

---

## ⚡ Quick Start (5 minutes)

### 1️⃣ Start Backend (Django API)

**PowerShell:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**Or use the script:**
```powershell
.\run_backend.ps1
```

✅ **Backend ready at:** http://127.0.0.1:8000

### 2️⃣ Start Frontend (React App)

**In a new terminal:**
```powershell
cd frontend
npm install
npm run dev
```

✅ **Frontend ready at:** http://localhost:3000

---

## 📚 Important URLs

| Component | URL |
|-----------|-----|
| **Main App** | http://localhost:3000 |
| **API** | http://127.0.0.1:8000 |
| **API Docs** | http://127.0.0.1:8000/api/docs/ |
| **Admin Panel** | http://127.0.0.1:8000/admin/ |

---

## 🔑 Create Admin User

```powershell
cd backend
python manage.py createsuperuser
```

Then login at: http://127.0.0.1:8000/admin/

---

## 📦 Create Demo Data (Optional)

Includes 1 admin, 1 teacher, 15 students, and sample exams:

```powershell
cd backend
python manage.py seed_demo_data
```

---

## 📁 Project Structure

```
Online_Test_website/
├── backend/                  # Django API
│   ├── apps/                # Django apps (users, exams, questions, etc.)
│   ├── config/              # Django configuration
│   ├── requirements.txt      # Python dependencies
│   └── manage.py            # Django CLI
├── frontend/                # React + Vite
│   ├── src/                # React components
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
├── docs/                   # Documentation
└── installation_guidance/  # Setup guides
```

---

## 🛠️ Common Commands

### Backend

```bash
# Activate environment
cd backend
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create demo data
python manage.py seed_demo_data

# Start server
python manage.py runserver

# Run tests
pytest

# Create static files
python manage.py collectstatic --noinput
```

### Frontend

```bash
cd frontend

# Install packages
npm install

# Development server
npm run dev

# Build for production
npm build

# Preview build
npm preview
```

---

## 🐛 Troubleshooting

### "Python not found"
```powershell
py --version
# If works, use 'py' instead of 'python'
```

### "Node not found"
→ Install Node.js from https://nodejs.org/ and restart terminal

### "Virtual environment not activating"
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### "Port 8000 already in use"
```powershell
python manage.py runserver 0.0.0.0:8001
```

### "pip install hangs or times out"
```powershell
pip install --no-cache-dir -r requirements.txt
```

---

## 📖 Full Documentation

- **Installation Guide:** `installation_guidance_anduserage/02-installation-on-new-laptop.md`
- **User Guide:** `docs/user-guide.md`
- **Architecture:** `docs/architecture.md`
- **Deployment:** `docs/deployment.md`

---

## 🎯 Next Steps

1. ✅ Backend running at http://127.0.0.1:8000
2. ✅ Frontend running at http://localhost:3000
3. 📝 Create admin user (see above)
4. 🎓 Create students and exams in admin panel or use demo data
5. 📚 Check documentation for features and workflows

---

## 🚀 Deployment

For deploying to production:
- See: `docs/deployment.md`
- Docker: `docker-compose.yml`
- Environment: Copy `.env.example` to `.env` and update variables

---

## 💬 Support

- Check documentation in `docs/` folder
- Installation guides in `installation_guidance_anduserage/`
- API docs at http://127.0.0.1:8000/api/docs/ (Swagger)

---

**Built with ❤️ by Mewati Institute of Technology**
