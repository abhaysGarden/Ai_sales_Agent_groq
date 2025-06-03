import streamlit as st
import datetime
import asyncio
import requests

from app.core.llm_orchestrator import process_message_pipeline
from app.models.schemas import Message, ProcessMessageRequest

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
    # Record user message in session
    st.session_state.messages.append({
        "sender": "user",
        "content": prompt,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    # Normalize sender names for model input
    def normalize_sender(sender):
        return "prospect" if sender == "user" else "agent"

    try:
        # Format messages into pydantic schema
        conversation_history = [
            Message(
                sender=normalize_sender(m["sender"]),
                content=m["content"],
                timestamp=m["timestamp"]
            )
            for m in st.session_state.messages
        ]

        user_msg = Message(
            sender="prospect",
            content=prompt,
            timestamp=datetime.datetime.utcnow().isoformat()
        )

        request_data = ProcessMessageRequest(
            prospect_id="demo_user",
            conversation_history=conversation_history,
            current_prospect_message=user_msg
        )

        # Run orchestrator directly (no FastAPI call)
        response = asyncio.run(process_message_pipeline(request_data))
        assistant_reply = response.suggested_response_draft

    except Exception as e:
        assistant_reply = f"❌ Error: {e}"

    # Show assistant reply and store in session
    message_placeholder.markdown(assistant_reply)
    st.session_state.messages.append({
        "sender": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
