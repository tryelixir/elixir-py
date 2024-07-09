from vapi_python import Vapi
import os
from dotenv import load_dotenv
from app.tools import tools

load_dotenv()
vapi = Vapi(api_key=os.getenv("VAPI_PUBLIC_KEY"))

SERVER_URL = os.getenv("SERVER_URL") or "https://elixir-chat-app.onrender.com"


prompt = """
You are a scheduling assistant for a medical clinic. Be concise and keep your introduction brief.
You are a voice agent, so produce output in human-readable English without using markdown (lists, asterisks, bullets, etc.).

Present available times in 12-hour format (AM/PM).

If given document search results, concisely respond with English instead of a bulleted list. You will be punished for regurgitating the entire document.
**Good Example**: Yes, the clinic supports Anthem Insurance PPO, but not HMO.
**Bad Example**: - **HMO (Health Maintenance Organization)** plans are supported.
"""

assistant = {
    "firstMessage": "Hi! Thanks for calling the Elixir clinic. I'm here to help you schedule an appointment. How can I assist you today?",
    "context": prompt,
    "voice": "jennifer-playht",
    "recordingEnabled": True,
    "interruptionsEnabled": True,
    "model": {
        "provider": "custom-llm",
        "model": "gpt-4o",
        "url": f"{SERVER_URL}/api/custom-llm",
        "provider": "custom-llm",
        "maxTokens": 250,
        "temperature": 1,
        "tools": tools,
    },
    "serverUrl": f"{SERVER_URL}/api/webhook",
}

if __name__ == "__main__":
    try:
        vapi.start(assistant=assistant)
    except KeyboardInterrupt:
        vapi.stop()
