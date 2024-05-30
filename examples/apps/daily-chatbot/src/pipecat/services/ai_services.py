#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import io
import wave

from abc import abstractmethod
from typing import AsyncGenerator

from pipecat.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    TTSStartedFrame,
    TTSStoppedFrame,
    TextFrame,
    VisionImageRawFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.utils.audio import calculate_audio_volume
from pipecat.utils.utils import exp_smoothing


class AIService(FrameProcessor):
    def __init__(self):
        super().__init__()

    async def process_generator(self, generator: AsyncGenerator[Frame, None]):
        async for f in generator:
            if isinstance(f, ErrorFrame):
                await self.push_error(f)
            else:
                await self.push_frame(f)


class LLMService(AIService):
    """This class is a no-op but serves as a base class for LLM services."""

    def __init__(self):
        super().__init__()


class TTSService(AIService):
    def __init__(self, aggregate_sentences: bool = True):
        super().__init__()
        self._aggregate_sentences: bool = aggregate_sentences
        self._current_sentence: str = ""

    # Converts the text to audio.
    @abstractmethod
    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        pass

    async def say(self, text: str):
        await self.process_frame(TextFrame(text=text), FrameDirection.DOWNSTREAM)

    async def _process_text_frame(self, frame: TextFrame):
        text: str | None = None
        if not self._aggregate_sentences:
            text = frame.text
        else:
            self._current_sentence += frame.text
            if self._current_sentence.strip().endswith((".", "?", "!")):
                text = self._current_sentence.strip()
                self._current_sentence = ""

        if text:
            await self._push_tts_frames(text)

    async def _push_tts_frames(self, text: str):
        await self.push_frame(TTSStartedFrame())
        await self.process_generator(self.run_tts(text))
        await self.push_frame(TTSStoppedFrame())
        # We send the original text after the audio. This way, if we are
        # interrupted, the text is not added to the assistant context.
        await self.push_frame(TextFrame(text))

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, TextFrame):
            await self._process_text_frame(frame)
        elif isinstance(frame, EndFrame):
            if self._current_sentence:
                await self._push_tts_frames(self._current_sentence)
            await self.push_frame(frame)
        else:
            await self.push_frame(frame, direction)


class STTService(AIService):
    """STTService is a base class for speech-to-text services."""

    def __init__(self,
                 min_volume: float = 0.6,
                 max_silence_secs: float = 0.3,
                 max_buffer_secs: float = 1.5,
                 sample_rate: int = 16000,
                 num_channels: int = 1):
        super().__init__()
        self._min_volume = min_volume
        self._max_silence_secs = max_silence_secs
        self._max_buffer_secs = max_buffer_secs
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        (self._content, self._wave) = self._new_wave()
        self._silence_num_frames = 0
        # Volume exponential smoothing
        self._smoothing_factor = 0.4
        self._prev_volume = 1 - self._smoothing_factor

    @abstractmethod
    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Returns transcript as a string"""
        pass

    def _new_wave(self):
        content = io.BytesIO()
        ww = wave.open(content, "wb")
        ww.setsampwidth(2)
        ww.setnchannels(self._num_channels)
        ww.setframerate(self._sample_rate)
        return (content, ww)

    def _get_smoothed_volume(self, frame: AudioRawFrame) -> float:
        volume = calculate_audio_volume(frame.audio, frame.sample_rate)
        return exp_smoothing(volume, self._prev_volume, self._smoothing_factor)

    async def _append_audio(self, frame: AudioRawFrame):
        # Try to filter out empty background noise
        volume = self._get_smoothed_volume(frame)
        if volume >= self._min_volume:
            # If volume is high enough, write new data to wave file
            self._wave.writeframes(frame.audio)
            self._silence_num_frames = 0
        else:
            self._silence_num_frames += frame.num_frames
        self._prev_volume = volume

        # If buffer is not empty and we have enough data or there's been a long
        # silence, transcribe the audio gathered so far.
        silence_secs = self._silence_num_frames / self._sample_rate
        buffer_secs = self._wave.getnframes() / self._sample_rate
        if self._content.tell() > 0 and (
                buffer_secs > self._max_buffer_secs or silence_secs > self._max_silence_secs):
            self._silence_num_frames = 0
            self._wave.close()
            self._content.seek(0)
            await self.process_generator(self.run_stt(self._content.read()))
            (self._content, self._wave) = self._new_wave()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Processes a frame of audio data, either buffering or transcribing it."""
        if isinstance(frame, CancelFrame) or isinstance(frame, EndFrame):
            self._wave.close()
            await self.push_frame(frame, direction)
        elif isinstance(frame, AudioRawFrame):
            # In this service we accumulate audio internally and at the end we
            # push a TextFrame. We don't really want to push audio frames down.
            await self._append_audio(frame)
        else:
            await self.push_frame(frame, direction)


class ImageGenService(AIService):

    def __init__(self):
        super().__init__()

    # Renders the image. Returns an Image object.
    @ abstractmethod
    async def run_image_gen(self, prompt: str) -> AsyncGenerator[Frame, None]:
        pass

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, TextFrame):
            await self.push_frame(frame, direction)
            await self.process_generator(self.run_image_gen(frame.text))
        else:
            await self.push_frame(frame, direction)


class VisionService(AIService):
    """VisionService is a base class for vision services."""

    def __init__(self):
        super().__init__()
        self._describe_text = None

    @ abstractmethod
    async def run_vision(self, frame: VisionImageRawFrame) -> AsyncGenerator[Frame, None]:
        pass

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, VisionImageRawFrame):
            await self.process_generator(self.run_vision(frame))
        else:
            await self.push_frame(frame, direction)
