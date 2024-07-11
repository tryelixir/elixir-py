import asyncio
import aiohttp
import os
import sys
import argparse

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator,
)
from pipecat.frames.frames import LLMMessagesFrame, EndFrame
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.openai import OpenAILLMContext
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial

from elixir import Elixir

from services.pipecat import OpenAILLMService
from tools import tools, functions

from loguru import logger

from dotenv import load_dotenv

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilioclient = Client(twilio_account_sid, twilio_auth_token)

daily_api_key = os.getenv("DAILY_API_KEY", "")

Elixir.init()

prompt = """
You are a scheduling assistant for a medical clinic. Be concise and keep your introduction brief.
You are a voice agent, so produce output in human-readable English without using markdown (lists, asterisks, bullets, etc.).

Present available times in 12-hour format (AM/PM).

If given document search results, concisely respond with English instead of a bulleted list. You will be punished for regurgitating the entire document.
**Good Example**: Yes, the clinic supports Anthem Insurance PPO, but not HMO.
**Bad Example**: - **HMO (Health Maintenance Organization)** plans are supported.
"""


async def main(room_url: str, token: str, callId: str, sipUri: str):
    async with aiohttp.ClientSession() as session:
        # diallin_settings are only needed if Daily's SIP URI is used
        # If you are handling this via Twilio, Telnyx, set this to None
        # and handle call-forwarding when on_dialin_ready fires.
        transport = DailyTransport(
            room_url,
            token,
            "Chatbot",
            DailyParams(
                api_key=daily_api_key,
                dialin_settings=None,  # Not required for Twilio
                audio_in_enabled=True,
                audio_out_enabled=True,
                camera_out_enabled=False,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                transcription_enabled=True,
            ),
        )

        tts = ElevenLabsTTSService(
            aiohttp_session=session,
            api_key=os.getenv("ELEVENLABS_API_KEY", ""),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
        )

        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", session_id=callId
        )
        for function_name, function in functions.items():
            llm.register_function(
                function_name,
                function["callback"],
                start_callback=function["start_callback"],
            )

        messages = [
            {"role": "system", "content": prompt},
        ]

        context = OpenAILLMContext(messages, tools)
        tma_in = LLMUserContextAggregator(context)
        tma_out = LLMAssistantContextAggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),
                tma_in,
                llm,
                tts,
                transport.output(),
                tma_out,
            ]
        )

        task = PipelineTask(pipeline, PipelineParams(allow_interruptions=True))

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            transport.capture_participant_transcription(participant["id"])
            await task.queue_frames([LLMMessagesFrame(messages)])

        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            await task.queue_frame(EndFrame())

        @transport.event_handler("on_dialin_ready")
        async def on_dialin_ready(transport, cdata):
            # For Twilio, Telnyx, etc. You need to update the state of the call
            # and forward it to the sip_uri..
            print(f"Forwarding call: {callId} {sipUri}")

            try:
                response = VoiceResponse()
                dial = Dial(
                    record="record-from-answer",
                    # recording_status_callback_method="POST",
                    # recording_status_callback="/twilio/recording",
                )
                dial.sip(sipUri)
                response.append(dial)

                # The TwiML is updated using Twilio's client library
                twilioclient.calls(callId).update(twiml=str(response))
            except Exception as e:
                raise Exception(f"Failed to forward call: {str(e)}")

        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Simple ChatBot")
    parser.add_argument("-u", type=str, help="Room URL")
    parser.add_argument("-t", type=str, help="Token")
    parser.add_argument("-i", type=str, help="Call ID")
    parser.add_argument("-s", type=str, help="SIP URI")
    config = parser.parse_args()

    asyncio.run(main(config.u, config.t, config.i, config.s))
