import pytest
import time
from unittest.mock import patch
from uuid import uuid4

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.node import NodeExecutionFulfilledBody, NodeExecutionFulfilledEvent
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.runner.runner import WorkflowRunner

from tests.workflows.workflow_stream_fails.workflow import AlwaysFailsWorkflow


@pytest.fixture
def mock_stream(mocker):
    return mocker.patch("vellum.workflows.workflows.base.WorkflowRunner._stream")


def test_run_workflow__stream_fails(mock_stream):
    # GIVEN a workflow that will always fail within its `_stream` method
    workflow = AlwaysFailsWorkflow()
    mock_stream.side_effect = Exception("Stream failed")

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed with a failure
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the correct error is raised
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message == "An unexpected error occurred while streaming Workflow events"


def test_run_workflow__stream_crash():
    # GIVEN a workflow that will always fail within its `_stream` method
    workflow = AlwaysFailsWorkflow()

    # AND the failure happens after the _stream thread has started
    def mock_stream_side_effect(self):
        time.sleep(0.2)  # Wait for the _stream thread to start
        raise Exception("Stream failed")

    # WHEN we run the workflow
    with patch.object(WorkflowRunner, "_stream", new=mock_stream_side_effect):
        terminal_event = workflow.run()

    # THEN the workflow should have completed with a failure
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the correct error is raised
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message == "An unexpected error occurred while streaming Workflow events"


def test_run_workflow__stream_fails__last_event_is_not_workflow_event():
    # GIVEN a workflow that will always fail within its `_stream` method
    workflow = AlwaysFailsWorkflow()

    # AND the failure happens after a NODE FULFILLED event
    def mock_stream_side_effect(self):
        self._workflow_event_outer_queue.put(
            NodeExecutionFulfilledEvent(
                trace_id=uuid4(),
                span_id=uuid4(),
                body=NodeExecutionFulfilledBody(
                    node_definition=BaseNode,
                    outputs=BaseOutputs(),
                ),
            )
        )
        raise Exception("Stream failed")

    # WHEN we run the workflow
    with patch.object(WorkflowRunner, "_stream", new=mock_stream_side_effect):
        terminal_event = workflow.run()

    # THEN the workflow should have completed with a failure
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the correct error is raised
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message == "An unexpected error occurred while streaming Workflow events"
