import streamlit as st
import requests

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="OpenRouter AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 OpenRouter AI Chatbot")
st.caption("Chat with different AI models using your OpenRouter API key")

# ----------------------------
# Sidebar - Settings
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")

    model = st.selectbox(
        "Choose a model",
        [
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct",
            "mistralai/mistral-7b-instruct:free",
            "poolside/laguna-m.1:freepoolside/laguna-m.1:free"
        ],
        index=0,
    )

    system_prompt = st.text_area(
        "System Prompt (optional)",
        value="You are a helpful assistant.",
        height=100,
    )

    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "Get your free API key at [openrouter.ai/keys](https://openrouter.ai/keys)"
    )

# ----------------------------
# Session State - Chat History
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Display Chat History
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Function to Call OpenRouter API
# ----------------------------
def get_ai_response(messages, api_key, model, temperature):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

# ----------------------------
# Chat Input
# ----------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    if not api_key:
        st.error("⚠️ Please enter your OpenRouter API key in the sidebar first.")
    else:
        # Add user message to history and display it
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build message list including system prompt
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages += st.session_state.messages

        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = get_ai_response(api_messages, api_key, model, temperature)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Something went wrong: {e}")