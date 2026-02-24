"""
import_cars.py
──────────────
Reads TITAN V.1.xlsx, normalises the multi-row / merged-cell header layout,
and upserts every car variant into the `cars` table in titancare.db.

Run from the backend/ directory:
    uv run python scripts/import_cars.py
"""

import sys
import os
import openpyxl

# Ensure the backend root is on the path so we can import database / models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine, SessionLocal
from models.car import Car  # noqa: F401  – needed so Base knows about the table
from models.appointment import Appointment  # noqa: F401


# ── helpers ──────────────────────────────────────────────────────────────────

def _str(v) -> str | None:
    """Convert a cell value to a stripped string, or None if empty."""
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _float(v) -> float | None:
    try:
        return float(v) if v is not None else None
    except (ValueError, TypeError):
        return None


def _bool_from_checkmark(v) -> bool | None:
    if v is None:
        return None
    s = str(v).strip()
    if s in ("✓", "Yes", "yes", "TRUE", "True", "true", "1"):
        return True
    if s in ("✕", "No", "no", "FALSE", "False", "false", "0"):
        return False
    return None


# ── main ─────────────────────────────────────────────────────────────────────

XLSX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "TITAN V.1.xlsx",
)

# Column indices (0-based) matching the Excel layout
COL_MODEL = 0
COL_SUBMODEL = 1
COL_SUBMODEL2 = 2   # some rows use col C for an additional sub-model label
COL_PRICE = 3
COL_LWH = 4
COL_WHEELBASE = 5
COL_SEATS = 6
COL_TRUNK = 7
COL_WEIGHT = 8
COL_BATT_TYPE = 9
COL_BATT_CAP = 10
COL_RANGE = 11
COL_AC_PORT = 12
COL_DC_PORT = 13
COL_POWER = 14
COL_TORQUE = 15
COL_ACCEL = 16
COL_DRIVE_MODE = 17
COL_MAX_DC_KW = 18
COL_DC_TIME = 19
COL_V2L = 20


def parse_xlsx() -> list[dict]:
    wb = openpyxl.load_workbook(XLSX_PATH)
    ws = wb["Sheet1"]

    rows = list(ws.iter_rows(min_row=4, values_only=True))  # data starts at row 4

    records = []
    current_model: str | None = None
    current_lwh: str | None = None
    current_wheelbase: float | None = None
    current_seats: int | None = None
    current_batt_type: str | None = None
    current_ac_port: str | None = None
    current_drive_mode: str | None = None

    for row in rows:
        # Carry-forward: model spans multiple sub-model rows
        if row[COL_MODEL]:
            current_model = _str(row[COL_MODEL])
            current_lwh = _str(row[COL_LWH])
            current_wheelbase = _float(row[COL_WHEELBASE])
            current_seats = int(row[COL_SEATS]) if row[COL_SEATS] else None
            current_batt_type = _str(row[COL_BATT_TYPE])
            current_ac_port = _str(row[COL_AC_PORT])
            current_drive_mode = _str(row[COL_DRIVE_MODE])

        # sub_model: prefer col B, fall back to col C
        sub_model = _str(row[COL_SUBMODEL]) or _str(row[COL_SUBMODEL2])

        # Some dimension / spec fields also carry forward across sub-models
        lwh = _str(row[COL_LWH]) or current_lwh
        wheelbase = _float(row[COL_WHEELBASE]) or current_wheelbase
        seats = (int(row[COL_SEATS]) if row[COL_SEATS] else None) or current_seats
        batt_type = _str(row[COL_BATT_TYPE]) or current_batt_type
        ac_port = _str(row[COL_AC_PORT]) or current_ac_port
        drive_mode = _str(row[COL_DRIVE_MODE]) or current_drive_mode

        record = {
            "model":                    current_model,
            "sub_model":                sub_model,
            "starting_price":           _float(row[COL_PRICE]),
            "length_width_height_mm":   lwh,
            "wheelbase_mm":             wheelbase,
            "seating_capacity":         seats,
            "trunk_volume_l":           _str(row[COL_TRUNK]),
            "curb_weight_kg":           _str(row[COL_WEIGHT]),
            "battery_type":             batt_type,
            "battery_capacity_kwh":     _float(row[COL_BATT_CAP]),
            "range_km":                 _str(row[COL_RANGE]),
            "ac_charging_port":         ac_port,
            "dc_charging_port":         _str(row[COL_DC_PORT]),
            "max_dc_fast_charging_kw":  _float(row[COL_MAX_DC_KW]),
            "dc_fast_charging_time_30_80": _str(row[COL_DC_TIME]),
            "v2l":                      _bool_from_checkmark(row[COL_V2L]),
            "max_power_kw":             _float(row[COL_POWER]),
            "max_torque_nm":            _float(row[COL_TORQUE]),
            "acceleration_0_100_s":     _float(row[COL_ACCEL]),
            "drive_mode":               drive_mode,
        }
        records.append(record)

    return records


def seed():
    # Create tables if they don't exist yet
    Base.metadata.create_all(bind=engine)

    records = parse_xlsx()

    db = SessionLocal()
    try:
        # Clear existing car rows so re-runs are idempotent
        deleted = db.query(Car).delete()
        print(f"Cleared {deleted} existing car records.")

        for rec in records:
            car = Car(**rec)
            db.add(car)

        db.commit()
        print(f"✅  Inserted {len(records)} car variants into `cars` table.")

        # Quick sanity print
        all_cars = db.query(Car).all()
        for c in all_cars:
            price_str = f"{c.starting_price:,.0f} THB" if c.starting_price is not None else "N/A"
            print(f"   [{c.id:02d}] {c.model} – {c.sub_model} | {price_str}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
