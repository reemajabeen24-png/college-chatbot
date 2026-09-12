import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["TAVILY_API_KEY"]
    except Exception:
        pass

if not api_key:
    raise ValueError("TAVILY_API_KEY not found. Please check your .env file.")

tavily_client = TavilyClient(api_key=api_key)


def search_college_info(query, max_results=5):
    """
    Searches the web for information related to the query.
    Returns a list of dicts with 'title', 'url', 'content'.
    """
    response = tavily_client.search(
        query=query,
        max_results=max_results,
        include_answer=False
    )
    results = response.get("results", [])
    return results


def test_search():
    """Simple test to confirm Tavily API is working."""
    results = search_college_info("IIT Bombay admission process")
    return results