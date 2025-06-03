import streamlit as st
from app.core.llm_orchestrator import process_message_pipeline
from app.models.schemas import ProcessMessageRequest

# Streamlit UI
st.title("🧠 AI Sales Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

    # Build input schema
    request = ProcessMessageRequest(
        prospect_id="demo_user",
        conversation_history=st.session_state.messages,
        current_message=prompt
    )

    try:
        result = process_message_pipeline(request)
        assistant_reply = result.suggested_response
    except Exception as e:
        assistant_reply = f"Error: {e}"

    placeholder.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
