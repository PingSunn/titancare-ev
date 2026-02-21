def mock_book_appointment(date: str, time: str, service: str) -> str:
    """Mock tool to book an appointment. Use this whenever the user requests a booking."""
    return f"Appointment booked successfully for {service} on {date} at {time}."
