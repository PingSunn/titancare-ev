from data_connectors.sql_connector import get_sql_database
from langchain_core.tools import tool
from langchain_classic.chains import create_sql_query_chain
from core_agents.llm_config import local_llm
from sqlalchemy import text as sa_text

@tool
def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    This accepts a natural language query about cars and generates the SQL needed to answer it.

    The database contains a `cars` table with the following columns:
    - model: brand/model name (e.g. 'BYD ATTO 3', 'MG ZS', 'TESLA Model 3')
    - sub_model: trim level (e.g. 'STANDARD', 'PREMIUM', 'LONG RANGE')
    - starting_price: price in Thai Baht (THB)
    - length_width_height_mm: exterior dimensions string (e.g. '4270 x 1850 x 1575')
    - wheelbase_mm: wheelbase in millimetres
    - seating_capacity: number of seats
    - trunk_volume_l: luggage space in litres (may be a range string)
    - curb_weight_kg: kerb weight in kg (may be a range string)
    - battery_type: battery chemistry (e.g. 'LITHIUM IRON PHOSPHATE', 'BYD Blade Battery')
    - battery_capacity_kwh: usable battery size in kWh
    - range_km: driving range with test-cycle label (e.g. '400 (NEDC)')
    - ac_charging_port: AC charging power (e.g. '7 kW', '11 kW')
    - dc_charging_port: DC fast-charge power (e.g. '87 kW', '150 kW')
    - max_dc_fast_charging_kw: maximum DC fast-charge power in kW (numeric)
    - dc_fast_charging_time_30_80: time to charge 30→80 % via DC (e.g. '24 min')
    - v2l: Vehicle-to-Load capability (1 = yes, 0 = no)
    - max_power_kw: peak motor output in kW
    - max_torque_nm: peak torque in Nm
    - acceleration_0_100_s: 0–100 km/h time in seconds
    - drive_mode: available drive modes (e.g. 'ECO/NORMAL/SPORT', 'Front Wheel Drive')

    Use this tool for questions about price, range, battery, performance, dimensions, charging, or comparing models.
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
