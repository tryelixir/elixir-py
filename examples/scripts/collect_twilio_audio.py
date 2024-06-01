import asyncio
from elixir.utils.twilio import upload_twilio_recording

from dotenv import load_dotenv

load_dotenv()


async def main():
    session_id = "session-id"
    recording_url = "https://api.twilio.com/2010-04-01/Accounts/AC8b79674bec1217a9c3c37b032836af8e/Recordings/RE5c549240da4c350d6096bfe0b63202ea"
    await upload_twilio_recording(session_id, recording_url)


# Ideal Flow
# 1. Bucket is identified via API key
# 2. Pass in some unique identifier for the call (CallSid)
# await upload_twilio_recording(call_sid, recording_url)

if __name__ == "__main__":
    asyncio.run(main())
