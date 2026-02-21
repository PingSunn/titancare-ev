from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from tools.sql_tools import query_database_tool
from tools.pdf_tools import search_brochures_tool

local_llm = Ollama(model="llama3.1", request_timeout=360.0, context_window=8000)

def create_question_agent():
    agent = FunctionAgent(
        name="QuestionAgent",
        description="Search for car details and specs using the SQL database or PDF brochures. Pass notes to the SummarizerAgent.",
        system_prompt=(
            "You are a specialized agent for car details and brochures. "
            "Use your tools to query the SQL database for structured car specs or "
            "search the PDF brochures for unstructured documentation. "
            "Once you have gathered the necessary facts, immediately hand off to the SummarizerAgent "
            "with your notes so it can formulate the final response."
        ),
        llm=local_llm,
        tools=[query_database_tool, search_brochures_tool],
        can_handoff_to=["SummarizerAgent"],
    )
    return agent
