import inspect
import uuid
from opentelemetry import trace
from functools import wraps
from contextlib import AbstractAsyncContextManager

tracer = trace.get_tracer(__name__)


class ElixirSession(AbstractAsyncContextManager):
    def __init__(self, span_name, **attributes):
        self.span_name = span_name
        self.attributes = attributes
        self.root_span = None

    async def __aenter__(self):
        # TODO: Hit the Elixir API to get the session ID. Attach user information.
        session_id = str(uuid.uuid4())  # Generate a unique session ID

        self.root_span = tracer.start_span(self.span_name)
        self.root_span.set_attribute("session_id", session_id)
        for key, value in self.attributes.items():
            self.root_span.set_attribute(key, value)

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.root_span:
            self.root_span.end()

    def trace(self, instance, method_name):
        if not hasattr(instance, method_name):
            raise AttributeError(
                f"'{type(instance).__name__}' object has no attribute '{method_name}'"
            )

        original_method = getattr(instance, method_name)

        if inspect.iscoroutinefunction(original_method):

            @wraps(original_method)
            async def new_method(*args, **kwargs):
                with trace.use_span(self.root_span, end_on_exit=False):
                    return await original_method(*args, **kwargs)

        else:

            @wraps(original_method)
            def new_method(*args, **kwargs):
                with trace.use_span(self.root_span, end_on_exit=False):
                    return original_method(*args, **kwargs)

        setattr(instance, method_name, new_method)
