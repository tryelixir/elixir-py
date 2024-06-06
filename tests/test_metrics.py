from opentelemetry.sdk.metrics.export import MetricsData


def test_metrics(metrics_reader, openai_client):
    openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
    )
    metrics: MetricsData = metrics_reader.get_metrics_data()
    metric = metrics.resource_metrics[0].scope_metrics[0].metrics[0]

    assert metric.name == "gen_ai.client.token.usage"

    data_point = metric.data.data_points[0]
    assert data_point.attributes["gen_ai.system"] == "openai"
    assert data_point.attributes["gen_ai.response.model"] == "gpt-3.5-turbo-0125"
