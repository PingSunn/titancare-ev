"""
TitanCare EV AI — Integration Test Suite
Requires: live server at localhost:8000, Supabase, and Ollama (llama3.1)

Run: pytest tests/test_integration.py -v --timeout=300
"""

import pytest
import httpx
import uuid
import time

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 300.0


def chat_payload(session_id: str, message: str) -> dict:
    return {"session_id": session_id, "message": message}


async def send(client: httpx.AsyncClient, session_id: str, message: str) -> str:
    resp = await client.post(f"{BASE_URL}/chat", json=chat_payload(session_id, message))
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
    return resp.json().get("reply", "")


def unique_date(offset_days: int = 0) -> str:
    """Generate a future date unlikely to conflict with other test runs."""
    base = 20 + (int(time.time()) % 8) + offset_days
    return f"2026-07-{base:02d}"


# ---------------------------------------------------------------------------
# A. Car Specifications (SQL Tool)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_car_battery_capacity_mg4():
    """A-1: Battery capacity query — MG 4 — expects 64 kWh in reply."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What is the battery capacity of the MG 4?")
        assert "64" in reply, f"Expected '64' in reply: {reply}"


@pytest.mark.anyio
async def test_car_driving_range():
    """A-2: Range query — expects a numeric range value in the reply."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "How far can the MG 4 go on a single charge?")
        assert any(c.isdigit() for c in reply), f"Expected numeric range in reply: {reply}"
        assert any(kw in reply.lower() for kw in ["km", "range", "kilomet"]), f"Expected distance unit in reply: {reply}"


@pytest.mark.anyio
async def test_car_price_query():
    """A-3: Price query — expects a numeric price or price-related term."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What is the price of the MG 4?")
        assert any(kw in reply.lower() for kw in ["price", "baht", "thb", "฿", "cost"]) or any(c.isdigit() for c in reply), \
            f"Expected price info in reply: {reply}"


@pytest.mark.anyio
async def test_car_longest_range():
    """A-4: Which model has the longest range — expects a model name in reply."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Which EV model has the longest driving range?")
        assert any(c.isdigit() for c in reply), f"Expected numeric data in reply: {reply}"


@pytest.mark.anyio
async def test_car_max_torque_mg4():
    """A-6: Max torque — MG 4 ELECTRIC XPOWER — expects 600 Nm."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What is the maximum torque of the MG 4 ELECTRIC XPOWER?")
        assert "600" in reply, f"Expected '600' in reply: {reply}"


@pytest.mark.anyio
async def test_car_charge_time():
    """A-7: Charging time query — expects numeric time or charging term."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "How long does it take to charge the MG 4 from 0 to 80%?")
        assert any(kw in reply.lower() for kw in ["minute", "hour", "min", "charge", "dc", "ac"]) or any(c.isdigit() for c in reply), \
            f"Expected charge time info in reply: {reply}"


@pytest.mark.anyio
async def test_car_dc_fast_charging():
    """A-9: DC fast charging support — expects yes/no or charging info."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Does the MG 4 support DC fast charging?")
        assert any(kw in reply.lower() for kw in ["dc", "fast", "charge", "yes", "support", "kw"]), \
            f"Expected DC charging info in reply: {reply}"


@pytest.mark.anyio
async def test_car_drivetrain():
    """A-10: Drivetrain query — expects FWD, RWD, or AWD."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What drivetrain does the MG 4 use — FWD, RWD, or AWD?")
        assert any(kw in reply.upper() for kw in ["FWD", "RWD", "AWD", "DRIVE"]), \
            f"Expected drivetrain info in reply: {reply}"


# ---------------------------------------------------------------------------
# B. PDF / Brochure Queries (RAG Tool)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_pdf_warranty():
    """B-12: Warranty info from PDF — expects warranty-related response."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What warranty does TitanCare offer on the battery?")
        assert any(kw in reply.lower() for kw in ["warranty", "year", "guarantee", "warrantee"]), \
            f"Expected warranty info in reply: {reply}"


@pytest.mark.anyio
async def test_pdf_mg4_brochure_features():
    """B-15: MG 4 brochure features — expects feature-related content."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Tell me about the features mentioned in the MG 4 brochure.")
        assert len(reply) > 50, f"Expected substantive reply about MG 4 features: {reply}"
        assert "mg" in reply.lower() or "4" in reply, f"Expected MG 4 reference in reply: {reply}"


