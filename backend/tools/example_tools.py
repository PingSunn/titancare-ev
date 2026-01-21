"""
Example function tools demonstrating the @function_tool decorator.
Add your custom tools here or create new modules for domain-specific tools.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from agents import function_tool


@function_tool
def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current date and time in a specified timezone.

    Args:
        timezone: IANA timezone name (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo').
                  Defaults to 'UTC'.

    Returns:
        Current date and time formatted as a string.
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error getting time for timezone '{timezone}': {str(e)}"


@function_tool
def search_web(query: str) -> str:
    """
    Search the web for information (placeholder implementation).

    Args:
        query: The search query string.

    Returns:
        Search results as a string.
    """
    # TODO: Implement actual web search integration
    # This is a placeholder that demonstrates the tool pattern
    return f"[Placeholder] Web search results for: '{query}'. Implement actual search API integration."


@function_tool
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., '2 + 2', '10 * 5').

    Returns:
        The result of the calculation as a string.
    """
    # Only allow safe mathematical operations
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains invalid characters. Only numbers and basic operators (+, -, *, /, .) are allowed."

    try:
        # Use eval with restricted globals for safety
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def get_example_tools() -> list:
    """
    Get a list of example tools for agents.

    Returns:
        List of function tools.
    """
    return [
        get_current_time,
        search_web,
        calculate,
    ]
