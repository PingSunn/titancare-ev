from llama_index.core.agent import FunctionAgent
from llama_index.llms.ollama import Ollama
from data_connectors import query_database_tool, search_brochures_tool

# Configure default Ollama LLM to point to local instance
local_llm = Ollama(model="llama3.1", request_timeout=360.0, context_window=8000)

def create_specialized_agent():
    """
    Creates the FunctionAgent equipped with PDF and SQL connector tools.
    """
    agent = FunctionAgent(
        tools=[query_database_tool, search_brochures_tool],
        llm=local_llm,
        system_prompt=(
            "You are TitanCare EV, a specialized assistant for car details and brochures. "
            "Use your tools to query the SQL database for structured car specs or "
            "search the PDF brochures for unstructured documentation. "
            "Always try to answer using factual data."
        )
    )
    return agent
