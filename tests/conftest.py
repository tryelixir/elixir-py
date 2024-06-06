"""Unit tests configuration module."""

import os
from unittest.mock import PropertyMock, patch
import pytest
from elixir import Elixir
from elixir.instruments import Instruments
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.trace import set_tracer_provider


class OTelReceivers:
    def __init__(self):
        self.exporter = InMemorySpanExporter()
        self.metrics_reader = InMemoryMetricReader()


@pytest.fixture
def openai_client():
    from openai import OpenAI

    return OpenAI()


@pytest.fixture(autouse=True)
def environment():
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = "test_api_key"


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "ignore_hosts": ["openaipublic.blob.core.windows.net"],
        "record_mode": "once",
    }


@pytest.fixture(autouse=True, scope="session")
def mock_once_instances():
    from opentelemetry.util._once import Once

    original_do_once = Once.do_once

    def new_do_once(self, func):
        with self._lock:
            self._done = False
        return original_do_once(self, func)

    with patch.object(Once, "do_once", new_do_once):
        yield


@pytest.fixture(autouse=True, scope="session")
def mock_is_instrumented():
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

    with patch.object(
        BaseInstrumentor, "_is_instrumented_by_opentelemetry", new_callable=PropertyMock
    ) as mock_property:
        mock_property.return_value = False
        yield


@pytest.fixture(autouse=True, scope="function")
def reset_otel_context():
    from opentelemetry.context import Context, attach, detach

    context = Context()
    token = attach(context)

    yield

    detach(token)


@pytest.fixture(autouse=True, scope="function")
def manage_singletons():
    from elixir.metrics.metrics import MetricsWrapper
    from elixir.tracing.tracing import TracerWrapper

    os.environ["ELIXIR_METRICS_ENABLED"] = "true"
    os.environ["ELIXIR_TRACE_ENABLED"] = "true"

    # Clear singletons before each test
    if hasattr(TracerWrapper, "instance"):
        del TracerWrapper.instance
    if hasattr(MetricsWrapper, "instance"):
        del MetricsWrapper.instance

    set_tracer_provider(None)

    yield


@pytest.fixture(scope="function")
def metrics_reader():
    receivers = OTelReceivers()
    Elixir.init(
        disable_batch=True,
        _test_exporter=receivers.exporter,
        _test_metrics_reader=receivers.metrics_reader,
    )
    return receivers.metrics_reader


@pytest.fixture(scope="function")
def exporter():
    receivers = OTelReceivers()
    Elixir.init(
        app_name="test",
        resource_attributes={"something": "yes"},
        disable_batch=True,
        _test_exporter=receivers.exporter,
        _test_metrics_reader=receivers.metrics_reader,
    )
    return receivers.exporter


@pytest.fixture(scope="function")
def exporter_with_custom_instrumentations():
    receivers = OTelReceivers()
    Elixir.init(
        disable_batch=True,
        instruments=[i for i in Instruments],
        _test_exporter=receivers.exporter,
        _test_metrics_reader=receivers.metrics_reader,
    )
    return receivers.exporter


@pytest.fixture(scope="function")
def exporter_with_no_metrics():
    os.environ["ELIXIR_METRICS_ENABLED"] = "false"

    receivers = OTelReceivers()
    Elixir.init(
        disable_batch=True,
        instruments=[i for i in Instruments],
        _test_exporter=receivers.exporter,
        _test_metrics_reader=receivers.metrics_reader,
    )
    return receivers.exporter
