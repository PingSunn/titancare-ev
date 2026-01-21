# TitanCare Backend

Multi-agent AI backend built with [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), FastAPI, and Redis session storage.

## Architecture

```
User Request
     │
     ▼
┌─────────────────┐
│  FastAPI API    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ ◄── Decides which specialized agent to use
│     Agent       │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐   ┌───────┐
│Agent A│ │Agent B│...│Agent N│  ◄── Specialized agents
└───┬───┘ └───┬───┘   └───┬───┘
    │         │           │
    └────┬────┴───────────┘
         │
         ▼
┌─────────────────┐
│   Summarizer    │ ◄── Creates final cohesive response
│     Agent       │
└────────┬────────┘
         │
         ▼
    Final Response
```

## Project Structure

```
backend/
├── pyproject.toml              # Dependencies (uv)
├── .env.example                # Environment template
├── docker-compose.yml          # Redis + Backend services
├── Dockerfile                  # Container build
├── config.py                   # Configuration (pydantic-settings)
├── llms.txt                    # Model alias mapping
├── main.py                     # FastAPI entry point
│
├── core_agents/                # Agent definitions
│   ├── orchestrator_agent.py   # Central decision maker
│   ├── summarizer_agent.py     # Response synthesizer
│   └── specialized/            # Task-specific agents
│       ├── general_assistant_agent.py
│       └── _template_agent.py  # Template for new agents
│
├── models/                     # LLM configuration
│   └── loader.py               # Model registry from llms.txt
│
├── tools/                      # Function tools for agents
│   └── example_tools.py        # @function_tool examples
│
├── sessions/                   # Session management
│   └── redis_session.py        # Redis session wrapper
│
└── api/                        # API routes
    └── routes.py               # Chat endpoints
```

## Quick Start

### 1. Setup Environment

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - GOOGLE_API_KEY (for Gemini)
# - ANTHROPIC_API_KEY (for Claude)
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Run for Development (Recommended)

```bash
# Start Redis + RedisInsight GUI
docker-compose up redis redisinsight -d

# Run backend locally with hot reload
uv run uvicorn main:app --reload

# Access:
#   Backend API:  http://localhost:8000
#   RedisInsight: http://localhost:5540 (connect to: redis://redis:6379)
```

### 4. Run All in Docker (Production)

```bash
# Start Redis + Backend
docker-compose --profile full up -d

# View logs
docker-compose logs -f backend
```

### 5. Redis Data Management

```bash
# Redis data persists in Docker volume
# To check volume:
docker volume ls | grep redis

# To clear Redis data:
docker-compose down
docker volume rm backend_redis_data
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Send message to agents |
| `POST` | `/api/session` | Create new session |
| `GET` | `/api/models` | List available models |
| `DELETE` | `/api/session/{id}` | Clear session |

### Chat Request Example

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "session_id": "optional-session-id",
    "model": "gemini-flash"
  }'
```

### Response

```json
{
  "response": "Agent's response here...",
  "session_id": "session_abc123"
}
```

## Model Configuration

Models are configured in `llms.txt` using simple alias mapping:

```txt
# OpenAI (direct)
gpt4o=gpt-4o

# Gemini (via LiteLLM)
gemini-flash=litellm/gemini/gemini-2.0-flash

# Claude (via LiteLLM)
claude-sonnet=litellm/anthropic/claude-3-5-sonnet-20241022

# Default model
default=litellm/gemini/gemini-2.0-flash
```

Use aliases in API requests: `"model": "gemini-flash"`

## Creating New Agents

1. **Copy the template:**
   ```bash
   cp core_agents/specialized/_template_agent.py \
      core_agents/specialized/my_new_agent.py
   ```

2. **Edit your agent file:**
   - Update function name: `create_my_new_agent()`
   - Customize instructions
   - Add relevant tools
   - Set `handoff_description`

3. **Register in `specialized/__init__.py`:**
   ```python
   from .my_new_agent import create_my_new_agent
   
   def get_specialized_agents(model_registry):
       return [
           create_general_assistant_agent(model_registry),
           create_my_new_agent(model_registry),  # Add here
       ]
   ```

## Creating Custom Tools

Use the `@function_tool` decorator in `tools/`:

```python
from agents import function_tool

@function_tool
def my_custom_tool(param1: str, param2: int) -> str:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    """
    # Your implementation
    return f"Result: {param1}, {param2}"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google Gemini API key | - |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | - |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `DEFAULT_MODEL` | Default model alias | `gemini-flash` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Debug mode | `false` |

## Session Management

Sessions are stored in Redis for conversation continuity:

```python
from sessions import get_redis_session

# Get or create a session
session = get_redis_session("user_123")

# Use with Runner
result = await Runner.run(agent, "message", session=session)
```

## License

MIT
