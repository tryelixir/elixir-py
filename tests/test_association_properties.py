import json
from elixir import Elixir
from elixir.decorators import observe


def test_user_without_traits(exporter):
    Elixir.identify("user1")

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.attributes["elixir.association.properties.user_id"] == "user1"
    assert (
        workflow_span.attributes.get("elixir.association.properties.user_properties")
        is None
    )


def test_user_with_traits(exporter):
    Elixir.identify("user1", {"name": "John Doe"})

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.attributes["elixir.association.properties.user_id"] == "user1"
    assert workflow_span.attributes[
        "elixir.association.properties.user_properties"
    ] == json.dumps({"name": "John Doe"})


def test_conversation_without_traits(exporter):
    Elixir.init_conversation("conversation1")

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert (
        workflow_span.attributes["elixir.association.properties.conversation_id"]
        == "conversation1"
    )
    assert (
        workflow_span.attributes.get(
            "elixir.association.properties.conversation_properties"
        )
        is None
    )


def test_conversation_with_traits(exporter):
    Elixir.init_conversation("conversation1", {"type": "sales_call"})

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert (
        workflow_span.attributes["elixir.association.properties.conversation_id"]
        == "conversation1"
    )
    assert workflow_span.attributes[
        "elixir.association.properties.conversation_properties"
    ] == json.dumps({"type": "sales_call"})


def test_association_properties(exporter):
    Elixir.set_association_properties({"test": "123"})

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.attributes["elixir.association.properties.test"] == "123"


def test_association_properties_with_user_and_conversation(exporter):
    Elixir.identify("user1")
    Elixir.init_conversation("conversation1")

    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.attributes["elixir.association.properties.user_id"] == "user1"
    assert (
        workflow_span.attributes["elixir.association.properties.conversation_id"]
        == "conversation1"
    )
