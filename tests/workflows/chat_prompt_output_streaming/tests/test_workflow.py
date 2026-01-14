import pytest
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.chat_prompt_output_streaming.workflow import ChatPromptOutputStreamingWorkflow, Inputs


@pytest.mark.xfail(
    reason="Chat Prompt Output Streaming does not stream at the workflow level when there's an intermediate node"
)
def test_workflow_stream__chat_prompt_output_streaming(vellum_adhoc_prompt_client):
    """
    Tests that streaming a workflow with multiple Prompt nodes in sequence
    properly streams the final node's output at the workflow level.

    This reproduces the issue where Chat Prompt Output Streaming does not stream
    at the workflow level when there's an intermediate node between the prompt
    and the workflow output.
    """

    # GIVEN a workflow with two prompt nodes in sequence (Chat >> HaikuHelper)
    workflow = ChatPromptOutputStreamingWorkflow()

    call_count = 0

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[ExecutePromptEvent]:
        nonlocal call_count
        call_count += 1
        execution_id = str(uuid4())

        if call_count == 1:
            # First call: Chat node generates a haiku
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
        else:
            # Second call: HaikuHelper improves the haiku
            expected_outputs = [
                StringVellumValue(value="Ocean waves crash soft, Salt spray kisses the shore, Peace in every drop"),
            ]
            events = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value="Ocean waves"),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value=" crash soft,"),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value=" Salt spray kisses the shore,"),
                    output_index=0,
                ),
                StreamingExecutePromptEvent(
                    execution_id=execution_id,
                    output=StringVellumValue(value=" Peace in every drop"),
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

    # AND there should be workflow.execution.streaming events for the final output
    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]

    # Filter for streaming events related to the 'response' output
    response_streaming_events = [event for event in streaming_events if event.output.name == "response"]

    # THEN we expect streaming events for the HaikuHelper output at the workflow level
    # This is the key assertion - we expect 6 streaming events:
    # 1 initiated + 4 streaming chunks + 1 fulfilled
    initiated_events = [e for e in response_streaming_events if e.output.is_initiated]
    streaming_chunk_events = [e for e in response_streaming_events if e.output.is_streaming]
    fulfilled_events = [e for e in response_streaming_events if e.output.is_fulfilled]

    assert len(initiated_events) == 1, f"Expected 1 initiated event, got {len(initiated_events)}"
    assert len(streaming_chunk_events) == 4, f"Expected 4 streaming chunk events, got {len(streaming_chunk_events)}"
    assert len(fulfilled_events) == 1, f"Expected 1 fulfilled event, got {len(fulfilled_events)}"

    # AND the streaming chunks should contain the expected content
    assert streaming_chunk_events[0].output.delta == "Ocean waves"
    assert streaming_chunk_events[1].output.delta == " crash soft,"
    assert streaming_chunk_events[2].output.delta == " Salt spray kisses the shore,"
    assert streaming_chunk_events[3].output.delta == " Peace in every drop"

    # AND the fulfilled event should have the complete value
    assert (
        fulfilled_events[0].output.value == "Ocean waves crash soft, Salt spray kisses the shore, Peace in every drop"
    )
