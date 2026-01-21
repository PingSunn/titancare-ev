"""
Summarizer Agent - Aggregates and summarizes responses from specialized agents.
"""

from agents import Agent

from models import ModelRegistry


def create_summarizer_agent(
    model_registry: ModelRegistry,
    model_alias: str | None = None,
) -> Agent:
    """
    Create the summarizer agent that produces final cohesive responses.

    The summarizer takes the output from specialized agents and creates
    a clear, well-structured final response for the user.

    Args:
        model_registry: Model registry for resolving model aliases.
        model_alias: Optional model alias override (uses default if not specified).

    Returns:
        Configured summarizer Agent instance.
    """
    # Resolve model
    model = model_registry.get(model_alias or model_registry.get_default())

    instructions = """You are the Summarizer Agent - responsible for creating the final response to users.

Your role is to:
1. Review the conversation history and outputs from specialized agents
2. Synthesize the information into a clear, cohesive response
3. Ensure the response directly addresses the user's original request
4. Format the response in a user-friendly manner

Guidelines:
- Be concise but comprehensive
- Use clear formatting (bullet points, headers) when appropriate
- Highlight key takeaways or action items
- Maintain a helpful and professional tone
- If there were any issues or limitations, mention them clearly
- Do not add information that wasn't provided by the specialized agents
"""

    return Agent(
        name="Summarizer",
        instructions=instructions,
        model=model,
        handoff_description="Synthesizes outputs from specialized agents into a final response",
    )
