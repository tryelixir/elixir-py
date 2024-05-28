from functools import wraps
from opentelemetry import trace
from pipecat.processors.frame_processor import FrameProcessor

tracer = trace.get_tracer(__name__)


def trace_frame_processor(span_name):
    def decorator(cls):
        original_init = cls.__init__

        @wraps(cls.__init__)
        def new_init(self, *args, **kwargs):
            self._root_span = tracer.start_span(span_name)
            trace.set_span_in_context(self._root_span)
            original_init(self, *args, **kwargs)

            original_cleanup = self.cleanup
            original_process_frame = self.process_frame

            @wraps(self.cleanup)
            def new_cleanup(*args, **kwargs):
                self._root_span.end()
                return original_cleanup(*args, **kwargs)

            @wraps(self.process_frame)
            async def new_process_frame(*args, **kwargs):
                with trace.use_span(self._root_span, end_on_exit=False):
                    return await original_process_frame(*args, **kwargs)

            self.cleanup = new_cleanup
            self.process_frame = new_process_frame

        cls.__init__ = new_init
        return cls

    return decorator
