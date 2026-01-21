# TitanCare

An AI Agent chatbot that supports user questions using a multi-agent architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              (React + Vite + shadcn/ui)                     │
│                   localhost:5173                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────────┐
│                        Backend                               │
│                (FastAPI + OpenAI Agents SDK)                │
│                   localhost:8000                             │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator Agent ──► Specialized Agents ──► Summarizer   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Redis                                    │
│               (Session Storage)                              │
│                   localhost:6379                             │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
titancare-ev/
├── backend/                    # Python backend (FastAPI + Agents SDK)
│   ├── core_agents/            # Agent definitions
│   │   ├── orchestrator_agent.py
│   │   ├── summarizer_agent.py
│   │   └── specialized/
│   ├── api/                    # FastAPI routes
│   ├── models/                 # LLM model mapping (llms.txt)
│   ├── tools/                  # Custom function tools
│   ├── sessions/               # Redis session management
│   ├── docker-compose.yml      # Redis + Backend services
│   └── README.md               # Backend documentation
│
├── frontend/                   # React frontend (Vite + shadcn/ui)
│   ├── src/
│   │   ├── components/chat/    # Chat UI components
│   │   ├── hooks/              # React hooks
│   │   ├── services/           # API client
│   │   └── types/              # TypeScript types
│   └── package.json
│
└── .gitignore
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Redis)

### 1. Backend Setup

```bash
cd backend

# Copy environment template and add API keys
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, GOOGLE_API_KEY, etc.)

# Start Redis + Backend with Docker
docker-compose up -d

# Or run locally
uv sync
uv run uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

- **Multi-Agent System**: Orchestrator routes requests to specialized agents
- **LiteLLM Support**: Use OpenAI, Gemini, Claude via simple model aliases
- **Session Memory**: Redis-backed conversation persistence
- **Modern UI**: ChatGPT-style interface with shadcn/ui components

## Model Configuration

Edit `backend/llms.txt` to configure model aliases:

```txt
gpt4o=gpt-4o
gemini-flash=litellm/gemini/gemini-2.0-flash
claude-sonnet=litellm/anthropic/claude-3-5-sonnet-20241022
default=litellm/gemini/gemini-2.0-flash
```

## License

MIT
