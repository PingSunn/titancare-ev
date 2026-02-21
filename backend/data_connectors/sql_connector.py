import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine

# Temporary configuration for the SQLAlchemy engine
# In a real scenario, this would point to the actual database file
DB_URL = "sqlite:///./car_data.db"
engine = create_engine(DB_URL)

# Wrap engine with LlamaIndex SQLDatabase
sql_database = SQLDatabase(engine)

def get_sql_query_engine():
    """
    Returns a configured Natural Language SQL Table Query Engine.
    This engine converts natural language questions into SQL queries against the local DB.
    """
    # Note: Requires a corresponding LLM to be active in global Settings or passed explicitly
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        # tables=["cars", "brochure_stats"] # Optionally limit tables
    )
    return query_engine

def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    """
    engine = get_sql_query_engine()
    response = engine.query(query_str)
    return str(response)
