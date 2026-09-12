import streamlit as st
from utils.chatbot import get_chatbot_response

# Page configuration
st.set_page_config(
    page_title="College Info Chatbot",
    page_icon="🎓",
    layout="centered"
)

# ---- Custom styling ----
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown('<p class="main-title">🎓 College Info Chatbot</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask about admissions, fees, courses, or hostel life at any college worldwide.</p>', unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.header("💡 How to ask")
    st.write("For best results, mention:")
    st.markdown("""
    - **College name**
    - **City/location** (especially for common names)
    - **What you want to know** (fees, admission, courses, etc.)
    """)

    st.divider()
    st.subheader("Try asking:")
    example_questions = [
        "What are the admission requirements for IIT Delhi?",
        "Tell me about fees at Loyola College, Chennai",
        "What courses does Stanford University offer?",
        "Hostel facilities at BITS Pilani",
    ]
    for eq in example_questions:
        st.caption(f"• {eq}")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Built with Python, Streamlit & Gemini AI")
    st.caption("⚠️ Information is gathered from web search and AI — always verify with the official college website before making decisions.")

# ---- Initialize chat history ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Show welcome message if chat is empty ----
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hi! I'm your college info assistant. Ask me about admissions, "
            "fees, courses, or anything about a specific college — just be sure "
            "to mention the location if the college name is common!"
        )

# ---- Display chat history ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- Chat input ----
user_input = st.chat_input("Ask about a college...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking..."):
            try:
                bot_response = get_chatbot_response(user_input, st.session_state.messages)
            except Exception as e:
                bot_response = f"⚠️ Something went wrong: {e}"
            st.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})