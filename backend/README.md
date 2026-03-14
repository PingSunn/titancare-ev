# TitanCare EV — Backend API

Multi-agent AI backend for the TitanCare EV dealership assistant. Handles car queries (specs, inventory, brochures) and appointment scheduling via a LangGraph orchestrator.

---

## Architecture

```
POST /api/v1/chat
        │
        ▼
  Orchestrator (LLM router)
        │
   ┌────┴────────────┐
   ▼                 ▼
car_node       appointment_node
   │
 ┌─┴──────────────────┐
 ▼                    ▼
query_database    search_brochures
(SQL / Supabase)  (PDF RAG / FAISS)
```

**Agents**

| Agent | File | Responsibility |
|-------|------|----------------|
| Orchestrator | `core_agents/orchestrator.py` | Routes messages to the correct agent |
| Car | `core_agents/car.py` | Specs, inventory, PDF brochure lookup |
| Appointment | `core_agents/appointment.py` | Book/manage service appointments |
| Summarizer | `core_agents/summarizer.py` | Condenses long tool outputs |

**Tools**

| Tool | File | Description |
|------|------|-------------|
| `query_database` | `tools/sql_tools.py` | Natural language → SQL against Supabase (Prisma) |
| `search_brochures` | `tools/pdf_tools.py` | FAISS RAG over PDF brochures in `data/` |

---

## Stack

- **Framework**: FastAPI + Uvicorn
- **AI**: LangChain + LangGraph + LangChain-Ollama
- **LLM**: Ollama (`qwen3:8b` by default, configurable via `llms.txt`)
- **Embeddings**: `BAAI/bge-base-en-v1.5` (HuggingFace, runs locally)
- **Vector store**: FAISS (in-memory, rebuilt on startup)
- **Database**: Supabase (PostgreSQL via Prisma)
- **Session storage**: SQLite (aiosqlite)
- **Python**: 3.13+ / managed with `uv`

---

## Quick Start (Docker) — for frontend dev

**Prerequisites:** Docker Desktop installed and running.

```bash
# 1. Copy env and fill in Supabase credentials
cp .env.example .env

# 2. Start the backend
docker compose up -d
```

API is now available at `http://localhost:8000`.

Health check: `curl http://localhost:8000/api/v1/health`

To stop: `docker compose down`

---

## Local Dev Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

Copy and fill in `.env`:

```bash
# Ollama endpoint (local or remote)
OLLAMA_API_BASE=http://localhost:11434
# OLLAMA_API_BASE=http://<remote-host>:11434

# Supabase
DATABASE_URL="postgresql://..."
DIRECT_URL="postgresql://..."
```

### 3. Generate Prisma client

```bash
uv run prisma generate
```

### 4. Add PDF brochures

Place PDF files in `backend/data/`. They are loaded and chunked into FAISS on startup.

Currently available brochures:
- ALON UT, BYD ATTO 3, BYD SEALION 7, GEELY EX2, GEELY EX5
- JAECOO 6 EV, MG 4, MG ZS, NETA V-II, Tesla Model 3 (2024+)

### 5. Run the server

```bash
uv run python main.py
```

Server starts at `http://localhost:8000`.

---

## Switch LLM Model

Edit `llms.txt` and change the `default` alias:

```
default=qwen3        # qwen3:8b (current)
# default=llama3.1  # llama3.1:latest
```

Restart the server after changes.

---

## API

### `POST /api/v1/chat`

```json
{
  "session_id": "uuid-string",
  "message": "What is the battery capacity of the MG 4 XPOWER?"
}
```

Response:

```json
{
  "reply": "The MG 4 ELECTRIC (XPOWER) has a 64 kWh battery and 600 Nm of torque."
}
```

### `GET /api/v1/health`

Returns `{ "status": "ok" }`.

---

## Testing

Requires a running server at `localhost:8000`, Supabase connection, and Ollama.

```bash
# Run all integration tests
uv run pytest tests/test_integration.py -v --timeout=300

# Run specific tests
uv run pytest tests/test_integration.py::test_chat_car_details tests/test_integration.py::test_chat_unsupported_car -v --timeout=300
```
