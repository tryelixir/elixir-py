import os


def is_tracing_enabled() -> bool:
    return (os.getenv("ELIXIR_TRACING_ENABLED") or "true").lower() == "true"


def is_metrics_enabled() -> bool:
    return (os.getenv("ELIXIR_METRICS_ENABLED") or "true").lower() == "true"
