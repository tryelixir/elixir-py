import asyncio
import os
from elixir.collect.s3 import generate_presigned_s3_url
from elixir.collect.twilio import upload_twilio_recording

from dotenv import load_dotenv

load_dotenv()


async def main():
    recording_url = "https://api.twilio.com/2010-04-01/Accounts/AC8b79674bec1217a9c3c37b032836af8e/Recordings/RE686a9f5fefa49ed8f7575f9046aa8b99"
    presigned_url = generate_presigned_s3_url(
        "elixir-123456",
        "RE686a9f5fefa49ed8f7575f9046aa8b99",
    )
    await upload_twilio_recording(
        os.getenv("TWILIO_AUTH_TOKEN"), recording_url, presigned_url
    )


# Ideal Flow
# 1. Bucket is identified via API key
# 2. Pass in some unique identifier for the call (CallSid)
# await upload_twilio_recording(call_sid, recording_url, os.getenv("TWILIO_AUTH_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
