from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.llms.ollama import Ollama
from core_agents.question import create_question_agent
from core_agents.appointment import create_appointment_agent
from core_agents.summarizer import create_summarizer_agent

local_llm = Ollama(model="llama3.1", request_timeout=360.0, context_window=8000)

def create_workflow() -> AgentWorkflow:
    question_agent = create_question_agent()
    appointment_agent = create_appointment_agent()
    summarizer_agent = create_summarizer_agent()

    orchestrator_agent = FunctionAgent(
        name="OrchestratorAgent",
        description="The main entry point. Routes to QuestionAgent for car details, or AppointmentAgent for bookings.",
        system_prompt=(
            "You are the TitanCare orchestrator. Analyze the user request. "
            "If they are asking for car details, inventory, or specifications, hand off to the QuestionAgent. "
            "If they are asking to book an appointment or schedule service, hand off to the AppointmentAgent. "
            "If it is a general greeting or simple question, hand off directly to the SummarizerAgent with your message."
        ),
        llm=local_llm,
        tools=[],
        can_handoff_to=["QuestionAgent", "AppointmentAgent", "SummarizerAgent"],
    )

    workflow = AgentWorkflow(
        agents=[orchestrator_agent, question_agent, appointment_agent, summarizer_agent],
        root_agent="OrchestratorAgent",
    )
    
    return workflow
