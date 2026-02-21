from data_connectors.sql_connector import get_sql_database
from langchain_core.tools import tool
from langchain_classic.chains import create_sql_query_chain
from core_agents.llm_config import local_llm
from sqlalchemy import text as sa_text

@tool
def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    This accepts a natural language query about cars and figures out the SQL needed to answer it.
    """
    db = get_sql_database()
    
    # Use create_sql_query_chain — this prompts the LLM to generate SQL directly.
    # No tool-calling API is used, so it works with standard llama3.
    chain = create_sql_query_chain(local_llm, db)
    
    try:
        # Step 1: Generate the SQL
        generated_sql = chain.invoke({"question": query_str})
        
        # Step 2: Strip any markdown fencing the model might add
        sql = generated_sql.strip()
        if sql.startswith("```"):
            sql = sql.split("```")[1].strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()
        
        # Step 3: Execute the query
        result = db.run(sql)
        return result if result else "No results found."
    except Exception as e:
        return f"Database query failed: {e}"
