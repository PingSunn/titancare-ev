from data_connectors.sql_connector import get_sql_query_engine

def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    """
    engine = get_sql_query_engine()
    response = engine.query(query_str)
    return str(response)
