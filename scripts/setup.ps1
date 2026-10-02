# Setup script for Hinglish Order Desk (Windows PowerShell)

Write-Host '🚀 Setting up Hinglish Order Desk...' -ForegroundColor Green

# Check Python version
python --version

# Create virtual environment
Write-Host '📦 Creating virtual environment...' -ForegroundColor Cyan
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install backend dependencies
Write-Host '📦 Installing backend dependencies...' -ForegroundColor Cyan
pip install -r requirements.txt
cd backend; pip install -r requirements.txt; cd ..

# Install frontend dependencies
Write-Host '📦 Installing frontend dependencies...' -ForegroundColor Cyan
cd frontend; npm install; cd ..

# Create database directory
New-Item -ItemType Directory -Force -Path "backend\data" | Out-Null

# Copy environment file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host '✅ Created .env from .env.example' -ForegroundColor Green
}

Write-Host '✅ Setup complete!' -ForegroundColor Green
Write-Host ''
Write-Host 'To run the project:' -ForegroundColor Yellow
Write-Host '  Backend:  cd backend; python -m uvicorn app.main:app --reload' -ForegroundColor White
Write-Host '  Frontend: cd frontend; npm run dev' -ForegroundColor White