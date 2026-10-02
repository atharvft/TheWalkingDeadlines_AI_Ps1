# Hinglish Order Desk for Small Shopkeepers

A prototype for converting casual Hinglish grocery orders (text/voice) into structured orders.

## Project Structure

```
hinglish-order-desk/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
├── ai/                # AI/ML modules (ASR, NLP, Matching, Rules)
├── data/              # Static/seed data (catalog, test cases, audio)
├── tests/             # Integration tests
├── scripts/           # Setup and utility scripts
├── docs/              # Documentation
├── .env.example       # Environment variables template
├── .gitignore
├── README.md
└── requirements.txt   # Python dependencies
```

## Quick Start

```bash
# Setup
./scripts/setup.sh

# Run backend
cd backend && python -m uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed architecture.