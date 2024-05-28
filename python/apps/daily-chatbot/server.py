import os
import argparse
import subprocess
import atexit
from typing import Optional

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from twilio.twiml.voice_response import VoiceResponse, Dial

from utils.daily_helpers import check_room_participants, create_room, get_token

MAX_BOTS_PER_ROOM = 1

# Bot sub-process dict for status reporting and concurrency control
bot_procs = {}


def cleanup():
    # Clean up function, just to be extra safe
    for proc, room_url in bot_procs.values():
        proc.terminate()
        proc.wait()


atexit.register(cleanup)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_room_with_bot():
    print(f"!!! Creating room")
    room_url, room_name, room_sip_uri = create_room()
    print(f"!!! Room URL: {room_url}")
    # Ensure the room property is present
    if not room_url:
        raise HTTPException(
            status_code=500,
            detail="Missing 'room' property in request data. Cannot start agent without a target room!",
        )

    # Check if there is already an existing process running in this room
    num_bots_in_room = sum(
        1
        for proc in bot_procs.values()
        if proc[1] == room_url and proc[0].poll() is None
    )
    if num_bots_in_room >= MAX_BOTS_PER_ROOM:
        raise HTTPException(
            status_code=500, detail=f"Max bot limited reach for room: {room_url}"
        )

    # Get the token for the room
    token = get_token(room_url)

    if not token:
        raise HTTPException(
            status_code=500, detail=f"Failed to get token for room: {room_url}"
        )

    # Spawn a new agent, and join the user session
    # Note: this is mostly for demonstration purposes (refer to 'deployment' in README)
    try:
        proc = subprocess.Popen(
            [f"python3 -m bot -u {room_url} -t {token}"],
            shell=True,
            bufsize=1,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        bot_procs[proc.pid] = (proc, room_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start subprocess: {e}")

    return room_url, room_name, room_sip_uri


@app.get("/start")
async def start_agent():
    room_url, room_name, room_sip_uri = create_room_with_bot()
    return RedirectResponse(room_url)


@app.post("/twilio")
async def handle_twilio_call():
    room_url, room_name, room_sip_uri = create_room_with_bot()

    # Wait for bot to join the room
    check_room_participants(room_name)

    response = VoiceResponse()
    dial = Dial(record="record-from-answer", method="POST", action="/twilio-postdial")
    dial.sip(room_sip_uri)
    response.append(dial)

    return PlainTextResponse(str(response))


@app.post("/twilio-postdial")
async def handle_twilio_postdial(
    DialCallSid: Optional[str] = Form(None),
    DialCallStatus: Optional[str] = Form(None),
    DialCallDuration: Optional[int] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
):
    # Log or process the recording URL and other call details
    print(f"DialCallSid: {DialCallSid}")
    print(f"DialCallStatus: {DialCallStatus}")
    print(f"DialCallDuration: {DialCallDuration}")
    print(f"Recording URL: {RecordingUrl}")

    return {}


@app.get("/status/{pid}")
def get_status(pid: int):
    # Look up the subprocess
    proc = bot_procs.get(pid)

    # If the subprocess doesn't exist, return an error
    if not proc:
        raise HTTPException(
            status_code=404, detail=f"Bot with process id: {pid} not found"
        )

    # Check the status of the subprocess
    if proc[0].poll() is None:
        status = "running"
    else:
        status = "finished"

    return JSONResponse({"bot_id": pid, "status": status})


if __name__ == "__main__":
    import uvicorn

    default_host = os.getenv("HOST", "0.0.0.0")
    default_port = int(os.getenv("FAST_API_PORT", "7860"))

    parser = argparse.ArgumentParser(description="Daily Storyteller FastAPI server")
    parser.add_argument("--host", type=str, default=default_host, help="Host address")
    parser.add_argument("--port", type=int, default=default_port, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Reload code on change")

    config = parser.parse_args()

    uvicorn.run(
        "server:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
    )
