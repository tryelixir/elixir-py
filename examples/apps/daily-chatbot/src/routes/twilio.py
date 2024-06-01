from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

from elixir.utils.twilio import upload_twilio_recording
from services.bot import create_room_with_bot
from utils.daily import check_room_participants
from twilio.twiml.voice_response import VoiceResponse, Dial

twilio_router = APIRouter()


@twilio_router.post("")
async def handle_twilio_call(
    CallSid: Optional[str] = Form(None),
):
    room = create_room_with_bot(session_id=CallSid)

    # Wait for bot to join the room
    check_room_participants(room.name)

    response = VoiceResponse()
    dial = Dial(
        record="record-from-answer",
        recording_status_callback_method="POST",
        recording_status_callback=f"/twilio/recording",
    )
    dial.sip(room.sip_uri)
    response.append(dial)

    return PlainTextResponse(str(response))


@twilio_router.post("/recording")
async def handle_twilio_postdial(
    CallSid: str = Form(...),
    RecordingDuration: int = Form(...),
    RecordingUrl: str = Form(...),
    RecordingStatus: str = Form(...),
):
    if RecordingStatus != "completed":
        return {}

    # Log or process the recording URL and other call details
    print(f"CallSid: {CallSid}")
    print(f"RecordingDuration: {RecordingDuration}")
    print(f"Recording URL: {RecordingUrl}")

    await upload_twilio_recording(CallSid, RecordingUrl)

    return {}
