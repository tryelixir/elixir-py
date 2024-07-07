import aiohttp
import os
import sys

from pipecat.frames.frames import EndFrame, LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantResponseAggregator,
    LLMUserResponseAggregator,
)
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)
from pipecat.vad.silero import SileroVADAnalyzer
from pipecat.serializers.twilio import TwilioFrameSerializer
from services.pipecat import OpenAILLMService
from elixir import Elixir
from tools import functions
from loguru import logger
from dotenv import load_dotenv

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

Elixir.init()

prompt = """
You are a scheduling assistant for a medical clinic. Be concise and keep your introduction brief.
You are a voice agent, so produce output in human-readable English without using markdown (lists, asterisks, bullets, etc.).

Present available times in 12-hour format (AM/PM).

If given document search results, concisely respond with English instead of a bulleted list. You will be punished for regurgitating the entire document.
**Good Example**: Yes, the clinic supports Anthem Insurance PPO, but not HMO.
**Bad Example**: - **HMO (Health Maintenance Organization)** plans are supported.
"""


async def run_bot(websocket_client, stream_sid):
    async with aiohttp.ClientSession() as session:
        transport = FastAPIWebsocketTransport(
            websocket=websocket_client,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                add_wav_header=False,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                vad_audio_passthrough=True,
                serializer=TwilioFrameSerializer(stream_sid),
            ),
        )

        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", session_id=stream_sid
        )
        for function_name, function in functions.items():
            llm.register_function(
                function_name,
                function["callback"],
                start_callback=function["start_callback"],
            )

        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

        tts = ElevenLabsTTSService(
            aiohttp_session=session,
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        )

        messages = [
            {"role": "system", "content": prompt},
        ]

        tma_in = LLMUserResponseAggregator(messages)
        tma_out = LLMAssistantResponseAggregator(messages)

        pipeline = Pipeline(
            [
                transport.input(),  # Websocket input from client
                stt,  # Speech-To-Text
                tma_in,  # User responses
                llm,  # LLM
                tts,  # Text-To-Speech
                transport.output(),  # Websocket output to client
                tma_out,  # LLM responses
            ]
        )

        task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            # Kick off the conversation.
            messages.append(
                {"role": "system", "content": "Please introduce yourself to the user."}
            )
            await task.queue_frames([LLMMessagesFrame(messages)])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            await task.queue_frames([EndFrame()])

        runner = PipelineRunner(handle_sigint=False)

        await runner.run(task)
