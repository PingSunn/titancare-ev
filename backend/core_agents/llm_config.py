import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

def get_llm():
    """Reads llms.txt, resolves the default alias, and returns the configured LLM."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "llms.txt")

    aliases = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    aliases[key.strip()] = val.strip()

    # Resolve default model
    model_val = aliases.get("default", "llama3.1")

    # Resolve through aliases (e.g., default -> stepfun-flash -> openrouter/...)
    visited = set()
    while model_val in aliases and model_val not in visited:
        visited.add(model_val)
        model_val = aliases[model_val]

    # OpenRouter provider
    if model_val.startswith("openrouter/"):
        model_id = model_val[len("openrouter/"):]
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        return ChatOpenAI(
            model=model_id,
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    # Ollama provider (default)
    if model_val.startswith("ollama/"):
        model_val = model_val[len("ollama/"):]
    ollama_base_url = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    return ChatOllama(model=model_val, temperature=0.0, base_url=ollama_base_url)

# Create a singleton instance for global use
local_llm = get_llm()
