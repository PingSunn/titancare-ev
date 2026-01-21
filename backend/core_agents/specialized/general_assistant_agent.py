"""
Example Specialized Agent - General Assistant.
Use this as a template for creating new specialized agents.
"""

from agents import Agent

from models import ModelRegistry
from tools import get_example_tools


def create_general_assistant_agent(
    model_registry: ModelRegistry,
    model_alias: str | None = None,
) -> Agent:
    """
    Create a general assistant agent.

    This is an example specialized agent that handles general queries.
    Use this as a template for creating domain-specific agents.

    Args:
        model_registry: Model registry for resolving model aliases.
        model_alias: Optional model alias override (uses default if not specified).

    Returns:
        Configured Agent instance.
    """
    # Resolve model
    model = model_registry.get(model_alias or model_registry.get_default())

    instructions = """You are a General Assistant - a helpful AI that can assist with a wide variety of tasks.

Your capabilities include:
- Answering questions on various topics
- Providing explanations and clarifications
- Helping with general problem-solving
- Offering suggestions and recommendations

Guidelines:
- Be helpful, accurate, and concise
- If you're unsure about something, say so
- Use the available tools when appropriate
- Provide structured responses when dealing with complex topics
"""

    return Agent(
        name="General Assistant",
        instructions=instructions,
        model=model,
        tools=get_example_tools(),
        handoff_description="Handles general queries and provides helpful information on various topics",
    )
