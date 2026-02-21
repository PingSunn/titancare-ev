from typing import Optional
from langchain_core.tools import tool
from database import SessionLocal
from models.appointment import Appointment
from schemas.appointment import AppointmentCreate
from datetime import datetime

@tool
def book_appointment(
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    vehicle_model: str,
    service_type: str,
    appointment_date: str,
    appointment_time: str,
    notes: Optional[str] = None
) -> str:
    """
    Tool to definitely book an appointment. Use this whenever the user requests a booking and provides all necessary information.
    The appointment_date should be in YYYY-MM-DD format. The appointment_time should be in HH:MM format.
    """
    try:
        date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(appointment_time, "%H:%M").time()
        
        # Validate data using Pydantic, which ensures Email format is correct amongst other things
        appointment_data = AppointmentCreate(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            vehicle_model=vehicle_model,
            service_type=service_type,
            appointment_date=date_obj,
            appointment_time=time_obj,
            notes=notes
        )
    except Exception as e:
        return f"Failed to parse appointment details: {e}. Please ensure date is YYYY-MM-DD and time is HH:MM."

    db = SessionLocal()
    try:
        db_appointment = Appointment(**appointment_data.model_dump())
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return (f"Appointment booked successfully for {db_appointment.customer_name} "
                f"({db_appointment.service_type} for {db_appointment.vehicle_model}) "
                f"on {db_appointment.appointment_date} at {db_appointment.appointment_time}. "
                f"Confirmation Reference ID: {db_appointment.id}")
    except Exception as e:
        db.rollback()
        return f"Failed to book appointment due to database error: {e}"
    finally:
        db.close()
