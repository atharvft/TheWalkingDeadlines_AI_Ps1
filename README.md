# Hinglish Order Desk for Small Shopkeepers

A demo-ready Hinglish/FMCG transaction resolver. Text and browser voice notes are
normalized, parsed, matched against the catalog, validated against SQLite stock,
clarified when needed, and billed deterministically.

## Project Structure

```
hinglish-order-desk/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
├── ai/                # Deterministic NLP, matching, and business rules
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
# Setup (Python 3.11 is required by the pinned FastAPI/Pydantic stack)
./scripts/setup.sh

# Run backend
cd backend && python -m uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev
```

Voice transcription is performed by OpenAI on the backend. API keys are never
sent to the browser and no local speech model is loaded during startup.

Copy `.env.example` to a backend-only `.env` and configure `OPENAI_API_KEY`
for transcription plus `GEMINI_API_KEY` or `OPENAI_API_KEY` for order parsing.

## BigBasket catalog pipeline

Keep the downloaded Kaggle CSV unchanged under `data/raw/`, then build the
application catalog:

```bash
python scripts/build_catalog.py data/raw/bigbasket.csv
python scripts/seed_data.py
```

The application automatically prefers `data/catalog/normalized_products.json`
when present and otherwise uses the small curated fallback catalog included for
offline demos. The normalized catalog carries source IDs, pack sizes, aliases,
brands, categories, and prices; SQLite is seeded from that output.

## Verification

```bash
python -m pytest -q
cd frontend && npm run build
```

For a live text request, use `POST /api/orders/parse`. For voice, upload a
browser recording to `POST /api/transcribe`, then send the returned transcript
to the same order endpoint.

The API keeps clarification state in SQLite, so an answer such as `sunflower`
or `1L` updates the pending item instead of restarting the order.

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed architecture.
