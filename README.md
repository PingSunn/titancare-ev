# TitanCare EV

An AI Agent chatbot that supports user questions using a multi-agent architecture powered by local AI capabilities.

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
│                (FastAPI + LlamaIndex)                       │
│                    localhost:8000                           │
├─────────────────────────────────────────────────────────────┤
│  Data Connectors ──► Specialized Agents                     │
│  (SQL & PDF RAG)                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     SQLite                                  │
│             (Structured Data & Sessions)                    │
│                 Local DB Files                              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```text
titancare-ev/
├── backend/                    # Python backend (FastAPI + LlamaIndex)
│   ├── core_agents/            # Agent definitions
│   │   └── specialized.py
│   ├── api/                    # FastAPI routes
│   ├── data_connectors/        # SQL and PDF integrations
│   │   ├── sql_connector.py
│   │   └── pdf_connector.py
│   ├── sessions/               # SQLite session management
│   ├── llms.txt                # LiteLLM/Local Ollama model mapping
│   ├── pyproject.toml          # uv managed dependencies
│   └── main.py                 # FastAPI entry point
│
├── frontend/                   # React frontend (Vite + JavaScript)
│   ├── public/                 # Static assets
│   ├── src/                    # React source code folder
│   ├── package.json            # Managed by Bun
│   └── vite.config.js          # Vite configuration
│
└── README.md                   # Project documentation
```

## Quick Start

### Prerequisites

- Python 3.13+ (using `uv` package manager)
- Bun (for JavaScript dependencies)
- Local Ollama setup (for models)

### 1. Backend Setup

```bash
cd backend

# Copy environment template
cp .env.example .env

# Run FastAPI backend (uv handles dependencies automatically)
uv run main.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies using Bun
bun install

# Start dev server
bun run dev
```

### 3. Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

- **Multi-Agent System**: Agents armed with tools to assist locally using LlamaIndex workflows.
- **Data Integration**: Incorporates PDF brochures (RAG via PyMuPDF + local HuggingFace Embeddings) and relational databases (SQLAlchemy engine).
- **Local AI Strategy**: Designed natively for local deployment models via Ollama.
- **Session Memory**: SQLite-based conversational persistence.
- **Modern UI**: Scalable React framework initialized via blazing-fast Vite + Bun.

## Model Configuration

Edit `backend/llms.txt` to configure your primary models and aliases connecting your local `ollama` endpoints.

```txt
ollama/llama3=ollama/llama3
default=ollama/llama3
```

## License

MIT
