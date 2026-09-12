def parse_query(user_question, conversation_context=""):
    """
    Uses Gemini to extract structured info from the student's question:
    - college_name
    - location (city/state/country if mentioned)
    - topic (admissions, fees, courses, hostel, placement, etc.)
    - needs_clarification (True if college name is ambiguous without location)
    - is_off_topic (True if the question has nothing to do with colleges)

    conversation_context: previous messages, to handle follow-up questions
    like "what about hostel fees?" referring to a college mentioned earlier.
    """

    prompt = f"""
You are a query parser for a college information chatbot.
Analyze the student's question and extract structured information.

Previous conversation context (may be empty):
\"\"\"
{conversation_context}
\"\"\"

Student's current question:
\"\"\"
{user_question}
\"\"\"

Respond ONLY with a valid JSON object (no markdown, no extra text) in this exact format:
{{
    "college_name": "extracted college name, corrected for obvious spelling mistakes, or null if not mentioned/unclear",
    "location": "city/state/country mentioned, or null if not mentioned",
    "topic": "one of: admissions, fees, courses, hostel, placements, eligibility, general, other",
    "is_followup": true or false,
    "is_off_topic": true or false (true if the question is unrelated to colleges/education entirely, e.g. 'what's the weather today' or 'write me a poem'),
    "needs_clarification": true or false,
    "clarification_question": "a polite question asking the student to specify the location/city, or null if needs_clarification is false"
}}

Rules:
- If the question is a general greeting (hi, hello, thanks) set is_off_topic to false, college_name to null, and topic to "general" — greetings are fine.
- If the question is about something completely unrelated to colleges/education (weather, sports, coding help, etc.), set is_off_topic to true.
- If a college name seems slightly misspelled (e.g. "Loyala College" instead of "Loyola College"), correct it in college_name using your best judgment.
- If it's a followup question, use context to figure out college_name and location, and set is_followup to true.
- Only set needs_clarification to true if the college name is genuinely ambiguous (common name, likely multiple locations) and no location was given or inferable from context.
- Be conservative: if a location IS mentioned or inferable from context, do NOT ask for clarification.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {
            "college_name": None,
            "location": None,
            "topic": "general",
            "is_followup": False,
            "is_off_topic": False,
            "needs_clarification": False,
            "clarification_question": None
        }

    # Ensure the key always exists even if AI forgets it
    parsed.setdefault("is_off_topic", False)

    return parsed