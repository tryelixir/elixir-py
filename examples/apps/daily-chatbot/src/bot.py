import asyncio
import aiohttp
import os
import sys

from PIL import Image

from elixir.decorators.trace import ElixirSession
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantResponseAggregator,
    LLMUserResponseAggregator,
)
from pipecat.frames.frames import (
    AudioRawFrame,
    ImageRawFrame,
    SpriteFrame,
    Frame,
    LLMMessagesFrame,
    TTSStoppedFrame,
    EndFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.services.daily import (
    DailyParams,
    DailyTranscriptionSettings,
    DailyTransport,
)
from pipecat.vad.silero import SileroVADAnalyzer
from elixir import Elixir, Instruments

from runner import configure

from loguru import logger

from dotenv import load_dotenv

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

Elixir.init(disable_batch=True, instruments=[Instruments.OPENAI])

sprites = []

script_dir = os.path.dirname(__file__)

for i in range(1, 26):
    # Build the full path to the image file
    full_path = os.path.join(script_dir, f"assets/robot0{i}.png")
    # Get the filename without the extension to use as the dictionary key
    # Open the image and convert it to bytes
    with Image.open(full_path) as img:
        sprites.append(
            ImageRawFrame(image=img.tobytes(), size=img.size, format=img.format)
        )

flipped = sprites[::-1]
sprites.extend(flipped)

# When the bot isn't talking, show a static image of the cat listening
quiet_frame = sprites[0]
talking_frame = SpriteFrame(images=sprites)


class TalkingAnimation(FrameProcessor):
    """
    This class starts a talking animation when it receives an first AudioFrame,
    and then returns to a "quiet" sprite when it sees a TTSStoppedFrame.
    """

    def __init__(self):
        super().__init__()
        self._is_talking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, AudioRawFrame):
            if not self._is_talking:
                await self.push_frame(talking_frame)
                self._is_talking = True
        elif isinstance(frame, TTSStoppedFrame):
            await self.push_frame(quiet_frame)
            self._is_talking = False

        await self.push_frame(frame)


async def main(room_url: str, token):
    async with aiohttp.ClientSession() as session:
        async with ElixirSession("daily_chatbot", room_url=room_url) as elixir_session:
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
            )
            elixir_session.trace(llm, "process_frame")

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful LLM in a WebRTC call. Be brief. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way.",
                },
            ]

            tma_in = LLMUserResponseAggregator(messages)
            tma_out = LLMAssistantResponseAggregator(messages)

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

            task = PipelineTask(pipeline, allow_interruptions=True)

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
    (url, token) = configure()
    asyncio.run(main(url, token))
