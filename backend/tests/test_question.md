# TitanCare EV AI — Test Questions

## A. Car Specifications (SQL Tool)

1. What is the battery capacity of the MG 4?
2. How far can the MG 4 go on a single charge?
3. What is the price of the BYD ATTO 3?
4. Which EV model has the longest driving range?
5. Compare the MG 4 and BYD ATTO 3 — which has faster charging?
6. What is the maximum torque of the MG 4?
7. How long does it take to charge the MG 4 from 0 to 80%?
8. What are the dimensions (length, width, height) of the BYD ATTO 3?
9. Does the MG 4 support DC fast charging?
10. What drivetrain does the MG 4 use — FWD, RWD, or AWD?

## B. PDF / Brochure Queries (RAG Tool)

11. When is the next CPE Sport Day event?
12. What warranty does TitanCare offer on the battery?
13. What accessories are included with the MG 4?
14. Are there any ongoing promotions for the MG 4?
15. Tell me about the features mentioned in the MG 4 brochure.

## C. Appointment Booking (Happy Path)

16. I want to book a test drive for the MG 4 on March 20 at 10am. My name is John, email john@example.com, phone 0812345678.
17. I'd like to book a service appointment. *(multi-turn — let AI ask for details)*
18. Book a test drive for MG 4 on Saturday at 2pm for Somchai, somchai@email.com, 0898765432.

## D. Appointment Booking (Edge Cases / Validation)

19. I want to book a test drive at 7am tomorrow.
20. Can I book at 6pm?
21. I want to test drive a Tesla Model 3.
22. *(Book the same model + date + time twice — check conflict response)*
23. *(Book without providing an email — check if AI prompts for missing field)*
24. *(Provide invalid phone format — check if AI validates or accepts it)*

## E. Routing / Intent Classification

25. What cars do you sell?
26. I want to make an appointment.
27. What's the weather like today?
28. Hello, who are you?
29. Can you tell me about EV charging in Thailand?
30. ฉันอยากจองรถทดสอบ

## F. Multi-turn Conversation & Memory

31. What is the MG 4 range? → *(follow up)* How does that compare to other models?
32. *(Start appointment booking, abandon mid-way, then ask a car question)*
33. *(Ask the same question twice — check for consistent answers)*

## G. Bilingual Support (Thai/English)

34. MG 4 มีราคาเท่าไหร่?
35. แบตเตอรี่ MG 4 จุได้กี่ kWh?
36. อยากนัดซ่อมรถ

## H. Negative / Robustness

37. What is the price of the Rivian R1T?
38. *(Send an empty message or whitespace)*
39. Write me a Python function to sort a list.
40. *(Provide conflicting appointment details mid-conversation)*