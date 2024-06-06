"""Unit tests configuration module."""

import os
from openai import OpenAI
import pytest
from elixir import Elixir
from elixir.instruments import Instruments
from elixir.tracing.tracing import TracerWrapper
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from tests.utils.in_memory_metrics_exporter import InMemoryMetricExporter

pytest_plugins = []


@pytest.fixture
def openai_client():
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


@pytest.fixture(autouse=True)
def clear_exporter(exporter):
    exporter.clear()


@pytest.fixture(scope="session")
def exporter():
    exporter = InMemorySpanExporter()
    metrics_exporter = InMemoryMetricExporter()

    Elixir.init(
        app_name="test",
        resource_attributes={"something": "yes"},
        disable_batch=True,
        _test_exporter=exporter,
        _test_metrics_exporter=metrics_exporter,
    )

    return exporter


@pytest.fixture(scope="session")
def exporter_with_custom_instrumentations():
    # Clear singleton if existed
    if hasattr(TracerWrapper, "instance"):
        _trace_wrapper_instance = TracerWrapper.instance
        del TracerWrapper.instance

    exporter = InMemorySpanExporter()
    metrics_exporter = InMemoryMetricExporter()

    Elixir.init(
        _test_exporter=exporter,
        _test_metrics_exporter=metrics_exporter,
        disable_batch=True,
        instruments=[i for i in Instruments],
    )

    yield exporter

    # Restore singleton if any
    if _trace_wrapper_instance:
        TracerWrapper.instance = _trace_wrapper_instance


@pytest.fixture(scope="session")
def exporter_with_no_metrics():
    # Clear singleton if existed
    if hasattr(TracerWrapper, "instance"):
        _trace_wrapper_instance = TracerWrapper.instance
        del TracerWrapper.instance

    os.environ["ELIXIR_METRICS_ENABLED"] = "false"

    exporter = InMemorySpanExporter()
    metrics_exporter = InMemoryMetricExporter()

    Elixir.init(
        _test_exporter=exporter,
        _test_metrics_exporter=metrics_exporter,
        disable_batch=True,
    )

    yield exporter

    # Restore singleton if any
    if _trace_wrapper_instance:
        TracerWrapper.instance = _trace_wrapper_instance
        os.environ["ELIXIR_METRICS_ENABLED"] = "true"
