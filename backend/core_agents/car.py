import json
from core_agents.llm_config import local_llm
from tools.sql_tools import query_database_tool
from tools.pdf_tools import search_brochures_tool
from langchain_core.messages import SystemMessage, AIMessage

_CAR_SYSTEM_PROMPT = """You are a specialized agent for car details and EV brochures at TitanCare EV.

To look up information, you have access to two tools:
1. query_database: Use this to search structured car data (specs, pricing, inventory)
2. search_brochures: Use this to search PDF brochures for unstructured documentation

If you need to use a tool, respond ONLY with a JSON object like this:
{"action": "query_database", "query": "your natural language query here"}
OR
{"action": "search_brochures", "query": "your natural language query here"}

If you already have the information to answer the user directly, respond naturally in plain text.
"""

def car_node(state):
    """
    Search for car details and specs using the SQL database or PDF brochures.
    Uses prompt-based tool extraction for compatibility with llama3.
    """
    messages = [SystemMessage(content=_CAR_SYSTEM_PROMPT)] + state["messages"]

    # First LLM call — decide if a tool is needed
    response = local_llm.invoke(messages)
    response_text = response.content.strip()
    
    tool_result = None
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            action = parsed.get("action")
            query = parsed.get("query", "")

            if action == "query_database":
                tool_result = query_database_tool.invoke({"query_str": query})
            elif action == "search_brochures":
                tool_result = search_brochures_tool.invoke({"query_str": query})
    except (json.JSONDecodeError, KeyError):
        pass

    if tool_result:
        # Feed the tool result back so the LLM can form a final answer
        summary_prompt = (
            f"Based on the following data retrieved from our database/brochures, "
            f"please answer the user's question in a friendly and informative way:\n\n"
            f"Data: {tool_result}"
        )
        final_messages = messages + [AIMessage(content=summary_prompt)]
        final_response = local_llm.invoke(final_messages)
        return {"messages": [final_response]}

    return {"messages": [response]}
