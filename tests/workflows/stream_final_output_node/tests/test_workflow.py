from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.stream_final_output_node.workflow import StreamFinalOutputWorkflow


def test_workflow__happy_path(vellum_adhoc_prompt_client):
    # GIVEN a workflow with a prompt and a final output
    workflow = StreamFinalOutputWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Hello, world!"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
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

    # THEN there should be a workflow.execution.streaming event emitted
    streaming_events = [event for event in events if event.name == "workflow.execution.streaming"]
    assert len(streaming_events) == 1

    # AND the streaming event should have an output
    streaming_event = streaming_events[0]
    assert streaming_event.output.value == "Hello, world!"
