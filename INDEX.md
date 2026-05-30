# 📌 Setup Documentation Index

Welcome! Your Django Online Test Website has been set up. Use this index to find what you need.

---

## 🚀 **START HERE** ⭐

### **[README_SETUP.md](README_SETUP.md)** ← READ THIS FIRST
- ✅ What has been accomplished
- ❌ What still needs to be done
- 🚀 How to run the application
- ❓ Frequently asked questions

**Time to read:** 5 minutes

---

## 📚 Complete Guides

### **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Full summary
All details about what was done, what's ready, and what's next.

### **[QUICK_START.md](QUICK_START.md)** - 5-minute reference
Essential commands, URLs, and quick fixes.

### **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Step-by-step
Detailed checklist to verify everything is working correctly.

### **[FILE_GUIDE.md](FILE_GUIDE.md)** - Documentation map
Guide to all the files and what they contain.

---

## 🎯 For Different Situations

### "I just want to start the app"
👉 Read: **README_SETUP.md** → Section: "After Installation"

### "Something isn't working"
👉 Read: **SETUP_CHECKLIST.md** → Section: "Troubleshooting"

### "I need the commands quickly"
👉 Read: **QUICK_START.md**

### "I want to understand the full setup"
👉 Read: **SETUP_COMPLETE.md**

### "I'm new to this project"
👉 Read in order:
1. **README_SETUP.md** (overview)
2. **QUICK_START.md** (commands)
3. **SETUP_CHECKLIST.md** (details)

---

## 🔧 Startup Scripts

Quick commands to get everything running:

```powershell
# Start Django backend
.\run_backend.ps1

# Then in another terminal, start React frontend
cd frontend
npm install
npm run dev
```

---

## 📍 What's Ready

| Component | Status | Start With |
|-----------|--------|-----------|
| **Backend (Django)** | ✅ Ready | `.\run_backend.ps1` |
| **Frontend (React)** | ⏳ Waiting | Install Node.js first |
| **Database** | ✅ Ready | Automatic |
| **Admin Panel** | ✅ Ready | After creating user |

---

## 🚨 What You Need To Do NOW

1. **Install Node.js** from https://nodejs.org/ (LTS version)
2. **Restart your terminal** after installing Node.js
3. **Run the startup script:**
   ```powershell
   .\run_backend.ps1
   ```

That's it! Frontend setup is automatic.

---

## 🌐 Access URLs (after running)

```
Main App:    http://localhost:3000
API:         http://127.0.0.1:8000
API Docs:    http://127.0.0.1:8000/api/docs/
Admin Panel: http://127.0.0.1:8000/admin/
```

---

## 📂 Original Documentation

(From the project, still helpful for features and deployment)

```
docs/
├── user-guide.md           # Feature guide
├── architecture.md         # System design
├── deployment.md           # Production setup
├── quickstart-admin.md
├── quickstart-teacher.md
└── quickstart-student.md

installation_guidance_anduserage/
├── 01-downloads-and-versions.md
├── 02-installation-on-new-laptop.md
├── 03-admin-teacher-student-guidance.md
└── 04-deploy-online.md
```

---

## ✅ Quick Status

```
Backend:  ✅ INSTALLED & READY
Frontend: ⏳ READY (needs Node.js)
Database: ✅ INITIALIZED
```

---

## 🎯 Your Checklist

- [ ] Read README_SETUP.md (5 min)
- [ ] Install Node.js from nodejs.org
- [ ] Restart terminal
- [ ] Run: `.\run_backend.ps1`
- [ ] In new terminal: `cd frontend && npm install && npm run dev`
- [ ] Open http://localhost:3000
- [ ] Create admin: `python manage.py createsuperuser`
- [ ] Login and test!

---

## 💡 Pro Tips

- **First npm install** takes 2-5 minutes (it's normal)
- **Backend reloads automatically** when you edit files
- **Keep 2 terminals open:** one for backend, one for frontend
- **Check API docs first:** http://127.0.0.1:8000/api/docs/

---

## ❓ Need Help?

1. Check the relevant documentation file above
2. Look in **SETUP_CHECKLIST.md** → Troubleshooting section
3. Run: `python manage.py check` (for Django issues)
4. Check `.env` files are correct

---

## 🎉 Ready to Begin?

👉 **[Open README_SETUP.md](README_SETUP.md)**

---

**Project:** MIT Online Examination Platform  
**Updated:** May 30, 2026  
**Status:** ✅ Backend Ready | ⏳ Frontend Ready (just needs Node.js)
