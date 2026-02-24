from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    model = Column(String, nullable=False, index=True)
    sub_model = Column(String, nullable=True, index=True)
    starting_price = Column(Float, nullable=True)

    # Dimensions
    length_width_height_mm = Column(String, nullable=True)   # e.g. "4270 x 1850 x 1575"
    wheelbase_mm = Column(Float, nullable=True)
    seating_capacity = Column(Integer, nullable=True)
    trunk_volume_l = Column(String, nullable=True)           # may be a range e.g. "440 - 1660"
    curb_weight_kg = Column(String, nullable=True)           # may be a range e.g. "1760 - 1851"

    # Battery & Range
    battery_type = Column(String, nullable=True)
    battery_capacity_kwh = Column(Float, nullable=True)
    range_km = Column(String, nullable=True)                 # includes test cycle label e.g. "400 (NEDC)"

    # Charging
    ac_charging_port = Column(String, nullable=True)         # e.g. "7 kW" (Type 2)
    dc_charging_port = Column(String, nullable=True)         # e.g. "87 kW" (CCS2)
    max_dc_fast_charging_kw = Column(Float, nullable=True)
    dc_fast_charging_time_30_80 = Column(String, nullable=True)  # e.g. "24 min"
    v2l = Column(Boolean, nullable=True)                     # Vehicle-to-Load

    # Performance
    max_power_kw = Column(Float, nullable=True)
    max_torque_nm = Column(Float, nullable=True)
    acceleration_0_100_s = Column(Float, nullable=True)
    drive_mode = Column(String, nullable=True)
