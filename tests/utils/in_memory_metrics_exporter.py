from typing import Sequence
from opentelemetry.sdk.metrics.export import MetricExporter, Metric, MetricExportResult


# Implementation: https://github.com/open-telemetry/opentelemetry-python/blob/4febd337b019ea013ccaab74893bd9883eb59000/opentelemetry-sdk/tests/metrics/test_metrics.py#L475
class InMemoryMetricExporter(MetricExporter):
    def __init__(self):
        super().__init__()
        self.metrics = {}
        self._counter = 0

    def export(
        self,
        metrics: Sequence[Metric],
        timeout_millis: float = 10_000,
        **kwargs,
    ) -> MetricExportResult:
        self.metrics[self._counter] = metrics
        self._counter += 1
        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        pass

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        return True
