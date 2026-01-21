"""
Template for creating new specialized agents.

To create a new agent:
1. Copy this file and rename it to `your_agent_name_agent.py`
2. Update the function name and docstrings
3. Customize the instructions and tools
4. Register the agent in specialized/__init__.py
"""

from agents import Agent

from models import ModelRegistry
from tools import get_example_tools  # Import tools as needed


def create_template_agent(
    model_registry: ModelRegistry,
    model_alias: str | None = None,
) -> Agent:
    """
    Create a template agent.

    Replace this with your agent's description.

    Args:
        model_registry: Model registry for resolving model aliases.
        model_alias: Optional model alias override (uses default if not specified).

    Returns:
        Configured Agent instance.
    """
    # Resolve model - you can use a specific model alias or the default
    model = model_registry.get(model_alias or model_registry.get_default())

    # Define the agent's instructions
    # Be specific about:
    # - What the agent does
    # - What capabilities it has
    # - How it should behave
    # - Any constraints or guidelines
    instructions = """You are a [Agent Name] - describe your role here.

Your capabilities include:
- Capability 1
- Capability 2
- Capability 3

Guidelines:
- Guideline 1
- Guideline 2
- Guideline 3
"""

    # Create and return the agent
    return Agent(
        name="Template Agent",  # Display name for the agent
        instructions=instructions,
        model=model,
        tools=get_example_tools(),  # Add your tools here
        handoff_description="Brief description for the orchestrator to know when to use this agent",
    )
