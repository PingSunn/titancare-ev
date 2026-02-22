import pytest
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage

def test_json_output_parser_clean():
    llm_output = AIMessage(content='```json\n{"action": "search_brochures", "query": "Model 3 range"}\n```')
    parser = JsonOutputParser()
    parsed = parser.invoke(llm_output)
    assert parsed.get("action") == "search_brochures"
    assert parsed.get("query") == "Model 3 range"

def test_json_output_parser_conversational_fallback():
    output_text = '''Let's get started with booking your appointment.

Here's a JSON object representing your booking:
{
  "action": "book_appointment",
  "customer_name": "Alice",
  "appointment_time": "14:00"
}
Is this correct?'''
    
    # The pure parser fails on this
    parser = JsonOutputParser()
    with pytest.raises(Exception):
        parser.invoke(AIMessage(content=output_text))
        
    # Our manual hybrid extraction logic should succeed
    json_start = output_text.find("{")
    json_end = output_text.rfind("}") + 1
    assert json_start != -1 and json_end > json_start
    
    json_str = output_text[json_start:json_end]
    parsed = parser.invoke(json_str)
    assert parsed.get("action") == "book_appointment"
    assert parsed.get("customer_name") == "Alice"
