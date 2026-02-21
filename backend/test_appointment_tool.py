from tools.appointment_tools import book_appointment
from database import SessionLocal
from models.appointment import Appointment
import datetime

def test_booking_logic():
    # 1. Test Out of Hours (8 AM)
    print("Testing 08:00 (Out of Hours)...")
    res1 = book_appointment.invoke({
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "customer_phone": "12345",
        "vehicle_model": "Model 3",
        "service_type": "Test Drive",
        "appointment_date": "2026-04-01",
        "appointment_time": "08:00"
    })
    print(f"Result: {res1}\n")

    # 2. Test Success (10 AM)
    print("Testing 10:00 (Success)...")
    res2 = book_appointment.invoke({
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "customer_phone": "123456",
        "vehicle_model": "Model 3",
        "service_type": "Test Drive",
        "appointment_date": "2026-04-01",
        "appointment_time": "10:00"
    })
    print(f"Result: {res2}\n")

    # 3. Test Conflict (10 AM again)
    print("Testing 10:00 again (Conflict)...")
    res3 = book_appointment.invoke({
        "customer_name": "Conflict User",
        "customer_email": "conflict@example.com",
        "customer_phone": "9999",
        "vehicle_model": "Model Y",
        "service_type": "Maintenance",
        "appointment_date": "2026-04-01",
        "appointment_time": "10:00"
    })
    print(f"Result: {res3}\n")

if __name__ == "__main__":
    test_booking_logic()
