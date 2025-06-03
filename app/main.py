from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input schema
class MessageRequest(BaseModel):
    prospect_id: str
    conversation_history: list
    current_message: str

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Main route for LLM logic
@app.post("/agent/route")
async def route_agent(msg: MessageRequest):
    # You can integrate your actual Groq logic here
    user_input = msg.current_message
    print(f"[INFO] Got message from user: {user_input}")

    # Simulated response
    reply = f"🤖 Simulated LLM response to: '{user_input}'"

    return {
        "suggested_response": reply,
        "intent": "demo_intent",
        "tools_to_call": [],
        "internal_next_steps": "none"
    }
