"""
Orchestrator Agent - The central decision maker that routes requests to specialized agents.
"""

from agents import Agent

from models import get_model, ModelRegistry
from .specialized import get_specialized_agents
from .summarizer_agent import create_summarizer_agent


def create_orchestrator_agent(
    model_registry: ModelRegistry,
    model_alias: str | None = None,
) -> Agent:
    """
    Create the orchestrator agent that decides which specialized agent to use.

    The orchestrator analyzes incoming requests and delegates to the appropriate
    specialized agent based on the task type.

    Args:
        model_registry: Model registry for resolving model aliases.
        model_alias: Optional model alias override (uses default if not specified).

    Returns:
        Configured orchestrator Agent instance.
    """
    # Resolve model
    model = model_registry.get(model_alias or model_registry.get_default())

    # Get all specialized agents for handoffs
    specialized_agents = get_specialized_agents(model_registry)
    summarizer = create_summarizer_agent(model_registry)

    # Build handoff descriptions for instructions
    agent_descriptions = "\n".join(
        f"- {agent.name}: {agent.handoff_description or 'No description'}"
        for agent in specialized_agents
    )

    instructions = f"""You are the Orchestrator Agent - the central coordinator of a multi-agent system.

Your role is to:
1. Analyze the user's request to understand what they need
2. Decide which specialized agent is best suited to handle the request
3. Hand off to the appropriate agent

Available specialized agents:
{agent_descriptions}

After a specialized agent completes its task, hand off to the Summarizer agent to provide a final, cohesive response.

Guidelines:
- Be decisive - choose the most appropriate agent quickly
- If the request spans multiple domains, start with the most relevant agent
- If unsure, ask the user for clarification before delegating
- Always ensure the conversation flows naturally to the summarizer for final output
"""

    return Agent(
        name="Orchestrator",
        instructions=instructions,
        model=model,
        handoffs=[*specialized_agents, summarizer],
        handoff_description="Central coordinator that routes requests to specialized agents",
    )
