from typing import Optional


from elixir.decorators.base import (
    aentity_class,
    aentity_method,
    entity_class,
    entity_method,
)
from elixir.tracing.semconv import ElixirSpanKindValues


def observe(
    name: Optional[str] = None,
    method_name: Optional[str] = None,
    elixir_span_kind: Optional[ElixirSpanKindValues] = None,
):
    if method_name is None:
        return entity_method(name=name, elixir_span_kind=elixir_span_kind)
    else:
        return entity_class(
            name=name, method_name=method_name, elixir_span_kind=elixir_span_kind
        )


def task(name: Optional[str] = None, method_name: Optional[str] = None):
    return observe(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.TASK
    )


def workflow(name: Optional[str] = None, method_name: Optional[str] = None):
    return observe(
        name=name,
        method_name=method_name,
        elixir_span_kind=ElixirSpanKindValues.WORKFLOW,
    )


def agent(name: Optional[str] = None, method_name: Optional[str] = None):
    return observe(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.AGENT
    )


def tool(name: Optional[str] = None, method_name: Optional[str] = None):
    return observe(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.TOOL
    )


# Async Decorators
def aobserve(
    name: Optional[str] = None,
    method_name: Optional[str] = None,
    elixir_span_kind: Optional[ElixirSpanKindValues] = None,
):
    if method_name is None:
        return aentity_method(name=name, elixir_span_kind=elixir_span_kind)
    else:
        return aentity_class(
            name=name, method_name=method_name, elixir_span_kind=elixir_span_kind
        )


def atask(name: Optional[str] = None, method_name: Optional[str] = None):
    return aobserve(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.TASK
    )


def aworkflow(name: Optional[str] = None, method_name: Optional[str] = None):
    return aobserve(
        name=name,
        method_name=method_name,
        elixir_span_kind=ElixirSpanKindValues.WORKFLOW,
    )


def aagent(name: Optional[str] = None, method_name: Optional[str] = None):
    return aobserve(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.AGENT
    )


def atool(name: Optional[str] = None, method_name: Optional[str] = None):
    return aobserve(
        name=name, method_name=method_name, elixir_span_kind=ElixirSpanKindValues.TOOL
    )