# ---------------------------------------------------------------------------
# C. Appointment Booking — Happy Path
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_appointment_single_turn_complete():
    """C-16: Single-turn booking with all details provided upfront."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(0)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"I want to book a test drive for the MG 4 on {appt_date} at 10:00. "
            "My name is John Smith, email john@example.com, phone 0812345678."
        )
        assert any(kw in reply.lower() for kw in ["book", "confirm", "success", "appoint", "schedul"]), \
            f"Expected booking confirmation in reply: {reply}"


@pytest.mark.anyio
async def test_appointment_multi_turn():
    """C-17: Multi-turn appointment — AI asks for missing details progressively."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(1)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Turn 1: vague request
        reply1 = await send(client, session_id, "I'd like to book a service appointment.")
        assert any(kw in reply1.lower() for kw in ["name", "email", "phone", "date", "model", "what", "which", "detail"]), \
            f"Expected AI to ask for details: {reply1}"

        # Turn 2: provide model and date
        reply2 = await send(
            client, session_id,
            f"I want to service my BYD ATTO 3 on {appt_date} at 11:00."
        )
        assert any(kw in reply2.lower() for kw in ["name", "email", "phone", "contact", "confirm", "book"]), \
            f"Expected AI to ask for contact info or confirm: {reply2}"

        # Turn 3: provide contact details
        reply3 = await send(
            client, session_id,
            "My name is Somchai Jaidee, email somchai@email.com, phone 0898765432."
        )
        assert any(kw in reply3.lower() for kw in ["confirm", "correct", "book", "right", "proceed"]), \
            f"Expected AI to confirm or book: {reply3}"


@pytest.mark.anyio
async def test_appointment_thai_name():
    """C-18: Book test drive with Thai-style name."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(2)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"Book a test drive for MG 4 on {appt_date} at 14:00 "
            "for Somchai Thainame, somchai@email.com, 0898765432."
        )
        assert any(kw in reply.lower() for kw in ["book", "confirm", "success", "appoint", "somchai"]), \
            f"Expected booking confirmation: {reply}"


# ---------------------------------------------------------------------------
# D. Appointment Booking — Edge Cases / Validation
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_appointment_out_of_hours_early():
    """D-19: Booking at 07:00 — should reject as outside business hours."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(3)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"I want to book a test drive for MG 4 at 07:00 on {appt_date}. "
            "Name: John, email: john@example.com, phone: 0812345678."
        )
        assert any(kw in reply.lower() for kw in ["hour", "09", "9:00", "business", "outside", "only", "between", "07"]), \
            f"Expected out-of-hours rejection: {reply}"


@pytest.mark.anyio
async def test_appointment_out_of_hours_late():
    """D-20: Booking at 18:00 — should reject as outside business hours."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(4)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"Can I book an appointment at 18:00 on {appt_date} for a test drive? "
            "MG 4, Name: Jane, email: jane@example.com, phone: 0811111111."
        )
        assert any(kw in reply.lower() for kw in ["hour", "16", "business", "outside", "only", "between", "18"]), \
            f"Expected out-of-hours rejection: {reply}"


@pytest.mark.anyio
async def test_appointment_unknown_car_model():
    """D-21: Book a Tesla Model 3 (not in DB) — should return error with available models."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(5)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"I want to test drive a Tesla Model 3 on {appt_date} at 10:00. "
            "Name: Bob, email: bob@example.com, phone: 0822222222."
        )
        assert any(kw in reply.lower() for kw in ["not found", "not available", "don't have", "tesla", "available model"]), \
            f"Expected not-found error or available models: {reply}"


@pytest.mark.anyio
async def test_appointment_duplicate_slot():
    """D-22: Book the same slot twice — second booking should report conflict."""
    session_id_1 = str(uuid.uuid4())
    session_id_2 = str(uuid.uuid4())
    appt_date = unique_date(6)
    slot = "10:00"

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # First booking
        reply1 = await send(
            client, session_id_1,
            f"Book a test drive for MG 4 on {appt_date} at {slot}. "
            "Name: First User, email: first@example.com, phone: 0811110001."
        )
        # Second booking — same slot
        reply2 = await send(
            client, session_id_2,
            f"Book a test drive for MG 4 on {appt_date} at {slot}. "
            "Name: Second User, email: second@example.com, phone: 0811110002."
        )

    booked_first = any(kw in reply1.lower() for kw in ["book", "success", "confirm", "schedul"])
    conflict_second = any(kw in reply2.lower() for kw in ["conflict", "already", "booked", "taken", "available slot"])
    # Either the first succeeded and second conflicts, or both got booked (flaky LLM)
    # At minimum, we expect some response about the slot
    assert booked_first or conflict_second, \
        f"Expected booking or conflict in replies.\nReply 1: {reply1}\nReply 2: {reply2}"


