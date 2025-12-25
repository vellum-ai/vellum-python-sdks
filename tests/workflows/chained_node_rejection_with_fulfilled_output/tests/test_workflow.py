from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    PromptOutput,
    StreamingAdHocExecutePromptEvent,
    StringVellumValue,
)
from vellum.workflows.errors import WorkflowErrorCode

from tests.workflows.chained_node_rejection_with_fulfilled_output.workflow import (
    ChainedNodeRejectionWithFulfilledOutputWorkflow,
)


def test_stream_workflow__chained_node_rejection_with_fulfilled_output(vellum_adhoc_prompt_client):
    """
    Tests that a workflow is rejected when a node fails, even if the workflow output
    was already resolved from a successful upstream node that streamed its output.
    """

    # GIVEN a workflow where the first node is an inline prompt node that succeeds
    # and the second node fails, but the workflow output points to the first node's output
    workflow = ChainedNodeRejectionWithFulfilledOutputWorkflow()

    # AND the prompt will return 3 streaming chunks before fulfilling
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Hello world"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value="Hello"), output_index=0
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value=" "), output_index=0
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value="world"), output_index=0
            ),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is streamed
    events = list(workflow.stream())

    # THEN the last event should be a rejection event (not fulfilled)
    terminal_event = events[-1]
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the error should be from the second node's failure
    assert terminal_event.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert terminal_event.error.message == "Second node failed"
