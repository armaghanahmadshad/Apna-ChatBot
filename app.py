import streamlit as st
import google.generativeai as genai

# 1. Load API key securely from Streamlit secrets
# Add this to .streamlit/secrets.toml:
#   GEMINI_API_KEY = "your-real-key-here"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("⚠️ GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=API_KEY)

# 2. Page setup
st.set_page_config(page_title="Apna Chatbot", page_icon="🤖", layout="centered")
st.title("Chatbot made by AMG")
st.caption("A simple chatbot built with Python, Gemini, and Streamlit")

# Sidebar controls
with st.sidebar:
    st.subheader("Settings")
    model_name = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
    )
    if st.button("🗑️ Clear chat"):
        st.session_state.pop("chat_session", None)
        st.rerun()

# 3. Initialize chat session (recreate if model choice changes)
if "chat_session" not in st.session_state or st.session_state.get("model_name") != model_name:
    model = genai.GenerativeModel(model_name)
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.model_name = model_name

# 4. Display conversation history
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 5. Handle new input
if user_prompt := st.chat_input("Say something..."):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            response = st.session_state.chat_session.send_message(user_prompt, stream=True)
            for chunk in response:
                # Some chunks may not carry text (e.g. safety blocks) — guard against that
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response or "*No response generated.*")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            # Remove the failed exchange from history so it doesn't corrupt future turns
            if st.session_state.chat_session.history:
                st.session_state.chat_session.history = st.session_state.chat_session.history[:-1]