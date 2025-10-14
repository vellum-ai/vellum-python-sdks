from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.coalesce_output_streaming.workflow import CoalesceOutputStreamingTestWorkflow


def test_workflow_stream__coalesce_output_multiple_event(vellum_adhoc_prompt_client):
    """
    Tests that streaming a workflow with multiple Prompt nodes coalesced in the terminal
    node can still stream, maintaining backwards compatibility with the legacy workflow runner.
    """

    workflow = CoalesceOutputStreamingTestWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Hello, World!"),
    ]

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value="Hello,"),
                output_index=0,
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value=" World!"),
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
    stream = workflow.stream()
    events = list(stream)

    # THEN the workflow should have been fulfilled
    assert events[-1].name == "workflow.execution.fulfilled", events[-1].body

    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]
    assert len(streaming_events) == 4, f"Expected 4 streaming event, but got {len(streaming_events)}"

    # AND the streaming events should have the correct output values
    first_streaming_event = streaming_events[0]
    assert first_streaming_event.output.is_initiated
    assert first_streaming_event.output.name == "final_score"

    second_streaming_event = streaming_events[1]
    assert second_streaming_event.output.is_streaming
    assert second_streaming_event.output.name == "final_score"
    assert second_streaming_event.output.delta == "Hello,"

    third_streaming_event = streaming_events[2]
    assert third_streaming_event.output.is_streaming
    assert third_streaming_event.output.name == "final_score"
    assert third_streaming_event.output.delta == " World!"

    fourth_streaming_event = streaming_events[3]
    assert fourth_streaming_event.output.is_fulfilled
    assert fourth_streaming_event.output.name == "final_score"
    assert fourth_streaming_event.output.value == "Hello, World!"
