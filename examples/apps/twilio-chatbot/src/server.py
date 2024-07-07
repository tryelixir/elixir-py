import json
import os

import uvicorn

from fastapi import FastAPI, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from bot import run_bot
from elixir.utils.twilio import upload_twilio_recording
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

app = FastAPI()

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start_call")
async def start_call():
    print("POST TwiML")
    with open(f"{templates_dir}/streams.xml") as f:
        xml_content = f.read()

    xml_content = xml_content.replace("${BACKEND_URL}", os.getenv("BACKEND_URL"))
    return HTMLResponse(content=xml_content, media_type="application/xml")


@app.post("/record")
async def record(
    CallSid: str = Form(...),
    RecordingDuration: int = Form(...),
    RecordingUrl: str = Form(...),
    RecordingStatus: str = Form(...),
):
    print("POST Record")

    if RecordingStatus != "completed":
        return {}

    # Log or process the recording URL and other call details
    print(f"CallSid: {CallSid}")
    print(f"RecordingDuration: {RecordingDuration}")
    print(f"Recording URL: {RecordingUrl}")

    await upload_twilio_recording(CallSid, RecordingUrl)

    return {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_data = websocket.iter_text()
    await start_data.__anext__()

    call_data = json.loads(await start_data.__anext__())
    print(call_data, flush=True)
    stream_sid = call_data["start"]["streamSid"]
    account_sid = call_data["start"]["accountSid"]
    call_sid = call_data["start"]["callSid"]

    # TODO: Figure out how to record Twilio streams
    response = client.api.request(
        "POST",
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{call_sid}/Recordings.json",
        params={
            "RecordingStatusCallback": "/record",
            "RecordingChannels": "dual",
        },
    )
    print("Recording respones", response)

    print("WebSocket connection accepted")
    await run_bot(websocket, stream_sid)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