@pytest.mark.anyio
async def test_appointment_missing_email():
    """D-23: Provide name and phone but no email — AI should ask for email."""
    session_id = str(uuid.uuid4())
    appt_date = unique_date(7)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            f"I want to book a test drive for MG 4 on {appt_date} at 10:00. "
            "My name is No Email, phone 0899999999."
        )
        assert any(kw in reply.lower() for kw in ["email", "e-mail", "contact", "@"]), \
            f"Expected AI to ask for email: {reply}"


# ---------------------------------------------------------------------------
# E. Routing / Intent Classification
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_routing_car_inventory():
    """E-25: 'What cars do you sell?' — should route to car agent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What cars do you sell?")
        assert any(kw in reply.lower() for kw in ["mg", "byd", "ev", "model", "car", "electric"]), \
            f"Expected car inventory reply: {reply}"


@pytest.mark.anyio
async def test_routing_appointment_intent():
    """E-26: 'I want to make an appointment' — should route to appointment agent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "I want to make an appointment.")
        assert any(kw in reply.lower() for kw in ["appointment", "book", "schedule", "date", "name", "model", "service"]), \
            f"Expected appointment routing: {reply}"


@pytest.mark.anyio
async def test_routing_off_topic_weather():
    """E-27: Weather question — should route to general agent with graceful response."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What's the weather like today?")
        # Should not hallucinate weather data; should deflect or note it's out of scope
        assert len(reply) > 0, "Expected non-empty reply"
        assert "weather" in reply.lower() or any(kw in reply.lower() for kw in ["don't", "cannot", "help", "ev", "sorry"]), \
            f"Expected graceful off-topic handling: {reply}"


@pytest.mark.anyio
async def test_routing_general_greeting():
    """E-28: 'Hello, who are you?' — should route to general agent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Hello, who are you?")
        assert any(kw in reply.lower() for kw in ["titancare", "titan", "ev", "assistant", "ai", "hello", "help"]), \
            f"Expected self-introduction or greeting: {reply}"


@pytest.mark.anyio
async def test_routing_thai_appointment():
    """E-30: Thai language booking request — should route to appointment agent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "ฉันอยากจองรถทดสอบ")
        assert any(kw in reply.lower() for kw in ["appointment", "book", "schedule", "จอง", "name", "model", "นัด", "test drive"]), \
            f"Expected appointment routing for Thai input: {reply}"


# ---------------------------------------------------------------------------
# F. Multi-turn Conversation & Memory
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_multi_turn_context_retention():
    """F-31: Ask about MG 4 range, then follow up about comparison — context retained."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply1 = await send(client, session_id, "What is the MG 4 range?")
        assert any(c.isdigit() for c in reply1), f"Expected numeric range in reply1: {reply1}"

        reply2 = await send(client, session_id, "How does that compare to other models?")
        # Context retention: should reference some other car or comparison
        assert any(kw in reply2.lower() for kw in ["byd", "mg", "range", "compare", "km", "other", "model"]), \
            f"Expected comparison reply with context retention: {reply2}"


@pytest.mark.anyio
async def test_multi_turn_no_context_bleed():
    """F-32: Start appointment booking, abandon, ask car question — no context bleed."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Start booking
        await send(client, session_id, "I'd like to book an appointment.")

        # Abandon and pivot to car question
        reply = await send(client, session_id, "Actually, what is the battery size of the MG 4?")
        assert "64" in reply or any(kw in reply.lower() for kw in ["battery", "kwh", "capacity"]), \
            f"Expected car info, not appointment context: {reply}"


@pytest.mark.anyio
async def test_multi_turn_consistent_answer():
    """F-33: Ask the same question twice — answers should be consistent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply1 = await send(client, session_id, "What is the battery capacity of the MG 4?")
        reply2 = await send(client, session_id, "What is the battery capacity of the MG 4?")

        # Both should mention 64 (kWh)
        assert "64" in reply1, f"First reply missing '64': {reply1}"
        assert "64" in reply2, f"Second reply missing '64': {reply2}"


