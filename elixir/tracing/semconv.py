from opentelemetry.semconv.ai import SpanAttributes as BaseSpanAttributes


class SpanAttributes(BaseSpanAttributes):
    ELIXIR_SPAN_KIND = "elixir.span.kind"
    ELIXIR_ENTITY_NAME = "elixir.entity.name"
    ELIXIR_ENTITY_INPUT = "elixir.entity.input"
    ELIXIR_ENTITY_OUTPUT = "elixir.entity.output"
    ELIXIR_ASSOCIATION_PROPERTIES = "elixir.association.properties"


class ElixirContextValues:
    ASSOCIATION_PROPERTIES = "association_properties"
    ENTITY_NAME = "entity_name"
