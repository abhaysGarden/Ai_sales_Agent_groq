import streamlit as st
import requests

# Set the title of the Streamlit app
st.title("🧠 AI Sales Assistant")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input field for user message
if prompt := st.chat_input("Type your message here..."):
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    # Prepare the payload for the backend API
    payload = {
        "prospect_id": "demo_user",
        "conversation_history": [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ],
        "current_message": prompt
    }

    try:
        # Send POST request to the backend API
        response = requests.post(
            "http://localhost:8000/agent/route",  # Update with your backend URL
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Extract the assistant's response
        assistant_reply = data.get("suggested_response", "I'm sorry, I couldn't generate a response.")

    except requests.exceptions.RequestException as e:
        assistant_reply = f"Error: {e}"

    # Update the assistant response in the chat
    message_placeholder.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
