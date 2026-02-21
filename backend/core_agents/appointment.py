from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from tools.appointment_tools import mock_book_appointment

local_llm = Ollama(model="llama3.1", request_timeout=360.0, context_window=8000)

def create_appointment_agent():
    agent = FunctionAgent(
        name="AppointmentAgent",
        description="Handles booking and scheduling user appointments. Pass success info to SummarizerAgent.",
        system_prompt=(
            "You are an appointment booking agent. Your job is to help the user book appointments. "
            "Gather the Date, Time, and Service required, then definitively book the appointment using your tool. "
            "Once you have completed the booking steps, immediately hand off to the SummarizerAgent "
            "with your results so it can formulate the final response to the user."
        ),
        llm=local_llm,
        tools=[mock_book_appointment],
        can_handoff_to=["SummarizerAgent"],
    )
    return agent
