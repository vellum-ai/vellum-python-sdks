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

from tests.workflows.text_node_streaming_prompt.workflow import TextNodeStreamingPromptWorkflow


def test_streaming_workflow__one_streaming_event(vellum_adhoc_prompt_client):
    """
    Test that the workflow correctly does not stream when the final output points to a text node.
    """

    workflow = TextNodeStreamingPromptWorkflow()

    # AND we know what the Prompt will respond with (3 text deltas)
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Hello, this is a test!"),
    ]

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value="Hello, "),
                output_index=0,
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value="this is "),
                output_index=0,
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id,
                output=StringVellumValue(value="a test!"),
                output_index=0,
            ),
            FulfilledAdHocExecutePromptEvent(
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

    final_output_events = [e for e in streaming_events if e.output.name == "final_output"]

    # THEN there should be one final output event
    assert len(final_output_events) == 1

    assert final_output_events[0].output.is_fulfilled
    assert final_output_events[0].output.name == "final_output"
    assert final_output_events[0].output.value == "Hello from base node"
