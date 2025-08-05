from uuid import uuid4

from vellum.workflows.context import execution_context
from vellum.workflows.events.types import NodeParentContext
from vellum.workflows.types.definition import CodeResourceDefinition
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_parent_context.basic_workflow import TrivialWorkflow


def test_run_workflow__happy_path():
    workflow = TrivialWorkflow()
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.parent is not None
    assert terminal_event.parent.type == "EXTERNAL"


def test_stream_workflow__happy_path():
    workflow = TrivialWorkflow()
    events = list(workflow.stream(event_filter=root_workflow_event_filter))

    assert len(events) == 4

    assert events[0].name == "workflow.execution.initiated"
    assert events[0].parent is not None
    assert events[0].parent.type == "EXTERNAL"

    assert events[1].name == "node.execution.initiated"
    parent_context = events[1].parent.model_dump() if events[1].parent else {}
    assert parent_context.get("type") == "WORKFLOW"
    assert parent_context.get("parent") is not None
    assert parent_context.get("parent")["type"] == "EXTERNAL"
    assert parent_context.get("workflow_definition") is not None

    assert events[-1].name == "workflow.execution.fulfilled"
    assert events[-1].parent is not None
    assert events[-1].parent.type == "EXTERNAL"


def test_stream_workflow__happy_path_inital_context():
    initial_parent_context_json = {
        "span_id": uuid4(),
        "node_definition": {
            "id": uuid4(),
            "module": ["example", "test"],
            "name": "node_workflow",
        },
        "parent": None,
        "type": "WORKFLOW_NODE",
    }
    initial_parent_context_json["parent"] = {
        "span_id": uuid4(),
        "node_definition": {
            "id": uuid4(),
            "module": ["example", "test"],
            "name": "node_workflow",
        },
        "parent": None,
        "type": "WORKFLOW_NODE",
    }
    initial_parent_context = NodeParentContext(**initial_parent_context_json)
    assert isinstance(initial_parent_context, NodeParentContext)
    assert initial_parent_context is not None
    assert initial_parent_context.parent is not None
    assert type(initial_parent_context.node_definition) is CodeResourceDefinition

    with execution_context(parent_context=initial_parent_context):
        workflow = TrivialWorkflow()

        events = list(workflow.stream(event_filter=root_workflow_event_filter))

    assert len(events) == 4

    assert events[0].name == "workflow.execution.initiated"
    assert events[0].parent is not None
    assert events[0].parent == initial_parent_context

    assert events[1].name == "node.execution.initiated"
    assert events[1].parent is not None
    parent_context = events[1].parent.model_dump()
    assert parent_context is not None
    assert parent_context.get("type") == "WORKFLOW"
    assert parent_context.get("parent") == initial_parent_context_json
    assert parent_context.get("workflow_definition") is not None

    assert events[-1].name == "workflow.execution.fulfilled"
    assert events[-1].parent == initial_parent_context
