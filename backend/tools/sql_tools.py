from data_connectors.sql_connector import get_sql_database
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from core_agents.llm_config import local_llm

_SQL_SYSTEM_PROMPT = """You are a PostgreSQL expert. Given a natural language question, write a single valid SQL SELECT query for the `cars` table.

Schema for the `cars` table:
- model: TEXT — brand/model name (e.g. 'BYD ATTO 3', 'MG ZS EV', 'TESLA MODEL 3')
- sub_model: TEXT — trim level (e.g. 'STANDARD', 'PREMIUM', 'LONG RANGE')
- starting_price: NUMERIC — price in Thai Baht (THB)
- length_mm, width_mm, height_mm: INTEGER — exterior dimensions in mm
- wheelbase_mm: INTEGER
- seating_capacity: INTEGER
- trunk_volume_min_l, trunk_volume_max_l: NUMERIC — boot space in litres
- curb_weight_min_kg, curb_weight_max_kg: NUMERIC — kerb weight in kg
- battery_type: TEXT — battery chemistry (e.g. 'LFP', 'BYD Blade Battery')
- battery_capacity_kwh: NUMERIC — usable battery size in kWh
- range_km: INTEGER — driving range
- range_standard: TEXT — test cycle (e.g. 'NEDC', 'WLTP')
- ac_charging_kw, dc_charging_kw, max_dc_fast_charging_kw: NUMERIC — charge rates in kW
- dc_fast_charging_30_80_min: INTEGER — minutes to charge 30-80% via DC
- v2l: BOOLEAN — Vehicle-to-Load capability
- max_power_kw, max_torque_nm: NUMERIC — motor output
- acceleration_0_100_s: NUMERIC — 0-100 km/h time in seconds
- drive_type: TEXT — drivetrain (e.g. 'FWD', 'RWD', 'AWD')
- drive_modes: TEXT[] — array of drive modes

RULES:
- Output ONLY the SQL query — no explanation, no markdown, no code fences, no extra text.
- Always use ILIKE with wildcards for text filters, e.g. model ILIKE '%BYD%'
- For price range queries, use BETWEEN or >= / <=
- For price queries, NEVER use exact equality. Always use a range: price BETWEEN target*0.85 AND target*1.15
- Limit results to 10 rows unless the question asks for more
- Do NOT use service_type — that column does not exist
"""

@tool
def query_database_tool(query_str: str) -> str:
    """
    Useful for answering natural language questions about structured car data in the SQL database.
    Use for questions about price, range, battery, performance, dimensions, charging, or comparing models.
    """
    db = get_sql_database()

    try:
        messages = [
            SystemMessage(content=_SQL_SYSTEM_PROMPT),
            HumanMessage(content=query_str),
        ]
        response = local_llm.invoke(messages)
        sql = response.content.strip()

        # Strip markdown fencing if present
        if sql.startswith("```"):
            sql = sql.split("```")[1].strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()

        # Strip "SQLQuery:" prefix some models add
        lower_sql = sql.lower()
        if lower_sql.startswith("sqlquery:"):
            sql = sql[len("sqlquery:"):].strip()

        print("--- GENERATED SQL ---")
        print(sql)
        print("---------------------")

        if not sql.upper().startswith(("SELECT", "WITH", "EXPLAIN")):
            return f"Database query failed: unexpected LLM output: {sql[:200]}"

        result = db.run(sql)
        return result if result else "No results found."
    except Exception as e:
        return f"Database query failed: {e}"
