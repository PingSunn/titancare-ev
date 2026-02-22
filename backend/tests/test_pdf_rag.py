from tools.pdf_tools import search_brochures_tool
import pytest

def test_cpe_sport_day_date():
    """
    Test the PDF RAG tool with the newly uploaded CPE-SPORT-DAY THAI brochure 
    to extract the event date.
    """
    query = "What is the date of the CPE-SPORT-DAY 2568 event? / วันที่จัดโครงการ CPE-SPORT-DAY ประจำปี 2568 คือวันที่เท่าไหร่"
    
    result = search_brochures_tool.invoke({"query_str": query})
    
    print("\n--- LLM Response ---")
    print(result)
    print("--------------------")
    
    assert result is not None
    assert "Failed to retrieve" not in result
    assert "No PDF brochures" not in result
