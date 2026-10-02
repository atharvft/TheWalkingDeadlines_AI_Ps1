# Hinglish Order Desk - Architecture Documentation

## Overview

This document describes the system architecture for the Hinglish Order Desk, a prototype for converting casual Hinglish grocery orders (text/voice) into structured orders.

## High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│  Backend    │────▶│   AI/ML     │
│  (React)    │     │  (FastAPI)  │     │  (Python)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Database   │
                    │  (SQLite)   │
                    └─────────────┘
```

## Module Responsibilities

### Frontend (`frontend/`)
- Text/voice order input
- Transcript display
- Parsed order display
- Matched products with confidence
- Ambiguity/clarification UI
- Order confirmation
- Bill & delivery note display

### Backend (`backend/`)
- **API Layer** (`app/api/`): Thin HTTP route handlers
- **Core** (`app/core/`): Config, logging, exceptions, middleware
- **Database** (`app/db/`): SQLAlchemy setup, sessions, migrations
- **Models** (`app/models/`): SQLAlchemy ORM models
- **Schemas** (`app/schemas/`): Pydantic request/response models
- **Services** (`app/services/`): Business logic orchestration
- **Repositories** (`app/repositories/`): Data access layer
- **State** (`app/state/`): In-memory order conversation state

### AI/ML (`ai/`)
- **ASR** (`ai/asr/`): Whisper-based speech-to-text
- **NLP** (`ai/nlp/`): Hinglish parsing & normalization
- **Matching** (`ai/matching/`): Fuzzy + semantic product matching
- **Rules** (`ai/rules/`): Ambiguity, stock, quantity, unit validation
- **Models** (`ai/models/`): Model configuration

### Data (`data/`)
- Static catalog, aliases, categories
- Sample orders for testing
- Audio test files
- Test cases (normal, ambiguous, out-of-stock)

## Data Flow

```
User Input (Text/Voice)
         │
         ▼
Frontend (Input UI)
         │
         ▼
Backend API (/api/orders or /api/orders/voice)
         │
         ▼
Order Service (Orchestration)
         │
         ├──▶ AI ASR (voice only)
         ├──▶ AI NLP (parse Hinglish)
         ├──▶ AI Matching (catalog match)
         ├──▶ AI Rules (validate)
         │
         ▼
Validation Results
         │
         ├── Resolved ──▶ Confirm Order ──▶ Billing ──▶ Bill + Delivery Note
         │
         └── Ambiguous ──▶ Clarification Service ──▶ User Answers ──▶ Re-validate
```

## Database Schema

- **products**: Catalog items with aliases
- **inventory**: Stock levels per product
- **orders**: Main order entity
- **order_items**: Line items per order
- **conversation_state**: Persistent clarification state

## Key Design Principles

1. **Separation of Concerns**: AI understands language; backend owns data/truth
2. **Layered Architecture**: API → Service → Repository → Database
3. **No Direct DB Access**: AI modules never touch database
4. **Deterministic Billing**: Prices from DB, not AI
5. **Static Data Separation**: Catalog data in `data/`, runtime DB in `backend/data/`