import asyncio
from time import time
import aiohttp
import os
import sys

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator,
)
from pipecat.frames.frames import (
    LLMMessagesFrame,
)
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.transports.services.daily import (
    DailyParams,
    DailyTransport,
)
from pipecat.vad.silero import SileroVADAnalyzer
from elixir import Elixir

from runner import configure

from loguru import logger

from dotenv import load_dotenv

from services.pipecat import OpenAILLMContext, OpenAILLMService
from tools import tools, functions

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

Elixir.init(disable_batch=True)

prompt = """
You are a scheduling assistant for a medical clinic. Be concise and keep your introduction brief.
You are a voice agent, so produce output in human-readable English without using markdown (lists, asterisks, bullets, etc.).

Present available times in 12-hour format (AM/PM).

If given document search results, concisely respond with English instead of a bulleted list. You will be punished for regurgitating the entire document.
**Good Example**: Yes, the clinic supports Anthem Insurance PPO, but not HMO.
**Bad Example**: - **HMO (Health Maintenance Organization)** plans are supported.
"""


async def main(room_url: str, token: str, session_id: str):
    async with aiohttp.ClientSession() as session:
        transport = DailyTransport(
            room_url,
            token,
            "Respond bot",
            DailyParams(
                audio_out_enabled=True,
                transcription_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

        tts = ElevenLabsTTSService(
            aiohttp_session=session,
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id="CmldcosPAwpjgHPovfRW",
        )

        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4-turbo-preview",
            session_id=session_id,
        )
        for function_name, function in functions.items():
            llm.register_function(
                function_name,
                function["callback"],
                start_callback=function["start_callback"],
            )

        messages = [
            {
                "role": "system",
                "content": prompt,
                "timestamp": time(),
            },
        ]

        context = OpenAILLMContext(messages, tools)
        tma_in = LLMUserContextAggregator(context)
        tma_out = LLMAssistantContextAggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),  # Transport user input
                tma_in,  # User responses
                llm,  # LLM
                tts,  # TTS
                transport.output(),  # Transport bot output
                tma_out,  # Assistant spoken responses
            ]
        )

        task = PipelineTask(pipeline, PipelineParams(allow_interruptions=True))

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            transport.capture_participant_transcription(participant["id"])
            # Kick off the conversation.
            messages.append(
                {
                    "role": "system",
                    "content": "Please introduce yourself to the user.",
                    "timestamp": time(),
                }
            )
            await task.queue_frame(LLMMessagesFrame(messages))

        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            await task.cancel()
            # await task.queue_frame(EndFrame())

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    (url, token, session_id) = configure()
    asyncio.run(main(url, token, session_id))
