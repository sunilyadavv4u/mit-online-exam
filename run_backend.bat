@echo off
REM Django Online Test Website - Backend Setup Script for Windows
REM This script sets up and runs the Django backend server

echo ========================================
echo MIT Online Examination Platform
echo Backend Setup & Run Script
echo ========================================
echo.

cd backend

REM Create virtual environment if not exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    py -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -q Django djangorestframework djangorestframework-simplejwt drf-spectacular django-cors-headers django-filter dj-database-url python-decouple -q

REM Run migrations
echo Running database migrations...
python manage.py migrate --no-input

REM Seed demo data (optional)
echo.
echo Demo data setup (optional):
echo If you want to create demo users, run: python manage.py seed_demo_data
echo.

REM Start server
echo.
echo ========================================
echo Starting Django Development Server...
echo ========================================
echo.
echo Backend API: http://127.0.0.1:8000
echo API Docs:    http://127.0.0.1:8000/api/docs/
echo Admin:       http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000
