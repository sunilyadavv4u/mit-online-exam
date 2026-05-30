# Django Online Test Website - Backend Setup Script for PowerShell
# This script sets up and runs the Django backend server

Write-Host "========================================" -ForegroundColor Green
Write-Host "MIT Online Examination Platform" -ForegroundColor Green
Write-Host "Backend Setup & Run Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$backendPath = "backend"
cd $backendPath

# Create virtual environment if not exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    py -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# List of core packages needed
$essentialPackages = @(
    "Django>=5.0,<5.2",
    "djangorestframework>=3.15",
    "djangorestframework-simplejwt>=5.3",
    "drf-spectacular>=0.27",
    "django-cors-headers>=4.3",
    "django-filter>=24.2",
    "dj-database-url>=2.2",
    "python-decouple>=3.8",
    "celery>=5.4",
    "redis>=5.0",
    "django-redis>=5.4",
    "Pillow>=10.4",
    "gunicorn>=22.0",
    "requests>=2.32"
)

Write-Host "Installing core Python packages..." -ForegroundColor Yellow
foreach ($package in $essentialPackages) {
    pip install -q $package
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate --no-input

Write-Host ""
Write-Host "Demo data setup (optional):" -ForegroundColor Cyan
Write-Host "If you want to create demo users, run:" -ForegroundColor Cyan
Write-Host "  python manage.py seed_demo_data" -ForegroundColor Yellow
Write-Host ""

# Start server
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Django Development Server..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Docs:    http://127.0.0.1:8000/api/docs/" -ForegroundColor Cyan
Write-Host "Admin:       http://127.0.0.1:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

python manage.py runserver 0.0.0.0:8000
