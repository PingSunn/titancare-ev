from typing import TypedDict, Annotated, Literal
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from core_agents.car import car_node
from core_agents.appointment import appointment_node
from core_agents.llm_config import local_llm

# 1. Define the State
class AgentState(TypedDict):
    # The `operator.add` reducer means messages are appended rather than overwritten
    messages: Annotated[list[BaseMessage], operator.add]

# 2. Define the Router Logic
def route_query(state: AgentState) -> Literal["car_node", "appointment_node", "general"]:
    """
    Analyzes the latest user message and routes to the appropriate specialized node.
    """
    last_message = state["messages"][-1]
    
    routing_prompt = (
        "You are the TitanCare orchestrator. Analyze the following user request and output ONLY ONE WORD indicating the target agent:\n"
        "- 'CAR' if they are asking for car details, inventory, specifications, or brochures.\n"
        "- 'APPOINTMENT' if they are asking to book an appointment, schedule service, or test drive.\n"
        "- 'GENERAL' if it is a general greeting or simple question.\n\n"
        f"User Request: {last_message.content}\n"
        "Target Agent:"
    )
    
    # We use the raw LLM here to get a string response
    response_text = local_llm.invoke(routing_prompt).content.strip().upper()
    
    if "CAR" in response_text:
        return "car_node"
    elif "APPOINTMENT" in response_text:
        return "appointment_node"
    else:
        return "general"

def general_node(state: AgentState):
    """Fallback node for basic conversational greetings."""
    response = local_llm.invoke(
        [SystemMessage(content="You are TitanCare, a helpful EV assistant. Please greet the user.")] + state["messages"]
    )
    return {"messages": [response]}

# 3. Build the Graph
def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("car_node", car_node)
    workflow.add_node("appointment_node", appointment_node)
    workflow.add_node("general_node", general_node)
    
    # Define routing
    workflow.add_conditional_edges(
        START,
        route_query,
        {
            "car_node": "car_node",
            "appointment_node": "appointment_node",
            "general": "general_node"
        }
    )
    
    # All nodes simply end after generation right now. 
    # Tool execution happens autonomously inside the bounds of the LangChain LLM
    workflow.add_edge("car_node", END)
    workflow.add_edge("appointment_node", END)
    workflow.add_edge("general_node", END)
    
    return workflow.compile()
