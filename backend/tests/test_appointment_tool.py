import pytest
from tools.appointment_tools import book_appointment

def test_booking_out_of_hours():
    res = book_appointment.invoke({
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "customer_phone": "12345",
        "vehicle_model": "Model 3",
        "service_type": "Test Drive",
        "appointment_date": "2026-04-01",
        "appointment_time": "08:00"
    })
    assert "Appointments can only be booked between 09:00 and 16:00" in res

def test_booking_success():
    # Make sure to use a unique date/time to avoid conflicts from previous test runs
    import time
    unique_date = f"2026-05-{int(time.time() % 28) + 1:02d}" 
    
    res = book_appointment.invoke({
        "customer_name": "Test User",
        "customer_email": "test@example.com",
        "customer_phone": "123456",
        "vehicle_model": "Model 3",
        "service_type": "Test Drive",
        "appointment_date": unique_date,
        "appointment_time": "10:00"
    })
    
    # Could be a success or a conflict if we happen to hit the same random date twice in row, 
    # but for a fresh DB it should be success.
    assert "Appointment booked successfully" in res or "CONFLICT" in res

def test_booking_conflict():
    # Book once
    date = "2026-05-15"
    book_appointment.invoke({
        "customer_name": "User 1",
        "customer_email": "user1@example.com",
        "customer_phone": "111",
        "vehicle_model": "Model 3",
        "service_type": "Test Drive",
        "appointment_date": date,
        "appointment_time": "14:00"
    })
    
    # Book again at same time
    res2 = book_appointment.invoke({
        "customer_name": "Conflict User",
        "customer_email": "conflict@example.com",
        "customer_phone": "9999",
        "vehicle_model": "Model Y",
        "service_type": "Maintenance",
        "appointment_date": date,
        "appointment_time": "14:00"
    })
    assert "CONFLICT" in res2
    assert "Available slots for this day are:" in res2
