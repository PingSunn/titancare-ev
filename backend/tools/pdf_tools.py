from data_connectors.pdf_connector import get_brochure_index

def search_brochures_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about car details from unstructured PDF brochures.
    """
    index = get_brochure_index()
    query_engine = index.as_query_engine()
    response = query_engine.query(query_str)
    return str(response)
