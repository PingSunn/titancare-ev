from typing import Optional
from langchain_core.tools import tool
from database import SessionLocal
from models.appointment import Appointment
from models.car import Car
from schemas.appointment import AppointmentCreate
from datetime import datetime


@tool
def get_available_car_models() -> str:
    """
    Returns the list of all EV car models and sub-models available in the database.
    Call this tool BEFORE booking an appointment so you know which vehicle models
    are valid and can help the user choose the correct one.
    """
    db = SessionLocal()
    try:
        cars = db.query(Car.model, Car.sub_model).distinct().order_by(Car.model, Car.sub_model).all()
        if not cars:
            return "No car models found in the database."
        lines = []
        for model, sub_model in cars:
            if sub_model:
                lines.append(f"- {model} ({sub_model})")
            else:
                lines.append(f"- {model}")
        return "Available car models:\n" + "\n".join(lines)
    except Exception as e:
        return f"Failed to retrieve car models: {e}"
    finally:
        db.close()


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
    Before calling this tool, call get_available_car_models to validate the vehicle model.
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
        # Validate vehicle model against the cars table (case-insensitive)
        matched_car = db.query(Car).filter(
            Car.model.ilike(f"%{vehicle_model}%")
        ).first()

        if not matched_car:
            # Fetch available models to guide the user
            cars = db.query(Car.model, Car.sub_model).distinct().order_by(Car.model).all()
            model_list = ", ".join(
                f"{m} ({s})" if s else m for m, s in cars
            ) or "none found"
            return (
                f"ERROR: Vehicle model '{vehicle_model}' was not found in our database. "
                f"Available models are: {model_list}. "
                "Please ask the user to choose a valid model."
            )

        # Validate business hours (9 AM - 4 PM)
        from datetime import time
        opening_time = time(9, 0)
        closing_time = time(16, 0)
        
        if time_obj < opening_time or time_obj > closing_time:
            return (f"ERROR: Appointments can only be booked between 09:00 and 16:00. "
                    f"The requested time {appointment_time} is outside business hours. "
                    "Please ask the user to choose a time between 9 AM and 4 PM.")

        # Check for existing appointment at the same date and time
        existing = db.query(Appointment).filter(
            Appointment.appointment_date == date_obj,
            Appointment.appointment_time == time_obj
        ).first()
        
        if existing:
            # Generate suggested slots for the same day (9 AM to 4 PM)
            all_slots = [time(hour, 0) for hour in range(9, 17)]  # 9 to 16 inclusive
            booked_slots = {
                a.appointment_time for a in db.query(Appointment).filter(
                    Appointment.appointment_date == date_obj
                ).all()
            }
            available_slots = [s.strftime("%H:%M") for s in all_slots if s not in booked_slots]
            
            suggestions = ", ".join(available_slots) if available_slots else "No other slots available for this day."
            return (f"CONFLICT: The time {appointment_time} on {appointment_date} is already booked. "
                    f"Available slots for this day are: {suggestions}. "
                    "Please ask the user if they would like to pick one of these times.")

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
