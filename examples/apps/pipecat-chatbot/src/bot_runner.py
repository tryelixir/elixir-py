"""
bot_runner.py

HTTP service that listens for incoming calls from either Daily or Twilio,
provisioning a room and starting a Pipecat bot in response.

Refer to README for more information.
"""

import os
import argparse
import subprocess
from pipecat.transports.services.helpers.daily_rest import (
    DailyRESTHelper,
    DailyRoomObject,
    DailyRoomProperties,
    DailyRoomSipParams,
    DailyRoomParams,
)
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import aiohttp
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from dotenv import load_dotenv
from elixir import Elixir

load_dotenv()

Elixir.init()

# ------------ Configuration ------------ #

MAX_SESSION_TIME = 5 * 60  # 5 minutes
REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "DAILY_API_KEY",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
]

daily_rest_helper = DailyRESTHelper(
    os.getenv("DAILY_API_KEY", ""),
    os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
)


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# ----------------- API ----------------- #

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Create Daily room, tell the bot if the room is created for Twilio's SIP or Daily's SIP (vendor).
When the vendor is Daily, the bot handles the call forwarding automatically,
i.e, forwards the call from the "hold music state" to the Daily Room's SIP URI.

Alternatively, when the vendor is Twilio (not Daily), the bot is responsible for
updating the state on Twilio. So when `dialin-ready` fires, it takes appropriate
action using the Twilio Client library.
"""


def _create_daily_room(room_url, callId, callDomain=None):
    if not room_url:
        params = DailyRoomParams(
            properties=DailyRoomProperties(
                # Note: these are the default values, except for the display name
                sip=DailyRoomSipParams(
                    display_name="dialin-user",
                    video=False,
                    sip_mode="dial-in",
                    num_endpoints=1,
                )
            )
        )

        print("Creating new room...")
        room: DailyRoomObject = daily_rest_helper.create_room(params=params)

    else:
        # Check passed room URL exist (we assume that it already has a sip set up!)
        try:
            print(f"Joining existing room: {room_url}")
            room: DailyRoomObject = daily_rest_helper.get_room_from_url(room_url)
        except Exception:
            raise HTTPException(status_code=500, detail=f"Room not found: {room_url}")

    print(f"Daily room: {room.url} {room.config.sip_endpoint}")

    # Give the agent a token to join the session
    token = daily_rest_helper.get_token(room.url, MAX_SESSION_TIME)

    if not room or not token:
        raise HTTPException(status_code=500, detail="Failed to get room or token token")

    # Spawn a new agent, and join the user session
    # Note: this is mostly for demonstration purposes (refer to 'deployment' in docs)
    bot_proc = f"python3 -m bot_twilio -u {room.url} -t {token} -i {callId} -s {room.config.sip_endpoint}"

    try:
        subprocess.Popen(
            [bot_proc],
            shell=True,
            bufsize=1,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start subprocess: {e}")

    return room


@app.post("/twilio_start_bot", response_class=PlainTextResponse)
async def twilio_start_bot(request: Request):
    print("POST /twilio_voice_bot")

    # twilio_start_bot is invoked directly by Twilio (as a web hook).
    # On Twilio, under Active Numbers, pick the phone number
    # Click Configure and under Voice Configuration,
    # "a call comes in" choose webhook and point the URL to
    # where this code is hosted.
    data = {}
    try:
        # shouldnt have received json, twilio sends form data
        form_data = await request.form()
        data = dict(form_data)
    except Exception:
        pass

    room_url = os.getenv("DAILY_SAMPLE_ROOM_URL", None)
    callId = data.get("CallSid")

    if not callId:
        raise HTTPException(status_code=500, detail="Missing 'CallSid' in request")

    print("CallId: %s" % callId)

    # create room and tell the bot to join the created room
    # note: Twilio does not require a callDomain
    _create_daily_room(room_url, callId, None)

    print("Put Twilio on hold...")
    # We have the room and the SIP URI,
    # but we do not know if the Daily SIP Worker and the Bot have joined the call
    # put the call on hold until the 'on_dialin_ready' fires.
    # Then, the bot will update the called sid with the sip uri.
    # http://com.twilio.music.classical.s3.amazonaws.com/BusyStrings.mp3
    resp = VoiceResponse()
    resp.play(
        url="http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3",
        loop=10,
    )
    return str(resp)


@app.post("/twilio_recording", response_class=PlainTextResponse)
async def twilio_recording(request: Request):
    print("POST /twilio_recording")

    data = {}
    try:
        # shouldnt have received json, twilio sends form data
        form_data = await request.form()
        data = dict(form_data)
    except Exception:
        pass

    callId = data.get("CallSid")
    recordingUrl = data.get("RecordingUrl")

    if not callId or not recordingUrl:
        raise HTTPException(
            status_code=500, detail="Missing 'CallSid' or 'RecordingUrl' in request"
        )

    # Download the recording from Twilio
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{recordingUrl}.mp3?RequestedChannels=2",
            auth=aiohttp.BasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        ) as response:
            if response.status == 200:
                recording_content = await response.read()
                content_type = response.headers.get("Content-Type")

                print(
                    f"Recording content: {content_type}, {len(recording_content)} bytes"
                )

                await Elixir.upload_audio(
                    conversation_id=callId,
                    audio_buffer=recording_content,
                    audio_content_type=content_type,
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to download recording from Twilio"
                )


# ----------------- Main ----------------- #


if __name__ == "__main__":
    # Check environment variables
    for env_var in REQUIRED_ENV_VARS:
        if env_var not in os.environ:
            raise Exception(f"Missing environment variable: {env_var}.")

    parser = argparse.ArgumentParser(description="Pipecat Bot Runner")
    parser.add_argument(
        "--host", type=str, default=os.getenv("HOST", "0.0.0.0"), help="Host address"
    )
    parser.add_argument(
        "--port", type=int, default=os.getenv("PORT", 7860), help="Port number"
    )
    parser.add_argument(
        "--reload", action="store_true", default=True, help="Reload code on change"
    )

    config = parser.parse_args()

    try:
        import uvicorn

        uvicorn.run(
            "bot_runner:app", host=config.host, port=config.port, reload=config.reload
        )

    except KeyboardInterrupt:
        print("Pipecat runner shutting down...")
