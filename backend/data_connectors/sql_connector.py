import os
from langchain_community.utilities import SQLDatabase

# Configuration for the SQLAlchemy engine
DB_URL = "sqlite:///./titancare.db"

def get_sql_database():
    """
    Returns a configured LangChain SQLDatabase connection.
    This database object can be passed to a create_sql_query_chain or similar tool.
    """
    return SQLDatabase.from_uri(DB_URL)


