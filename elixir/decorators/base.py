import json
from functools import wraps
import types
from typing import Any, Callable, Optional

from opentelemetry import trace
from opentelemetry import context as context_api

from elixir.telemetry import Telemetry
from elixir.tracing.context_manager import get_tracer
from elixir.tracing.semconv import SpanAttributes
from elixir.tracing.tracing import (
    TracerWrapper,
    set_entity_name,
    get_chained_entity_name,
)
from elixir.utils.string import camel_to_snake


def entity_method(name: Optional[str] = None):
    def decorate(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            if not TracerWrapper.verify_initialized():
                return fn(*args, **kwargs)

            span_name = _get_span_name(name=name, fn=fn)

            with get_tracer() as tracer:
                span = _create_span(
                    tracer=tracer,
                    span_name=span_name,
                    entity_name=name,
                    args=args,
                    kwargs=kwargs,
                )

                res = fn(*args, **kwargs)

                # span will be ended in the generator
                if isinstance(res, types.GeneratorType):
                    return _handle_generator(span, fn, args, kwargs)

                _trace_output(span, res)

                return res

        return wrap

    return decorate


def entity_class(name: Optional[str], method_name: str):
    def decorator(cls):
        task_name = name if name else camel_to_snake(cls.__name__)
        method = getattr(cls, method_name)
        setattr(cls, method_name, entity_method(name=task_name)(method))
        return cls

    return decorator


def _handle_generator(span, fn, args, kwargs):
    for part in fn(*args, **kwargs):
        yield part

    span.end()


# Async Decorators


def aentity_method(name: Optional[str] = None):
    def decorate(fn):
        @wraps(fn)
        async def wrap(*args, **kwargs):
            if not TracerWrapper.verify_initialized():
                return await fn(*args, **kwargs)

            span_name = _get_span_name(name=name, fn=fn)

            with get_tracer() as tracer:
                span = _create_span(
                    tracer=tracer,
                    span_name=span_name,
                    entity_name=name,
                    args=args,
                    kwargs=kwargs,
                )

                res = await fn(*args, **kwargs)

                # span will be ended in the generator
                if isinstance(res, types.AsyncGeneratorType):
                    return await _ahandle_generator(span, fn, args, kwargs)

                _trace_output(span, res)

                return res

        return wrap

    return decorate


def aentity_class(name: Optional[str], method_name: str):
    def decorator(cls):
        task_name = name if name else camel_to_snake(cls.__name__)
        method = getattr(cls, method_name)
        setattr(cls, method_name, aentity_method(name=task_name)(method))
        return cls

    return decorator


async def _ahandle_generator(span, fn, args, kwargs):
    async for part in fn(*args, **kwargs):
        yield part

    span.end()


# Shared helpers


def _get_span_name(name: str, fn: Callable) -> str:
    return name or fn.__name__


def _create_span(
    tracer: trace.Tracer,
    span_name: str,
    entity_name: str,
    args: tuple,
    kwargs: dict,
) -> trace.Span:
    span = tracer.start_span(span_name)
    ctx = trace.set_span_in_context(span)
    context_api.attach(ctx)

    chained_entity_name = get_chained_entity_name(entity_name)
    set_entity_name(chained_entity_name)

    span.set_attribute(SpanAttributes.ELIXIR_ENTITY_NAME, chained_entity_name)

    try:
        span.set_attribute(
            SpanAttributes.ELIXIR_ENTITY_INPUT,
            json.dumps({"args": args, "kwargs": kwargs}),
        )
    except TypeError as e:
        Telemetry().log_exception(e)

    return span


def _trace_output(span: trace.Span, res: Any):
    try:
        span.set_attribute(SpanAttributes.ELIXIR_ENTITY_OUTPUT, json.dumps(res))
    except TypeError as e:
        Telemetry().log_exception(e)

    span.end()
