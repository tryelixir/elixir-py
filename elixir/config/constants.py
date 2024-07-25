import os


def get_base_url() -> bool:
    return os.getenv("ELIXIR_BASE_URL") or "https://elixir-backend-33v6.onrender.com"


def get_collector_url() -> bool:
    return (
        os.getenv("ELIXIR_COLLECTOR_URL")
        or "https://elixir-backend-33v6.onrender.com/ingestion"
    )
