import json
from core_agents.llm_config import local_llm
from tools.appointment_tools import book_appointment
from langchain_core.messages import SystemMessage, AIMessage

_BOOKING_SYSTEM_PROMPT = """You are an appointment booking agent for TitanCare EV. Your job is to help the user book an appointment.

To book an appointment, you MUST collect ALL of the following details:
1. customer_name (Full name)
2. customer_email
3. customer_phone
4. vehicle_model (EV model of interest)
5. service_type (e.g., Test Drive, Maintenance)
6. appointment_date (YYYY-MM-DD)
7. appointment_time (HH:MM) - Note: Bookings are only available between 09:00 and 16:00.

If the user provides all the information, respond with a JSON object in the following format and NOTHING ELSE:
{
  "action": "book_appointment",
  "customer_name": "...",
  "customer_email": "...",
  "customer_phone": "...",
  "vehicle_model": "...",
  "service_type": "...",
  "appointment_date": "YYYY-MM-DD",
  "appointment_time": "HH:MM"
}

If any information is missing, respond naturally and ask the user to provide the missing details. Always inform the user that bookings are only possible between 9 AM and 4 PM.

If the booking tool returns a 'CONFLICT' or 'ERROR' related to timing, apologize to the user, inform them of the issue (e.g., specific conflict or time out of range), show them any available alternative slots provided in the message, and ask them to choose one or suggest a different time within business hours (9 AM - 4 PM).
"""


def appointment_node(state):
    """
    Handles booking and scheduling user appointments.
    Uses a prompt-based approach for compatibility with llama3 (no native tool calling).
    """
    messages = [SystemMessage(content=_BOOKING_SYSTEM_PROMPT)] + state["messages"]
    
    # Get LLM response
    response = local_llm.invoke(messages)
    response_text = response.content.strip()

    # Attempt to parse the JSON tool call from the model output
    try:
        # Find JSON block in response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            
            if parsed.get("action") == "book_appointment":
                # Execute the actual tool
                result = book_appointment.invoke({
                    "customer_name": parsed.get("customer_name"),
                    "customer_email": parsed.get("customer_email"),
                    "customer_phone": parsed.get("customer_phone"),
                    "vehicle_model": parsed.get("vehicle_model"),
                    "service_type": parsed.get("service_type"),
                    "appointment_date": parsed.get("appointment_date"),
                    "appointment_time": parsed.get("appointment_time"),
                })
                # Respond with booking confirmation
                final_response = AIMessage(content=f"Great news! I've successfully booked your appointment. {result}")
                return {"messages": [final_response]}
    except (json.JSONDecodeError, KeyError):
        pass  # Not a tool call, return the conversational response as-is

    return {"messages": [response]}
