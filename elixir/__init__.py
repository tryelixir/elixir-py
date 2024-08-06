import json
import os
import sys

from typing import Optional, Set
from colorama import Fore
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.sdk.metrics.export import MetricReader

from elixir.api.requests import post_body_request, post_file_request
from elixir.config.constants import get_collector_url
from elixir.metrics.metrics import MetricsWrapper
from elixir.telemetry import Telemetry
from elixir.instruments import Instruments
from elixir.config import (
    is_tracing_enabled,
    is_metrics_enabled,
)
from elixir.tracing.tracing import (
    TracerWrapper,
    set_association_properties,
)
from typing import Dict


class Elixir:
    __tracer_wrapper: TracerWrapper

    @staticmethod
    def init(
        app_name: Optional[str] = sys.argv[0],
        api_key: str = None,
        disable_batch=False,
        headers: Dict[str, str] = {},
        metrics_headers: Dict[str, str] = None,
        should_enrich_metrics: bool = True,
        resource_attributes: dict = {},
        instruments: Optional[Set[Instruments]] = None,
        _test_exporter: SpanExporter = None,
        _test_metrics_reader: MetricReader = None,
    ) -> None:
        Telemetry()

        Elixir.api_endpoint = get_collector_url()
        Elixir.api_key = os.getenv("ELIXIR_API_KEY") or api_key
        Elixir.association_properties = {}

        if not is_tracing_enabled():
            print(Fore.YELLOW + "Tracing is disabled" + Fore.RESET)
        else:
            headers = {
                **(os.getenv("ELIXIR_HEADERS") or headers),
                "Authorization": f"Bearer {Elixir.api_key}",
            }

            # Tracer init
            resource_attributes.update({SERVICE_NAME: app_name})
            TracerWrapper.set_static_params(
                resource_attributes, Elixir.api_endpoint, headers
            )
            Elixir.__tracer_wrapper = TracerWrapper(
                disable_batch=disable_batch,
                should_enrich_metrics=should_enrich_metrics,
                instruments=instruments,
                exporter=_test_exporter,
            )

        if not is_metrics_enabled():
            print(Fore.YELLOW + "Metrics are disabled" + Fore.RESET)
        else:
            metrics_headers = {
                **(os.getenv("ELIXIR_METRICS_HEADERS") or metrics_headers or headers),
                "Authorization": f"Bearer {Elixir.api_key}",
            }

            MetricsWrapper.set_static_params(
                resource_attributes, Elixir.api_endpoint, metrics_headers
            )

            Elixir.__metrics_wrapper = MetricsWrapper(reader=_test_metrics_reader)

    def track_user(user_id: str, user_properties: Optional[dict] = None) -> None:
        association_properties = {"user_id": user_id}
        if user_properties:
            association_properties["user_properties"] = json.dumps(user_properties)
        Elixir.set_association_properties(association_properties)

    def track_conversation(
        conversation_id: str, conversation_properties: Optional[dict] = None
    ) -> None:
        association_properties = {"conversation_id": conversation_id}
        if conversation_properties:
            association_properties["conversation_properties"] = json.dumps(
                conversation_properties
            )
        Elixir.set_association_properties(association_properties)

    def set_association_properties(properties: dict) -> None:
        Elixir.association_properties = Elixir.association_properties | properties
        set_association_properties(Elixir.association_properties)

    async def upload_audio(
        conversation_id: str,
        audio_url: Optional[str] = None,
        audio_buffer: Optional[bytes] = None,
        audio_content_type: Optional[str] = None,
    ) -> None:
        if audio_buffer and audio_content_type:
            return await post_file_request(
                endpoint="/ingestion/audio-file",
                api_key=Elixir.api_key,
                body={"conversation_id": conversation_id},
                file_content=audio_buffer,
                content_type=audio_content_type,
            )

        if audio_url:
            return await post_body_request(
                endpoint="/ingestion/audio-url",
                api_key=Elixir.api_key,
                body={
                    "audio_url": audio_url,
                    "conversation_id": conversation_id,
                },
            )

        raise ValueError("Either audio_url or audio_buffer must be provided")
