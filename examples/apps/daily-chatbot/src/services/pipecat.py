from pipecat.frames.frames import Frame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.openai import OpenAILLMService as BaseOpenAILLMService
from elixir import Elixir


class OpenAILLMService(BaseOpenAILLMService):
    def __init__(self, session_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = session_id

    def process_frame(self, frame: Frame, direction: FrameDirection):
        Elixir.set_association_properties({"session_id": self.session_id})
        return super().process_frame(frame, direction)
