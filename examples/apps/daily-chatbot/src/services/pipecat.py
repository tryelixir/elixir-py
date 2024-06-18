from time import time
from pipecat.frames.frames import Frame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.openai import OpenAILLMService as BaseOpenAILLMService
from pipecat.services.openai import OpenAILLMContext as BaseOpenAILLMContext
from elixir import Elixir
from openai.types.chat import (
    ChatCompletionMessageParam,
)


class OpenAILLMContext(BaseOpenAILLMContext):
    def add_message(
        self,
        message: ChatCompletionMessageParam,
    ):
        return super().add_message({**message, "timestamp": time()})


class OpenAILLMService(BaseOpenAILLMService):
    def __init__(self, session_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = session_id

    def process_frame(self, frame: Frame, direction: FrameDirection):
        Elixir.set_association_properties({"session_id": self.session_id})
        return super().process_frame(frame, direction)
