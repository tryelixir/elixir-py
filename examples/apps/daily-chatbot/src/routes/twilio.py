from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

from services.bot import create_room_with_bot
from utils.daily import check_room_participants
from twilio.twiml.voice_response import VoiceResponse, Dial

twilio_router = APIRouter()


@twilio_router.post("")
async def handle_twilio_call():
    room_url, room_name, room_sip_uri = create_room_with_bot()

    # Wait for bot to join the room
    check_room_participants(room_name)

    response = VoiceResponse()
    dial = Dial(record="record-from-answer", method="POST", action="/twilio/postdial")
    dial.sip(room_sip_uri)
    response.append(dial)

    return PlainTextResponse(str(response))


@twilio_router.post("/postdial")
async def handle_twilio_postdial(
    ParentCallSid: Optional[str] = Form(None),
    DialCallSid: Optional[str] = Form(None),
    DialCallStatus: Optional[str] = Form(None),
    DialCallDuration: Optional[int] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
):
    # Log or process the recording URL and other call details
    print(f"ParentCallSid: {ParentCallSid}")
    print(f"DialCallSid: {DialCallSid}")
    print(f"DialCallStatus: {DialCallStatus}")
    print(f"DialCallDuration: {DialCallDuration}")
    print(f"Recording URL: {RecordingUrl}")

    return {}
