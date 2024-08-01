import os


def get_base_url() -> bool:
    return os.getenv("ELIXIR_BASE_URL") or "https://api.tryelixir.ai"


def get_collector_url() -> bool:
    return os.getenv("ELIXIR_COLLECTOR_URL") or "https://api.tryelixir.ai/ingestion"
