import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase

load_dotenv()


def get_sql_database() -> SQLDatabase:
    """
    Returns a LangChain SQLDatabase connected to Supabase (PostgreSQL).
    Used by create_sql_query_chain for natural-language SQL generation.
    """
    url = os.environ["DIRECT_URL"]
    return SQLDatabase.from_uri(url)
