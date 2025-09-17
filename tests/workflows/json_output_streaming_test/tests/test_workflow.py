from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.json_vellum_value import JsonVellumValue
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.streaming_execute_prompt_event import StreamingExecutePromptEvent

from tests.workflows.json_output_streaming_test.workflow import JsonOutputStreamingTestWorkflow


def test_workflow_stream__json_output_single_event(vellum_adhoc_prompt_client):
    """
    Tests that streaming a workflow with JSON output reference produces only one streaming event.
    This test is expected to fail on main due to multiple streaming events being emitted.
    """

    workflow = JsonOutputStreamingTestWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        JsonVellumValue(value={"score": 35, "reasoning": "Hello World"}),
    ]

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=JsonVellumValue(value='{"score": 35,'),
                output_index=0,
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id,
                output=JsonVellumValue(value=' "reasoning": "Hello World"}'),
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

    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]
    assert len(streaming_events) == 1, f"Expected 1 streaming event, but got {len(streaming_events)}"

    # AND the streaming event should have the correct output value
    streaming_event = streaming_events[0]
    assert streaming_event.output.value == 35
