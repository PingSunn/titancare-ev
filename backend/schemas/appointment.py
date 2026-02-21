from pydantic import BaseModel, EmailStr
from datetime import date, time, datetime
from typing import Optional

class AppointmentBase(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    vehicle_model: str
    service_type: str
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None
    status: str = "Scheduled"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
