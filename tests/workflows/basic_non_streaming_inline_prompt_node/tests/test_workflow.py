from uuid import uuid4

from vellum import RejectedAdHocExecutePromptEvent, VellumError
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_non_streaming_inline_prompt_node.workflow import (
    BasicNonStreamingInlinePromptWorkflow,
    WorkflowInputs,
)


def test_non_streaming_workflow__timeout(vellum_adhoc_prompt_client):
    """Confirm that when a timeout occurs in non-streaming mode, we receive both node and workflow rejection events"""

    # GIVEN a non-streaming workflow that's set up to hit a Prompt
    workflow = BasicNonStreamingInlinePromptWorkflow()

    # AND the prompt will fail with a timeout error
    expected_error = VellumError(
        message="Provider Error: OpenAI error: stream timeout",
        code="PROVIDER_ERROR",
    )

    rejected_event = RejectedAdHocExecutePromptEvent(
        execution_id=str(uuid4()),
        error=expected_error,
    )

    vellum_adhoc_prompt_client.adhoc_execute_prompt.return_value = rejected_event

    # WHEN we stream the workflow
    result = workflow.stream(inputs=WorkflowInputs(noun="color"), event_filter=all_workflow_event_filter)
    events = list(result)

    # THEN we should receive workflow initiation event
    assert events[0].name == "workflow.execution.initiated"

    node_initiated_event = events[1]
    assert node_initiated_event.name == "node.execution.initiated"

    # AND we should receive a node rejection event
    node_rejected_event = events[2]
    assert node_rejected_event.name == "node.execution.rejected"
    assert node_rejected_event.error.code.value == "PROVIDER_ERROR"
    assert node_rejected_event.error.message == "Provider Error: OpenAI error: stream timeout"

    # AND we should receive a workflow rejection event
    workflow_rejected_event = events[3]
    assert workflow_rejected_event.name == "workflow.execution.rejected"
    assert workflow_rejected_event.error.code.value == "PROVIDER_ERROR"
    assert workflow_rejected_event.error.message == "Provider Error: OpenAI error: stream timeout"

    assert len(events) == 4
