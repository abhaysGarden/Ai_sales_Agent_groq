import streamlit as st
import requests
import datetime

st.set_page_config(page_title="AI Sales Assistant", page_icon="🤖")
st.title("🧠 AI Sales Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["sender"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({
        "sender": "user",
        "content": prompt,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    # Prepare payload for FastAPI
    try:
        payload = {
            "prospect_id": "demo_user",
            "conversation_history": st.session_state.messages,
            "current_prospect_message": {
                "sender": "user",
                "content": prompt,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        }

        response = requests.post(
            "http://localhost:8000/process_message",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        assistant_reply = data.get("suggested_response", "⚠️ No response generated.")

    except Exception as e:
        assistant_reply = f"❌ Error: {e}"

    # Show assistant reply
    message_placeholder.markdown(assistant_reply)

    st.session_state.messages.append({
        "sender": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
