import streamlit as st
import datetime
import asyncio
import requests

from app.core.llm_orchestrator import process_message_pipeline
from app.models.schemas import Message, ProcessMessageRequest

st.set_page_config(page_title="AI Sales Assistant", page_icon="🤖")
st.title("🧠 AI Sales Assistant")

# Initialize chat history with correct Message fields
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["sender"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    timestamp = datetime.datetime.utcnow().isoformat()

    # Add user message to history with correct 'sender' literal: 'prospect'
    user_msg = {
        "sender": "prospect",  # must be 'prospect' or 'agent' per your model
        "content": prompt,
        "timestamp": timestamp
    }
    st.session_state.messages.append(user_msg)

    with st.chat_message("prospect"):
        st.markdown(prompt)

    # Prepare ProcessMessageRequest payload
    request_data = ProcessMessageRequest(
        prospect_id="demo_user",
        conversation_history=[Message(**m) for m in st.session_state.messages],
        current_prospect_message=Message(**user_msg)
    )

    # Show loading indicator and run async orchestrator call
    with st.chat_message("agent"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        try:
            response = asyncio.run(process_message_pipeline(request_data))
            assistant_reply = response.suggested_response_draft

        except Exception as e:
            assistant_reply = f"❌ Error: {e}"

        placeholder.markdown(assistant_reply)

    # Add assistant reply to history with 'agent' sender
    st.session_state.messages.append({
        "sender": "agent",
        "content": assistant_reply,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
