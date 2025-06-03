import streamlit as st
import requests
import os

# Set Streamlit config
st.set_page_config(page_title="AI Sales Agent", layout="wide")
st.title("🧠 AI Sales Assistant")
st.markdown("Welcome to the **AI Sales Agent** powered by Groq. Start chatting below.")

# Load secrets if available
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Check backend health (optional)
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    if r.status_code != 200:
        st.warning("⚠️ Backend server is not healthy.")
except:
    st.warning("⚠️ Could not connect to backend server.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    # Build payload
    payload = {
        "prospect_id": "demo_user",
        "conversation_history": st.session_state.messages,
        "current_message": prompt
    }

    try:
        response = requests.post("http://localhost:8000/agent/route", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        assistant_reply = data.get("suggested_response_draft", "I'm sorry, I couldn't generate a response.")
    except requests.exceptions.RequestException as e:
        assistant_reply = f"Error: {e}"
        data = {}

    message_placeholder.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # Optional: Debug JSON
    with st.expander("🔍 Debug Info"):
        st.json(data)