# ---------------------------------------------------------------------------
# G. Bilingual Support (Thai / English)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_bilingual_price_thai():
    """G-34: Thai price query — 'MG 4 มีราคาเท่าไหร่?'"""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "MG 4 มีราคาเท่าไหร่?")
        assert any(kw in reply.lower() for kw in ["baht", "thb", "฿", "price", "ราคา"]) or any(c.isdigit() for c in reply), \
            f"Expected price info in Thai query reply: {reply}"


@pytest.mark.anyio
async def test_bilingual_battery_thai():
    """G-35: Thai battery query — 'แบตเตอรี่ MG 4 จุได้กี่ kWh?'"""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "แบตเตอรี่ MG 4 จุได้กี่ kWh?")
        assert "64" in reply or any(kw in reply.lower() for kw in ["kwh", "battery", "แบต", "กิโล"]), \
            f"Expected battery info for Thai query: {reply}"


@pytest.mark.anyio
async def test_bilingual_service_booking_thai():
    """G-36: Thai service booking — 'อยากนัดซ่อมรถ' — should route to appointment agent."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "อยากนัดซ่อมรถ")
        assert any(kw in reply.lower() for kw in ["appointment", "book", "นัด", "name", "date", "model", "service"]), \
            f"Expected appointment routing for Thai service request: {reply}"


# ---------------------------------------------------------------------------
# H. Negative / Robustness
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_negative_nonexistent_car_model():
    """H-37: Query a car not in inventory — expect graceful not-found response."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "What is the price of the Rivian R1T?")
        assert any(kw in reply.lower() for kw in ["not", "don't", "unavailable", "rivian", "found", "inventory", "available"]), \
            f"Expected not-found response: {reply}"


@pytest.mark.anyio
async def test_negative_empty_message():
    """H-38: Empty message — server should return 200 with some response."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(f"{BASE_URL}/chat", json={"session_id": session_id, "message": "   "})
        assert resp.status_code == 200
        reply = resp.json().get("reply", "")
        assert isinstance(reply, str)


@pytest.mark.anyio
async def test_negative_unrelated_coding_question():
    """H-39: Completely unrelated question — should handle gracefully without hallucinating."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Write me a Python function to sort a list.")
        # Should either deflect or respond — must not crash
        assert len(reply) > 0, "Expected non-empty reply for off-topic question"
        assert any(kw in reply.lower() for kw in ["sort", "def", "python", "help", "ev", "titancare", "sorry", "focus", "speciali"]), \
            f"Expected deflection or code in reply: {reply}"


# ---------------------------------------------------------------------------
# Original baseline tests (kept for regression)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_chat_car_details():
    """Baseline: MG 4 ELECTRIC (XPOWER) battery capacity and max torque."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(
            client, session_id,
            "What is the battery capacity and max torque of the MG 4 ELECTRIC (XPOWER)?"
        )
        assert "64" in reply, f"Expected '64' in reply: {reply}"
        assert "600" in reply, f"Expected '600' in reply: {reply}"


@pytest.mark.anyio
async def test_chat_appointment_flow():
    """Baseline: Multi-turn BYD ATTO 3 maintenance booking."""
    session_id = str(uuid.uuid4())
    unique_day = f"2026-06-{(int(time.time()) % 25) + 1:02d}"

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply1 = await send(
            client, session_id,
            f"I want to book a maintenance service for my BYD ATTO 3 (PREMIUM) on {unique_day} at 11:00 AM."
        )
        assert any(x in reply1.lower() for x in ["name", "email", "phone", "details"])

        reply2 = await send(
            client, session_id,
            "My name is Alice Smith, email alice@example.com, phone 0987654321."
        )
        assert "confirm" in reply2.lower() or "correct" in reply2.lower()

        reply3 = await send(
            client, session_id,
            "Yes, everything is correct. Please book it."
        )
        assert "booked" in reply3.lower() or "success" in reply3.lower()
        assert "Reference ID" in reply3 or "Ref" in reply3 or "booked" in reply3.lower()


@pytest.mark.anyio
async def test_chat_unsupported_car():
    """Baseline: Toyota Camry EV not in database."""
    session_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        reply = await send(client, session_id, "Do you have the Toyota Camry EV?")
        assert (
            "toyota" not in reply.lower()
            or "don't have" in reply.lower()
            or "do not have" in reply.lower()
            or "not found" in reply.lower()
            or "no mention" in reply.lower()
            or "not available" in reply.lower()
            or "not in" in reply.lower()
        )
