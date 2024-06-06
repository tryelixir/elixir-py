import os
import sys

from typing import Optional, Set
from colorama import Fore
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.sdk.metrics.export import MetricReader

from elixir.config.constants import ELIXIR_COLLECTOR_URL
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

        api_endpoint = ELIXIR_COLLECTOR_URL
        api_key = os.getenv("ELIXIR_API_KEY") or api_key

        if not is_tracing_enabled():
            print(Fore.YELLOW + "Tracing is disabled" + Fore.RESET)
        else:
            headers = {
                **(os.getenv("ELIXIR_HEADERS") or headers),
                "Authorization": f"Bearer {api_key}",
            }

            # Tracer init
            resource_attributes.update({SERVICE_NAME: app_name})
            TracerWrapper.set_static_params(resource_attributes, api_endpoint, headers)
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
                "Authorization": f"Bearer {api_key}",
            }

            MetricsWrapper.set_static_params(
                resource_attributes, api_endpoint, metrics_headers
            )

            Elixir.__metrics_wrapper = MetricsWrapper(reader=_test_metrics_reader)

    def set_association_properties(properties: dict) -> None:
        set_association_properties(properties)
