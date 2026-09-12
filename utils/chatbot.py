import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


def test_connection():
    """Simple test to confirm Gemini API is working."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Say hello in one short sentence."
    )
    return response.text
from utils.search_engine import search_college_info


def build_conversation_context(chat_history, max_messages=6):
    """
    Builds a simple text summary of recent conversation for context.
    chat_history: list of {"role": "user"/"assistant", "content": "..."}
    """
    recent = chat_history[-max_messages:] if len(chat_history) > max_messages else chat_history
    context_lines = []
    for msg in recent:
        role = "Student" if msg["role"] == "user" else "Bot"
        context_lines.append(f"{role}: {msg['content']}")
    return "\n".join(context_lines)


def generate_answer(user_question, search_results, college_name, location, topic):
    """
    Uses Gemini to synthesize a final answer from search results.
    Always states which college/location the answer is about.
    """
    if not search_results:
        return (
            f"I couldn't find reliable information about **{college_name}"
            f"{', ' + location if location else ''}** regarding {topic}. "
            "Could you double-check the college name, or provide more details like the city/state?"
        )

    # Build a context block from search results
    sources_text = ""
    for i, r in enumerate(search_results, 1):
        sources_text += f"\nSource {i} ({r.get('url', 'unknown')}):\n{r.get('content', '')[:600]}\n"

    prompt = f"""
You are a helpful college information assistant.
A student asked: "{user_question}"

You identified this question is about:
- College: {college_name}
- Location: {location if location else "not specified, but inferred from search"}
- Topic: {topic}

Here is information gathered from web search:
{sources_text}

Instructions:
1. Answer the student's question clearly and concisely using ONLY the information from the sources above.
2. Start your answer by confirming which college and location you're providing information about (e.g., "Here's information about [College Name] in [Location]:").
3. If the sources don't clearly answer the question, say so honestly rather than guessing.
4. If the sources seem to be about a DIFFERENT location than what was asked, mention this discrepancy clearly instead of presenting it as fact.
5. Keep the tone friendly and helpful, like a college counselor.
6. Use bullet points for lists (fees breakdown, course lists, etc.) where appropriate.
7. Do not fabricate specific numbers, dates, or facts not present in the sources.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text


def get_chatbot_response(user_question, chat_history):
    """
    Main entry point: takes the student's question and full chat history,
    returns the bot's response (either a clarification question or a full answer).
    """
    from utils.query_parser import parse_query

    context = build_conversation_context(chat_history)
    parsed = parse_query(user_question, conversation_context=context)

    # Case 0: Off-topic question
    if parsed.get("is_off_topic"):
        return (
            "I'm specifically designed to help with college-related questions — "
            "admissions, fees, courses, hostel life, and more. "
            "Feel free to ask me about any college! 🎓"
        )

    # Case 1: Needs clarification (ambiguous college name, no location)
    if parsed.get("needs_clarification"):
        clarification = parsed.get("clarification_question")
        if clarification:
            return clarification
        return f"Could you tell me which city/location '{parsed.get('college_name')}' is in? There might be multiple colleges with that name."

    # Case 2: No college mentioned at all (general chat/greeting)
    if not parsed.get("college_name"):
        return (
            "I'd be happy to help! Please tell me the name of the college "
            "you're asking about (and its city, if possible) along with your question — "
            "for example, 'What are the fees at Loyola College, Chennai?'"
        )

    # Case 3: We have enough info — search and answer
    college_name = parsed.get("college_name")
    location = parsed.get("location")
    topic = parsed.get("topic", "general")

    search_query = f"{college_name} {location if location else ''} {topic} official information".strip()

    try:
        search_results = search_college_info(search_query, max_results=5)
    except Exception as e:
        return f"⚠️ I ran into an issue searching for information right now. Please try again in a moment. (Error: {e})"

    # Case 4: Search returned nothing useful
    if not search_results or len(search_results) == 0:
        location_text = f" in {location}" if location else ""
        return (
            f"I couldn't find reliable information about **{college_name}{location_text}** "
            f"regarding {topic}. This could mean:\n"
            f"- The college name might be spelled differently\n"
            f"- The location might need to be more specific\n"
            f"- Try rephrasing your question\n\n"
            f"Could you double-check the details and try again?"
        )

    answer = generate_answer(user_question, search_results, college_name, location, topic)
    return answer