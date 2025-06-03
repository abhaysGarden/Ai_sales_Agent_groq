import streamlit as st
import requests
from app.models.schemas import ProcessMessageRequest

st.set_page_config(page_title="AI Sales Assistant", page_icon="🤖")
st.title("🧠 AI Sales Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    # --- ✅ Sanitize and prepare payload ---
    try:
        conversation_history = []
        for msg in st.session_state.messages:
            conversation_history.append({
                "role": str(msg.get("role", "")),
                "content": str(msg.get("content", ""))
            })

        current_message = str(prompt)

        request_payload = ProcessMessageRequest(
            prospect_id="demo_user",
            conversation_history=conversation_history,
            current_message=current_message
        ).dict()

        # --- ✅ Make backend API call ---
        response = requests.post(
            "http://localhost:8000/process_message",
            json=request_payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        assistant_reply = data.get("suggested_response", "⚠️ No response generated.")

    except Exception as e:
        assistant_reply = f"❌ Error: {e}"

    # Show assistant reply
    message_placeholder.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
