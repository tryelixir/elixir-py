from enum import Enum
from opentelemetry.semconv.ai import SpanAttributes as BaseSpanAttributes


class SpanAttributes(BaseSpanAttributes):
    ELIXIR_SPAN_KIND = "elixir.span.kind"
    ELIXIR_WORKFLOW_NAME = "elixir.workflow.name"
    ELIXIR_ENTITY_NAME = "elixir.entity.name"
    ELIXIR_ENTITY_INPUT = "elixir.entity.input"
    ELIXIR_ENTITY_OUTPUT = "elixir.entity.output"
    ELIXIR_ASSOCIATION_PROPERTIES = "elixir.association.properties"


class ElixirSpanKindValues(Enum):
    WORKFLOW = "workflow"
    TASK = "task"
    AGENT = "agent"
    TOOL = "tool"
    UNKNOWN = "unknown"


class ElixirContextValues:
    ASSOCIATION_PROPERTIES = "association_properties"
    ENTITY_NAME = "entity_name"
    WORKFLOW_NAME = "workflow_name"
