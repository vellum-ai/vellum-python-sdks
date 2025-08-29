from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.events.types import VellumCodeResourceDefinition
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_node_rejection.workflow import BasicRejectedWorkflow


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a node that will fail
    workflow = BasicRejectedWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the output error message should be as expected
    assert terminal_event.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert terminal_event.error.message == "Node was rejected"

    # AND the traceback should contain meaningful stack trace information
    assert terminal_event.body.traceback is not None
    assert "NodeException" in terminal_event.body.traceback
    assert "Node was rejected" in terminal_event.body.traceback
    assert "workflow.py" in terminal_event.body.traceback
    assert "in run" in terminal_event.body.traceback


def test_stream_workflow__parent_context():
    # GIVEN a workflow that references a node that will fail
    workflow = BasicRejectedWorkflow()

    # WHEN the workflow is streamed
    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)

    # THEN the parent context be as expected
    workflow_rejected_event = events[-1]
    assert workflow_rejected_event.name == "workflow.execution.rejected"
    assert workflow_rejected_event.parent is not None
    assert workflow_rejected_event.parent.type == "EXTERNAL"

    node_rejected_event = events[-2]
    assert node_rejected_event.name == "node.execution.rejected"
    assert node_rejected_event.parent is not None
    assert node_rejected_event.parent.type == "WORKFLOW"
    assert node_rejected_event.parent.workflow_definition == VellumCodeResourceDefinition.encode(BasicRejectedWorkflow)
    assert node_rejected_event.parent.span_id == workflow_rejected_event.span_id
