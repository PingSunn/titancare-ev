from data_connectors.sql_connector import get_sql_database
from langchain_core.tools import tool
from langchain_classic.chains import create_sql_query_chain
from core_agents.llm_config import local_llm

@tool
def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    This accepts a natural language query about cars and generates the SQL needed to answer it.

    The database contains a `cars` table (PostgreSQL/Supabase) with the following columns:
    - model: brand/model name (e.g. 'BYD ATTO 3', 'MG ZS', 'TESLA MODEL 3')
    - sub_model: trim level (e.g. 'STANDARD', 'PREMIUM', 'LONG RANGE')
    - starting_price: price in Thai Baht (THB), numeric
    - length_mm, width_mm, height_mm: exterior dimensions in mm, integer columns
    - wheelbase_mm: wheelbase in mm, integer
    - seating_capacity: number of seats, integer
    - trunk_volume_min_l, trunk_volume_max_l: boot space in litres (max is NULL for single value)
    - curb_weight_min_kg, curb_weight_max_kg: kerb weight in kg (max is NULL for single value)
    - battery_type: battery chemistry (e.g. 'LFP', 'BYD Blade Battery', 'Liquid-cooled Li-ion')
    - battery_capacity_kwh: usable battery size in kWh, numeric
    - range_km: driving range as integer (e.g. 400)
    - range_standard: test cycle used, text (e.g. 'NEDC', 'WLTP')
    - ac_charging_kw: AC charge rate in kW, numeric
    - dc_charging_kw: DC charge rate in kW, numeric
    - max_dc_fast_charging_kw: peak DC fast-charge power in kW, numeric
    - dc_fast_charging_30_80_min: time to charge 30-80% via DC, integer minutes
    - v2l: Vehicle-to-Load capability, boolean
    - max_power_kw: peak motor output in kW, numeric
    - max_torque_nm: peak torque in Nm, numeric
    - acceleration_0_100_s: 0-100 km/h time in seconds, numeric
    - drive_type: drivetrain (e.g. 'FWD', 'RWD', 'AWD')
    - drive_modes: array of available drive modes (e.g. ARRAY['ECO','NORMAL','SPORT'])

    IMPORTANT: There is NO 'service_type' column in the cars table. Do NOT filter by service_type.
    Use this tool for questions about price, range, battery, performance, dimensions, charging, or comparing models.
    """
    db = get_sql_database()
    
    # Use create_sql_query_chain — this prompts the LLM to generate SQL directly.
    # No tool-calling API is used, so it works with standard llama3.
    chain = create_sql_query_chain(local_llm, db)
    
    try:
        # Step 1: Generate the SQL.
        # Instruct the LLM to use ILIKE with wildcards for model name matching,
        # because model names in the DB are full strings like "MG 4 ELECTRIC"
        # and users often type partial names like "MG 4".
        augmented_query = (
            f"{query_str}\n\n"
            "IMPORTANT SQL RULE: When filtering by model name or any text column, "
            "ALWAYS use ILIKE with wildcards, e.g. model ILIKE '%MG 4%'. "
            "Never use exact equality (=) for model name filters."
        )
        generated_sql = chain.invoke({"question": augmented_query})

        # Step 2: Extract only the SQL portion from the LLM output.
        # llama3 / create_sql_query_chain often echoes the full prompt:
        #   "Question: ...
        #    SQLQuery: SELECT ..."
        # We must strip everything before (and including) "SQLQuery:".
        sql = generated_sql.strip()

        # Handle "SQLQuery:" prefix (case-insensitive)
        lower_sql = sql.lower()
        sql_keyword = "sqlquery:"
        if sql_keyword in lower_sql:
            sql = sql[lower_sql.index(sql_keyword) + len(sql_keyword):].strip()

        # Handle markdown fencing (```sql ... ``` or ``` ... ```)
        if sql.startswith("```"):
            sql = sql.split("```")[1].strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()

        # Safety: reject anything that still starts with a non-SQL keyword
        if not sql.upper().startswith(("SELECT", "WITH", "EXPLAIN")):
            return f"Database query failed: LLM produced an unexpected output: {sql[:200]}"

        # Step 3: Execute the query
        result = db.run(sql)
        return result if result else "No results found."
    except Exception as e:
        return f"Database query failed: {e}"
