import json
import re
from core_agents.llm_config import local_llm
from tools.sql_tools import query_database_tool
from tools.pdf_tools import search_brochures_tool
from langchain_core.messages import SystemMessage, AIMessage

_CAR_SYSTEM_PROMPT = """You are a specialized agent for car details and EV brochures at TitanCare EV.

To look up information, you have access to two tools:
1. query_database: Use this to search structured car data (pricing, current inventory, color availability)
2. search_brochures: Use this to search PDF brochures for detailed vehicle specs, interior/exterior dimensions, and unstructured documentation

IMPORTANT: If you need to use a tool, you MUST respond with ONLY a raw JSON object — no markdown, no XML, no function call syntax.
Use exactly this format:
{"action": "query_database", "query": "your natural language query here"}
OR
{"action": "search_brochures", "query": "the EXACT original question the user asked (do not shorten it)"}

Do NOT use <tool_call>, <function>, XML tags, or any other format. Only plain JSON.

If you already have the information to answer the user directly, respond naturally in plain text.
"""

def car_node(state):
    """
    Search for car details and specs using the SQL database or PDF brochures.
    Uses prompt-based tool extraction for compatibility with llama3.
    """
    messages = [SystemMessage(content=_CAR_SYSTEM_PROMPT)] + state["messages"]

    from langchain_core.output_parsers import JsonOutputParser
    
    # First LLM call — decide if a tool is needed
    response = local_llm.invoke(messages)
    response_text = response.content.strip()
    print("--- CAR NODE INITIAL LLM RESPONSE ---")
    print(response_text)
    print("-------------------------------------")
    
    tool_result = None
    action = None
    query = None

    # Try JSON format: {"action": "...", "query": "..."}
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            print("--- EXTRACTED JSON STRING ---")
            print(json_str)
            parser = JsonOutputParser()
            parsed = parser.invoke(json_str)
            print("--- PARSED JSON DICT ---")
            print(parsed)
            action = parsed.get("action")
            query = parsed.get("query", "")
    except Exception:
        print("--- JSON PARSE FAILED, TRYING XML FALLBACK ---")

    # Fallback: parse XML-style <tool_call> <function=...> <parameter=query> ... </parameter>
    if not action and "<tool_call>" in response_text:
        try:
            fn_match = re.search(r"<function=(\w+)>", response_text)
            q_match = re.search(r"<parameter=query>(.*?)</parameter>", response_text, re.DOTALL)
            if fn_match and q_match:
                action = fn_match.group(1)
                query = q_match.group(1).strip()
                print(f"--- XML FALLBACK PARSED: action={action}, query={query} ---")
        except Exception:
            import traceback
            traceback.print_exc()

    if action and query:
        print(f"--- MATCHING ACTION: {action} ---")
        try:
            if action == "query_database":
                tool_result = query_database_tool.invoke({"query_str": query})
            elif action == "search_brochures":
                print("--- INVOKING PDF TOOL ---")
                tool_result = search_brochures_tool.invoke({"query_str": query})
                print("--- PDF TOOL FINISHED ---")
        except Exception:
            print("--- TOOL EXECUTION ERROR ---")
            import traceback
            traceback.print_exc()
            print("----------------------------")

    if tool_result:
        print("--- TOOL EXECUTION RESULT ---")
        print(tool_result)
        print("-----------------------------")
        from langchain_core.messages import HumanMessage
        # Feed the tool result back so the LLM can form a final answer
        user_question = state["messages"][-1].content
        summary_prompt = (
            f"A tool retrieved this exact text from our brochures/database:\n"
            f"---\n{tool_result}\n---\n\n"
            f"User question: {user_question}\n\n"
            f"INSTRUCTIONS: The retrieved text above contains the answer. "
            f"Find the specific numbers and facts in it and state them directly. "
            f"If you see a number in the retrieved text, include it in your answer. "
            f"Never say 'not specified' or 'not available' if the retrieved text contains relevant values."
        )
        # Create a new system message that doesn't demand JSON
        summary_system = SystemMessage(content="You are a specialized car agent for TitanCare EV. Answer the user in plain text.")
        final_messages = [summary_system] + state["messages"] + [HumanMessage(content=summary_prompt)]
        final_response = local_llm.invoke(final_messages)
        return {"messages": [final_response]}

    return {"messages": [response]}
