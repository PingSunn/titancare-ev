from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama

local_llm = Ollama(model="llama3.1", request_timeout=360.0, context_window=8000)

def create_summarizer_agent():
    agent = FunctionAgent(
        name="SummarizerAgent",
        description="Summarizes the information from other agents into a concise, user-friendly response.",
        system_prompt=(
            "You are the final summarizer agent. Your job is to take the raw data or notes "
            "gathered by the QuestionAgent, AppointmentAgent, or OrchestratorAgent and format them into a single, cohesive, "
            "friendly, and professional response for the end user. You are the last step in the chain."
        ),
        llm=local_llm,
        tools=[],
    )
    return agent
