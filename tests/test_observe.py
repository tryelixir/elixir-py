from elixir.decorators import observe


def test_base_name(exporter):
    @observe()
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.name == "run_workflow"


def test_custom_name(exporter):
    @observe("custom")
    def run_workflow():
        pass

    run_workflow()

    spans = exporter.get_finished_spans()
    workflow_span = spans[0]
    assert workflow_span.name == "custom"
