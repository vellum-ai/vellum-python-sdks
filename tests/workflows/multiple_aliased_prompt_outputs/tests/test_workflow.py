import pytest
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.multiple_aliased_prompt_outputs.workflow import Inputs, MultipleAliasedPromptOutputsWorkflow


@pytest.mark.xfail(reason="Multiple workflow outputs aliasing the same prompt text only stream for the first output")
def test_workflow_stream__multiple_aliased_outputs(vellum_adhoc_prompt_client):
    """
    Tests that streaming events are emitted for ALL workflow outputs that alias
    the same prompt node's text output, not just the first one.

    This reproduces the issue where the early return in __directly_emit_workflow_output__
    causes only the first matching workflow output to receive streaming events.
    """

    # GIVEN a workflow with two outputs that both reference Chat.Outputs.text
    workflow = MultipleAliasedPromptOutputsWorkflow()

    # AND we know what the Prompt will respond with
    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        expected_outputs: List[PromptOutput] = [
            StringVellumValue(value="Ocean waves crash soft"),
        ]
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value="Ocean"),
                output_index=0,
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value=" waves"),
                output_index=0,
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value=" crash soft"),
                output_index=0,
            ),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is streamed
    stream = workflow.stream(inputs=Inputs())
    events = list(stream)

    # THEN the workflow should have been fulfilled
    assert events[-1].name == "workflow.execution.fulfilled", events[-1]

    # AND there should be workflow.execution.streaming events for both outputs
    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]

    # Filter for streaming events related to the 'response' output
    response_streaming_events = [event for event in streaming_events if event.output.name == "response"]

    # Filter for streaming events related to the 'response_copy' output
    response_copy_streaming_events = [event for event in streaming_events if event.output.name == "response_copy"]

    # THEN we expect streaming events for the 'response' output
    response_streaming_chunks = [e for e in response_streaming_events if e.output.is_streaming]
    assert (
        len(response_streaming_chunks) == 3
    ), f"Expected 3 streaming chunk events for 'response', got {len(response_streaming_chunks)}"

    # AND we expect streaming events for the 'response_copy' output as well
    response_copy_streaming_chunks = [e for e in response_copy_streaming_events if e.output.is_streaming]
    assert (
        len(response_copy_streaming_chunks) == 3
    ), f"Expected 3 streaming chunk events for 'response_copy', got {len(response_copy_streaming_chunks)}"

    # AND both outputs should have the same streaming content
    assert response_streaming_chunks[0].output.delta == "Ocean"
    assert response_streaming_chunks[1].output.delta == " waves"
    assert response_streaming_chunks[2].output.delta == " crash soft"

    assert response_copy_streaming_chunks[0].output.delta == "Ocean"
    assert response_copy_streaming_chunks[1].output.delta == " waves"
    assert response_copy_streaming_chunks[2].output.delta == " crash soft"
