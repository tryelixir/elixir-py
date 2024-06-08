import asyncio
import aiohttp
import os
import sys
from openai.types.chat import ChatCompletionToolParam

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
from pipecat.services.openai import OpenAILLMContext
from pipecat.transports.services.daily import (
    DailyParams,
    DailyTransport,
)
from pipecat.vad.silero import SileroVADAnalyzer
from elixir import Elixir

from runner import configure

from loguru import logger

from dotenv import load_dotenv

from services.pipecat import OpenAILLMService
from tools.fetch_weather import fetch_weather_from_api, start_fetch_weather

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

Elixir.init(disable_batch=True)


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
        llm.register_function(
            "get_current_weather",
            fetch_weather_from_api,
            start_callback=start_fetch_weather,
        )

        tools = [
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "get_current_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The temperature unit to use. Infer this from the users location.",
                            },
                        },
                        "required": ["location", "format"],
                    },
                },
            )
        ]
        messages = [
            {
                "role": "system",
                "content": "You are a helpful LLM in a WebRTC call. Be brief. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way.",
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
