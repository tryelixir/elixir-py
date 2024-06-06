import pytest
from elixir.decorators import observe


def test_nested_tasks(exporter):
    @observe(name="some_workflow")
    def some_workflow():
        return outer_task()

    @observe(name="outer_task")
    def outer_task():
        return inner_task()

    @observe(name="inner_task")
    def inner_task():
        return inner_inner_task()

    @observe(name="inner_inner_task")
    def inner_inner_task():
        return

    some_workflow()

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "inner_inner_task",
        "inner_task",
        "outer_task",
        "some_workflow",
    ]

    inner_inner_task_span = spans[0]
    inner_task_span = spans[1]
    outer_task_span = spans[2]
    some_workflow_span = spans[3]
    assert (
        inner_inner_task_span.attributes["elixir.entity.name"]
        == "some_workflow.outer_task.inner_task.inner_inner_task"
    )
    assert (
        inner_task_span.attributes["elixir.entity.name"]
        == "some_workflow.outer_task.inner_task"
    )
    assert (
        outer_task_span.attributes["elixir.entity.name"] == "some_workflow.outer_task"
    )
    assert some_workflow_span.attributes["elixir.entity.name"] == "some_workflow"
