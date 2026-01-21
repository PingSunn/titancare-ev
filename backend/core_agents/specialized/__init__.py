"""
Specialized agents for specific tasks.

Each agent is defined in its own *_agent.py file.
Add new specialized agents here and register them in get_specialized_agents().
"""

from agents import Agent

from models import ModelRegistry
from .general_assistant_agent import create_general_assistant_agent


def get_specialized_agents(model_registry: ModelRegistry) -> list[Agent]:
    """
    Get all specialized agents for the orchestrator.

    Add new specialized agents to this list as they are created.

    Args:
        model_registry: Model registry for resolving model aliases.

    Returns:
        List of specialized Agent instances.
    """
    return [
        create_general_assistant_agent(model_registry),
        # Add more specialized agents here:
        # from .research_agent import create_research_agent
        # from .coding_agent import create_coding_agent
        # create_research_agent(model_registry),
        # create_coding_agent(model_registry),
    ]


__all__ = [
    "get_specialized_agents",
    "create_general_assistant_agent",
]
