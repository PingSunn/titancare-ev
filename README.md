# TitanCare EV

An AI-powered chatbot for TitanCare EV that answers customer questions about car specifications and handles service appointment bookings, using a multi-agent architecture powered by local AI.

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│               (React + Vite + JavaScript)                   │
│                    localhost:5173                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────────┐
│                        Backend                              │
│              (FastAPI + LangChain + LangGraph)              │
│                    localhost:8000                           │
├─────────────────────────────────────────────────────────────┤
│                    Orchestrator Agent                       │
│                            │                                │
│             ┌──────────────┴──────────────┐                 │
│             ▼                             ▼                 │
│    Appointment Agent                  Car Agent             │
│   (SQL: appointments table)       (SQL cars table +         │
│                                    PDF Brochure RAG)        │
│             │                             │                 │
│             └──────────────┬──────────────┘                 │
│                            ▼                                │
│                     Summarizer Agent                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
       ┌──────────────┴──────────────┐
       ▼                             ▼
┌─────────────┐             ┌────────────────┐
│ titancare.db│             │  sessions.db   │
│  (SQLite)   │             │   (SQLite)     │
│ cars table  │             │ session history│
│ appointments│             └────────────────┘
└─────────────┘
```

## Project Structure

```text
titancare-ev/
├── backend/
│   ├── core_agents/            # LangGraph agent definitions
│   │   ├── orchestrator.py     # Routes to appointment or car agent
│   │   ├── appointment.py      # Booking & scheduling agent
│   │   ├── car.py              # Car details & specs agent
│   │   ├── summarizer.py       # Final response formatter
│   │   └── llm_config.py       # Ollama LLM configuration
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── appointment.py
│   │   └── car.py              # Car specs (imported from Excel)
│   ├── tools/                  # LangChain agent tools
│   │   ├── sql_tools.py        # Natural language → SQL query tool
│   │   ├── pdf_tools.py        # PDF brochure RAG search tool
│   │   └── appointment_tools.py
│   ├── data_connectors/        # DB & vector store connections
│   │   ├── sql_connector.py    # SQLAlchemy + LangChain SQLDatabase
│   │   └── pdf_connector.py    # FAISS vector store loader
│   ├── scripts/                # Utility scripts
│   │   ├── import_cars.py      # Excel → SQLite import (re-runnable)
│   │   └── verify_import.py    # Validate DB matches Excel source
│   ├── sessions/               # Async SQLite session management
│   │   └── db.py
│   ├── api/                    # FastAPI route handlers
│   ├── data/                   # PDF brochures for RAG
│   ├── titancare.db            # Main SQLite database
│   ├── sessions.db             # Session storage database
│   ├── database.py             # SQLAlchemy engine & session setup
│   ├── main.py                 # FastAPI application entry point
│   ├── pyproject.toml          # Dependencies (managed by uv)
│   └── .env.example            # Environment variable template
│
├── frontend/                   # React frontend (Vite + JavaScript)
│   ├── src/                    # React components & pages
│   ├── public/                 # Static assets
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.13+ with [`uv`](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.com/) running locally with `llama3` (or your preferred model)
- [Bun](https://bun.sh/) for frontend dependencies

### 1. Backend Setup

```bash
cd backend

# Copy environment template and configure
cp .env.example .env

# Start the FastAPI backend (uv installs dependencies automatically)
uv run main.py
```

### 2. Seed Car Data (first run)

Place `TITAN V.1.xlsx` in the project root, then run the import script to populate the database:

```bash
cd backend
uv run python scripts/import_cars.py
```

> **Re-runnable**: The script is idempotent — it clears and re-inserts all records on each run.
> To verify the import: `uv run python scripts/verify_import.py`

### 3. Frontend Setup

```bash
cd frontend
bun install
bun run dev
```

### 4. Access

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## Databases

| File | Engine | Purpose |
|---|---|---|
| `backend/titancare.db` | SQLite (SQLAlchemy) | Car inventory & appointment records |
| `backend/sessions.db` | SQLite (aiosqlite) | Conversational session history |
| `backend/data/` | FAISS (in-memory) | Vector embeddings for PDF brochure RAG |

## Car Inventory

Car data is imported from `TITAN V.1.xlsx` into the `cars` table with the following fields:

| Column | Description |
|---|---|
| `model` / `sub_model` | Brand & trim level |
| `starting_price` | Price in THB |
| `length_width_height_mm` | Exterior dimensions |
| `battery_capacity_kwh` / `range_km` | Battery & range |
| `ac_charging_port` / `dc_charging_port` | Charging speeds |
| `max_power_kw` / `max_torque_nm` | Motor performance |
| `acceleration_0_100_s` | 0–100 km/h time |
| `v2l` | Vehicle-to-Load support |

Currently includes **24 variants** across 9 brands: ALON UT, BYD ATTO 3, BYD SEALION 7, GEELY EX2, GEELY EX5, JAECOO 6 EV, MG ZS, MG 4 ELECTRIC, NETA V-II, TESLA Model 3.

## Features

- **Multi-Agent System**: LangGraph-based orchestrator routes queries to specialized agents.
- **Natural Language SQL**: Car agent translates questions into SQL queries via LangChain.
- **PDF Brochure RAG**: PyMuPDF + FAISS + HuggingFace Embeddings for detailed spec lookup.
- **Appointment Booking**: Full CRUD for service bookings stored in SQLite.
- **Local AI First**: Designed for local deployment via Ollama — no cloud API required.
- **Session Memory**: Async SQLite-backed conversational context per session.

## Model Configuration

Edit `backend/llms.txt` to map model aliases to your local Ollama endpoints:

```txt
llama3.1=ollama/llama3.1:latest
default=llama3.1
```

Update `OLLAMA_API_BASE` in `.env` if your Ollama runs on a different host/port.

## License

MIT
