#!/bin/bash
# Setup script for Hinglish Order Desk (Linux/macOS)

set -e

echo "🚀 Setting up Hinglish Order Desk..."

# Check Python version
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt
cd backend && pip install -r requirements.txt && cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Create database directory
mkdir -p backend/data

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

echo "✅ Setup complete!"
echo ""
echo "To run the project:"
echo "  Backend:  cd backend && python -m uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"