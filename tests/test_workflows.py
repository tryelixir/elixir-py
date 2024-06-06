import pytest
import json
from openai import OpenAI
from elixir.decorators import observe, aobserve


@pytest.mark.vcr
def test_simple_workflow(exporter, openai_client):
    @observe(name="something_creator")
    def create_something(what: str, subject: str):
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Tell me a {what} about {subject}"}],
        )
        return completion.choices[0].message.content

    @observe(name="pirate_joke_generator")
    def joke_workflow():
        return create_something("joke", subject="OpenTelemetry")

    joke = joke_workflow()

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "openai.chat",
        "something_creator",
        "pirate_joke_generator",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["gen_ai.prompt.0.content"]
        == "Tell me a joke about OpenTelemetry"
    )
    assert open_ai_span.attributes.get("gen_ai.completion.0.content")

    task_span = spans[1]
    assert json.loads(task_span.attributes["elixir.entity.input"]) == {
        "args": ["joke"],
        "kwargs": {"subject": "OpenTelemetry"},
    }

    assert json.loads(task_span.attributes.get("elixir.entity.output")) == joke


@pytest.mark.vcr
def test_streaming_workflow(exporter, openai_client):

    @observe(name="pirate_joke_generator")
    def joke_workflow():
        response_stream = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Tell me a joke about OpenTelemetry"}
            ],
            stream=True,
        )
        for chunk in response_stream:
            yield chunk

    joke_stream = joke_workflow()
    for _ in joke_stream:
        pass

    spans = exporter.get_finished_spans()
    assert set([span.name for span in spans]) == set(
        [
            "openai.chat",
            "pirate_joke_generator",
        ]
    )
    workflow_span = next(span for span in spans if span.name == "pirate_joke_generator")
    openai_span = next(span for span in spans if span.name == "openai.chat")

    assert openai_span.parent.span_id == workflow_span.context.span_id
    assert openai_span.end_time <= workflow_span.end_time


def test_unserializable_workflow(exporter):
    @observe(name="unserializable_task")
    def unserializable_task(obj: object):
        return object()

    unserializable_task(object())

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == ["unserializable_task"]


@pytest.mark.asyncio
async def test_unserializable_async_workflow(exporter):
    @aobserve(name="unserializable_task")
    async def unserializable_task(obj: object):
        return object()

    await unserializable_task(object())

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == ["unserializable_task"]
