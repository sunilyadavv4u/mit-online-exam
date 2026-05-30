# 📋 New Setup Documentation - File Reference

These files were created to help you quickly set up and run the Django Online Test Website.

---

## 🚀 START HERE

### 1. **README_SETUP.md** ⭐ PRIMARY GUIDE
   - What has been accomplished
   - What you still need to do (Install Node.js)
   - Complete step-by-step instructions
   - Common questions answered
   - **READ THIS FIRST!**

---

## 📖 Reference Guides

### 2. **QUICK_START.md**
   - Quick 5-minute setup overview
   - Essential commands
   - Common URLs and ports
   - Troubleshooting for common issues
   - **Good for quick reference**

### 3. **SETUP_CHECKLIST.md**
   - Detailed step-by-step checklist
   - Prerequisites verification
   - Backend setup steps
   - Frontend setup steps
   - Test verification steps
   - Common commands reference
   - **Best for following along step-by-step**

### 4. **SETUP_STATUS.md**
   - Current installation status
   - What's complete vs. in-progress
   - Architecture overview
   - Configuration details
   - **Good for understanding current state**

---

## 🔧 Startup Scripts

### 5. **run_backend.ps1**
   - PowerShell script to start backend
   - Automatically creates venv if needed
   - Installs dependencies
   - Runs migrations
   - Starts Django server on port 8000
   - **Usage:** `.\run_backend.ps1`

### 6. **run_backend.bat**
   - Batch file version for Command Prompt
   - Same functionality as PowerShell script
   - **Usage:** `run_backend.bat`

---

## 📁 File Tree

```
Online_Test_website/
├── README_SETUP.md ⭐ START HERE
├── QUICK_START.md
├── SETUP_CHECKLIST.md
├── SETUP_STATUS.md
├── run_backend.ps1
├── run_backend.bat
│
├── backend/
│   ├── requirements.txt
│   ├── requirements-basic.txt (created by setup)
│   ├── .env
│   ├── manage.py
│   └── ...
│
├── frontend/
│   ├── package.json
│   ├── .env
│   └── ...
│
├── docs/
│   ├── user-guide.md
│   ├── architecture.md
│   └── ...
│
└── installation_guidance_anduserage/
    ├── 01-downloads-and-versions.md
    ├── 02-installation-on-new-laptop.md
    ├── 03-admin-teacher-student-guidance.md
    └── 04-deploy-online.md
```

---

## ✅ Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Python | ✅ Ready | 3.14 installed and configured |
| Django | ✅ Ready | Version 5.1.15 with all packages |
| Virtual Env | ✅ Ready | Located at `backend/.venv` |
| Database | ✅ Ready | SQLite initialized |
| Backend Server | ✅ Ready | Can start with one command |
| Node.js | ❌ Missing | **REQUIRED** - Install from nodejs.org |
| Frontend | ⏳ Waiting | Ready once Node.js is installed |

---

## 🚀 Quick Commands

### Start Backend (Django API)
```powershell
.\run_backend.ps1
```

### Start Frontend (React App)
```powershell
cd frontend
npm install      # First time only
npm run dev
```

### Access Application
| URL | Purpose |
|-----|---------|
| http://localhost:3000 | Main web application |
| http://127.0.0.1:8000 | Backend API |
| http://127.0.0.1:8000/api/docs/ | API documentation |
| http://127.0.0.1:8000/admin/ | Django admin panel |

---

## 📚 Original Documentation

These are the original setup guides from the project:

1. `installation_guidance_anduserage/01-downloads-and-versions.md`
   - What to download before installing

2. `installation_guidance_anduserage/02-installation-on-new-laptop.md`
   - Step-by-step installation for Windows (original guide)

3. `installation_guidance_anduserage/03-admin-teacher-student-guidance.md`
   - How to create users and use the system

4. `installation_guidance_anduserage/04-deploy-online.md`
   - Production deployment guide

---

## 🎯 Reading Order

For best results, read in this order:

1. **README_SETUP.md** - Understand what's done and what's next
2. **QUICK_START.md** - Get the commands you need
3. **SETUP_CHECKLIST.md** - Follow step-by-step if something needs fixing
4. **Original guides** - Refer to for detailed information

---

## 🔑 Key Information

### What's Already Done
- ✅ Backend fully configured and ready
- ✅ Python environment set up
- ✅ Database initialized
- ✅ all Django packages installed
- ✅ Django development server can start immediately

### What You Need To Do
- ❌ Install Node.js (critical requirement)
- Then: `npm install && npm run dev` in frontend folder

### Before Running
1. Install Node.js from https://nodejs.org/
2. Restart your terminal
3. Run the startup scripts

---

## 💡 Tips

- **First run will be slow:** npm install takes 2-5 minutes
- **Subsequent runs are fast:** < 30 seconds after first setup
- **Backend starts instantly:** Django reloads automatically on file changes
- **Keep two terminals open:** One for backend, one for frontend

---

## ❓ Need Help?

1. Check the **Troubleshooting** section in SETUP_CHECKLIST.md
2. Run: `python manage.py check` (for Django issues)
3. Check environment variables in `.env` files
4. Refer to original documentation in `docs/` and `installation_guidance_anduserage/`

---

## 📞 File Purposes at a Glance

| File | Purpose | When to Use |
|------|---------|------------|
| README_SETUP.md | Complete setup overview | First thing to read |
| QUICK_START.md | Essential commands quick ref | Need commands quickly |
| SETUP_CHECKLIST.md | Detailed verification steps | Troubleshooting or detailed setup |
| SETUP_STATUS.md | Current status report | Understanding what's installed |
| run_backend.ps1 | Automated backend startup | To start the Django server |
| run_backend.bat | Alternative startup method | If using Command Prompt |

---

**Last Updated:** May 30, 2026  
**Project:** MIT Online Examination Platform  
**Status:** Backend ✅ Ready | Frontend ⏳ Waiting for Node.js
