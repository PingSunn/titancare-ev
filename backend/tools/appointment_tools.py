import asyncio
from datetime import datetime, time, date
from typing import Optional

from langchain_core.tools import tool
from prisma import Prisma


def _run_async(coro_fn):
    """
    Run an async function from a sync context (safe inside thread pool executor).
    Creates a fresh Prisma client per call to avoid event-loop-closed errors
    when the singleton's loop has been closed between calls.
    """
    async def _wrapper():
        db = Prisma()
        await db.connect()
        try:
            return await coro_fn(db)
        finally:
            await db.disconnect()

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_wrapper())
    finally:
        loop.close()


@tool
def get_available_car_models() -> str:
    """
    Returns the list of all EV car models and sub-models available in the database.
    Call this tool BEFORE booking an appointment so you know which vehicle models
    are valid and can help the user choose the correct one.
    """
    async def _fetch(db):
        cars = await db.car.find_many(order={"model": "asc"})
        if not cars:
            return "No car models found in the database."
        lines = []
        for car in cars:
            if car.sub_model:
                lines.append(f"- {car.model} ({car.sub_model})")
            else:
                lines.append(f"- {car.model}")
        return "Available car models:\n" + "\n".join(lines)

    return _run_async(_fetch)


@tool
def book_appointment(
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    vehicle_model: str,
    service_type: str,
    appointment_date: str,
    appointment_time: str,
    notes: Optional[str] = None,
) -> str:
    """
    Book an appointment. Requires all fields collected from the user.
    appointment_date: YYYY-MM-DD format.
    appointment_time: HH:MM format. Bookings only available 09:00-16:00.
    Call get_available_car_models first to validate the vehicle model.
    """
    try:
        date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(appointment_time, "%H:%M").time()
    except ValueError as e:
        return f"Failed to parse appointment details: {e}. Please ensure date is YYYY-MM-DD and time is HH:MM."

    if time_obj < time(9, 0) or time_obj > time(16, 0):
        return (
            f"ERROR: Appointments can only be booked between 09:00 and 16:00. "
            f"The requested time {appointment_time} is outside business hours."
        )

    async def _book(db):
        matched = await db.car.find_first(
            where={"model": {"contains": vehicle_model, "mode": "insensitive"}}
        )
        if not matched:
            all_cars = await db.car.find_many(order={"model": "asc"})
            model_list = ", ".join(
                f"{c.model} ({c.sub_model})" if c.sub_model else c.model
                for c in all_cars
            ) or "none found"
            return (
                f"ERROR: Vehicle model '{vehicle_model}' was not found in our database. "
                f"Available models are: {model_list}."
            )

        appt_date_dt = datetime.combine(date_obj, time(0, 0))
        appt_time_dt = datetime.combine(date.min, time_obj)

        existing = await db.appointment.find_first(
            where={"appointment_date": appt_date_dt, "appointment_time": appt_time_dt}
        )
        if existing:
            all_slots = [time(h, 0) for h in range(9, 17)]
            same_day = await db.appointment.find_many(
                where={"appointment_date": appt_date_dt}
            )
            booked_set = {a.appointment_time.time() for a in same_day}
            available = [s.strftime("%H:%M") for s in all_slots if s not in booked_set]
            suggestions = ", ".join(available) if available else "No other slots available for this day."
            return (
                f"CONFLICT: The time {appointment_time} on {appointment_date} is already booked. "
                f"Available slots for this day are: {suggestions}."
            )

        appt = await db.appointment.create(
            data={
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "car_id": matched.id,
                "vehicle_model": matched.model,
                "service_type": service_type,
                "appointment_date": appt_date_dt,
                "appointment_time": appt_time_dt,
                "notes": notes,
                "status": "Scheduled",
            }
        )
        return (
            f"Appointment booked successfully for {appt.customer_name} "
            f"({appt.service_type} for {appt.vehicle_model}) "
            f"on {appointment_date} at {appointment_time}. "
            f"Confirmation Reference ID: {appt.id}"
        )

    return _run_async(_book)
